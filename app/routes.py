#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 17:06:22 2021

@author: mgomes
"""
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm
from app.models import User

# The decorators '@app.route' associate the URLs '/' and '/index' to the
# function index. The decorator @login_required redirects users to the login
# page if they try to access a protected page.
@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [{'author': {'username':'John'},
              'body': 'Beautiful day in Portland!'},
             {'author': {'username': 'Susan'},
              'body': 'The Avengers movie was so cool!'},
             {'author': {'username': 'Julia'},
              'body': 'I love the cat!'}]
    return render_template('index.html', title = 'Home', posts = posts)

@app.route('/login', methods=['GET','POST'])
def login():
    # Authentication
    # If user is already authenticated, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('index'))

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
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # If user is authenticated, log it in, and record user's option to be
        # remembered. If user was redirected from a protected page, keep track
        # of it.
        login_user(user,remember = form.remember_me.data)
        next_page = request.args.get('next')
        # If user came from a protected page, redirect post-authentication to
        # the home page. If next is an absolute path, redirect uset to index
        # (this can prevent attacks by malicious users).
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title = 'Sign in', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    # If user is authenticated, redirect to home.
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # Else, begin registration process.
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully!')
        next_page = url_for('login')
        return redirect(next_page)
    return render_template('register.html', title = 'Register', form = form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username = username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    form = EmptyForm()
    return render_template('user.html', user = user, posts = posts, form = form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        # No db.session.add() necessary: when referencing current_user Flask-
        # login will invoke the user loader callback, which puts the user in
        # the database session.
        db.session.commit()

@app.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit(): # write to database
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        # if initial request, populate fields with existing data
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    # else validation failed
    return render_template('edit_profile.html',title='Edit Profile',form = form)

@app.route('/follow/<username>', methods = ['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash('User {} not found'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash("You cannot follow yourself!")
            return redirect(url_for('user', username = username))
        current_user.follow(user)
        db.session.commit()
        flash("You are following {}".format(username))
        return redirect(url_for('user', username = username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash('User {} not found'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username = username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are no longer following {}'.format(username))
        return redirect(url_for('user', username = username))
    else:
        return redirect(url_for('index'))
