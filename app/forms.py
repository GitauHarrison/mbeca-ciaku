from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


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


class BudgetItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    budget = SubmitField('Add')


class IncomeSourceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    income = SubmitField('Add')


class AssetItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    asset = SubmitField('Add')


class LiabilityItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    liability = SubmitField('Add')
