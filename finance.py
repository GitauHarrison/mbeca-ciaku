from app import app, db
from app.models import User, BudgetItem, Expenses, Asset, \
    Liability, ActualIncome, Help


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        BudgetItem=BudgetItem,
        Expenses=Expenses,
        Asset=Asset,
        Liability=Liability,
        ActualIncome=ActualIncome,
        Help=Help)
