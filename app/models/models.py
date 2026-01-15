from datetime import datetime, timezone
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
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    quotes = db.relationship('Quote', backref='client', lazy='dynamic')
    invoices = db.relationship('Invoice', backref='client', lazy='dynamic')
    
    def __repr__(self):
        return f'<Client {self.name}>'

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    base_price = db.Column(db.Float)
    
    def __repr__(self):
        return f'<Service {self.name}>'

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expiration_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    total = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    
    # Relationships
    items = db.relationship('QuoteItem', backref='quote', cascade='all, delete-orphan')
    invoice = db.relationship('Invoice', backref='quote_origin', uselist=False)
    
    def __repr__(self):
        return f'<Quote {self.id} for Client {self.client_id}>'
        
class QuoteItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Float, default=1)
    price = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<QuoteItem {self.service_name} for Quote {self.quote_id}>'

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'))
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='unpaid')
    total = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    
    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Invoice {self.id} for Client {self.client_id}>'

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Float, default=1)
    price = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<InvoiceItem {self.service_name} for Invoice {self.invoice_id}>' 