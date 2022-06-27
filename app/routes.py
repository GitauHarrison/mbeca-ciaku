from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, BudgetItemForm, \
    AssetForm, LiabilityForm, ActualIncomeForm, ActualExpenseForm
from app.models import User, BudgetItem, Expenses, \
    Asset, Liability, ActualIncome
from flask_login import current_user, login_user, logout_user, login_required
from app.data_income import income_data
from app.data_budget import budget_data
from app.data_assets import assets_data
from app.data_expense import expenses_data
from app.data_liabilities import liabilities_data


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
    return render_template('index.html', title='Index')


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

    # Get current user's budget
    months = budget_data()[0]
    all_budget_items = budget_data()[1]
    budget_amount = budget_data()[2]

    # print("Months:", months)
    # print("New Month:", new_month)
    # print("Budget items:", all_budget_items)
    # print("Budget amounts:", budget_amount)

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

    # Get current user's assets
    assets_months = assets_data()[0]
    all_assets = assets_data()[1]
    assets_amounts = assets_data()[2]

    # ==========================================================
    # USER LIABILITY
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

    # Get current user's liabilities
    liabilities_months = liabilities_data()[0]
    all_liabilities = liabilities_data()[1]
    liabilities_amounts = liabilities_data()[2]

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
            budget_items=budget_items,
            months=months,
            all_budget_items=all_budget_items,
            budget_amount=budget_amount,

            # Income data
            actual_income_form=actual_income_form,
            actual_incomes=actual_incomes,
            income_months=income_months,
            income_items=income_items,
            income_amounts=income_amounts,

            # Assets data
            asset_form=asset_form,
            assets=assets,
            assets_months=assets_months,
            all_assets=all_assets,
            assets_amounts=assets_amounts,

            # Expenses data
            expense_form=expense_form,
            actual_expenses=actual_expenses,
            expense_months=expense_months,
            expense_items=expense_items,
            expense_amounts=expense_amounts,

            # Liabilities data
            liability_form=liability_form,
            liabilities=liabilities,
            liabilities_months=liabilities_months,
            all_liabilities=all_liabilities,
            liabilities_amounts=liabilities_amounts,
            )


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


@app.route('/delete/actual-income-<int:id>')
def actual_income_delete(id):
    actual_income = ActualIncome.query.get_or_404(id)
    db.session.delete(actual_income)
    db.session.commit()
    flash(str(actual_income.amount) + ' has been deleted from actual income')
    return redirect(url_for('update', anchor='income-sources'))
