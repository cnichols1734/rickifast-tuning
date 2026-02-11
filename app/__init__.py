import os
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    from app.routes.auth import auth
    from app.routes.clients import clients
    from app.routes.invoices import invoices
    from app.routes.payments import payments

    app.register_blueprint(auth)
    app.register_blueprint(clients)
    app.register_blueprint(invoices)
    app.register_blueprint(payments)

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        from app.models import Client, Invoice, Payment
        from datetime import datetime, timezone, date
        from sqlalchemy import func

        total_clients = Client.query.count()

        all_invoices = Invoice.query.all()
        outstanding = [inv for inv in all_invoices if inv.get_status() in ('sent', 'partial', 'overdue')]
        outstanding_total = sum(inv.calculate_balance() for inv in outstanding)
        outstanding_count = len(outstanding)

        now = datetime.now(timezone.utc)
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_payments = Payment.query.filter(
            Payment.payment_date >= first_of_month.date()
        ).all()
        monthly_revenue = sum(p.amount for p in monthly_payments)

        all_time_revenue = db.session.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).scalar()

        recent_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()
        recent_clients = Client.query.order_by(Client.created_at.desc()).limit(5).all()
        recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(5).all()

        return render_template('dashboard.html',
                               total_clients=total_clients,
                               outstanding_total=outstanding_total,
                               outstanding_count=outstanding_count,
                               monthly_revenue=monthly_revenue,
                               all_time_revenue=all_time_revenue,
                               recent_invoices=recent_invoices,
                               recent_clients=recent_clients,
                               recent_payments=recent_payments)

    with app.app_context():
        db.create_all()

    return app
