from app import create_app, db
from app.models import User, Client, Invoice, InvoiceItem, Payment

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Client': Client,
        'Invoice': Invoice,
        'InvoiceItem': InvoiceItem,
        'Payment': Payment,
    }


if __name__ == '__main__':
    app.run(debug=True, port=5007)
