# Imports from standard libraries
from threading import Thread
# Imports from downloaded libraries
from flask import render_template
from flask_mail import Message
from flask_babel import _
# Imports from local modules
from app import app, mail

def send_async_email(app, msg):
    # mail.send() needs the configuration values for the email server, stored
    # in the application content.
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
  msg = Message(subject, sender = sender, recipients = recipients)
  msg.body = text_body
  msg.html = html_body
  # Flask uses contexts to avoid passing arguments across functions
  # A custmo thread needs the application context.
  Thread(target = send_async_email, args = (app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(_('[Microblog] Reset Your Password'),
        sender = app.config['ADMINS'][0], recipients = [user.email],
        text_body = render_template(
            'email/reset_password.txt',
            user = user,
            token = token),
        html_body = render_template(
            'email/reset_password.html',
            user = user,
            token = token))
