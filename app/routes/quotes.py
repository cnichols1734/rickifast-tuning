from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required
from app import db
from app.models.models import Quote, QuoteItem, Client, Service, Invoice, InvoiceItem
from app.forms.quote_forms import QuoteForm, QuoteItemForm
from datetime import datetime, timedelta, timezone
from app.utils.email_utils import send_quote_email
from app.utils import get_or_404

quotes = Blueprint('quotes', __name__, url_prefix='/quotes')

@quotes.route('/')
@login_required
def index():
    quotes = Quote.query.order_by(Quote.date.desc()).all()
    return render_template('quotes/index.html', quotes=quotes)

@quotes.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = QuoteForm()
    form.client_id.choices = [(c.id, c.name) for c in Client.query.order_by(Client.name).all()]
    
    if form.validate_on_submit():
        quote = Quote(
            client_id=form.client_id.data,
            date=datetime.now(timezone.utc),
            expiration_date=datetime.now(timezone.utc) + timedelta(days=30),
            status='pending',
            notes=form.notes.data
        )
        db.session.add(quote)
        db.session.commit()
        flash('Quote created successfully!')
        return redirect(url_for('quotes.edit', id=quote.id))
    
    return render_template('quotes/form.html', form=form, title='Create New Quote')

@quotes.route('/<int:id>')
@login_required
def view(id):
    quote = get_or_404(Quote, id)
    return render_template('quotes/view.html', quote=quote)

@quotes.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    quote = get_or_404(Quote, id)
    services = Service.query.all()
    
    form = QuoteForm(obj=quote)
    form.client_id.choices = [(c.id, c.name) for c in Client.query.order_by(Client.name).all()]
    item_form = QuoteItemForm()
    
    if form.validate_on_submit():
        form.populate_obj(quote)
        db.session.commit()
        flash('Quote updated successfully!')
        return redirect(url_for('quotes.view', id=quote.id))
    
    return render_template('quotes/edit.html', 
                          quote=quote, 
                          form=form,
                          item_form=item_form,
                          services=services)

@quotes.route('/<int:id>/add_item', methods=['POST'])
@login_required
def add_item(id):
    quote = Quote.query.get_or_404(id)
    form = QuoteItemForm()
    
    if form.validate_on_submit():
        item = QuoteItem(
            quote_id=quote.id,
            service_name=form.service_name.data,
            description=form.description.data,
            quantity=form.quantity.data,
            price=form.price.data
        )
        db.session.add(item)
        
        # Update quote total
        quote.total += (item.price * item.quantity)
        db.session.commit()
        
        flash('Item added to quote')
        
    return redirect(url_for('quotes.edit', id=quote.id))

@quotes.route('/<int:id>/remove_item/<int:item_id>', methods=['POST'])
@login_required
def remove_item(id, item_id):
    quote = Quote.query.get_or_404(id)
    item = QuoteItem.query.get_or_404(item_id)
    
    # Ensure item belongs to this quote
    if item.quote_id != quote.id:
        flash('Error: Item does not belong to this quote')
        return redirect(url_for('quotes.edit', id=id))
    
    # Update quote total
    quote.total -= (item.price * item.quantity)
    
    # Remove the item
    db.session.delete(item)
    db.session.commit()
    
    flash('Item removed from quote')
    return redirect(url_for('quotes.edit', id=id))

@quotes.route('/<int:id>/convert_to_invoice', methods=['POST'])
@login_required
def convert_to_invoice(id):
    quote = Quote.query.get_or_404(id)
    
    # Create a new invoice based on the quote
    invoice = Invoice(
        client_id=quote.client_id,
        quote_id=quote.id,
        date=datetime.now(timezone.utc),
        due_date=datetime.now(timezone.utc) + timedelta(days=30),
        status='unpaid',
        total=quote.total,
        notes=quote.notes
    )
    db.session.add(invoice)
    db.session.flush()  # Get the invoice ID without committing the transaction
    
    # Copy quote items to invoice items
    for quote_item in quote.items:
        invoice_item = InvoiceItem(
            invoice_id=invoice.id,
            service_name=quote_item.service_name,
            description=quote_item.description,
            quantity=quote_item.quantity,
            price=quote_item.price
        )
        db.session.add(invoice_item)
    
    # Update quote status
    quote.status = 'converted'
    db.session.commit()
    
    flash('Quote successfully converted to invoice')
    return redirect(url_for('invoices.view', id=invoice.id))

@quotes.route('/<int:id>/send_email', methods=['POST'])
@login_required
def send_email(id):
    quote = Quote.query.get_or_404(id)
    
    try:
        send_quote_email(quote)
        flash('Quote email sent successfully!')
    except Exception as e:
        flash(f'Error sending email: {str(e)}', 'error')
    
    return redirect(url_for('quotes.view', id=id)) 