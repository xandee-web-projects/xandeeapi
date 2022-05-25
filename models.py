from enum import unique
from . import db

from flask_login import UserMixin

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    file_data = db.Column(db.String(64))
    api_id = db.Column(db.String(128), unique=True)
    is_json = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    salt = db.Column(db.String(128))
    member = db.Column(db.Boolean)
    username = db.Column(db.String(128), unique=True)
    email_confirmation_sent_on = db.Column(db.Integer)
    email_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    otp = db.Column(db.String(6))
    time_created = db.Column(db.Integer)
    calls = db.Column(db.Integer, default=100)
    files = db.relationship("File")

