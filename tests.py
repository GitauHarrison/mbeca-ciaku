import unittest
from app.models import User, Expenses, Asset, Liability, ActualIncome, \
    BudgetItem
from app import app, db


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_database_update(self):
        u = User(username='susan')
        expense = Expenses(user_id=u.id, amount=100)
        expense2 = Expenses(user_id=u.id, amount=200)
        asset = Asset(user_id=u.id, amount=100)
        liabilities = Liability(user_id=u.id)
        actual_income = ActualIncome(user_id=u.id, amount=100)
        budget = BudgetItem(user_id=u.id, amount=100)
        db.session.add(u)
        db.session.add(expense)
        db.session.add(expense2)
        db.session.add(asset)
        db.session.add(liabilities)
        db.session.add(actual_income)
        db.session.add(budget)
        db.session.commit()
        self.assertTrue(u.expenses, 300)
        self.assertFalse(u.expenses.count(), [])
        self.assertTrue(u.assets, 100)
        self.assertFalse(u.assets.count(), [])
        self.assertTrue(u.liabilities, None)
        self.assertFalse(u.liabilities.first(), None)
        self.assertTrue(u.actual_incomes, 100)
        self.assertFalse(u.actual_incomes.count(), [])
        self.assertTrue(u.budget_items, 100)
        self.assertFalse(u.budget_items.count(), [])





if __name__ == '__main__':
    unittest.main(verbosity=2)
