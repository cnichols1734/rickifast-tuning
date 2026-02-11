import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DB_PATH = os.environ.get('DB_PATH', os.path.join(basedir, 'crm.db'))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TAX_RATE = float(os.environ.get('TAX_RATE', '0.0825'))
