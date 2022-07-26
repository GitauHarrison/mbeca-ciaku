from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, DateField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField


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
