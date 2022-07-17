from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from hashlib import md5
import bleach
from markdown import markdown
from time import time
import jwt


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@login.user_loader
def load_admin(id):
    return Admin.query.get(int(id))

@login.user_loader
def load_support(id):
    return Support.query.get(int(id))


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    verification_phone = db.Column(db.String(20))

    def __repr__(self):
        return f'Admin: {self.username}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return Admin.query.get(id)

    def two_factor_enabled(self):
        return self.verification_phone is not None

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


class Support(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    verification_phone = db.Column(db.String(20))
    user_questions = db.relationship('Help', backref='support', lazy='dynamic')

    def __repr__(self):
        return f'Support: {self.username}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return Admin.query.get(id)

    def two_factor_enabled(self):
        return self.verification_phone is not None


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    verification_phone = db.Column(db.String(20))

    budget_items = db.relationship(
        'BudgetItem', backref='user', lazy='dynamic')
    expenses = db.relationship(
        'Expenses', backref='user', lazy='dynamic')
    assets = db.relationship(
        'Asset', backref='user', lazy='dynamic')
    liabilities = db.relationship(
        'Liability', backref='user', lazy='dynamic')
    actual_incomes = db.relationship(
        'ActualIncome', backref='user', lazy='dynamic')
    questions = db.relationship(
        'Help', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'User: {self.username}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def two_factor_enabled(self):
        return self.verification_phone is not None

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class BudgetItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64), index=True)
    amount = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'BudgetItem: {self.name}, {self.amount}, {self.date}'


class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    date = db.Column(db.String(64), index=True)
    amount = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'ActualIncome: {self.name}: {self.amount}'


class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64), index=True)
    amount = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Asset: {self.name}'


class Liability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64), index=True)
    amount = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Liability: {self.name}'


class ActualIncome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    date = db.Column(db.String(64), index=True)
    amount = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'ActualIncome: {self.name}: {self.amount}'


class Help(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    body_html = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    suppport_id = db.Column(db.Integer, db.ForeignKey('support.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
        markdown(value, output_format='html'),
        tags=allowed_tags, strip=True))

    def __repr__(self):
        return f'Help: {self.body}'

db.event.listen(Help.body, 'set', Help.on_changed_body)
