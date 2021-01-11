#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 17:06:22 2021

@author: mgomes
"""
from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

# The decorators '@app.route' associate the URLs '/' and '/index' to the function
# index
@app.route('/')
@app.route('/index')
def index():
    user = {'username':'Marlon Gomes'}
    posts = [
                {'author': {'username':'John'},
                 'body': 'Beautiful day in Portland!'
                 },
                {'author': {'username': 'Susan'},
                 'body': 'The Avengers movie was so cool!'},
                {'author': {'username': 'Julia'},
                 'body': 'I love the cat!'}
            ]
    return render_template('index.html', 
                           title = 'Home',
                           user = user,
                           posts = posts
                           )

@app.route('/login', 
           methods=['GET','POST']
           )
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me = {}'.format(form.username.data,
                                                                     form.remember_me.data
                                                                     )
              )
        return redirect(url_for('index'))
    return render_template('login.html',
                           title = 'Sign in',
                           form = form
                           )

