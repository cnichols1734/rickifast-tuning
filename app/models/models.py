from datetime import datetime, date, timezone
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    vehicle_year = db.Column(db.String(4))
    vehicle_make = db.Column(db.String(50))
    vehicle_model = db.Column(db.String(50))
    vehicle_trim = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    invoices = db.relationship('Invoice', backref='client', lazy='dynamic',
                               cascade='all, delete-orphan')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def vehicle_display(self):
        parts = [p for p in [self.vehicle_year, self.vehicle_make,
                             self.vehicle_model, self.vehicle_trim] if p]
        return ' '.join(parts) if parts else 'No vehicle'

    def __repr__(self):
        return f'<Client {self.full_name}>'


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft or sent
    due_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    tax_rate = db.Column(db.Float, default=0.0825)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    items = db.relationship('InvoiceItem', backref='invoice',
                            cascade='all, delete-orphan', lazy='dynamic')
    payments = db.relationship('Payment', backref='invoice',
                               cascade='all, delete-orphan', lazy='dynamic',
                               order_by='Payment.payment_date.desc()')

    @staticmethod
    def generate_number():
        last = Invoice.query.order_by(Invoice.id.desc()).first()
        next_num = (last.id + 1) if last else 1
        return f'INV-{next_num:04d}'

    def calculate_subtotal(self):
        return sum(item.amount for item in self.items)

    def calculate_tax(self):
        return sum(item.amount for item in self.items if item.taxable) * self.tax_rate

    def calculate_total(self):
        return self.calculate_subtotal() + self.calculate_tax()

    def calculate_paid(self):
        return sum(p.amount for p in self.payments)

    def calculate_balance(self):
        return self.calculate_total() - self.calculate_paid()

    def get_status(self):
        total = self.calculate_total()
        paid = self.calculate_paid()
        if self.status == 'draft':
            return 'draft'
        if total > 0 and paid >= total:
            return 'paid'
        if paid > 0:
            return 'partial'
        if self.due_date and self.due_date < date.today():
            return 'overdue'
        return 'sent'

    def days_overdue(self):
        if self.due_date and self.due_date < date.today():
            return (date.today() - self.due_date).days
        return 0

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'


class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    taxable = db.Column(db.Boolean, default=False)

    @property
    def amount(self):
        return self.quantity * self.unit_price

    def __repr__(self):
        return f'<InvoiceItem {self.description}>'


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=lambda: date.today())
    method = db.Column(db.String(20), default='cash')  # cash/check/zelle/venmo/card/other
    reference_note = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Payment ${self.amount} on Invoice {self.invoice_id}>'
