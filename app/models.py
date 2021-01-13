#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 20:23:15 2021

@author: mgomes
"""
# Imports from standard libraries
from datetime import datetime
from time import time
from hashlib import md5
# Imports from downloaded libraries
import jwt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# Import from local modules
from app import app, db, login

# Create a followers association table. This is an auxilliary table,
# containing no data other than the foreign keys, and it does not need to
# have a model class.
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    # Relationship (and auxilliary) fields
    posts = db.relationship(
        'Post', # User-to-Post
        backref='author', # from Post's perspective, User is the author
        lazy='dynamic' # don't evaluate unless requested
        )
    # Declare the 'followed' relationship as part of the 'User' table.
    followed = db.relationship(
        'User', # User(follower)-to-User(followed)
        secondary = followers, # configures aux. association table
        # Links parent user if it belongs to child user's followers table.
        primaryjoin = (followers.c.follower_id == id),
        # Links parent user if it belongs to child user's followed table.
        secondaryjoin = (followers.c.followed_id == id),
        # defines how the relationship is viewed from the child node
        backref = db.backref(
            'followers',# Users to the left of the child node are its followers.
            lazy='dynamic'),
        lazy = 'dynamic'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        # for other options offered by Gravatar, check the documentation
        # https://gravatar.com/site/implement/images
        return 'https://www.gravatar.com/avatar/{}?id=identicon&s={}'.format(
            digest,size)

    # Password-related functions
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in = 600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try: # to decode
            id = jwt.decode(token, app.config['SECRET_KEY'],
                algorithms = ['HS256'])['reset_password']
        except: # if invalid or expired
            return
        return User.query.get(id)

    # User interactions
    def follow(self, user):
        if not self.is_following(user): # check for duplicates
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user): # check for duplicates
            self.followed.remove(user)

    def is_following(self, user):
        """Queries the 'followed' relationship to check if a link between two
        users already exists"""
        return self.followed.filter(followers.c.followed_id == user.id).all()

    def followed_posts(self):
        followed = Post.query.join(
            followers, # join Post to followers
            # if post's author is followed by someone
            (followers.c.followed_id == Post.user_id)
            ).filter(
                # filter join table by posts whose authors are followed by self
                followers.c.follower_id == self.id
            )
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

# User-level functions
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


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
