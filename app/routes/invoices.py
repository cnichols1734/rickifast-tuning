from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from datetime import date, datetime, timezone
from app import db
from app.models import Client, Invoice, InvoiceItem, Payment
from app.email_utils import send_invoice_email

invoices = Blueprint('invoices', __name__, url_prefix='/invoices')


@invoices.route('/')
@login_required
def index():
    status_filter = request.args.get('status', 'all')

    # Single query — items & payments already eager-loaded via selectin
    all_invoices = Invoice.query.options(
        db.joinedload(Invoice.client)
    ).order_by(Invoice.created_at.desc()).all()

    # Compute each invoice's status once
    invoice_with_status = [(inv, inv.get_status()) for inv in all_invoices]

    counts = {'all': len(all_invoices)}
    for s in ['draft', 'sent', 'partial', 'paid', 'overdue']:
        counts[s] = sum(1 for _, st in invoice_with_status if st == s)

    if status_filter != 'all':
        filtered = [inv for inv, st in invoice_with_status if st == status_filter]
    else:
        filtered = all_invoices

    return render_template('invoices/index.html', invoices=filtered,
                           status_filter=status_filter, counts=counts)


@invoices.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        client_id = request.form.get('client_id', type=int)
        if not client_id:
            flash('Please select a client.', 'error')
            return redirect(url_for('invoices.create'))

        status = request.form.get('status', 'draft')
        due_date_str = request.form.get('due_date', '')
        due_date = None
        if due_date_str:
            try:
                due_date = date.fromisoformat(due_date_str)
            except ValueError:
                pass

        tax_rate = request.form.get('tax_rate', 0.0825, type=float)
        notes = request.form.get('notes', '').strip()

        invoice = Invoice(
            client_id=client_id,
            invoice_number=Invoice.generate_number(),
            status=status,
            due_date=due_date,
            tax_rate=tax_rate,
            notes=notes,
        )
        db.session.add(invoice)
        db.session.flush()

        descriptions = request.form.getlist('item_description[]')
        quantities = request.form.getlist('item_quantity[]')
        prices = request.form.getlist('item_price[]')
        taxables = request.form.getlist('item_taxable[]')

        for i, desc in enumerate(descriptions):
            if not desc.strip():
                continue
            try:
                qty = float(quantities[i]) if i < len(quantities) else 1
                price = float(prices[i]) if i < len(prices) else 0
            except (ValueError, IndexError):
                continue

            taxable = str(i) in taxables

            item = InvoiceItem(
                invoice_id=invoice.id,
                description=desc.strip(),
                quantity=qty,
                unit_price=price,
                taxable=taxable,
            )
            db.session.add(item)

        db.session.commit()
        flash('Invoice created.', 'success')
        return redirect(url_for('invoices.view', id=invoice.id))

    clients = Client.query.order_by(Client.last_name).all()
    next_number = Invoice.generate_number()
    return render_template('invoices/form.html', invoice=None, clients=clients,
                           next_number=next_number, editing=False)


@invoices.route('/<int:id>')
@login_required
def view(id):
    invoice = Invoice.query.options(
        db.joinedload(Invoice.client)
    ).get_or_404(id)
    return render_template('invoices/view.html', invoice=invoice, today=date.today().isoformat())


@invoices.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    invoice = db.get_or_404(Invoice, id)

    if request.method == 'POST':
        invoice.client_id = request.form.get('client_id', type=int)
        invoice.status = request.form.get('status', 'draft')
        invoice.tax_rate = request.form.get('tax_rate', 0.0825, type=float)
        invoice.notes = request.form.get('notes', '').strip()

        due_date_str = request.form.get('due_date', '')
        invoice.due_date = date.fromisoformat(due_date_str) if due_date_str else None

        # Clear existing items and rebuild
        InvoiceItem.query.filter_by(invoice_id=invoice.id).delete()

        descriptions = request.form.getlist('item_description[]')
        quantities = request.form.getlist('item_quantity[]')
        prices = request.form.getlist('item_price[]')
        taxables = request.form.getlist('item_taxable[]')

        for i, desc in enumerate(descriptions):
            if not desc.strip():
                continue
            try:
                qty = float(quantities[i]) if i < len(quantities) else 1
                price = float(prices[i]) if i < len(prices) else 0
            except (ValueError, IndexError):
                continue

            taxable = str(i) in taxables

            item = InvoiceItem(
                invoice_id=invoice.id,
                description=desc.strip(),
                quantity=qty,
                unit_price=price,
                taxable=taxable,
            )
            db.session.add(item)

        db.session.commit()
        flash('Invoice updated.', 'success')
        return redirect(url_for('invoices.view', id=invoice.id))

    clients = Client.query.order_by(Client.last_name).all()
    return render_template('invoices/form.html', invoice=invoice, clients=clients,
                           next_number=invoice.invoice_number, editing=True)


@invoices.route('/<int:id>/print')
@login_required
def print_view(id):
    invoice = db.get_or_404(Invoice, id)
    return render_template('invoices/print.html', invoice=invoice)


@invoices.route('/<int:id>/duplicate', methods=['POST'])
@login_required
def duplicate(id):
    original = db.get_or_404(Invoice, id)

    new_invoice = Invoice(
        client_id=original.client_id,
        invoice_number=Invoice.generate_number(),
        status='draft',
        due_date=None,
        tax_rate=original.tax_rate,
        notes=original.notes,
    )
    db.session.add(new_invoice)
    db.session.flush()

    for item in original.items:
        new_item = InvoiceItem(
            invoice_id=new_invoice.id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            taxable=item.taxable,
        )
        db.session.add(new_item)

    db.session.commit()
    flash(f'Invoice duplicated as {new_invoice.invoice_number}.', 'success')
    return redirect(url_for('invoices.view', id=new_invoice.id))


@invoices.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    invoice = db.get_or_404(Invoice, id)
    db.session.delete(invoice)
    db.session.commit()
    flash('Invoice deleted.', 'success')
    return redirect(url_for('invoices.index'))


@invoices.route('/<int:id>/payments', methods=['POST'])
@login_required
def record_payment(id):
    invoice = db.get_or_404(Invoice, id)

    amount = request.form.get('amount', type=float)
    if not amount or amount <= 0:
        flash('Please enter a valid payment amount.', 'error')
        return redirect(url_for('invoices.view', id=invoice.id))

    method = request.form.get('method', 'cash')
    reference_note = request.form.get('reference_note', '').strip()
    payment_date_str = request.form.get('payment_date', '')

    payment_dt = date.today()
    if payment_date_str:
        try:
            payment_dt = date.fromisoformat(payment_date_str)
        except ValueError:
            pass

    payment = Payment(
        invoice_id=invoice.id,
        amount=amount,
        payment_date=payment_dt,
        method=method,
        reference_note=reference_note,
    )
    db.session.add(payment)

    # Auto-set status to sent if still draft
    if invoice.status == 'draft':
        invoice.status = 'sent'

    db.session.commit()
    flash(f'Payment of ${amount:,.2f} recorded.', 'success')
    return redirect(url_for('invoices.view', id=invoice.id))


@invoices.route('/<int:id>/email', methods=['POST'])
@login_required
def email_invoice(id):
    invoice = db.get_or_404(Invoice, id)

    recipients = request.form.get('recipients', '').strip()
    if not recipients:
        flash('Please enter at least one email address.', 'error')
        return redirect(url_for('invoices.view', id=invoice.id))

    success = send_invoice_email(invoice, recipients, include_pdf=True)

    if success:
        # Mark invoice as sent if still draft
        if invoice.status == 'draft':
            invoice.status = 'sent'
            db.session.commit()
        flash(f'Invoice emailed to {recipients}.', 'success')
    else:
        flash('Failed to send invoice email. Please try again.', 'error')

    return redirect(url_for('invoices.view', id=invoice.id))
