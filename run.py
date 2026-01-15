from app import create_app, db
from app.models.models import User, Client, Service, Quote, QuoteItem, Invoice, InvoiceItem

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Client': Client, 
        'Service': Service, 
        'Quote': Quote, 
        'QuoteItem': QuoteItem, 
        'Invoice': Invoice, 
        'InvoiceItem': InvoiceItem
    }

if __name__ == '__main__':
    app.run(debug=True) 