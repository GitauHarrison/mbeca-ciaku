from crypt import methods
from app import app, db
from flask import render_template, flash, redirect, url_for, session,\
    abort
from app.forms import LoginForm, RegistrationForm, BudgetItemForm, \
    AssetForm, LiabilityForm, ActualIncomeForm, ActualExpenseForm, \
    DownloadDataForm
from app.models import User, BudgetItem, Expenses, Asset, Liability,\
    ActualIncome
from flask_login import current_user, login_user, logout_user, \
    login_required
from app.data_income import income_data
from app.data_budget import budget_data
from app.download_budget_data import download_budget_pdf
from app.download_assets_data import download_assets_pdf
from app.download_liabilities_data import download_liabilities_pdf
from app.data_assets import assets_data
from app.data_expense import expenses_data
from app.data_liabilities import liabilities_data
from app.encrypt_pdf import encrypt_pdf
import os


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
    return render_template('index.html', title='Income Statement')


@app.route('/help')
@login_required
def help():
    return render_template('help.html', title='Help')


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
        login_user(user, remember=form.remember_me.data)
        flash('Welcome back, ' + user.username)
        return redirect(url_for('index'))
    return render_template('login.html', title='Login', form=form)


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


# ==================== GET USER DATA FUNCTIONS ====================

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
    liability_years = list(user_liabilities_data[0].keys())
    liability_months = list(user_liabilities_data[0].values())
    liability_amounts = list(user_liabilities_data[1].values())
    liability_reps = len(liability_years) # Used in chartjs to loop through the values from the dict
    liability_colors = ['61481C', '#673ab7', '1F4690', 'FFE5B4', '66BFBF',
                        'FF0063', 'A47E3B', '#9c27b0', '#2196f3', '#ffeb3b']

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

    # Get current user's incomes
    income_months = income_data()[0]
    income_items = income_data()[1]
    income_amounts = income_data()[2]

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

    # Get current user's expenses
    expense_months = expenses_data()[0]
    expense_items = expenses_data()[1]
    expense_amounts = expenses_data()[2]

    return render_template(
            'update.html',
            title='Update Items',

            # Budget data
            budget_form=budget_form,
            user_budget_data=user_budget_data,
            budget_years=budget_years,
            budget_months=budget_months,
            budget_amounts=budget_amounts,
            budget_items=budget_items,
            reps=reps,
            colors=colors,

            # Income data
            actual_income_form=actual_income_form,
            actual_incomes=actual_incomes,
            income_months=income_months,
            income_items=income_items,
            income_amounts=income_amounts,

            # Assets data
            asset_form=asset_form,
            assets=assets,
            user_assets_data=user_assets_data,
            asset_years=asset_years,
            asset_months=asset_months,
            asset_amounts=asset_amounts,
            asset_reps=asset_reps,
            asset_colors=asset_colors,

            # Expenses data
            expense_form=expense_form,
            actual_expenses=actual_expenses,
            expense_months=expense_months,
            expense_items=expense_items,
            expense_amounts=expense_amounts,

            # Liabilities data
            liability_form=liability_form,
            liabilities=liabilities,
            user_liabilities_data=user_liabilities_data,
            liability_years=liability_years,
            liability_months=liability_months,
            liability_amounts=liability_amounts,
            liability_reps=liability_reps,
            liability_colors=liability_colors
            )

# ==================== END OF GET DATA FUNCTIONS ====================

# ==================== DELETE USER DATA ====================


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

# ==================== END OF DELETE USER DATA ====================

# ==================== DOWNLOAD USER DATA ====================


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
        session['year'] = download_data_form.year.data
        download_budget_pdf(user)
        flash('Your budget data has been downloaded. Click Save to keep a copy.')
        encrypt_pdf(
            input_pdf=app.config['PDF_FOLDER'] + 'budget_data' + session['year'] + '.pdf',
            password=user.username)
        del session['year']
        return redirect(url_for('update', anchor='budget'))
    return render_template(
        'download_data_form.html',
        title='Download Budget Data',
        download_data_form=download_data_form)


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
        flash('Your asset data has been downloaded. Click Save to keep a copy.')
        encrypt_pdf(
            input_pdf=app.config['PDF_FOLDER'] + 'asset_data' + session['year'] + '.pdf',
            password=user.username)
        del session['year']
        return redirect(url_for('update', anchor='assets'))
    return render_template(
        'download_data_form.html',
        title='Download Asset Data',
        download_data_form=download_data_form)


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
        flash('Your liabilities data has been downloaded. Click Save to keep a copy.')
        encrypt_pdf(
            input_pdf=app.config['PDF_FOLDER'] + 'liabilities_data' + session['year'] + '.pdf',
            password=user.username)
        del session['year']
        return redirect(url_for('update', anchor='liabilities'))
    return render_template(
        'download_data_form.html',
        title='Download Liabilities Data',
        download_data_form=download_data_form)
# ==================== DOWNLOAD USER DATA ====================
