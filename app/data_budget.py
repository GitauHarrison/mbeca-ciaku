from app.models import User
from flask_login import current_user


def budget_data():
    """
    Retrieve current user's budget data from the database.
    """
    user = User.query.filter_by(username=current_user.username).first()
    budget = user.budget_items.all()

    # Get individual items from the budget
    budget_item = [item.name for item in budget]
    amount = [item.amount for item in budget]

    # Get months from the budget dates
    date = sorted([budget_date.date.split('-') for budget_date in budget])

    # Get month number from date
    month = sorted([int(date[i][1]) for i in range(len(date))])
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
    new_items = [] # list of budget items, not repeated

    # Get amount in each month
    for i in range(len(month)):
        if month[i] in new_month:
            index = new_month.index(month[i])
            budget_amount[index] += amount[i]
        else:
            new_month.append(month[i])
            budget_amount.append(amount[i])
            new_month_name.append(month_names_in_budget[i])
            new_items.append(budget_item[i])

    return new_month_name, budget_item, budget_amount, new_month
