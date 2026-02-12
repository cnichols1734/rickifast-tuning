"""
Migration script to create Supabase database tables
This script initializes all tables for the Rickifast Tuning CRM
"""
from app import create_app, db
from app.models.models import User, Client, Invoice, InvoiceItem, Payment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_database():
    """Initialize the database with all tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ All tables created successfully!")
        
        # Print table names
        print("\nTables created:")
        print("  - user")
        print("  - client")
        print("  - invoice")
        print("  - invoice_item")
        print("  - payment")
        
        # Check if any users exist
        user_count = User.query.count()
        if user_count == 0:
            print("\n⚠ No users found. You may want to create an admin user.")
            print("  Run: python create_admin.py")
        else:
            print(f"\n✓ Database has {user_count} user(s)")

if __name__ == '__main__':
    init_database()
