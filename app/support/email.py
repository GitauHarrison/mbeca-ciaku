from flask import current_app
from flask import render_template
from app.email import send_email


def send_answer_email(user):
    token = user.get_reset_password_token()
    send_email('[Mbeca Ciaku] Answered Question',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template(
                'auth/email/support/support_answer_email.txt',
                user=user, token=token),
               html_body=render_template(
                'auth/email/support/support_answer_email.html',
                user=user, token=token))
