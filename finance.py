from app import app, db
from app.models import User, BudgetItem, IncomeSource, AssetItem, LiabilityItem


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        BudgetItem=BudgetItem,
        IncomeSource=IncomeSource,
        AssetItem=AssetItem,
        LiabilityItem=LiabilityItem)
