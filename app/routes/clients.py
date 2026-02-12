from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models import Client, Invoice

clients = Blueprint('clients', __name__, url_prefix='/clients')


@clients.route('/search')
@login_required
def search_api():
    """JSON API for live client search."""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])

    search = f'%{q}%'
    results = Client.query.filter(
        db.or_(
            Client.first_name.ilike(search),
            Client.last_name.ilike(search),
            Client.email.ilike(search),
            Client.phone.ilike(search),
            Client.vehicle_make.ilike(search),
            Client.vehicle_model.ilike(search),
        )
    ).order_by(Client.last_name.asc()).limit(20).all()

    return jsonify([{
        'id': c.id,
        'full_name': c.full_name,
        'vehicle': c.vehicle_display,
        'phone': c.phone or '',
        'email': c.email or '',
        'url': url_for('clients.view', id=c.id),
    } for c in results])


@clients.route('/')
@login_required
def index():
    q = request.args.get('q', '').strip()
    query = Client.query

    if q:
        search = f'%{q}%'
        query = query.filter(
            db.or_(
                Client.first_name.ilike(search),
                Client.last_name.ilike(search),
                Client.email.ilike(search),
                Client.phone.ilike(search),
                Client.vehicle_make.ilike(search),
                Client.vehicle_model.ilike(search),
            )
        )

    clients_list = query.order_by(Client.last_name.asc()).all()
    return render_template('clients/index.html', clients=clients_list, q=q)


@clients.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        client = Client(
            first_name=request.form.get('first_name', '').strip(),
            last_name=request.form.get('last_name', '').strip(),
            email=request.form.get('email', '').strip(),
            phone=request.form.get('phone', '').strip(),
            vehicle_year=request.form.get('vehicle_year', '').strip(),
            vehicle_make=request.form.get('vehicle_make', '').strip(),
            vehicle_model=request.form.get('vehicle_model', '').strip(),
            vehicle_trim=request.form.get('vehicle_trim', '').strip(),
            notes=request.form.get('notes', '').strip(),
        )

        if not client.first_name or not client.last_name:
            flash('First and last name are required.', 'error')
            return render_template('clients/form.html', client=client, editing=False)

        db.session.add(client)
        db.session.commit()
        flash('Client created.', 'success')
        return redirect(url_for('clients.view', id=client.id))

    return render_template('clients/form.html', client=None, editing=False)


@clients.route('/<int:id>')
@login_required
def view(id):
    client = db.get_or_404(Client, id)
    # Explicit query with eager-loaded items/payments (via selectin default)
    invoices = Invoice.query.filter_by(client_id=client.id) \
        .order_by(Invoice.created_at.desc()).all()
    total_spent = sum(inv.calculate_paid() for inv in invoices)
    return render_template('clients/view.html', client=client,
                           invoices=invoices, total_spent=total_spent)


@clients.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    client = db.get_or_404(Client, id)

    if request.method == 'POST':
        client.first_name = request.form.get('first_name', '').strip()
        client.last_name = request.form.get('last_name', '').strip()
        client.email = request.form.get('email', '').strip()
        client.phone = request.form.get('phone', '').strip()
        client.vehicle_year = request.form.get('vehicle_year', '').strip()
        client.vehicle_make = request.form.get('vehicle_make', '').strip()
        client.vehicle_model = request.form.get('vehicle_model', '').strip()
        client.vehicle_trim = request.form.get('vehicle_trim', '').strip()
        client.notes = request.form.get('notes', '').strip()

        if not client.first_name or not client.last_name:
            flash('First and last name are required.', 'error')
            return render_template('clients/form.html', client=client, editing=True)

        db.session.commit()
        flash('Client updated.', 'success')
        return redirect(url_for('clients.view', id=client.id))

    return render_template('clients/form.html', client=client, editing=True)


@clients.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    client = db.get_or_404(Client, id)
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted.', 'success')
    return redirect(url_for('clients.index'))
