from app import db
from app.admin import bp
from app.models import Admin, Support
from flask import render_template, flash, redirect, url_for
from app.admin.forms import SupportRegistrationForm
from flask_login import current_user, login_required
from app.admin.email import send_registration_email, send_account_deletion_email


@bp.route('/dashboard/<username>', methods=['GET', 'POST'])
@login_required
def admin_dashboard(username):
    admin = Admin.query.filter_by(username=username).first_or_404()
    form = SupportRegistrationForm()
    if form.validate_on_submit():
        support = Support(username=form.username.data,email=form.email.data)
        support.set_password(form.password.data)
        db.session.add(support)
        db.session.commit()
        send_registration_email(support)
        flash(f'You have successfully registered {support.username} a support team member!')
        return redirect(url_for('admin.admin_dashboard', username=admin.username))
    support_team = Support.query.all()
    return render_template(
        'admin/admin_dashboard.html',
        title='Admin Dashboard',
        admin=admin,
        support_team=support_team,
        form=form)


@bp.route('/dashboard/<username>/support-member/delete-<int:id>', methods=['GET', 'POST'])
def admin_delete_support_member(username, id):
    admin = Admin.query.filter_by(username=username).first_or_404()
    support = Support.query.filter_by(id=id).first_or_404()
    send_account_deletion_email(support)
    answers = support.user_questions.all()
    for answer in answers:
        db.session.delete(answer)
    db.session.delete(support)
    db.session.commit()
    flash(f'You have successfully deleted {support.username} from the support team!')
    return redirect(url_for('admin.admin_dashboard', username=admin.username))


@bp.route('/dashboard/<username>/delete/account', methods=['GET', 'POST'])
def admin_delete_account(username):
    admin = Admin.query.filter_by(username=username).first_or_404()
    db.session.delete(admin)
    db.session.commit()
    flash(f'You have successfully deleted {admin.username} from the admin team!')
    return redirect(url_for('auth.login'))
