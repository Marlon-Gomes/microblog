#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 17:17:58 2021

@author: mgomes
"""
# Imports from local modules
from app import app, db, cli
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    context = {'db': db,
               'User': User,
               'Post': Post}
    return context
