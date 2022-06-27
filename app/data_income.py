from app.models import User
from flask_login import current_user

def income_data():
    """
    Retrieve current user's income data from the database.
    """
    user = User.query.filter_by(username=current_user.username).first()
    income = user.actual_incomes.all()

    # Get individual items from a user's actual incomes
    income_item = [item.name for item in income]
    amount = [item.amount for item in income]

    # Get months from the actual incomes dates
    date = sorted([income_date.date.split('-') for income_date in income])

    # Get month number from date
    month = sorted([int(date[i][1]) for i in range(len(date))])
    # Replace month numbers with names
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
    month_names_in_income = [month_names[int(month[i]) - 1] for i in range(len(month))]

    # Create lists needed by ChartJS:
    # month_names: month in list should not be repeated
    # income_item: list of income items in database
    # income_amount: list of amounts for each income item

    new_month = [] # number of month in list, not repeated
    new_month_name = [] # month name in list, not repeated
    income_amount = [] # amount of each income item
    new_items = [] # list of income items, not repeated

    # Get amount in each month
    for i in range(len(month)):
        if month[i] in new_month:
            index = new_month.index(month[i])
            income_amount[index] += amount[i]
        else:
            new_month.append(month[i])
            income_amount.append(amount[i])
            new_month_name.append(month_names_in_income[i])
            new_items.append(income_item[i])

    return new_month_name, new_items, income_amount, new_month