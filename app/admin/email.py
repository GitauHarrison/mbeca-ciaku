from flask import current_app
from flask import render_template
from app.email import send_email


def send_registration_email(support):
    token = support.get_reset_password_token()
    send_email('[Mbeca Ciaku] You have been registered as Support',
               sender=current_app.config['ADMINS'][0],
               recipients=[support.email],
               text_body=render_template(
                'auth/email/support/support_registration_email.txt',
                support=support, token=token),
               html_body=render_template(
                'auth/email/support/support_registration_email.html',
                support=support, token=token))
