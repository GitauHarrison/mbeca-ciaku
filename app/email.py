from flask_mail import Message
from app import mail, app
from flask import render_template
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Mbeca Ciaku] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template(
                'email/reset_password.txt',
                user=user, token=token),
               html_body=render_template(
                'email/reset_password.html',
                user=user, token=token))


def send_admin_password_reset_email(admin):
    token = admin.get_reset_password_token()
    send_email('[Mbeca Ciaku] Admin Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[admin.email],
               text_body=render_template(
                'email/admin_reset_password.txt',
                admin=admin, token=token),
               html_body=render_template(
                'email/admin_reset_password.html',
                admin=admin, token=token))


def send_support_password_reset_email(support):
    token = support.get_reset_password_token()
    send_email('[Mbeca Ciaku] Support Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[support.email],
               text_body=render_template(
                'email/support_reset_password.txt',
                support=support, token=token),
               html_body=render_template(
                'email/support_reset_password.html',
                support=support, token=token))


def send_new_question_email(support):
    token = support.get_reset_password_token()
    send_email('[Mbeca Ciaku] New Question',
               sender=app.config['ADMINS'][0],
               recipients=[support.email],
               text_body=render_template(
                'email/support_new_question_email.txt',
                support=support, token=token),
               html_body=render_template(
                'email/support_new_question_email.html',
                support=support, token=token))


def send_answer_email(user):
    token = user.get_reset_password_token()
    send_email('[Mbeca Ciaku] Answered Question',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template(
                'email/support_answer_email.txt',
                user=user, token=token),
               html_body=render_template(
                'email/support_answer_email.html',
                user=user, token=token))


def send_registration_email(support):
    token = support.get_reset_password_token()
    send_email('[Mbeca Ciaku] You have been registered as Support',
               sender=app.config['ADMINS'][0],
               recipients=[support.email],
               text_body=render_template(
                'email/support_registration_email.txt',
                support=support, token=token),
               html_body=render_template(
                'email/support_registration_email.html',
                support=support, token=token))
