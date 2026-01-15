from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, FloatField, DateField, DecimalField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import datetime, timedelta

class InvoiceForm(FlaskForm):
    client_id = SelectField('Client', validators=[DataRequired()], coerce=int)
    due_date = DateField('Due Date', format='%Y-%m-%d', 
                        validators=[Optional()], 
                        default=(datetime.now() + timedelta(days=15)))
    status = SelectField('Status', 
                       choices=[('unpaid', 'Unpaid'), ('paid', 'Paid'), ('overdue', 'Overdue'), ('cancelled', 'Cancelled')],
                       default='unpaid')
    payment_terms = SelectField('Payment Terms',
                             choices=[
                                 ('due_on_receipt', 'Due on Receipt'),
                                 ('net_15', 'Net 15'),
                                 ('net_30', 'Net 30'),
                                 ('net_60', 'Net 60')
                             ],
                             default='net_15')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Invoice')

class InvoiceItemForm(FlaskForm):
    service_name = StringField('Service Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    quantity = DecimalField('Quantity', places=2, validators=[DataRequired(), NumberRange(min=0.01)], default=1)
    price = DecimalField('Price', places=2, validators=[DataRequired(), NumberRange(min=0)], default=0.00)
    submit = SubmitField('Add Item') 