from app.models import User
from flask_login import current_user


def expenses_data():
    """
    Retrieve current user's expense data from the database.
    """
    user = User.query.filter_by(username=current_user.username).first()
    expense = user.expenses.all()

    # Get individual items from the expense
    expense_item = [item.name for item in expense]
    amount = [item.amount for item in expense]

    # Get months from the expense dates
    date = sorted([expense_date.date.split('-') for expense_date in expense])

    # Get month number from date
    month = sorted([int(date[i][1]) for i in range(len(date))])
    # Replace month numbers with names
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
    month_names_in_expense = [month_names[int(month[i]) - 1] for i in range(len(month))]

    # Create lists needed by ChartJS:
    # month_names: month in list should not be repeated
    # expense_item: list of expense items in database
    # expense_amount: list of amounts for each expense item

    new_month = [] # number of month in list, not repeated
    new_month_name = [] # month name in list, not repeated
    expense_amount = [] # amount of each expense item
    new_items = [] # list of expense items, not repeated

    # Get amount in each month
    for i in range(len(month)):
        if month[i] in new_month:
            index = new_month.index(month[i])
            expense_amount[index] += amount[i]
        else:
            new_month.append(month[i])
            expense_amount.append(amount[i])
            new_month_name.append(month_names_in_expense[i])
            new_items.append(expense_item[i])

    return new_month_name, expense_item, expense_amount, new_month