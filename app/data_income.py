def income_data(user):
    """
    Retrieve current user's incomes data from the database.
    """
    incomes = user.actual_incomes.all()

    # Get individual items from the incomes
    incomes_item = [item.name for item in incomes]
    amount = [item.amount for item in incomes]

    # Split date into year, month, and day
    dates = [incomes_date.date.split('-') for incomes_date in incomes]


    # Months list will be replaced with month names
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
            sum([amount for date, amount in zip(dates, amount) if date[0] == year]))

        # Add the year and amount spent in that year to the dictionary
        expenditure_in_a_year[year] = expenditure_amounts_in_each_year[
            sorted_non_repetitive_expenditure_years.index(year)]

    # Get dictionary of the months and amounts in each year
    months_in_year = {}
    amounts_in_year = {}
    items_in_year = {}
    for year in sorted_non_repetitive_expenditure_years:
        months_in_year[year] = []
        amounts_in_year[year] = []
        items_in_year[year] = []
        for date, amount, item in zip(dates, amount, incomes_item):
            if date[0] == year:
                # Get the expenditure in each month
                # The months are converted to month names
                months_in_year[year].append(month_names[int(date[1]) - 1])
                amounts_in_year[year].append(amount)
                items_in_year[year].append(item)
    return months_in_year, amounts_in_year, items_in_year, expenditure_in_a_year, month_names
