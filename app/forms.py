from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, \
    SelectField, IntegerField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import phonenumbers
from flask_pagedown.fields import PageDownField


class RegistrationForm(FlaskForm):
    username = StringField(
        'Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class PhoneForm(FlaskForm):
    verification_phone = StringField(
        'Phone',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Ex. +254712345678'})
    submit = SubmitField('Add Phone')

    def validate_phone(self, phone):
        p = phonenumbers.parse(phone.data)
        try: 
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number.')


class VerifyForm(FlaskForm):
    token = StringField('Token', validators=[DataRequired()])
    submit = SubmitField('Verify')


class DisableForm(FlaskForm):
    submit = SubmitField('Disable')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class BudgetItemForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    name = StringField(
        'Name',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Ex. Food, Fare, etc.'})
    amount = IntegerField('Amount', validators=[DataRequired()])
    budget = SubmitField('Add')


class AssetForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    name = StringField(
        'Name',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Ex. Salon, Suguta Apartments, etc.'})
    amount = IntegerField('Amount', validators=[DataRequired()])
    asset = SubmitField('Add')


class LiabilityForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    name = StringField(
        'Name',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Ex. Credit Card, Toyota Rav4, etc.'})
    amount = IntegerField('Amount', validators=[DataRequired()])
    liability = SubmitField('Add')


class ActualIncomeForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    name = StringField(
        'Name',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Ex. Safaricom Salary, Sacco dividends, etc.'})
    amount = IntegerField('Amount', validators=[DataRequired()])
    actual_income = SubmitField('Add')


class ActualExpenseForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    name = StringField(
        'Name',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Ex. Food, Fare, etc.'})
    amount = IntegerField('Amount', validators=[DataRequired()])
    actual_expense = SubmitField('Add')


class DownloadDataForm(FlaskForm):
    year = SelectField('', choices=[])
    download_data = SubmitField('Download')


class HelpForm(FlaskForm):
    body = PageDownField(
        'Help',
        validators=[DataRequired()],
        render_kw={'placeholder': 'This form has markdown support.'})
    submit = SubmitField('Submit')
