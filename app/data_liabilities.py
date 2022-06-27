from app.models import User
from flask_login import current_user


def liabilities_data():
    """
    Retrieve current user's liabilities data from the database.
    """
    user = User.query.filter_by(username=current_user.username).first()
    liabilities = user.liabilities.all()

    # Get individual items from the liabilities
    liabilities_item = [item.name for item in liabilities]
    amount = [item.amount for item in liabilities]

    # Get months from the liabilities dates
    date = sorted([liabilities_date.date.split('-') for liabilities_date in liabilities])

    # Get month number from date
    month = sorted([int(date[i][1]) for i in range(len(date))])
    # Replace month numbers with names
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
    month_names_in_liabilities = [month_names[int(month[i]) - 1] for i in range(len(month))]

    # Create lists needed by ChartJS:
    # month_names: month in list should not be repeated
    # liabilities_item: list of liabilities items in database
    # liabilities_amount: list of amounts for each liabilities item

    new_month = [] # number of month in list, not repeated
    new_month_name = [] # month name in list, not repeated
    liabilities_amount = [] # amount of each liabilities item
    new_items = [] # list of liabilities items, not repeated

    # Get amount in each month
    for i in range(len(month)):
        if month[i] in new_month:
            index = new_month.index(month[i])
            liabilities_amount[index] += amount[i]
        else:
            new_month.append(month[i])
            liabilities_amount.append(amount[i])
            new_month_name.append(month_names_in_liabilities[i])
            new_items.append(liabilities_item[i])

    return new_month_name, liabilities_item, liabilities_amount, new_month
    