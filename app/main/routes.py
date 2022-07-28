from app import db
from app.main import bp
from flask import render_template, flash, redirect, url_for, session,\
    request, send_file, current_app
from app.main.forms import BudgetItemForm, AssetForm, LiabilityForm, \
    ActualIncomeForm, ActualExpenseForm, DownloadDataForm, HelpForm
from app.models import User, BudgetItem, Expenses, Asset, Liability,\
    ActualIncome, Help, Support
from flask_login import current_user, login_required
from app.main.data_income import income_data
from app.main.data_budget import budget_data
from app.main.data_expense import expenses_data
from app.main.download_budget_data import download_budget_pdf
from app.main.download_assets_data import download_assets_pdf
from app.main.download_liabilities_data import download_liabilities_pdf
from app.main.download_expenses_data import download_expenses_pdf
from app.main.download_income_data import download_income_pdf
from app.main.data_assets import assets_data
from app.main.data_expense import expenses_data
from app.main.data_liabilities import liabilities_data
from app.main.encrypt_pdf import encrypt_pdf
from io import BytesIO
import os
from app.main.email import send_new_question_email
import time

# The two functions below allow us to specify what forms
# are to be submitted in a post request
def validate_on_submit(self):
    return self.is_submitted() and self.validate()


def is_submitted(self):
    return self.form.is_submitted()


@bp.route('/<username>')
@bp.route('/index/<username>')
@login_required
def index(username):
    user = User.query.filter_by(username=username).first()

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
            # If either income or expenses is missing for a year,
            # then we will use 0 as the difference
            income_total.get(year, 0) - \
                # if expenses is empty, set it to 0
                # otherwise, set it to the value of the key
                # in the expenses dictionary
                expenses_total.get(year, 0))

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
            assets_total.get(year, 0) - \
                # if liabilities is empty, set it to 0
                # otherwise, set it to the value of the key
                # in the liabilities dictionary
                liabilities_total.get(year, 0))

    assets_liabilities_differences_per_year_dict = dict(
        zip(assets_years, assets_liabilities_differences_per_year))

    return render_template(
        'main/index.html',
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


@bp.route('/<username>/help', methods=['GET', 'POST'])
@login_required
def help(username):
    user = User.query.filter_by(username=username).first()
    support = Support.query.all()
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
        return redirect(url_for('main.help', username=user.username))
    page = request.args.get('page', 1, type=int)
    questions = Help.query.order_by(Help.timestamp.desc()).paginate(
        page, current_app.config['QUESTIONS_PER_PAGE'], False)
    next_url = url_for('main.help', username=user.username, page=questions.next_num) \
        if questions.has_next else None
    prev_url = url_for('main.help', username=user.username, page=questions.prev_num) \
        if questions.has_prev else None
    return render_template(
        'main/help.html',
        title='Help',
        form=form,
        user=user,
        support=support,
        questions=questions.items,
        next_url=next_url,
        prev_url=prev_url)


@bp.route('/<username>/edit-help/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_help(username, id):
    user = User.query.filter_by(username=username).first()
    question = Help.query.get_or_404(id)
    form = HelpForm()
    if form.validate_on_submit():
        if question.body == form.body.data:
            flash('There has been no change in the question, please try again.')
            return redirect(url_for('main.help', username=user.username))
        else:
            question.body = form.body.data
            question.edited = True
            db.session.commit()
            flash('Your question has been updated.')
            return redirect(url_for('main.help', username=user.username))
    form.body.data = question.body
    return render_template(
        'main/edit_help.html', title='Edit Help', form=form, user=user)


@bp.route('/delete/<username>/account')
@login_required
def delete_account(username):
    user = User.query.filter_by(username=username).first()
    items = user.budget_items.all()
    for item in items:
        db.session.delete(item)
    user_expenses = user.expenses.all()
    for expense in user_expenses:
        db.session.delete(expense)
    user_assets = user.assets.all()
    for asset in user_assets:
        db.session.delete(asset)
    user_liabilities = user.liabilities.all()
    for liability in user_liabilities:
        db.session.delete(liability)
    user_incomes = user.actual_incomes.all()
    for income in user_incomes:
        db.session.delete(income)
    user_questions = user.questions.all()
    for question in user_questions:
        db.session.delete(question)
    db.session.delete(user)
    db.session.commit()
    flash('Your account, and all its data has been deleted.')
    return redirect(url_for('auth.login'))


# ===============================================================
# Get User data
# ===============================================================

@bp.route('/update/<username>', methods=['GET', 'POST'])
@login_required
def update(username):
    user = User.query.filter_by(username=username).first()

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
        return redirect(url_for('main.update', username=user.username, anchor='budget'))
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
        return redirect(url_for('main.update', username=user.username, anchor='assets'))
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
        return redirect(url_for('main.update', username=user.username, anchor='liabilities'))
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
        return redirect(url_for('main.update', username=user.username, anchor='income-sources'))
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
        return redirect(url_for('main.update', username=user.username, anchor='expenses'))
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
            'main/update.html',
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


@bp.route('/<username>/delete/budget-item-<int:id>')
def budget_item_delete(username, id):
    user = User.query.filter_by(username=username).first_or_404()
    budget_item = BudgetItem.query.get_or_404(id)
    db.session.delete(budget_item)
    db.session.commit()
    flash(budget_item.name + ' has been deleted from budget items')
    return redirect(url_for('main.update', username=user.username, anchor='budget'))


@bp.route('/<username>/delete/expense-<int:id>')
def actual_expense_delete(username, id):
    user = User.query.filter_by(username=username).first_or_404()
    actual_expense = Expenses.query.get_or_404(id)
    db.session.delete(actual_expense)
    db.session.commit()
    flash(actual_expense.name + ' has been deleted from your expenses')
    return redirect(url_for('main.update', username=user.username, anchor='expenses'))


@bp.route('/<username>/delete/asset-<int:id>')
def asset_delete(username, id):
    user = User.query.filter_by(username=username).first_or_404()
    asset = Asset.query.get_or_404(id)
    db.session.delete(asset)
    db.session.commit()
    flash(asset.name + ' has been deleted from asset items')
    return redirect(url_for('main.update', username=user.username, anchor='assets'))


@bp.route('/<username>/delete/liability-<int:id>')
def liability_delete(username, id):
    user = User.query.filter_by(username=username).first_or_404()
    liability = Liability.query.get_or_404(id)
    db.session.delete(liability)
    db.session.commit()
    flash(liability.name + ' has been deleted from liability items')
    return redirect(url_for('main.update', username=user.username, anchor='liabilities'))


@bp.route('/<username>/delete/income-<int:id>')
def actual_income_delete(username, id):
    user = User.query.filter_by(username=username).first_or_404()
    actual_income = ActualIncome.query.get_or_404(id)
    db.session.delete(actual_income)
    db.session.commit()
    flash(str(actual_income.amount) + ' has been deleted from actual income')
    return redirect(url_for('main.update', username=user.username, anchor='income-sources'))

# ===============================================================
# End of Delete User data
# ===============================================================

# ===============================================================
# Download and Encrypt User data
# ===============================================================


@bp.route('/<username>/download-budget-data', methods=['GET', 'POST'])
@login_required
def download_budget_data(username):
    """Download budget data as pdf"""
    user = User.query.filter_by(username=username).first()
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
            input_pdf=current_app.config['PDF_FOLDER_PATH'] + 'budget_data' + \
                session['year'] + '.pdf', password=user.username)
        # Download file to local computer
        # File like objects are opend in binary mode
        buffer = BytesIO()
        buffer.write(open(current_app.config['PDF_FOLDER_PATH'] + 'budget_data' + \
            session['year'] + '.pdf', 'rb').read())
        # File pointer will be seeked to the start of the data
        buffer.seek(0)
        # Delete the downloaded pdf file from project folder (save space)
        os.remove(current_app.config['PDF_FOLDER_PATH'] + 'budget_data' + session['year'] + '.pdf')
        # Send the file to the browser as a pdf file
        return send_file(
            buffer,
            attachment_filename='budget_data' + session['year'] + '.pdf',
            as_attachment=True)
    return render_template(
        'main/download_data_form.html',
        title='Download Budget Data',
        download_data_form=download_data_form,
        user=user)


@bp.route('/<username>/download-asset-data', methods=['GET', 'POST'])
@login_required
def download_asset_data(username):
    """Download asset data as pdf"""
    user = User.query.filter_by(username=username).first()
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
            input_pdf=current_app.config['PDF_FOLDER_PATH'] + 'asset_data' + \
                session['year'] + '.pdf', password=user.username)
        buffer = BytesIO()
        buffer.write(open(
            current_app.config['PDF_FOLDER_PATH'] + 'asset_data' + \
                session['year'] + '.pdf', 'rb').read())
        buffer.seek(0)
        os.remove(current_app.config['PDF_FOLDER_PATH'] + 'asset_data' + session['year'] + '.pdf')
        return send_file(
            buffer,
            attachment_filename='asset_data' + session['year'] + '.pdf',
            as_attachment=True)
    return render_template(
        'main/download_data_form.html',
        title='Download Asset Data',
        download_data_form=download_data_form,
        user=user)


@bp.route('/<username>/download-liabilities-data', methods=['GET', 'POST'])
@login_required
def download_liabilities_data(username):
    """Download liabilities data as pdf"""
    user = User.query.filter_by(username=username).first()
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
            input_pdf=current_app.config['PDF_FOLDER_PATH'] + 'liabilities_data' + \
                session['year'] + '.pdf', password=user.username)
        buffer = BytesIO()
        buffer.write(open(
            current_app.config['PDF_FOLDER_PATH'] + 'liabilities_data' + \
                session['year'] + '.pdf', 'rb').read())
        buffer.seek(0)
        os.remove(current_app.config['PDF_FOLDER_PATH'] + 'liabilities_data' + \
            session['year'] + '.pdf')
        return send_file(
            buffer,
            attachment_filename='liabilities_data' + session['year'] + '.pdf',
            as_attachment=True)
    return render_template(
        'main/download_data_form.html',
        title='Download Liabilities Data',
        download_data_form=download_data_form,
        user=user)


@bp.route('/<username>/download-expenses-data', methods=['GET', 'POST'])
@login_required
def download_expenses_data(username):
    """Download expenses data as pdf"""
    user = User.query.filter_by(username=username).first()
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
            input_pdf=current_app.config['PDF_FOLDER_PATH'] + 'expenses_data' + \
                session['year'] + '.pdf', password=user.username)
        buffer = BytesIO()
        buffer.write(open(
            current_app.config['PDF_FOLDER_PATH'] + \
                'expenses_data' + session['year'] + '.pdf', 'rb').read())
        buffer.seek(0)
        os.remove(current_app.config['PDF_FOLDER_PATH'] + \
            'expenses_data' + session['year'] + '.pdf')
        return send_file(
            buffer,
            attachment_filename='expenses_data' + session['year'] + '.pdf',
            as_attachment=True)
    return render_template(
        'main/download_data_form.html',
        title='Download Expenses Data',
        download_data_form=download_data_form,
        user=user)


@bp.route('/<username>/download-income-data', methods=['GET', 'POST'])
@login_required
def download_income_data(username):
    """Download income data as pdf"""
    user = User.query.filter_by(username=username).first()
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
            input_pdf=current_app.config['PDF_FOLDER_PATH'] + 'income_data' + \
                session['year'] + '.pdf',password=user.username)
        buffer = BytesIO()
        buffer.write(open(current_app.config['PDF_FOLDER_PATH'] + \
            'income_data' + session['year'] + '.pdf', 'rb').read())
        buffer.seek(0)
        os.remove(current_app.config['PDF_FOLDER_PATH'] + 'income_data' + session['year'] + '.pdf')
        return send_file(
            buffer,
            attachment_filename='income_data' + session['year'] + '.pdf',
            as_attachment=True)
    return render_template(
        'main/download_data_form.html',
        title='Download Income Data',
        download_data_form=download_data_form,
        user=user)

# ===============================================================
# End of Download and Encrypt User data
# ===============================================================
