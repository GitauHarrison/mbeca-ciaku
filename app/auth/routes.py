from app import db
from app.auth import bp
from flask import render_template, flash, redirect, url_for, session,\
    request
from app.auth.forms import LoginForm, PhoneForm, RegistrationForm, PhoneForm,\
    VerifyForm, DisableForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from app.auth.twilio_verify_api import request_verification_token, \
    check_verification_token
from werkzeug.urls import url_parse
from app.auth.email import send_password_reset_email, \
    send_admin_password_reset_email, send_support_password_reset_email


# ==========================================================
# ADMIN ROUTES
# ==========================================================


@bp.route('register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        user = User(username=request.form['username'], email=request.form['email'])
        if request.form['password'] == request.form['confirm_password']:
            user.set_password(request.form['password'])
        else:
            flash('Your passwords do not match. Try again')
            return redirect(url_for('register_user'))
        db.session.add(user)
        db.session.commit()
        flash('You have been registered successfully. Login to continue.')
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.about'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('user.dashboard')
        if user.two_factor_enabled():
            request_verification_token(user.verification_phone)
            session['username'] = user.username
            username = session['username']
            session['phone'] = user.verification_phone
            return redirect(url_for(
                'auth.verify_2fa', username=user.username,
                next=next_page,
                remember='1' if request.form['remember_me'] else '0'))
        login_user(user)
        flash(f'Welcome back, {user.username}')
        return redirect(next_page)
    return redirect(url_for('main.about'))


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/request-password-reset', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            send_admin_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.about'))
    return render_template(
        'auth/email/reset_password_request.html',
        title='Admin Request Password Reset')


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        user.set_password(request.form['password'])
        db.session.commit()
        flash('Your password has been reset. Login to continue.')
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/email/reset_password.html',
        title='Reset Password')


# Two-factor authentication routes


@bp.route('/dashboard/enable-2fa', methods=['GET', 'POST'])
@login_required
def enable_2fa():
    if request.method == 'POST':
        session['phone'] = request.form['verification_phone']
        request_verification_token(session['phone'])
        return redirect(url_for('auth.verify_2fa'))
    return render_template(
        'auth/two_factor_auth/enable_2fa.html',
        title='Enable 2FA')


@bp.route('/admin/dashboard/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    if request.method == 'POST':
        phone = session['phone']
        if check_verification_token(phone, request.form['token']):
            del session['phone']
            if current_user.is_authenticated:
                user.verification_phone = phone
                db.session.commit()
                flash('You have enabled two-factor authentication on your account.')
                return redirect(url_for('user.dashboard'))
            else:
                username = session['username']
                del session['username']
                user = User.query.filter_by(username=username).first_or_404()
                next_page = request.args.get('next')
                remember = request.args.get('remember', '0') == '1'
                login_user(user, remember=remember)
                return redirect(next_page or url_for('user.dashboard'))
        request.form['token'].errors.append('Invalid token')
    return render_template(
        'auth/two_factor_auth/verify_2fa.html',
        title='Verify 2FA')


@bp.route('/admin/dashboard/disable-2fa', methods=['GET', 'POST'])
@login_required
def disable_2fa():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    if request.method == 'POST':
        user.verification_phone = None
        db.session.commit()
        flash('You have disabled two-factor authentication on your account.')
        return redirect(url_for('user.dashboard'))
    return render_template(
        'auth/two_factor_auth/disable_2fa.html',
        title='Disable 2FA')

# ==========================================================
# END OF USER ROUTES
# ==========================================================
