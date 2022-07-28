from app import db
from app.support import bp
from flask import render_template, flash, redirect, url_for, request,\
    current_app
from app.support.forms import HelpForm
from app.models import User, Help, Support, Admin
from flask_login import login_required
from app.support.email import send_answer_email, send_delete_account_email


@bp.route('/dashboard/<username>', methods=['GET', 'POST'])
@login_required
def support_dashboard(username):
    support = Support.query.filter_by(username=username).first_or_404()
    users = User.query.all()
    page = request.args.get('page', 1, type=int)
    all_questions = Help.query.order_by(Help.timestamp.desc()).paginate(
        page, current_app.config['QUESTIONS_PER_PAGE'], False)
    next_url = url_for(
        'support.support_dashboard',
        username=support.username,
        page=all_questions.next_num) \
            if all_questions.has_next else None
    prev_url = url_for(
        'support.support_dashboard', 
        username=support.username, 
        page=all_questions.prev_num) \
            if all_questions.has_prev else None
    return render_template(
        'support/support_dashboard.html',
        title='Support Dashboard',
        support=support,
        all_questions=all_questions.items,
        next_url=next_url,
        prev_url=prev_url,
        users=users)


@bp.route('/<username>/answer/question-<int:id>', methods=['GET', 'POST'])
@login_required
def answer(username, id):
    support = Support.query.filter_by(username=username).first_or_404()
    question_id = Help.query.filter_by(id=id).first_or_404()
    user = User.query.filter_by(username=question_id.author.username).first_or_404()
    form = HelpForm()
    if form.validate_on_submit():
        question_answer = Help(body=form.body.data, support=support)
        question_answer.answered = True
        db.session.add(question_answer)
        db.session.commit()
        send_answer_email(user)
        flash('You have successfully answered a question!'
              'An email has been sent to the user.')
        return redirect(url_for('support.support_dashboard', username=support.username))
    return render_template(
        'support/answer.html',
        title='Answer',
        question_id=question_id,
        form=form,
        support=support)


@bp.route('/<username>/delete/account', methods=['GET', 'POST'])
@login_required
def support_delete_account(username):
    support = Support.query.filter_by(username=username).first_or_404()
    admins = Admin.query.all()
    for admin in admins:
        send_delete_account_email(admin, support)
    # Update delete_account_status column to True
    # Support will not be able to request account deletion a second time
    support.delete_account_status = True
    db.session.commit()
    flash('Your request to delete your account has been sent to the admins. '
          'You will be notified when your account is deleted.')
    return redirect(url_for('support.support_dashboard', username=support.username))
