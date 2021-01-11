#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 18:53:34 2021

@author: mgomes
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username',
                            validators = [DataRequired()]
                            )
    password = PasswordField('Password',
                             validators = [DataRequired()]
                             )
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')
    