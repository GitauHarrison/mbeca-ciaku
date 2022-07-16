# Mbeca Ciaku

Mbeca (pronounced as 'besha') means "money" and Ciaku (pronounced as 'shiaku') means "mine" in Kikuyu, one of the venacular languages in Kenya. Put together, you get "My money". This project is aimed at helping a user to visualize his money.

![Project image here]()

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tools Used](#tools-used)
- [Deployed Application](#deployed-application)
- [Contributors](#contributors)
- [Testing The Application Locally](#testing-the-application-locally)

## Overview


For many years, I have always made use of Google Sheets to record how my money comes in and goes out. At the end of each day, preferably at night, I consistently update this sheet with the current state of my money.

![Excel Data](app/static/images/excel_data.png)

It works well, but it is quite cumbersome to use over a long period of time. For example, I have to manually create the table structures occassionally. I also have to manually add the formulas to generate a chart of my income and expenses. The data is good, but if you cannot visualize it, then it is hard to know what is going on.

### Sample expense data

![Visualize Expense Data](app/static/images/visualize_expense_data.png)

Besides detailed budget, income and expenses data, I wanted to have a summary of the health status of my money. I would compare my expenses to my budget and see if I was spending too much. Of course, expenses are made possible by my income. This cashflow is what can enable one to buy an asset and experience freedom or live a liability-filled life.

### Sample financial statement


![Visualize Financial Statement](app/static/images/visualize_financial_statement.png)

Mbeca Ciaku is an attempt to create an easier solution to this small problem. Besides simplicity, I wanted to make an application that would be usable by multiple other people. These users can download their data for offline analysis. The downloaded data would be organized and encrypted in a PDF file.

Inspired by [MPesa](https://en.wikipedia.org/wiki/M-Pesa), I found the encryption of personal data very interesting. If you are an active MPesa user, sometimes you would like to refer to your transactions to settle a dispute, confirm a payment, or to make a complaint. Whatever the case, [Safaricom](https://www.safaricom.co.ke/) allows you to easily request for a copy of your transaction data for free. The statement would be sent to you via email. This file is encrypted and can only be accessed by you. At the time of this writing, decrypting the file is dependant on the user providing their National ID number plus a one-time passcode sent to their phone. The decryption format is "ID-token". 

## Features

- [x] Password-based user authentication
- [ ] Two-factor authentication
- [ ] Email notification
- [x] Interactive tables with search, sort and pagination functionality
- [x] Download of user data as PDF file
- [x] Encryption of downloaded PDF file
- [ ] Tests
- [ ] Custom admin dashboard


## Tools Used

- [x] [Flask](https://flask.palletsprojects.com/en/2.1.x/) (Python framework)
- [x] [Flask Bootstrap](https://pythonhosted.org/Flask-Bootstrap/) for styling and cross-browser responsive design
- [x] [Flask-WTF](https://flask-wtf.readthedocs.io/en/latest/) for form validation
- [x] [Flask-Login](https://flask-login.readthedocs.io/en/latest/) for user authentication
- [ ] [Flask-Mail](https://pythonhosted.org/Flask-Mail/) for email notification
- [x] [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) for database management
- [x] [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) for database migrations
- [x] [PyFPDF](https://pyfpdf.readthedocs.io/en/latest/) for PDF generation
- [x] [PyPDF2](https://pypdf2.readthedocs.io/en/latest/) for PDF encryption
- [ ] [Unittest](https://docs.python.org/3/library/unittest.html) for unit testing

## Deployed Application

- [ ] [Mbeca Ciaku](https://mbecaciaku.herokuapp.com/) on Heroku

## Contributors

[![GitHub Contributors](https://img.shields.io/github/contributors/GitauHarrison/mbeca-ciaku)](https://github.com/GitauHarrison/mbeca-ciaku/graphs/contributors)


## Testing The Application Locally

1. Clone the repository

```python
$ git clone git@github.com:GitauHarrison/mbeca-ciaku.git
```

2. Change to the repository directory

```python
$ cd mbeca-ciaku
```

3. Create and activate a virtual environment

```python
$ virtualenv venv
$ source venv/bin/activate

# OR using virtualenvwrapper

$ mkvirtualenv mbeca-ciaku
```


4. Install dependencies

```python
(mbeca-ciaku)$ pip install -r requirements.txt
```


5. Create `.env` file to all needed environment variables


```python
(mbeca-ciaku)$ touch .env
```


6. Update `.env` file with the variables seen in `.env-template` file in the repository root directory



```python
# Example .env-template file

SECRET_KEY=
PDF_FOLDER=
QUESTIONS_PER_PAGE=
```

Note on how to generate a random string for the `SECRET_KEY` variable:

```python
# On terminal
$ python -c "import os; print(os.urandom(24))"

# Output: b'\xc5\xdd\xb3s\xab<\xcc;h$>\x83f>e$\x03\xb8\xc8\xd1\xce\tZ\xd1'

# Or

(mbeca-ciaku)$ python -c 'import secrets; print(secrets.token_hex(16))'

# Output:  ff4fcb6dc2243c5050677dca63c05112

# Or

# Get password from https://www.grc.com/passwords.htm

```


7. Run the application

```python
(mbeca-ciaku)$ flask run
```


8. Paste the localhost URL http://127.0.0.1:5000  into your browser. You should be able to see the application.


9. Run the tests

```python
(mbeca-ciaku)$ python3 -m tests.py
```

## Areas of Improvement

- [ ] User interface design
- [ ] Proper display of multiple graphs on specific charts (based on data years)
- [ ] Disabling of the _Edit_ link in the help page after a specified duration
- [ ] Automatic email notifications to remind users to update their data