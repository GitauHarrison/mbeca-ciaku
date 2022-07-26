from app import db
from app.auth import bp
from flask import render_template, flash, redirect, url_for, session,\
    request
from app.auth.forms import LoginForm, PhoneForm, RegistrationForm, PhoneForm, \
    VerifyForm, DisableForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Admin, Support
from flask_login import current_user, login_user, logout_user, login_required
from app.auth.twilio_verify_api import request_verification_token, \
    check_verification_token
from werkzeug.urls import url_parse
from app.auth.email import send_password_reset_email, \
    send_admin_password_reset_email, send_support_password_reset_email


# ==========================================================
# ADMIN ROUTES
# ==========================================================


@bp.route('/admin/register', methods=['GET', 'POST'])
def admin_dashboard_registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        admin = Admin(username=form.username.data,email=form.email.data)
        admin.set_password(form.password.data)
        db.session.add(admin)
        db.session.commit()
        flash('You have successfully registered as an admin!')
        return redirect(url_for('auth.admin_login'))
    return render_template(
        'auth/register.html',
        title='Registration',
        form=form)


@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin is None or not admin.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.admin_login'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('admin.admin_dashboard', username=admin.username)
        if admin.two_factor_enabled():
            request_verification_token(admin.verification_phone)
            session['username'] = admin.username
            username = session['username']
            session['phone'] = admin.verification_phone
            return redirect(url_for(
                'auth.admin_verify_2fa', username=admin.username,
                next=next_page,
                remember='1' if form.remember_me.data else '0'))
        login_user(admin, remember=form.remember_me.data)
        flash(f'Welcome back, {admin.username}')
        return redirect(next_page)
    return render_template('auth/admin_login.html', title='Admin Login', form=form)


@bp.route('/admin/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('auth.admin_login'))


@bp.route('/admin/request-password-reset', methods=['GET', 'POST'])
def admin_request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin:
            send_admin_password_reset_email(admin)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.admin_login'))
    return render_template(
        'auth/email/reset_password_request.html',
        title='Admin Request Password Reset',
        form=form)


@bp.route('/admin/reset-password/<token>', methods=['GET', 'POST'])
def admin_reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    admin = Admin.verify_reset_password_token(token)
    if not admin:
        return redirect(url_for('auth.admin_login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        admin.set_password(form.password.data)
        db.session.commit()
        flash('Your admin password has been reset.')
        return redirect(url_for('auth.admin_login'))
    return render_template(
        'auth/email/reset_password.html',
        title='Admin Reset Password',
        form=form)


# Two-factor authentication routes


@bp.route('/admin/dashboard/<username>/enable_2fa', methods=['GET', 'POST'])
@login_required
def admin_enable_2fa(username):
    admin = Admin.query.filter_by(username=username).first_or_404()
    form = PhoneForm()
    if form.validate_on_submit():
        session['phone'] = form.verification_phone.data
        request_verification_token(session['phone'])
        return redirect(url_for('auth.admin_verify_2fa', username=admin.username))
    return render_template(
        'auth/two_factor_auth/enable_2fa.html',
        title='Admin Enable 2FA',
        form=form,
        admin=admin)


@bp.route('/admin/dashboard/<username>/verify_2fa', methods=['GET', 'POST'])
def admin_verify_2fa(username):
    admin = Admin.query.filter_by(username=username).first_or_404()
    form = VerifyForm()
    if form.validate_on_submit():
        phone = session['phone']
        if check_verification_token(phone, form.token.data):
            del session['phone']
            if current_user.is_authenticated:
                current_user.verification_phone = phone
                db.session.commit()
                flash('You have enabled two-factor authentication on your account.')
                return redirect(url_for('admin.admin_dashboard', username=username))
            else:
                username = session['username']
                del session['username']
                admin = Admin.query.filter_by(username=username).first_or_404()
                next_page = request.args.get('next')
                remember = request.args.get('remember', '0') == '1'
                login_user(admin, remember=remember)
                return redirect(next_page or url_for('admin.admin_dashboard', username=username))
        form.token.errors.append('Invalid token')
    return render_template(
        'auth/two_factor_auth/verify_2fa.html',
        title='Admin Verify 2FA',
        form=form,
        admin=admin)


@bp.route('/admin/dashboard/<username>/disable_2fa', methods=['GET', 'POST'])
@login_required
def admin_disable_2fa(username):
    admin = Admin.query.filter_by(username=username).first_or_404()
    form = DisableForm()
    if form.validate_on_submit():
        current_user.verification_phone = None
        db.session.commit()
        flash('You have disabled two-factor authentication on your account.')
        return redirect(url_for('admin.admin_dashboard', username=username))
    return render_template(
        'auth/two_factor_auth/disable_2fa.html',
        title='Admin Disable 2FA',
        form=form,
        admin=admin)

# ==========================================================
# END OF ADMIN ROUTES
# ==========================================================



# ==========================================================
# SUPPORT ROUTES
# ==========================================================

# Basic authentication routes

@bp.route('/support/login', methods=['GET', 'POST'])
def support_login():
    if current_user.is_authenticated:
        return redirect(url_for('support.support_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        support = Support.query.filter_by(username=form.username.data).first()
        if support is None or not support.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.support_login'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('support.support_dashboard', username=support.username)
        if support.two_factor_enabled():
            request_verification_token(support.verification_phone)
            session['username'] = support.username
            username = session['username']
            session['phone'] = support.verification_phone
            return redirect(url_for(
                'auth.support_verify_2fa', username=support.username,
                next=next_page,
                remember='1' if form.remember_me.data else '0'))
        login_user(support, remember=form.remember_me.data)
        flash('Welcome back, ' + support.username)
        return redirect(next_page)
    return render_template(
        'auth/support_login.html', title='Support Login', form=form)


@bp.route('/support/logout')
def support_logout():
    logout_user()
    return redirect(url_for('auth.support_login'))


# Password reset routes


@bp.route('/support/request-password-reset', methods=['GET', 'POST'])
def support_request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('support.support_dashboard'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        support = Support.query.filter_by(email=form.email.data).first()
        if support:
            send_support_password_reset_email(support)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.support_login'))
    return render_template(
        'auth/email/reset_password_request.html',
        title='Support Request Password Reset',
        form=form)


@bp.route('/support/reset-password/<token>', methods=['GET', 'POST'])
def support_reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('support.support_dashboard'))
    support = Admin.verify_reset_password_token(token)
    if not support:
        return redirect(url_for('auth.support_login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        support.set_password(form.password.data)
        db.session.commit()
        flash('Your support password has been reset.')
        return redirect(url_for('auth.support_login'))
    return render_template(
        'auth/email/reset_password.html',
        title='Support Reset Password',
        form=form)


# Two-factor authentication routes


@bp.route('/support/dashboard/<username>/enable_2fa', methods=['GET', 'POST'])
@login_required
def support_enable_2fa(username):
    support = Support.query.filter_by(username=username).first_or_404()
    form = PhoneForm()
    if form.validate_on_submit():
        session['phone'] = form.verification_phone.data
        request_verification_token(session['phone'])
        return redirect(url_for('auth.support_verify_2fa', username=support.username))
    return render_template(
        'auth/two_factor_auth/enable_2fa.html',
        title='Enable 2FA',
        form=form,
        support=support)


@bp.route('/support/dashboard/<username>/verify_2fa', methods=['GET', 'POST'])
def support_verify_2fa(username):
    support = Support.query.filter_by(username=username).first_or_404()
    form = VerifyForm()
    if form.validate_on_submit():
        phone = session['phone']
        if check_verification_token(phone, form.token.data):
            del session['phone']
            if current_user.is_authenticated:
                current_user.verification_phone = phone
                db.session.commit()
                flash('You have enabled two-factor authentication on your account.')
                return redirect(url_for('support.support_dashboard', username=username))
            else:
                username = session['username']
                del session['username']
                support = Support.query.filter_by(username=username).first_or_404()
                next_page = request.args.get('next')
                remember = request.args.get('remember', '0') == '1'
                login_user(support, remember=remember)
                return redirect(next_page or url_for(
                    'support.support_dashboard', username=username))
        form.token.errors.append('Invalid token')
    return render_template(
        'auth/two_factor_auth/verify_2fa.html',
        title='Support Verify 2FA',
        form=form,
        support=support)


@bp.route('/support/dashboard/<username>/disable_2fa', methods=['GET', 'POST'])
@login_required
def support_disable_2fa(username):
    support = Support.query.filter_by(username=username).first_or_404()
    form = DisableForm()
    if form.validate_on_submit():
        current_user.verification_phone = None
        db.session.commit()
        flash('You have disabled two-factor authentication on your account.')
        return redirect(url_for('support.support_dashboard', username=username))
    return render_template(
        'auth/two_factor_auth/disable_2fa.html',
        title='Support Disable 2FA',
        form=form,
        support=support)

# ==========================================================
# END OF SUPPORT ROUTES
# ==========================================================


# ==========================================================
# USER ROUTES
# ==========================================================


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        if user.two_factor_enabled():
            request_verification_token(user.verification_phone)
            session['username'] = user.username
            session['phone'] = user.verification_phone
            return redirect(url_for(
                'auth.verify_2fa',
                next=next_page,
                remember='1' if form.remember_me.data else '0'))
        login_user(user, remember=form.remember_me.data)
        flash('Welcome back, ' + user.username)
        return redirect(next_page)
    return render_template('auth/login.html', title='User Login', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user! '
              'Login to continue')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/request-for-password-reset', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/email/reset_password_request.html',
        title='Request Password Reset ', form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/email/reset_password.html', form=form, title='Reset Password')


# ===============================================================
# Two-factor authentication
# ===============================================================


@bp.route('/enable-2fa', methods=['GET', 'POST'])
@login_required
def enable_2fa():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    form = PhoneForm()
    if form.validate_on_submit():
        session['phone'] = form.verification_phone.data
        request_verification_token(session['phone'])
        return redirect(url_for('auth.verify_2fa'))
    return render_template(
        'auth/two_factor_auth/enable_2fa.html',
        title='Enable 2FA',
        form=form,
        user=user)


@bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    form = VerifyForm()
    if form.validate_on_submit():
        phone = session['phone']
        if check_verification_token(phone, form.token.data):
            del session['phone']
            if current_user.is_authenticated:
                current_user.verification_phone = phone
                db.session.commit()
                flash('You have enabled two-factor authentication.')
                return redirect(url_for('main.help'))
            else:
                username = session['username']
                del session['username']
                user = User.query.filter_by(username=username).first()
                next_page = request.args.get('next')
                remember = request.args.get('remember', '0') == '1'
                login_user(user, remember=remember)
                flash('Welcome back ' + user.username)
                return redirect(next_page or url_for('main.index'))
        form.token.errors.append('Invalid token.')
    return render_template('auth/two_factor_auth/verify_2fa.html', title='Verify 2FA', form=form)


@bp.route('/disable-2fa', methods=['GET', 'POST'])
@login_required
def disable_2fa():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    form = DisableForm()
    if form.validate_on_submit():
        current_user.verification_phone = None
        db.session.commit()
        flash('You have disabled two-factor authentication.')
        return redirect(url_for('main.help'))
    return render_template(
        'auth/two_factor_auth/disable_2fa.html',
        title='Disable 2FA',
        form=form,
        user=user)


# ==========================================================
# END OF USER ROUTES
# ==========================================================
