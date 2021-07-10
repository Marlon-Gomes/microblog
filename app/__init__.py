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
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
# Imports from local modules
from config import Config

# The line below creates an instance,'app', of class Flask, using the predefined
#__name__ variable, which refers to the name of the module in which it is used.

# The lines below creates a database instance, 'db', and a database migration
# instance, 'migrate', and a login manager instance, 'login'
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'login'
# Translate login to user's browser language
login.login_message = _l('Please login to view this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()

# Create the application factory
def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    # Initialize application
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)


    # Error logging
    if not app.debug and not app.testing:
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

    return app

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

# Import blueprints
from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix = '/auth')
from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

# We import 'routes', 'models' at the end bottom to avoid circular
# import as they need to import 'app', 'db', 'login' defined on this script.
from app import routes, models
