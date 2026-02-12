"""
Create an admin user for the CRM
"""
from app import create_app, db
from app.models.models import User
from dotenv import load_dotenv
import getpass

load_dotenv()

def create_admin():
    """Create an admin user"""
    app = create_app()
    
    with app.app_context():
        print("Create Admin User")
        print("-" * 40)
        
        username = input("Username: ").strip()
        if not username:
            print("Username cannot be empty!")
            return
        
        # Check if user exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f"User '{username}' already exists!")
            return
        
        email = input("Email: ").strip()
        if not email:
            print("Email cannot be empty!")
            return
        
        # Check if email exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f"Email '{email}' already in use!")
            return
        
        password = getpass.getpass("Password: ")
        if len(password) < 6:
            print("Password must be at least 6 characters!")
            return
        
        password_confirm = getpass.getpass("Confirm Password: ")
        if password != password_confirm:
            print("Passwords do not match!")
            return
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"\n✓ Admin user '{username}' created successfully!")

if __name__ == '__main__':
    create_admin()
