from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class ClientForm(FlaskForm):
    name = StringField('Client Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone Number', validators=[Length(max=20), Optional()])
    address = StringField('Street Address', validators=[Length(max=200), Optional()])
    city = StringField('City', validators=[Length(max=100), Optional()])
    state = StringField('State/Province', validators=[Length(max=50), Optional()])
    postal_code = StringField('Postal Code', validators=[Length(max=20), Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Client') 