from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, BudgetItemForm, \
    IncomeSourceForm, AssetItemForm, LiabilityItemForm
from app.models import User, BudgetItem, IncomeSource, \
    AssetItem, LiabilityItem
from flask_login import current_user, login_user, logout_user, login_required


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Index')


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
        flash('Congratulations, you are now a registered user!'
              'Login to continue')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


def validate_on_submit(self):
    return self.is_submitted() and self.validate()


def is_submitted(self):
    return self.form.is_submitted()


@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    # Get all budget items for current user
    budget_form = BudgetItemForm()
    if budget_form.validate_on_submit() and budget_form.budget.data:
        budget_item = BudgetItem(
            name=budget_form.name.data, user_id=current_user.id)
        db.session.add(budget_item)
        db.session.commit()
        flash(budget_item.name + ' has been added to your budget items')
        return redirect(url_for('update', anchor='budget'))
    budget_items = BudgetItem.query.filter_by(user_id=current_user.id)

    # Get all income sources for current user
    income_form = IncomeSourceForm()
    if income_form.validate_on_submit() and income_form.income.data:
        income_source = IncomeSource(
            name=income_form.name.data, user_id=current_user.id)
        db.session.add(income_source)
        db.session.commit()
        flash(income_source.name + ' has been added to your income sources')
        return redirect(url_for('update', anchor='budget'))
    income_sources = IncomeSource.query.filter_by(user_id=current_user.id)

    # Get all asset items for current user
    asset_form = AssetItemForm()
    if asset_form.validate_on_submit() and asset_form.asset.data:
        asset_item = AssetItem(
            name=asset_form.name.data, user_id=current_user.id)
        db.session.add(asset_item)
        db.session.commit()
        flash(asset_item.name + ' has been added to your asset items')
        return redirect(url_for('update', anchor='assets'))
    asset_items = AssetItem.query.filter_by(user_id=current_user.id)

    # Get all liability items for current user
    liability_form = LiabilityItemForm()
    if liability_form.validate_on_submit() and liability_form.liability.data:
        liability_item = LiabilityItem(
            name=liability_form.name.data, user_id=current_user.id)
        db.session.add(liability_item)
        db.session.commit()
        flash(liability_item.name + ' has been added to your liability items')
        return redirect(url_for('update', anchor='liabilities'))
    liability_items = LiabilityItem.query.filter_by(user_id=current_user.id)
    return render_template(
            'update.html',
            title='Update',
            budget_form=budget_form,
            budget_items=budget_items,
            income_form=income_form,
            income_sources=income_sources,
            asset_form=asset_form,
            asset_items=asset_items,
            liability_form=liability_form,
            liability_items=liability_items)


@app.route('/delete/budget-item-<int:id>')
def budget_item_delete(id):
    budget_item = BudgetItem.query.get_or_404(id)
    db.session.delete(budget_item)
    db.session.commit()
    flash(budget_item.name + ' has been deleted from budget items')
    return redirect(url_for('update', anchor='budget'))


@app.route('/delete/income-source-<int:id>')
def income_source_delete(id):
    income_source = IncomeSource.query.get_or_404(id)
    db.session.delete(income_source)
    db.session.commit()
    flash(income_source.name + ' has been deleted from income sources')
    return redirect(url_for('update', anchor='income'))


@app.route('/delete/asset-item-<int:id>')
def asset_item_delete(id):
    asset_item = AssetItem.query.get_or_404(id)
    db.session.delete(asset_item)
    db.session.commit()
    flash(asset_item.name + ' has been deleted from asset items')
    return redirect(url_for('update', anchor='assets'))


@app.route('/delete/liability-item-<int:id>')
def liability_item_delete(id):
    liability_item = LiabilityItem.query.get_or_404(id)
    db.session.delete(liability_item)
    db.session.commit()
    flash(liability_item.name + ' has been deleted from liability items')
    return redirect(url_for('update', anchor='liabilities'))