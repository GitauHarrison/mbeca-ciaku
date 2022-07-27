from flask import render_template
from app.email import send_email
from flask import current_app



def send_new_question_email(support):
    token = support.get_reset_password_token()
    send_email('[Mbeca Ciaku] New Question',
               sender=current_app.config['ADMINS'][0],
               recipients=[support.email],
               text_body=render_template(
                'auth/email/support/support_new_question_email.txt',
                support=support, token=token),
               html_body=render_template(
                'auth/email/support/support_new_question_email.html',
                support=support, token=token))
