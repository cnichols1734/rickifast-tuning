from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.models import Client
from app.forms.client_forms import ClientForm
from app.utils import get_or_404

clients = Blueprint('clients', __name__, url_prefix='/clients')

@clients.route('/')
@login_required
def index():
    clients = Client.query.order_by(Client.name).all()
    return render_template('clients/index.html', clients=clients)

@clients.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ClientForm()
    if form.validate_on_submit():
        client = Client(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            postal_code=form.postal_code.data,
            notes=form.notes.data
        )
        db.session.add(client)
        db.session.commit()
        flash('Client added successfully!')
        return redirect(url_for('clients.index'))
    
    return render_template('clients/form.html', form=form, title='Add New Client')

@clients.route('/<int:id>')
@login_required
def view(id):
    client = get_or_404(Client, id)
    quotes = client.quotes.all()
    invoices = client.invoices.all()
    return render_template('clients/view.html', client=client, quotes=quotes, invoices=invoices)

@clients.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    client = get_or_404(Client, id)
    form = ClientForm(obj=client)
    
    if form.validate_on_submit():
        form.populate_obj(client)
        db.session.commit()
        flash('Client updated successfully!')
        return redirect(url_for('clients.view', id=client.id))
    
    return render_template('clients/form.html', form=form, title='Edit Client')

@clients.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    client = get_or_404(Client, id)
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted successfully!')
    return redirect(url_for('clients.index')) 