from app import app, db
from flask import render_template, flash, redirect, url_for, session,\
    request, send_file
from app.forms import LoginForm, PhoneForm, RegistrationForm, BudgetItemForm, \
    AssetForm, LiabilityForm, ActualIncomeForm, ActualExpenseForm, \
    DownloadDataForm, HelpForm, PhoneForm, VerifyForm, DisableForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, BudgetItem, Expenses, Asset, Liability,\
    ActualIncome, Help, Admin, Support
from flask_login import current_user, login_user, logout_user, \
    login_required
from app.data_income import income_data
from app.data_budget import budget_data
from app.data_expense import expenses_data
from app.download_budget_data import download_budget_pdf
from app.download_assets_data import download_assets_pdf
from app.download_liabilities_data import download_liabilities_pdf
from app.download_expenses_data import download_expenses_pdf
from app.download_income_data import download_income_pdf
from app.data_assets import assets_data
from app.data_expense import expenses_data
from app.data_liabilities import liabilities_data
from app.encrypt_pdf import encrypt_pdf
from app.twilio_verify_api import request_verification_token, \
    check_verification_token
from werkzeug.urls import url_parse
from io import BytesIO
import os
from app.email import send_password_reset_email, \
    send_admin_password_reset_email, send_support_password_reset_email, \
    send_new_question_email, send_answer_email, send_registration_email
import datetime

# The two functions below allow us to specify what forms
# are to be submitted in a post request
def validate_on_submit(self):
    return self.is_submitted() and self.validate()


def is_submitted(self):
    return self.form.is_submitted()


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = User.query.filter_by(username=current_user.username).first()

    # Income
    user_income_data = income_data(user)
    income_total = user_income_data[3]
    income_years = list(user_income_data[0].keys())

    # Expenses
    user_expenses_data = expenses_data(user)
    expenses_total = user_expenses_data[3]
    expenses_years = list(user_expenses_data[0].keys())

    # List differences in income and expenses per year
    income_expenses_differences_per_year = []
    for year in income_years:
        income_expenses_differences_per_year.append(
            income_total[year] - expenses_total[year])

    income_expenses_differences_per_year_dict  = dict(
        zip(income_years, income_expenses_differences_per_year))

    # Liabilities
    user_liabilities_data = liabilities_data(user)
    liabilities_total = user_liabilities_data[3]
    liabilities_years = list(user_liabilities_data[0].keys())

    # Assets
    user_assests_data = assets_data(user)
    assets_total = user_assests_data[3]
    assets_years = list(user_assests_data[0].keys())

    # List differences in assets and liabilities per year
    assets_liabilities_differences_per_year = []
    for year in assets_years:
        assets_liabilities_differences_per_year.append(
            assets_total[year] - liabilities_total[year])

    assets_liabilities_differences_per_year_dict = dict(
        zip(assets_years, assets_liabilities_differences_per_year))

    return render_template(
        'index.html',
        title='Income Statement',
        user=user,

        # Income
        income_total=income_total,
        income_years=income_years,

        # Liabilities
        liabilities_total=liabilities_total,
        liabilities_years=liabilities_years,

        # Expenses
        expenses_total=expenses_total,
        expenses_years=expenses_years,

        # Assets
        assets_total=assets_total,
        assets_years=assets_years,

        # Comparison
        income_expenses_differences_per_year_dict=income_expenses_differences_per_year_dict,
        assets_liabilities_differences_per_year_dict=assets_liabilities_differences_per_year_dict)


@app.route('/help', methods=['GET', 'POST'])
@login_required
def help():
    user = User.query.filter_by(username=current_user.username).first()
    form = HelpForm()
    if form.validate_on_submit():
        question = Help(
            body=form.body.data,
            author=user)
        db.session.add(question)
        db.session.commit()
        support_members = Support.query.all()
        for support in support_members:
            send_new_question_email(support)
        flash('An email has been sent to the support team.'
              ' You will receive an email notification when your question is answered.')
        return redirect(url_for('help'))
    page = request.args.get('page', 1, type=int)
    questions = Help.query.order_by(Help.timestamp.desc()).paginate(
        page, app.config['QUESTIONS_PER_PAGE'], False)
    next_url = url_for('help', page=questions.next_num) \
        if questions.has_next else None
    prev_url = url_for('help', page=questions.prev_num) \
        if questions.has_prev else None
    return render_template(
        'help.html',
        title='Help',
        form=form,
        user=user,
        questions=questions.items,
        next_url=next_url,
        prev_url=prev_url)


@app.route('/edit-help/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_help(id):
    user = User.query.filter_by(username=current_user.username).first()
    question = Help.query.get_or_404(id)
    form = HelpForm()
    if form.validate_on_submit():
        if question.body == form.body.data:
            flash('There has been no change in the question, please try again.')
            return redirect(url_for('help'))
        else:
            question.body = form.body.data
            question.edited = True
            db.session.commit()
            flash('Your question has been updated.')
            return redirect(url_for('help'))
    form.body.data = question.body
    return render_template(
        'edit_help.html', title='Edit Help', form=form, user=user)

# ==========================================================
# Admin Dashboard Routes
# ==========================================================


# Render admin dashboard


@app.route('/admin/dashboard/register', methods=['GET', 'POST'])
def admin_dashboard_registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        admin = Admin(username=form.username.data,email=form.email.data)
        admin.set_password(form.password.data)
        db.session.add(admin)
        db.session.commit()
        flash('You have successfully registered as an admin!')
        return redirect(url_for('admin_login'))
    return render_template(
        'register.html',
        title='Registration',
        form=form)


@app.route('/admin/dashboard/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin is None or not admin.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('admin_login'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('admin_dashboard', username=admin.username)
        if admin.two_factor_enabled():
            request_verification_token(admin.verification_phone)
            session['username'] = admin.username
            username = session['username']
            session['phone'] = admin.verification_phone
            return redirect(url_for(
                'admin_verify_2fa', username=admin.username,
                next=next_page,
                remember='1' if form.remember_me.data else '0'))
        login_user(admin, remember=form.remember_me.data)
        flash(f'Welcome back, {admin.username}')
        return redirect(next_page)
    return render_template('admin/admin_login.html', title='Admin Login', form=form)


@app.route('/admin/dashboard/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))


@app.route('/admin/request-password-reset', methods=['GET', 'POST'])
def admin_request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin:
            send_admin_password_reset_email(admin)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('admin_login'))
    return render_template(
        'reset_password_request.html',
        title='[Admin] Request Password Reset',
        form=form)


@app.route('/admin/reset-password/<token>', methods=['GET', 'POST'])
def admin_reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    admin = Admin.verify_reset_password_token(token)
    if not admin:
        return redirect(url_for('admin_login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        admin.set_password(form.password.data)
        db.session.commit()
        flash('Your admin password has been reset.')
        return redirect(url_for('admin_login'))
    return render_template(
        'reset_password.html',
        title='Reset Password',
        form=form)


@app.route('/admin/dashboard/<username>', methods=['GET', 'POST'])
@login_required
def admin_dashboard(username):
    admin = Admin.query.filter_by(username=username).first_or_404()
    form = RegistrationForm()
    if form.validate_on_submit():
        support = Support(username=form.username.data,email=form.email.data)
        support.set_password(form.password.data)
        db.session.add(support)
        db.session.commit()
        send_registration_email(support)
        flash(f'You have successfully registered {support.username} a support team member!')
        return redirect(url_for('admin_dashboard', username=admin.username))
    support_team = Support.query.all()
    return render_template(
        'admin/admin_dashboard.html',
        title='Admin Dashboard',
        admin=admin,
        support_team=support_team,
        form=form)


@app.route('/admin/dashboard/support-member/<username>/delete', methods=['GET', 'POST'])
def admin_delete_support_member(username):
    support = Support.query.filter_by(username=username).first_or_404()
    db.session.delete(support)
    db.session.commit()
    flash(f'You have successfully deleted {support.username} from the support team!')
    return redirect(url_for('admin_dashboard', username=current_user.username))


# Two-factor authentication routes


@app.route('/admin/dashboard/<username>/enable_2fa', methods=['GET', 'POST'])
@login_required
def admin_enable_2fa(username):
    admin = Admin.query.filter_by(username=username).first_or_404()
    form = PhoneForm()
    if form.validate_on_submit():
        session['phone'] = form.verification_phone.data
        request_verification_token(session['phone'])
        return redirect(url_for('admin_verify_2fa', username=admin.username))
    return render_template(
        'enable_2fa.html',
        title='Enable 2FA',
        form=form,
        admin=admin)


@app.route('/admin/dashboard/<username>/verify_2fa', methods=['GET', 'POST'])
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
                return redirect(url_for('admin_dashboard', username=username))
            else:
                username = session['username']
                del session['username']
                admin = Admin.query.filter_by(username=username).first_or_404()
                next_page = request.args.get('next')
                remember = request.args.get('remember', '0') == '1'
                login_user(admin, remember=remember)
                return redirect(next_page or url_for('admin_dashboard', username=username))
        form.token.errors.append('Invalid token')
    return render_template(
        'verify_2fa.html',
        title='Verify 2FA',
        form=form,
        admin=admin)


@app.route('/admin/dashboard/<username>/disable_2fa', methods=['GET', 'POST'])
@login_required
def admin_disable_2fa(username):
    admin = Admin.query.filter_by(username=username).first_or_404()
    form = DisableForm()
    if form.validate_on_submit():
        current_user.verification_phone = None
        db.session.commit()
        flash('You have disabled two-factor authentication on your account.')
        return redirect(url_for('admin_dashboard', username=username))
    return render_template(
        'disable_2fa.html',
        title='Disable 2FA',
        form=form,
        admin=admin)

# ==========================================================
# End of Admin Dashboard Routes
# ==========================================================



# ==========================================================
# Support Dashboard Routes
# ==========================================================

# Basic authentication routes

@app.route('/support/dashboard/login', methods=['GET', 'POST'])
def support_login():
    if current_user.is_authenticated:
        return redirect(url_for('support_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        support = Support.query.filter_by(username=form.username.data).first()
        if support is None or not support.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('support_login'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('support_dashboard', username=support.username)
        if support.two_factor_enabled():
            request_verification_token(support.verification_phone)
            session['username'] = support.username
            username = session['username']
            session['phone'] = support.verification_phone
            return redirect(url_for(
                'support_verify_2fa', username=support.username,
                next=next_page,
                remember='1' if form.remember_me.data else '0'))
        login_user(support, remember=form.remember_me.data)
        flash('Welcome back, ' + support.username)
        return redirect(next_page)
    return render_template(
        'support/support_login.html', title='Support Login', form=form)


@app.route('/dashboard/support/logout')
def support_logout():
    logout_user()
    return redirect(url_for('support_login'))


# Password reset routes


@app.route('/support/request-password-reset', methods=['GET', 'POST'])
def support_request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('support_dashboard'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        support = Support.query.filter_by(email=form.email.data).first()
        if support:
            send_support_password_reset_email(support)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('support_login'))
    return render_template(
        'reset_password_request.html',
        title='[Support] Request Password Reset',
        form=form)


@app.route('/support/reset-password/<token>', methods=['GET', 'POST'])
def support_reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('support_dashboard'))
    support = Admin.verify_reset_password_token(token)
    if not support:
        return redirect(url_for('support_login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        support.set_password(form.password.data)
        db.session.commit()
        flash('Your support password has been reset.')
        return redirect(url_for('support_login'))
    return render_template(
        'reset_password.html',
        title='Reset Password',
        form=form)


@app.route('/support/dashboard/<username>', methods=['GET', 'POST'])
@login_required
def support_dashboard(username):
    support = Support.query.filter_by(username=username).first_or_404()
    form = HelpForm()
    if form.validate_on_submit():
        answer = Help(body = form.body.data, support=support)
        db.session.add(answer)
        db.session.commit()
        flash(f'You have successfully answered a question!')
        return redirect(url_for('support_dashboard', username=support.username))
    users = User.query.all()
    # for user in users:
    #     question_author = user.author.username
    #     if question_author:
    #         send_answer_email(user)
    # flash('You have successfully answered a question! An email has been sent to the user.')
    page = request.args.get('page', 1, type=int)
    all_questions = Help.query.order_by(Help.timestamp.desc()).paginate(
        page, app.config['QUESTIONS_PER_PAGE'], False)
    next_url = url_for(
        'support_dashboard', username=support.username, page=all_questions.next_num) \
            if all_questions.has_next else None
    prev_url = url_for(
        'support_dashboard', username=support.username, page=all_questions.prev_num) \
            if all_questions.has_prev else None
    return render_template(
        'support/support_dashboard.html',
        title='Support Dashboard',
        support=support,
        form=form,
        all_questions=all_questions.items,
        next_url=next_url,
        prev_url=prev_url)


# Two-factor authentication routes


@app.route('/support/dashboard/<username>/enable_2fa', methods=['GET', 'POST'])
@login_required
def support_enable_2fa(username):
    support = Support.query.filter_by(username=username).first_or_404()
    form = PhoneForm()
    if form.validate_on_submit():
        session['phone'] = form.verification_phone.data
        request_verification_token(session['phone'])
        return redirect(url_for('support_verify_2fa', username=support.username))
    return render_template(
        'enable_2fa.html',
        title='Enable 2FA',
        form=form,
        support=support)


@app.route('/support/dashboard/<username>/verify_2fa', methods=['GET', 'POST'])
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
                return redirect(url_for('support_dashboard', username=username))
            else:
                username = session['username']
                del session['username']
                support = Support.query.filter_by(username=username).first_or_404()
                next_page = request.args.get('next')
                remember = request.args.get('remember', '0') == '1'
                login_user(support, remember=remember)
                return redirect(next_page or url_for('support_dashboard', username=username))
        form.token.errors.append('Invalid token')
    return render_template(
        'verify_2fa.html',
        title='Verify 2FA',
        form=form,
        support=support)


@app.route('/support/dashboard/<username>/disable_2fa', methods=['GET', 'POST'])
@login_required
def support_disable_2fa(username):
    support = Support.query.filter_by(username=username).first_or_404()
    form = DisableForm()
    if form.validate_on_submit():
        current_user.verification_phone = None
        db.session.commit()
        flash('You have disabled two-factor authentication on your account.')
        return redirect(url_for('support_dashboard', username=username))
    return render_template(
        'disable_2fa.html',
        title='Disable 2FA',
        form=form,
        support=support)

# ==========================================================
# End of Support Dashboard Routes
# ==========================================================


# ==========================================================
# User Basic Auth
# ==========================================================


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        if user.two_factor_enabled():
            request_verification_token(user.verification_phone)
            session['username'] = user.username
            session['phone'] = user.verification_phone
            return redirect(url_for(
                'verify_2fa',
                next=next_page,
                remember='1' if form.remember_me.data else '0'))
        login_user(user, remember=form.remember_me.data)
        flash('Welcome back, ' + user.username)
        return redirect(next_page)
    return render_template('login.html', title='User Login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user! '
              'Login to continue')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/request-for-password-reset', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template(
        'reset_password_request.html',
        title='Request Password Reset ', form=form)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template(
        'reset_password.html', form=form, title='Reset Password')


# ===============================================================
# Two-factor authentication
# ===============================================================


@app.route('/enable-2fa', methods=['GET', 'POST'])
@login_required
def enable_2fa():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    form = PhoneForm()
    if form.validate_on_submit():
        session['phone'] = form.verification_phone.data
        request_verification_token(session['phone'])
        return redirect(url_for('verify_2fa'))
    return render_template(
        'enable_2fa.html', title='Enable 2FA', form=form, user=user)


@app.route('/verify-2fa', methods=['GET', 'POST'])
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
                return redirect(url_for('help'))
            else:
                username = session['username']
                del session['username']
                user = User.query.filter_by(username=username).first()
                next_page = request.args.get('next')
                remember = request.args.get('remember', '0') == '1'
                login_user(user, remember=remember)
                flash('Welcome back ' + user.username)
                return redirect(next_page or url_for('index'))
        form.token.errors.append('Invalid token.')
    return render_template('verify_2fa.html', title='Verify 2FA', form=form)


@app.route('/disable-2fa', methods=['GET', 'POST'])
@login_required
def disable_2fa():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    form = DisableForm()
    if form.validate_on_submit():
        current_user.verification_phone = None
        db.session.commit()
        flash('You have disabled two-factor authentication.')
        return redirect(url_for('help'))
    return render_template(
        'disable_2fa.html', title='Disable 2FA', form=form, user=user)


# ===============================================================
# Get User data
# ===============================================================

@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    user = User.query.filter_by(username=current_user.username).first()

    # ==========================================================
    # USER BUDGET
    # ==========================================================

    # Get all budget items for current user
    budget_form = BudgetItemForm()
    if budget_form.validate_on_submit() and budget_form.budget.data:
        budget_item = BudgetItem(
            date=budget_form.date.data,
            name=budget_form.name.data,
            amount=budget_form.amount.data,
            user_id=current_user.id)
        db.session.add(budget_item)
        db.session.commit()
        flash(budget_item.name + ' has been added to your budget items')
        return redirect(url_for('update', anchor='budget'))
    budget_items = user.budget_items.all()
    user_budget_data = budget_data(user)

    # Get keys and values from user_budget_data[0]
    label_months = user_budget_data[4]
    budget_years = list(user_budget_data[0].keys())
    budget_months = list(user_budget_data[0].values())
    budget_amounts = list(user_budget_data[1].values())
    reps = len(budget_years) # Used in chartjs to loop through the values from the dict
    colors = ['#00bcd4', '#ff9800', '#9c27b0', '#2196f3', '#ffeb3b',
              '#ffc107', '#673ab7', '#795548', '#009688', '#607d8b']
    # ==========================================================
    # USER ASSETS
    # ==========================================================

    # Get all asset items for current user
    asset_form = AssetForm()
    if asset_form.validate_on_submit() and asset_form.asset.data:
        asset_item = Asset(
            date=asset_form.date.data,
            name=asset_form.name.data,
            amount=asset_form.amount.data,
            user_id=current_user.id)
        db.session.add(asset_item)
        db.session.commit()
        flash(asset_item.name + ' has been added to your assets')
        return redirect(url_for('update', anchor='assets'))
    assets = user.assets.all()
    user_assets_data = assets_data(user)

    # Get keys and values from user_assets_data[0]
    asset_label_months = user_assets_data[4]
    asset_years = list(user_assets_data[0].keys())
    asset_months = list(user_assets_data[0].values())
    asset_amounts = list(user_assets_data[1].values())
    asset_reps = len(asset_years) # Used in chartjs to loop through the values from the dict
    asset_colors = ['#ffc107', '#673ab7', '#795548', '#009688', '#607d8b',
                    '#00bcd4', '#ff9800', '#9c27b0', '#2196f3', '#ffeb3b']

    # ==========================================================
    # USER LIABILITIES
    # ==========================================================

    # Get all liability items for current user
    liability_form = LiabilityForm()
    if liability_form.validate_on_submit() and liability_form.liability.data:
        liability_item = Liability(
            date=liability_form.date.data,
            name=liability_form.name.data,
            amount=liability_form.amount.data,
            user_id=current_user.id)
        db.session.add(liability_item)
        db.session.commit()
        flash(liability_item.name + ' has been added to your liabilities')
        return redirect(url_for('update', anchor='liabilities'))
    liabilities = user.liabilities.all()
    user_liabilities_data = liabilities_data(user)

    # Get keys and values from user_liabilities_data[0]
    liability_label_months = user_liabilities_data[4]
    liability_years = list(user_liabilities_data[0].keys())
    liability_months = list(user_liabilities_data[0].values())
    liability_amounts = list(user_liabilities_data[1].values())
    liability_reps = len(liability_years) # Used in chartjs to loop through the values from the dict
    liability_colors = ['#61481C', '#673ab7', '31F4690', '#FFE5B4', '#66BFBF',
                        '#FF0063', '#A47E3B', '#9c27b0', '#2196f3', '#ffeb3b']

    # ==========================================================
    # USER INCOME
    # ==========================================================

    # Update current user's income
    actual_income_form = ActualIncomeForm()
    if actual_income_form.validate_on_submit() \
            and actual_income_form.actual_income.data:
        actual_income = ActualIncome(
            name=actual_income_form.name.data,
            date=actual_income_form.date.data,
            amount=actual_income_form.amount.data,
            user_id=current_user.id)
        db.session.add(actual_income)
        db.session.commit()
        flash(str(actual_income.amount) + ' has been added to your income')
        return redirect(url_for('update', anchor='income-sources'))
    actual_incomes = user.actual_incomes.all()
    user_income_data = income_data(user)

    # Get keys and values from user_income_data[0]
    income_label_months = user_income_data[4]
    income_years = list(user_income_data[0].keys())
    income_months = list(user_income_data[0].values())
    income_amounts = list(user_income_data[1].values())
    income_reps = len(income_years) # Used in chartjs to loop through the values from the dict
    income_colors = ['#ffc107', '#673ab7', '#795548', '#009688', '#607d8b' ,
                        '#00bcd4', '#ff9800', '#9c27b0', '#2196f3', '#ffeb3b']

    # ==========================================================
    # USER EXPENSES
    # ==========================================================

    # Update current user's expenses
    expense_form = ActualExpenseForm()  # same income form
    if expense_form.validate_on_submit() \
            and expense_form.actual_expense.data:
        actual_expense = Expenses(
            name=expense_form.name.data,
            date=expense_form.date.data,
            amount=expense_form.amount.data,
            user_id=current_user.id)
        db.session.add(actual_expense)
        db.session.commit()
        flash(str(actual_expense.amount) + ' has been added to your expenses')
        return redirect(url_for('update', anchor='expenses'))
    actual_expenses = user.expenses.all()
    user_expenses_data = expenses_data(user)

    # Get keys and values from user_expenses_data[0]
    expense_label_months = user_expenses_data[4]
    expense_years = list(user_expenses_data[0].keys())
    expense_months = list(user_expenses_data[0].values())
    expense_amounts = list(user_expenses_data[1].values())
    expense_reps = len(expense_years) # Used in chartjs to loop through the values from the dict
    expense_colors = ['#C8B6E2', '#377D71', '#795548', '#009688', '#495C83',
                        '#FBA1A1', '#ff9800', '#9c27b0', '#1A4D2E', '#ffeb3b']

    return render_template(
            'update.html',
            title='Update Your Financial Statement',
            user=user,

            # Budget data
            budget_form=budget_form,
            user_budget_data=user_budget_data,
            label_months=label_months,
            budget_years=budget_years,
            budget_months=budget_months,
            budget_amounts=budget_amounts,
            budget_items=budget_items,
            reps=reps,
            colors=colors,

            # Income data
            actual_income_form=actual_income_form,
            actual_incomes=actual_incomes,
            user_income_data=user_income_data,
            income_label_months=income_label_months,
            income_years=income_years,
            income_months=income_months,
            income_amounts=income_amounts,
            income_reps=income_reps,
            income_colors=income_colors,

            # Assets data
            asset_form=asset_form,
            assets=assets,
            user_assets_data=user_assets_data,
            asset_label_months=asset_label_months,
            asset_years=asset_years,
            asset_months=asset_months,
            asset_amounts=asset_amounts,
            asset_reps=asset_reps,
            asset_colors=asset_colors,

            # Expenses data
            expense_form=expense_form,
            actual_expenses=actual_expenses,
            user_expenses_data=user_expenses_data,
            expense_label_months=expense_label_months,
            expense_years=expense_years,
            expense_months=expense_months,
            expense_amounts=expense_amounts,
            expense_reps=expense_reps,
            expense_colors=expense_colors,

            # Liabilities data
            liability_form=liability_form,
            liabilities=liabilities,
            user_liabilities_data=user_liabilities_data,
            liability_label_months=liability_label_months,
            liability_years=liability_years,
            liability_months=liability_months,
            liability_amounts=liability_amounts,
            liability_reps=liability_reps,
            liability_colors=liability_colors)

# ===============================================================
# End of Get User data
# ===============================================================

# ===============================================================
# Delete User data
# ===============================================================


@app.route('/delete/budget-item-<int:id>')
def budget_item_delete(id):
    budget_item = BudgetItem.query.get_or_404(id)
    db.session.delete(budget_item)
    db.session.commit()
    flash(budget_item.name + ' has been deleted from budget items')
    return redirect(url_for('update', anchor='budget'))


@app.route('/delete/income-source-<int:id>')
def actual_expense_delete(id):
    actual_expense = Expenses.query.get_or_404(id)
    db.session.delete(actual_expense)
    db.session.commit()
    flash(actual_expense.name + ' has been deleted from your expenses')
    return redirect(url_for('update', anchor='expenses'))


@app.route('/delete/asset-<int:id>')
def asset_delete(id):
    asset = Asset.query.get_or_404(id)
    db.session.delete(asset)
    db.session.commit()
    flash(asset.name + ' has been deleted from asset items')
    return redirect(url_for('update', anchor='assets'))


@app.route('/delete/liability-<int:id>')
def liability_delete(id):
    liability = Liability.query.get_or_404(id)
    db.session.delete(liability)
    db.session.commit()
    flash(liability.name + ' has been deleted from liability items')
    return redirect(url_for('update', anchor='liabilities'))


@app.route('/delete/income-<int:id>')
def actual_income_delete(id):
    actual_income = ActualIncome.query.get_or_404(id)
    db.session.delete(actual_income)
    db.session.commit()
    flash(str(actual_income.amount) + ' has been deleted from actual income')
    return redirect(url_for('update', anchor='income-sources'))

# ===============================================================
# End of Delete User data
# ===============================================================

# ===============================================================
# Download and Encrypt User data
# ===============================================================


@app.route('/download-budget-data', methods=['GET', 'POST'])
@login_required
def download_budget_data():
    """Download budget data as pdf"""
    user = User.query.filter_by(username=current_user.username).first()
    user_budget_data = budget_data(user)

    # Get keys and values from user_budget_data[0]
    budget_years = list(user_budget_data[0].keys())

    # Download budget data as pdf
    download_data_form = DownloadDataForm()
    download_data_form.year.choices = [(year, year) for year in budget_years]
    if download_data_form.validate_on_submit() and download_data_form.year.data:
        # Save the year in session to be used in the naming of pdf
        session['year'] = download_data_form.year.data
        # Download the budget data as pdf file
        # Downloaded file will be saved in a chosen directory
        download_budget_pdf(user)
        flash('Save popup should have been triggered.')
        # Encrypt the pdf file
        encrypt_pdf(
            input_pdf=app.config['PDF_FOLDER_PATH'] + 'budget_data' + session['year'] + '.pdf',
            password=user.username)
        # Download file to local computer
        # File like objects are opend in binary mode
        buffer = BytesIO()
        buffer.write(open(
            app.config['PDF_FOLDER_PATH'] + 'budget_data' + session['year'] + '.pdf', 'rb').read())
        # File pointer will be seeked to the start of the data
        buffer.seek(0)
        # Delete the downloaded pdf file from project folder (save space)
        os.remove(app.config['PDF_FOLDER_PATH'] + 'budget_data' + session['year'] + '.pdf')
        # Send the file to the browser as a pdf file
        return send_file(
            buffer,
            attachment_filename='budget_data' + session['year'] + '.pdf',
            as_attachment=True)
    return render_template(
        'download_data_form.html',
        title='Download Budget Data',
        download_data_form=download_data_form,
        user=user)


@app.route('/download-asset-data', methods=['GET', 'POST'])
@login_required
def download_asset_data():
    """Download asset data as pdf"""
    user = User.query.filter_by(username=current_user.username).first()
    user_assets_data = assets_data(user)

    # Get keys and values from user_assets_data[0]
    asset_years = list(user_assets_data[0].keys())

    # Download asset data as pdf
    download_data_form = DownloadDataForm()
    download_data_form.year.choices = [(year, year) for year in asset_years]
    if download_data_form.validate_on_submit() and download_data_form.year.data:
        session['year'] = download_data_form.year.data
        download_assets_pdf(user)
        flash('Save popup should have been triggered.')
        encrypt_pdf(
            input_pdf=app.config['PDF_FOLDER_PATH'] + 'asset_data' + session['year'] + '.pdf',
            password=user.username)
        buffer = BytesIO()
        buffer.write(open(
            app.config['PDF_FOLDER_PATH'] + 'asset_data' + session['year'] + '.pdf', 'rb').read())
        buffer.seek(0)
        os.remove(app.config['PDF_FOLDER_PATH'] + 'asset_data' + session['year'] + '.pdf')
        return send_file(
            buffer,
            attachment_filename='asset_data' + session['year'] + '.pdf',
            as_attachment=True)
    return render_template(
        'download_data_form.html',
        title='Download Asset Data',
        download_data_form=download_data_form,
        user=user)


@app.route('/download-liabilities-data', methods=['GET', 'POST'])
@login_required
def download_liabilities_data():
    """Download liabilities data as pdf"""
    user = User.query.filter_by(username=current_user.username).first()
    user_liabilities_data = liabilities_data(user)

    # Get keys and values from user_liabilities_data[0]
    liability_years = list(user_liabilities_data[0].keys())

    # Download liabilities data as pdf
    download_data_form = DownloadDataForm()
    download_data_form.year.choices = [(year, year) for year in liability_years]
    if download_data_form.validate_on_submit() and download_data_form.year.data:
        session['year'] = download_data_form.year.data
        download_liabilities_pdf(user)
        flash('Save popup should have been triggered.')
        encrypt_pdf(
            input_pdf=app.config['PDF_FOLDER_PATH'] + 'liabilities_data' + session['year'] + '.pdf',
            password=user.username)
        buffer = BytesIO()
        buffer.write(open(
            app.config['PDF_FOLDER_PATH'] + 'liabilities_data' + session['year'] + '.pdf', 'rb').read())
        buffer.seek(0)
        os.remove(app.config['PDF_FOLDER_PATH'] + 'liabilities_data' + session['year'] + '.pdf')
        return send_file(
            buffer,
            attachment_filename='liabilities_data' + session['year'] + '.pdf',
            as_attachment=True)
    return render_template(
        'download_data_form.html',
        title='Download Liabilities Data',
        download_data_form=download_data_form,
        user=user)


@app.route('/download-expenses-data', methods=['GET', 'POST'])
@login_required
def download_expenses_data():
    """Download expenses data as pdf"""
    user = User.query.filter_by(username=current_user.username).first()
    user_expenses_data = expenses_data(user)

    # Get keys and values from user_expenses_data[0]
    expense_years = list(user_expenses_data[0].keys())

    # Download expenses data as pdf
    download_data_form = DownloadDataForm()
    download_data_form.year.choices = [(year, year) for year in expense_years]
    if download_data_form.validate_on_submit() and download_data_form.year.data:
        session['year'] = download_data_form.year.data
        download_expenses_pdf(user)
        flash('Save popup should have been triggered.')
        encrypt_pdf(
            input_pdf=app.config['PDF_FOLDER_PATH'] + 'expenses_data' + session['year'] + '.pdf',
            password=user.username)
        buffer = BytesIO()
        buffer.write(open(
            app.config['PDF_FOLDER_PATH'] + 'expenses_data' + session['year'] + '.pdf', 'rb').read())
        buffer.seek(0)
        os.remove(app.config['PDF_FOLDER_PATH'] + 'expenses_data' + session['year'] + '.pdf')
        return send_file(
            buffer,
            attachment_filename='expenses_data' + session['year'] + '.pdf',
            as_attachment=True)
    return render_template(
        'download_data_form.html',
        title='Download Expenses Data',
        download_data_form=download_data_form,
        user=user)


@app.route('/download-income-data', methods=['GET', 'POST'])
@login_required
def download_income_data():
    """Download income data as pdf"""
    user = User.query.filter_by(username=current_user.username).first()
    user_income_data = income_data(user)

    # Get keys and values from user_income_data[0]
    income_years = list(user_income_data[0].keys())

    # Download income data as pdf
    download_data_form = DownloadDataForm()
    download_data_form.year.choices = [(year, year) for year in income_years]
    if download_data_form.validate_on_submit() and download_data_form.year.data:
        session['year'] = download_data_form.year.data
        download_income_pdf(user)
        flash('Save popup should have been triggered.')
        encrypt_pdf(
            input_pdf=app.config['PDF_FOLDER_PATH'] + 'income_data' + session['year'] + '.pdf',
            password=user.username)
        buffer = BytesIO()
        buffer.write(open(
            app.config['PDF_FOLDER_PATH'] + 'income_data' + session['year'] + '.pdf', 'rb').read())
        buffer.seek(0)
        os.remove(app.config['PDF_FOLDER_PATH'] + 'income_data' + session['year'] + '.pdf')
        return send_file(
            buffer,
            attachment_filename='income_data' + session['year'] + '.pdf',
            as_attachment=True)
    return render_template(
        'download_data_form.html',
        title='Download Income Data',
        download_data_form=download_data_form,
        user=user)

# ===============================================================
# End of Download and Encrypt User data
# ===============================================================
