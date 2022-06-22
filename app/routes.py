from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, BudgetItemForm, \
    AssetForm, LiabilityForm, ActualIncomeForm, ActualExpenseForm
from app.models import User, BudgetItem, Expenses, \
    Asset, Liability, ActualIncome
from flask_login import current_user, login_user, logout_user, login_required


# The two functions below allow us to specify what forms
# are to be submitted in a post request
def validate_on_submit(self):
    return self.is_submitted() and self.validate()


def is_submitted(self):
    return self.form.is_submitted()


def budget_data():
    user = User.query.filter_by(username=current_user.username).first()
    budget = user.budget_items.all()

    # Get individual items from the budget
    budget_item = [item.name for item in budget]
    amount = [item.amount for item in budget]
    budget_date = [item.date for item in budget]

    # Get months from the budget dates
    date = [budget_date.date.split('-') for budget_date in budget]

    # Get month number from date
    month = [int(date[i][1]) for i in range(len(date))]
    # Replace month numbers with names
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
    month_names_in_budget = [month_names[int(month[i]) - 1] for i in range(len(month))]

    # Create lists needed by ChartJS:
    # month_names: month in list should not be repeated
    # budget_item: list of budget items in database
    # budget_amount: list of amounts for each budget item

    new_month = [] # number of month in list, not repeated
    new_month_name = [] # month name in list, not repeated
    budget_amount = [] # amount of each budget item

    for i in range(len(month)):
        # find if month in list
        if month[i] in new_month:
            # if month in list, find index of month
            index = new_month.index(month[i])
            # add amount to index
            budget_amount[index] += amount[i]
        else:
            # if month not in list, add month to list
            new_month.append(month[i])
            # add amount to list
            budget_amount.append(amount[i])
            # find month name
            new_month_name.append(month_names[month[i] - 1])

    return new_month_name, budget_item, budget_amount

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

    # Get item number
    item_number = [i for i in range(len(all_budget_items))]
    print(item_number)

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

    # Update current user's income
    actual_income_form = ActualIncomeForm()
    if actual_income_form.validate_on_submit() \
            and actual_income_form.actual_income.data:
        actual_income = ActualIncome(
            name=actual_income_form.name.data,
            date=actual_income_form.date.data,
            amount=actual_income_form.amount.data,
            description=actual_income_form.description.data,
            user_id=current_user.id)
        db.session.add(actual_income)
        db.session.commit()
        flash(str(actual_income.amount) + ' has been added to your income')
        return redirect(url_for('update', anchor='income-sources'))
    actual_incomes = user.actual_incomes.all()
    date = [actual_income.date.split('-') for actual_income in actual_incomes]
    #print(date)
    year = [int(date[i][0]) for i in range(len(date))]
    month = [int(date[i][1]) for i in range(len(date))]
    day = [int(date[i][2]) for i in range(len(date))]
    print('Year:month:day', year, month, day)

    # Update current user's expenses
    expense_form = ActualExpenseForm()  # same income form
    if expense_form.validate_on_submit() \
            and expense_form.actual_expense.data:
        actual_expense = Expenses(
            name=expense_form.name.data,
            date=expense_form.date.data,
            amount=expense_form.amount.data,
            description=expense_form.description.data,
            user_id=current_user.id)
        db.session.add(actual_expense)
        db.session.commit()
        flash(str(actual_expense.amount) + ' has been added to your expenses')
        return redirect(url_for('update', anchor='expenses'))
    actual_expenses = user.expenses.all()

    return render_template(
            'update.html',
            title='Update Items',
            budget_form=budget_form,
            budget_items=budget_items,
            expense_form=expense_form,
            actual_expenses=actual_expenses,
            asset_form=asset_form,
            assets=assets,
            liability_form=liability_form,
            liabilities=liabilities,
            actual_income_form=actual_income_form,
            actual_incomes=actual_incomes,

            # Budget data
            months=months,
            all_budget_items=all_budget_items,
            budget_amount=budget_amount,
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
