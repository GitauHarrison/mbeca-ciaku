from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm
from app.models import User


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Index')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!'
              'Login to continue')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
