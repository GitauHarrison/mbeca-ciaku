from app import db
from app.support import bp
from flask import render_template, flash, redirect, url_for, request,\
    current_app
from app.support.forms import HelpForm
from app.models import User, Help, Support
from flask_login import login_required
from app.support.email import send_answer_email


@bp.route('/dashboard/<username>', methods=['GET', 'POST'])
@login_required
def support_dashboard(username):
    support = Support.query.filter_by(username=username).first_or_404()
    form = HelpForm()
    if form.validate_on_submit():
        answer = Help(body = form.body.data, support=support)
        db.session.add(answer)
        db.session.commit()
        flash('You have successfully answered a question!')
        return redirect(url_for('support.support_dashboard', username=support.username))
    users = User.query.all()
    # for user in users:
    #     question_author = user.author.username
    #     if question_author:
    #         send_answer_email(user)
    # flash('You have successfully answered a question! An email has been sent to the user.')
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
        form=form,
        all_questions=all_questions.items,
        next_url=next_url,
        prev_url=prev_url)
