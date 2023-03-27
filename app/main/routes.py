from app import db
from app.main import bp
from flask import render_template, flash, redirect, url_for, session,\
    request, send_file, current_app, request
from flask_login import current_user
from app.models import User


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/home', methods=['GET', 'POST'])
def about():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    return render_template('main/about.html', title='Mbeca Ciaku')
