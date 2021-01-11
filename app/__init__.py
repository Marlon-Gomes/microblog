#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 17:00:50 2021

@author: mgomes
"""
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# The line below creates an instance,'app', of class Flask, using the predefined
#__name__ variable, which refers to the name of the module in which it is used.

app = Flask(__name__)
app.config.from_object(Config)

# The lines below creates a database instance, 'db', and a database migration
# instance, 'migrate'.
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# We import routes at the end bottom to avoid circular import. It needs to import
# the app variable defined in this script.
from app import routes, models
