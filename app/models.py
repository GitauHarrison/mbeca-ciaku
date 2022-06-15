from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    budget_items = db.relationship(
        'BudgetItem', backref='user', lazy='dynamic')
    income_sources = db.relationship(
        'IncomeSource', backref='user', lazy='dynamic')
    asset_items = db.relationship(
        'AssetItem', backref='user', lazy='dynamic')
    liability_item = db.relationship(
        'LiabilityItem', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'User: {self.username}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class BudgetItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'BudgetItem: {self.name}'


class IncomeSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'IncomeSource: {self.name}'


class AssetItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'AssetItem: {self.name}'


class LiabilityItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'LiabilityItem: {self.name}'
