from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField


class HelpForm(FlaskForm):
    body = PageDownField(
        'Help',
        validators=[DataRequired()],
        render_kw={'placeholder': 'This form has markdown support.'})
    submit = SubmitField('Submit')
