from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email

@bp.route('/login', methods=['GET','POST'])
def login():
    # Authentication
    # If user is already authenticated, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Else, begin authentication process
    form = LoginForm()
    if form.validate_on_submit():
        # Once form is submitted, attempt to match it to a user in the
        # database. Filter the db by username (from form), and pass first(),
        # which returns the user object if it exists, and None otherwise.
        user = User.query.filter_by(username = form.username.data).first()
        # Report authentication failure if user does not exist or password is
        # incorrect
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        # If user is authenticated, log it in, and record user's option to be
        # remembered. If user was redirected from a protected page, keep track
        # of it.
        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get('next')
        # If user came from a protected page, redirect post-authentication to
        # the home page. If next is an absolute path, redirect uset to index
        # (this can prevent attacks by malicious users).
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title = _('Sign in'), form = form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods = ['GET', 'POST'])
def register():
    # If user is authenticated, redirect to home.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    # Else, begin registration process.
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Registered successfully!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title = _('Register'),
        form = form)

@bp.route('/reset_password_request', methods = ['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for instructions to reset your password.'))
        return (redirect(url_for('auth.login')))
    return render_template('auth/reset_password_request.html',
        title = _('Reset Password'), form = form)

@bp.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return(redirect(url_for('main.index')))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form = form)
