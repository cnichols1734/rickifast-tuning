from datetime import datetime, date, timezone
import secrets
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
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='reset_tokens')

    @staticmethod
    def generate(user, hours=1):
        from datetime import timedelta
        token = secrets.token_urlsafe(48)
        expires = datetime.now(timezone.utc) + timedelta(hours=hours)
        prt = PasswordResetToken(user_id=user.id, token=token, expires_at=expires)
        db.session.add(prt)
        db.session.commit()
        return prt

    @property
    def is_valid(self):
        return not self.used and datetime.now(timezone.utc) < self.expires_at


class InviteCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(128), unique=True, nullable=False, index=True)
    invited_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    invited_by = db.relationship('User', backref='sent_invites')

    @staticmethod
    def generate(email, invited_by_user, hours=48):
        from datetime import timedelta
        code = secrets.token_urlsafe(48)
        expires = datetime.now(timezone.utc) + timedelta(hours=hours)
        invite = InviteCode(email=email, code=code, invited_by_id=invited_by_user.id, expires_at=expires)
        db.session.add(invite)
        db.session.commit()
        return invite

    @property
    def is_valid(self):
        return not self.used and datetime.now(timezone.utc) < self.expires_at


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), index=True)
    phone = db.Column(db.String(20))
    vehicle_year = db.Column(db.String(4))
    vehicle_make = db.Column(db.String(50))
    vehicle_model = db.Column(db.String(50))
    vehicle_trim = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    invoices = db.relationship('Invoice', backref='client', lazy='selectin',
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
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False, index=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='draft', index=True)  # draft or sent
    due_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    tax_rate = db.Column(db.Float, default=0.0825)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    items = db.relationship('InvoiceItem', backref='invoice',
                            cascade='all, delete-orphan', lazy='selectin')
    payments = db.relationship('Payment', backref='invoice',
                               cascade='all, delete-orphan', lazy='selectin',
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
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False, index=True)
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
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=lambda: date.today(), index=True)
    method = db.Column(db.String(20), default='cash', index=True)  # cash/check/zelle/venmo/card/other
    reference_note = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f'<Payment ${self.amount} on Invoice {self.invoice_id}>'
