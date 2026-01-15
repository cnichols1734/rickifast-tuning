import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configure the application
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///aquaforce.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Setup login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Register blueprints
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.routes.clients import clients as clients_blueprint
    app.register_blueprint(clients_blueprint)
    
    from app.routes.quotes import quotes as quotes_blueprint
    app.register_blueprint(quotes_blueprint)
    
    from app.routes.invoices import invoices as invoices_blueprint
    app.register_blueprint(invoices_blueprint)
    
    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app 