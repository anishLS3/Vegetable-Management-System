from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp

class BillingForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=255)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=255)])
    address = TextAreaField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired(), Length(max=255)])
    state = StringField('State', validators=[DataRequired(), Length(max=255)])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(max=20)])
    country = StringField('Country', validators=[DataRequired(), Length(max=255)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[DataRequired(), Length(max=255)])
    payment_method = SelectField('Payment Method', choices=[('credit_card', 'Credit/Debit Card'), ('paytm', 'Paytm')], validators=[DataRequired()])
    make_payment = SubmitField('Make Payment')

class PayTMForm(FlaskForm):
    paytm_id = StringField('PayTM ID', validators=[DataRequired(), Length(max=255)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    pin = PasswordField('PIN', validators=[DataRequired(), Length(min=4, max=6)])
    submit_paytm = SubmitField('Pay And Confirm')

class CreditCardForm(FlaskForm):
    credit_card_number = StringField('Credit Card Number', validators=[
        DataRequired(),
        Regexp(r'^\d{4} \d{4} \d{4} \d{4}$', message='Enter a valid 16-digit credit card number with spaces')
    ])
    expiry_date = StringField('Expiry Date (MM/YY)', validators=[
        DataRequired(),
        Regexp(r'^\d{2}/\d{2}$', message='Enter a valid expiry date in MM/YY format')
    ])
    cvv = PasswordField('CVV', validators=[
        DataRequired(),
        Regexp(r'^\d{3}$', message='Enter a valid 3-digit CVV')
    ])
    submit_credit_card = SubmitField('Pay And Confirm')
