from app import db
from app.user import bp
from flask import render_template, flash, redirect, url_for, request,\
    current_app
from app.user.forms import HelpForm
from app.models import User
from flask_login import login_required
from app.user.email import send_answer_email, send_delete_account_email


@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():   
    return render_template(
        'user/dashboard.html',
        title='Dashboard')
