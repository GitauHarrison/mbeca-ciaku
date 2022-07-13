def budget_data(user):
    """User budget data

    Find the budget data for the current user. This includes:
        - Years in budget
        - Months in budget
        - Sum of expenses in each month

    Returns:
        - Dictionary whose key is the year and values are the months and amounts

    ChartJS:
        - The X axis will be the months in an ascending order
        - The Y axis will be the sum of expenses in each month
        - The label will be the year of the budget
    """
    budget = user.budget_items.all()

    # Split dates into lists of year, month, day
    dates = [budget_date.date.split('-') for budget_date in budget]

    # Get a list of the amounts spent throughout the budget years
    amounts = [budget_date.amount for budget_date in budget]

    # Get a list of the budget items in the budget years
    items = [budget_date.name for budget_date in budget]

    # Month numbers will be replaced with month names
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December']

    # Get expenditure years
    expenditure_years = [date[0] for date in dates]
    non_repetitive_expenditure_years = []
    for i in range(len(expenditure_years)):
        if expenditure_years[i] not in non_repetitive_expenditure_years:
            non_repetitive_expenditure_years.append(expenditure_years[i])

    # Sorted expenditure years
    sorted_non_repetitive_expenditure_years = sorted(non_repetitive_expenditure_years)
    # Sum of amounts in each year
    expenditure_in_a_year = {}
    expenditure_amounts_in_each_year = []
    for year in sorted_non_repetitive_expenditure_years:
        # Pair the dates with the amount spent in that year
        # Find if the date years are already in the sorted list of years created earlier
        # If they are, add the amount to the amount spent in that year 
        # i.e (expenditure_amounts_in_each_year)
        # Add the amounts to get the total amount spent in that year
        expenditure_amounts_in_each_year.append(
            sum([amount for date, amount in zip(dates, amounts) if date[0] == year]))

        # Add the year and amount spent in that year to the dictionary
        expenditure_in_a_year[year] = expenditure_amounts_in_each_year[
            sorted_non_repetitive_expenditure_years.index(year)]

    # Get dictionary of the months and amounts in each year
    months_in_year = {}
    amounts_in_year = {}
    items_in_year = {}
    total_amount_spent_in_each_month = {}
    for year in sorted_non_repetitive_expenditure_years:
        months_in_year[year] = []
        amounts_in_year[year] = []
        items_in_year[year] = []
        for date, amount, item in zip(dates, amounts, items):
            if date[0] == year:
                # Get the expenditure in each month
                # The months are converted to month names
                months_in_year[year].append(month_names[int(date[1]) - 1])
                amounts_in_year[year].append(amount)
                items_in_year[year].append(item)
        # Total amount spent in each month in each year
        for month, amount in zip(months_in_year[year], amounts_in_year[year]):
            total_amount_spent_in_each_month[month] = \
                total_amount_spent_in_each_month.get(month, 0) + amount
        # Get total monthly expenditure in each year
        non_repetitive_months_in_year = {}
        for month in months_in_year[year]:
            if month not in non_repetitive_months_in_year:
                non_repetitive_months_in_year[month] = total_amount_spent_in_each_month[month]
        # Get the non-repetitive months in each year plus the total amount spent in each month
        months_in_year[year] = list(non_repetitive_months_in_year.keys())
        amounts_in_year[year] = list(non_repetitive_months_in_year.values())
        for i in range(len(sorted_non_repetitive_expenditure_years)):
            if sorted_non_repetitive_expenditure_years[i] == year:
                sorted_non_repetitive_expenditure_years[i] = non_repetitive_months_in_year.keys()
    return months_in_year, amounts_in_year, items_in_year, expenditure_in_a_year
