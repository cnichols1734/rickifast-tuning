from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.models import Invoice, InvoiceItem, Client, Service
from app.forms.invoice_forms import InvoiceForm, InvoiceItemForm
from datetime import datetime, timedelta, timezone
from app.utils.email_utils import send_invoice_email
from app.utils import get_or_404

invoices = Blueprint('invoices', __name__, url_prefix='/invoices')

@invoices.route('/')
@login_required
def index():
    invoices = Invoice.query.order_by(Invoice.date.desc()).all()
    return render_template('invoices/index.html', invoices=invoices)

@invoices.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = InvoiceForm()
    form.client_id.choices = [(c.id, c.name) for c in Client.query.order_by(Client.name).all()]
    
    if form.validate_on_submit():
        invoice = Invoice(
            client_id=form.client_id.data,
            date=datetime.now(timezone.utc),
            due_date=datetime.now(timezone.utc) + timedelta(days=30),
            status='unpaid',
            notes=form.notes.data
        )
        db.session.add(invoice)
        db.session.commit()
        flash('Invoice created successfully!')
        return redirect(url_for('invoices.edit', id=invoice.id))
    
    return render_template('invoices/form.html', form=form, title='Create New Invoice')

@invoices.route('/<int:id>')
@login_required
def view(id):
    invoice = get_or_404(Invoice, id)
    return render_template('invoices/view.html', invoice=invoice)

@invoices.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    invoice = Invoice.query.get_or_404(id)
    services = Service.query.all()
    
    form = InvoiceForm(obj=invoice)
    form.client_id.choices = [(c.id, c.name) for c in Client.query.order_by(Client.name).all()]
    item_form = InvoiceItemForm()
    
    if form.validate_on_submit():
        form.populate_obj(invoice)
        db.session.commit()
        flash('Invoice updated successfully!')
        return redirect(url_for('invoices.view', id=invoice.id))
    
    return render_template('invoices/edit.html', 
                          invoice=invoice, 
                          form=form,
                          item_form=item_form,
                          services=services)

@invoices.route('/<int:id>/add_item', methods=['POST'])
@login_required
def add_item(id):
    invoice = Invoice.query.get_or_404(id)
    form = InvoiceItemForm()
    
    if form.validate_on_submit():
        item = InvoiceItem(
            invoice_id=invoice.id,
            service_name=form.service_name.data,
            description=form.description.data,
            quantity=form.quantity.data,
            price=form.price.data
        )
        db.session.add(item)
        
        # Update invoice total
        invoice.total += (item.price * item.quantity)
        db.session.commit()
        
        flash('Item added to invoice')
        
    return redirect(url_for('invoices.edit', id=invoice.id))

@invoices.route('/<int:id>/remove_item/<int:item_id>', methods=['POST'])
@login_required
def remove_item(id, item_id):
    invoice = Invoice.query.get_or_404(id)
    item = InvoiceItem.query.get_or_404(item_id)
    
    # Ensure item belongs to this invoice
    if item.invoice_id != invoice.id:
        flash('Error: Item does not belong to this invoice')
        return redirect(url_for('invoices.edit', id=id))
    
    # Update invoice total
    invoice.total -= (item.price * item.quantity)
    
    # Remove the item
    db.session.delete(item)
    db.session.commit()
    
    flash('Item removed from invoice')
    return redirect(url_for('invoices.edit', id=id))

@invoices.route('/<int:id>/mark_paid', methods=['POST'])
@login_required
def mark_paid(id):
    invoice = Invoice.query.get_or_404(id)
    invoice.status = 'paid'
    db.session.commit()
    flash('Invoice marked as paid')
    return redirect(url_for('invoices.view', id=id))

@invoices.route('/<int:id>/send_email', methods=['POST'])
@login_required
def send_email(id):
    invoice = Invoice.query.get_or_404(id)
    
    try:
        send_invoice_email(invoice)
        flash('Invoice email sent successfully!')
    except Exception as e:
        flash(f'Error sending email: {str(e)}', 'error')
    
    return redirect(url_for('invoices.view', id=id)) 