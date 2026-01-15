from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.models import Client, Quote, Invoice

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    clients_count = Client.query.count()
    quotes_count = Quote.query.count()
    invoices_count = Invoice.query.count()
    
    recent_clients = Client.query.order_by(Client.created_at.desc()).limit(5).all()
    pending_quotes = Quote.query.filter_by(status='pending').order_by(Quote.date.desc()).limit(5).all()
    unpaid_invoices = Invoice.query.filter_by(status='unpaid').order_by(Invoice.date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                          clients_count=clients_count,
                          quotes_count=quotes_count,
                          invoices_count=invoices_count,
                          recent_clients=recent_clients,
                          pending_quotes=pending_quotes,
                          unpaid_invoices=unpaid_invoices) 