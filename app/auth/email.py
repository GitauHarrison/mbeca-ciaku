from flask import render_template, current_app
from flask import render_template
from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Mbeca Ciaku] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template(
                'auth/email/user/email/reset_password.txt',
                user=user, token=token),
               html_body=render_template(
                'auth/email/user/reset_password.html',
                user=user, token=token))


def send_admin_password_reset_email(admin):
    token = admin.get_reset_password_token()
    send_email('[Mbeca Ciaku] Admin Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[admin.email],
               text_body=render_template(
                'auth/email/admin/admin_reset_password.txt',
                admin=admin, token=token),
               html_body=render_template(
                'auth/email/admin/admin_reset_password.html',
                admin=admin, token=token))


def send_support_password_reset_email(support):
    token = support.get_reset_password_token()
    send_email('[Mbeca Ciaku] Support Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[support.email],
               text_body=render_template(
                'auth/email/support/support_reset_password.txt',
                support=support, token=token),
               html_body=render_template(
                'auth/email/support/support_reset_password.html',
                support=support, token=token))


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
