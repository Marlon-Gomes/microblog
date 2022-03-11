# Imports from standard libraries
from threading import Thread
# Imports from downloaded libraries
from flask import current_app
from flask_mail import Message
# Imports from local modules
from app import mail

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
    # A custom thread needs the application context.
    Thread(target = send_async_email,
           args = (current_app._get_current_object(), msg)).start()
