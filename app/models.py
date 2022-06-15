from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime


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
    expenses = db.relationship(
        'Expenses', backref='user', lazy='dynamic')
    assets = db.relationship(
        'Asset', backref='user', lazy='dynamic')
    liabilities = db.relationship(
        'Liability', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'User: {self.username}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class BudgetItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64), index=True, unique=True)
    amount = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'BudgetItem: {self.name}'


class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    date = db.Column(db.String(64), index=True)
    amount = db.Column(db.Integer, index=True)
    description = db.Column(db.String(64), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'ActualIncome: {self.name}: {self.amount}'


class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64), index=True, unique=True)
    amount = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Asset: {self.name}'


class Liability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64), index=True, unique=True)
    amount = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Liability: {self.name}'


class ActualIncome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    date = db.Column(db.String(64), index=True)
    amount = db.Column(db.Integer, index=True)
    description = db.Column(db.String(64), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'ActualIncome: {self.name}: {self.amount}'
