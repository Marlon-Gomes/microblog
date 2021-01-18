#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 17:00:50 2021

@author: mgomes
"""
# Imports from standard libraries
import os
import logging # Log errors
from logging.handlers import SMTPHandler, RotatingFileHandler
# Imports from downloaded libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
# Imports from local modules
from config import Config

# The line below creates an instance,'app', of class Flask, using the predefined
#__name__ variable, which refers to the name of the module in which it is used.

app = Flask(__name__)
app.config.from_object(Config)

# The lines below creates a database instance, 'db', and a database migration
# instance, 'migrate', and a login manager instance, 'login'
db = SQLAlchemy(app)
migrate = Migrate(app,db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

# Error logging
if not app.debug:
    # Log and mail errors immediately
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost = (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr = 'no-reply@' + app.config['MAIL_SERVER'],
            toaddrs = app.config['ADMINS'], subject = 'Microblog Failure',
            credentials = auth, secure = secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    #
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_hander = RotatingFileHandler(
        'logs/microblog.log',
        maxBytes = 10240,
        backupCount = 10)
    file_hander.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s \
            [in %(pathname)s: %(lineno)d]'))
    file_hander.setLevel(logging.INFO)

    app.logger.addHandler(file_hander)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

# We import 'routes', 'models', 'errors' at the end bottom to avoid circular
# import as they need to import 'app', 'db', 'login' defined on this script.
from app import routes, models, errors
