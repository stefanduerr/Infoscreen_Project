from datetime import datetime
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    sites = db.relationship('Site', backref='creator', lazy=True)


def __repr__(self):
    return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


def __repr__(self):
    return f"User('{self.username}', '{self.email}', '{self.image_file}')"