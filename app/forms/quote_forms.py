from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, FloatField, DateField, DecimalField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import datetime, timedelta

class QuoteForm(FlaskForm):
    client_id = SelectField('Client', validators=[DataRequired()], coerce=int)
    expiration_date = DateField('Valid Until', format='%Y-%m-%d', 
                               validators=[Optional()], 
                               default=(datetime.now() + timedelta(days=30)))
    status = SelectField('Status', 
                       choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                       default='pending')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Quote')

class QuoteItemForm(FlaskForm):
    service_name = StringField('Service Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    quantity = DecimalField('Quantity', places=2, validators=[DataRequired(), NumberRange(min=0.01)], default=1)
    price = DecimalField('Price', places=2, validators=[DataRequired(), NumberRange(min=0)], default=0.00)
    submit = SubmitField('Add Item') 