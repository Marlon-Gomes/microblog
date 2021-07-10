#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 17:06:22 2021

@author: mgomes
"""
# Imports from standard libraries
from datetime import datetime
# Imports from downloaded libraries
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from werkzeug.urls import url_parse
from guess_language import guess_language
# Imports from local modules
from app import db
from app.main import bp
from app.main.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, \
    PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post
from app.translate import translate

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        # No db.session.add() necessary: when referencing current_user Flask-
        # login will invoke the user loader callback, which puts the user in
        # the database session.
        db.session.commit()
    g.locale = str(get_locale())

# The decorators '@app.route' associate the URLs '/' and '/index' to the
# function index. The decorator @login_required redirects users to the login
# page if they try to access a protected page.
@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()

    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body = form.post.data, author = current_user,
            language = language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        # We redirect the user to index to reset the last request. If this is
        # not done, the user will be prompted to confirm form resubmission by
        # the web browser upon hitting the refresh button.
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type = int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page = posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page = posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title = _('Home'), form = form,
        posts = posts.items, next_url = next_url, prev_url = prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username = username).first_or_404()
    page = request.args.get('page', 1, type = int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username = user.username, page = posts.next_num)\
        if posts.has_next else None
    prev_url = url_for('user', username = user.username, page = posts.prev_num)\
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user = user, posts = posts.items,
        next_url = next_url, prev_url = prev_url, form = form)

@bp.route('/edit_profile', methods=['GET','POST'])
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
    return render_template('edit_profile.html',
        title=_('Edit Profile'), form = form)

@bp.route('/follow/<username>', methods = ['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash(_('User %(username)s not found.', username = username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_("You cannot follow yourself!"))
            return redirect(url_for('user', username = username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s.', username = username))
        return redirect(url_for('user', username = username))
    else:
        return redirect(url_for('index'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash('User {} not found'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('user', username = username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are no longer following %(username)s',
            username = username))
        return redirect(url_for('user', username = username))
    else:
        return redirect(url_for('index'))

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type = int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page = posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page = posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title = _('Explore'),
        posts = posts.items, next_url = next_url, prev_url = prev_url)

@bp.route('/translate', methods = ['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(
        request.form['text'],
        request.form['source_language'],
        request.form['dest_language'])})
