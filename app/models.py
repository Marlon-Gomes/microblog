#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 20:23:15 2021

@author: mgomes
"""
from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer,
                   primary_key = True)
    username = db.Column(db.String(64),
                         index = True,
                         unique = True)
    email = db.Column(db.String(120),
                      index = True,
                      unique = True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post',
                            backref='author',
                            lazy='dynamic')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class Post(db.Model):
    id = db.Column(db.Integer,
                   primary_key= True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime,
                          index = True,
                          default = datetime.utcnow)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id'))
    
    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
    