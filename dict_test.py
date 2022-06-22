date = [['2022', '05', '16'], ['2022', '06', '16'], ['2022', '06', '16'], ['2022', '07', '16'], ['2022', '07', '16'], ['2022', '08', '16']]
month = []
new_month = []
new_month_name = []
month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

items = ['rent', 'food', 'car', 'clothes', 'other']
amount = [230, 100, 200, 300, 400, 500]
budget_amount = []
skipped = []

for i in range(len(date)):
    month.append(int(date[i][1]))

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

    #     continue
    # else:
    #     new_month.append(month[i])
    #     new_month_name.append(month_names[month[i] - 1])
    #     # Add skipped amount to first item in list
    #     budget_amount.append(amount[i])
        
    # new_month.append(month_names[month[i] - 1])

print("All months: ", month)
print("Final months list: ", new_month_name)
print("Final amount list: ", budget_amount)
print("Budget Items: ", items)
