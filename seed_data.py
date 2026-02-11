"""Seed the database with sample data for testing."""
import os
import sys
from datetime import date, datetime, timedelta, timezone

# Ensure we can import the app
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User, Client, Invoice, InvoiceItem, Payment

app = create_app()

with app.app_context():
    # Drop and recreate all tables
    db.drop_all()
    db.create_all()

    # --- Admin user ---
    admin = User(username='admin', email='admin@autocrm.local')
    admin.set_password('admin123')
    db.session.add(admin)

    # --- Clients ---
    clients = [
        Client(
            first_name='Marcus', last_name='Johnson',
            email='marcus@example.com', phone='(512) 555-0101',
            vehicle_year='2020', vehicle_make='Honda', vehicle_model='Civic', vehicle_trim='Si',
            notes='Regular customer. Interested in full bolt-on setup.',
        ),
        Client(
            first_name='Sarah', last_name='Chen',
            email='sarah.chen@example.com', phone='(512) 555-0202',
            vehicle_year='2022', vehicle_make='Subaru', vehicle_model='WRX', vehicle_trim='STI',
            notes='Competition rally build. Budget-conscious.',
        ),
        Client(
            first_name='Tyler', last_name='Brooks',
            email='tyler.b@example.com', phone='(512) 555-0303',
            vehicle_year='2019', vehicle_make='Ford', vehicle_model='Mustang', vehicle_trim='GT',
            notes='Wants a street/strip setup. Has aftermarket exhaust already.',
        ),
        Client(
            first_name='Aisha', last_name='Ramirez',
            email='aisha.r@example.com', phone='(512) 555-0404',
            vehicle_year='2023', vehicle_make='Toyota', vehicle_model='GR Supra', vehicle_trim='3.0 Premium',
        ),
    ]
    db.session.add_all(clients)
    db.session.flush()

    # --- Invoice 1: Paid (Marcus - Civic Si) ---
    inv1 = Invoice(
        client_id=clients[0].id,
        invoice_number='INV-0001',
        status='sent',
        due_date=date.today() - timedelta(days=30),
        tax_rate=0.0825,
    )
    db.session.add(inv1)
    db.session.flush()

    inv1_items = [
        InvoiceItem(invoice_id=inv1.id, description='Stage 1 ECU Tune', quantity=1, unit_price=500.00, taxable=True),
        InvoiceItem(invoice_id=inv1.id, description='Dyno Session (3 pulls)', quantity=1, unit_price=150.00, taxable=True),
        InvoiceItem(invoice_id=inv1.id, description='Cold Air Intake Install (labor)', quantity=1, unit_price=75.00, taxable=False),
        InvoiceItem(invoice_id=inv1.id, description='PRL Cold Air Intake (part)', quantity=1, unit_price=350.00, taxable=True),
    ]
    db.session.add_all(inv1_items)
    db.session.flush()

    # Full payment
    pay1 = Payment(
        invoice_id=inv1.id,
        amount=inv1.calculate_total(),
        payment_date=date.today() - timedelta(days=25),
        method='zelle',
        reference_note='Paid in full',
    )
    db.session.add(pay1)

    # --- Invoice 2: Partial (Sarah - WRX STI) ---
    inv2 = Invoice(
        client_id=clients[1].id,
        invoice_number='INV-0002',
        status='sent',
        due_date=date.today() - timedelta(days=5),
        tax_rate=0.0825,
    )
    db.session.add(inv2)
    db.session.flush()

    inv2_items = [
        InvoiceItem(invoice_id=inv2.id, description='Stage 2 ECU Tune + E85 Map', quantity=1, unit_price=800.00, taxable=True),
        InvoiceItem(invoice_id=inv2.id, description='Downpipe Install (labor)', quantity=2, unit_price=125.00, taxable=False),
        InvoiceItem(invoice_id=inv2.id, description='Grimmspeed Downpipe (part)', quantity=1, unit_price=475.00, taxable=True),
        InvoiceItem(invoice_id=inv2.id, description='Dyno Session (5 pulls)', quantity=1, unit_price=250.00, taxable=True),
    ]
    db.session.add_all(inv2_items)
    db.session.flush()

    # Partial payment
    pay2 = Payment(
        invoice_id=inv2.id,
        amount=500.00,
        payment_date=date.today() - timedelta(days=3),
        method='cash',
        reference_note='Deposit',
    )
    db.session.add(pay2)

    # --- Invoice 3: Draft (Tyler - Mustang GT) ---
    inv3 = Invoice(
        client_id=clients[2].id,
        invoice_number='INV-0003',
        status='draft',
        due_date=date.today() + timedelta(days=14),
        tax_rate=0.0825,
    )
    db.session.add(inv3)
    db.session.flush()

    inv3_items = [
        InvoiceItem(invoice_id=inv3.id, description='Custom Dyno Tune (NA)', quantity=1, unit_price=650.00, taxable=True),
        InvoiceItem(invoice_id=inv3.id, description='Dyno Session (3 pulls)', quantity=1, unit_price=150.00, taxable=True),
        InvoiceItem(invoice_id=inv3.id, description='Intake Manifold Swap (labor)', quantity=3, unit_price=125.00, taxable=False),
    ]
    db.session.add_all(inv3_items)

    db.session.commit()
    print('Database seeded successfully!')
    print(f'  Admin user: admin / admin123')
    print(f'  Clients: {len(clients)}')
    print(f'  Invoices: 3 (1 paid, 1 partial, 1 draft)')
