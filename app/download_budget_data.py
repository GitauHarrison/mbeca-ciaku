from fpdf import FPDF
from app.data_budget import budget_data
from app.models import User
from flask import session
from app import app


def download_budget_pdf(user):
    # PDF()
    budget = user.budget_items.all()

    # Split dates into lists of year, month, day
    dates = [budget_date.date.split('-') for budget_date in budget]
    pdf_date = [budget_date.date for budget_date in budget]

    # Get a list of the amounts spent throughout the budget years
    amounts = [budget_date.amount for budget_date in budget]
    pdf_amount = [budget_date.amount for budget_date in budget]

    # Get a list of the budget items in the budget years
    items = [budget_date.name for budget_date in budget]

    # Month numbers will be replaced with month names
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
        ]

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

    print("Months in year:",months_in_year)
    print("Amounts in year:",amounts_in_year)
    # for amount in amounts_in_year['2020']:
    #     print(amount)
    print("Items in year:",items_in_year)
    print("Total:", expenditure_in_a_year['2020'])

    # Create a PDF
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # --- table showing budget items and amounts spent in each year ---

    # Colors, line width and bold font
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(25, 255, 155)
    # self.set_draw_color(255, 255, 255)
    # self.set_line_width(1)
    # Header
    pdf.cell(50, 10, 'Item', 1, 0, 'C')
    pdf.cell(50, 10, 'Date', 1, 0, 'C')
    pdf.cell(50, 10, 'Amount', 1, 1, 'C')
        # Table body
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    # Table data
    for year in months_in_year.keys():
        if session['year'] == year:
            # check if item is in items list
            for item in items_in_year[year]:
                print("Items in year:", items_in_year[year])
                if item in items:
                    print("Item index:",items.index(item))
                    pdf.cell(50, 10, item, 1, 0, 'C')
                    pdf.cell(50, 10, pdf_date[items.index(item)], 1, 1, 'C')
                    #pdf.cell(50, 10, amounts_in_year[year][items_in_year[year].index(item)], 1, 1, 'C')
    #                 #pdf.cell(50, 10, months_in_year[year][items_in_year[year].index(item)], 1, 0, 'C')
    #                 #pdf.cell(50, 10, amounts_in_year[year][items_in_year[year].index(item)], 1, 1, 'C')
    #             else:
    #                 pdf.cell(50, 10, '', 1, 0, 'C')
    #                 pdf.cell(50, 10, months_in_year[year][items_in_year[year].index(item)], 1, 0, 'C')
    #                 pdf.cell(50, 10, '', 1, 1, 'C')
    #         # for item in items_in_year[year]:
    #         #     pdf.cell(50, 10, item, 1, 0, 'C')
    #         # for month in months_in_year[year]:
    #         #     pdf.cell(50, 10, month, 1, 0, 'C')
    #         # for amount in amounts_in_year[year]:
    #         #     pdf.cell(50, 10, amount, 1, 1, 'C')
    # Total
    pdf.set_font('Times', 'B', 16)
    pdf.cell(100, 10, 'Total', 1, 0, 'C')
    if session['year'] in months_in_year.keys():
        pdf.cell(50, 10, str(expenditure_in_a_year[session['year']]), 1, 1, 'C')
        pdf.output(
            app.config['PDF_FOLDER'] + 'budget_data' + session["year"] + '.pdf', 'F')



class PDF(FPDF):
    def header(self):
        # Logo
        self.image('app/static/images/dreadlocks.jpg', 10, 8, 10, link='http://www.fpdf.org')
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(50, 10, 'Mbeca Ciaku'.upper(), 1, 0, 'C')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    # def table(self):
    #     # Colors, line width and bold font
    #     self.set_font('Arial', 'B', 16)
    #     self.set_text_color(25, 255, 155)
    #     # self.set_draw_color(255, 255, 255)
    #     # self.set_line_width(1)
    #     # Header
    #     self.cell(50, 10, 'Item', 0, 1, 'C')
    #     self.cell(50, 10, 'Date', 0, 1, 'C')
    #     self.cell(50, 10, 'Amount', 1, 1, 'C')
    #     # Table body
    #     self.set_font('Arial', '', 12)
    #     self.set_text_color(0, 0, 0)
    #     # Table data
    #     for year in months_in_year.keys():
    #         if session['year'] == year:
    #             for item in items_in_year[year].keys():
    #                 self.cell(50, 10, item, 0, 1, 'C')
    #             for date in amounts_in_year[year].keys():
    #                 self.cell(50, 10, date, 0, 1, 'C')
    #             for amount in amounts_in_year[year].values():
    #                 self.cell(50, 10, amount, 1, 1, 'C')
    #     # Total
    #     self.set_font('Times', 'B', 16)
    #     self.cell(50, 10, 'Total', 0, 1, 'C')
    #     for year in months_in_year.keys():
    #         if session['year'] == year:
    #             self.cell(50, 10, expenditure_in_a_year[year], 0, 1, 'C')

    #     def __init__(self):
    #         super().__init__()
    #         self.add_page()
    #         self.set_font('Arial', 'B', 16)
    #         self.cell(50, 10, 'Budget for ' + session['year'], 0, 1, 'C')
    #         self.table()
    #         if session['year'] in months_in_year.keys():
    #             self.output(
    #                 'app/static/files/budget_data'
    #                 '{{ user_budget_data[3][session\'year\'] }}.pdf', 'F')
