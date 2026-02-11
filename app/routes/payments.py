from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Payment

payments = Blueprint('payments', __name__, url_prefix='/payments')


@payments.route('/')
@login_required
def index():
    method_filter = request.args.get('method', 'all')
    query = Payment.query.order_by(Payment.payment_date.desc())

    if method_filter != 'all':
        query = query.filter_by(method=method_filter)

    payments_list = query.all()
    return render_template('payments/index.html', payments=payments_list,
                           method_filter=method_filter)


@payments.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    payment = db.get_or_404(Payment, id)
    invoice_id = payment.invoice_id
    db.session.delete(payment)
    db.session.commit()
    flash('Payment deleted.', 'success')
    return redirect(url_for('invoices.view', id=invoice_id))
