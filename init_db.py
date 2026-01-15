from app import create_app, db
from app.models.models import User, Service

def init_db():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('adminpassword')
            db.session.add(admin)
            
            # Add some default services
            services = [
                Service(name='House Washing', description='Complete exterior house washing', base_price=250.00),
                Service(name='Driveway Cleaning', description='Pressure washing of driveways', base_price=150.00),
                Service(name='Deck/Patio Cleaning', description='Deck and patio cleaning service', base_price=200.00),
                Service(name='Roof Cleaning', description='Soft wash roof cleaning', base_price=300.00),
                Service(name='Fence Cleaning', description='Fence cleaning and brightening', base_price=180.00),
            ]
            
            for service in services:
                db.session.add(service)
            
            db.session.commit()
            print('Database initialized with admin user and default services.')
        else:
            print('Admin user already exists. Database initialization skipped.')

if __name__ == '__main__':
    init_db() 