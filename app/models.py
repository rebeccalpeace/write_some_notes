import base64
import os
from datetime import datetime, timedelta
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    answers = db.relationship('Answer', backref='player', lazy='dynamic')
    token = db.Column(db.String(32), index=True, unique=True)      # index allows for a constant time look up, similar to a set
    token_expiration = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password(kwargs['password'])
        db.session.add(self)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "answers": [a.to_dict() for a in self.answers.all()]
        }

    def get_token(self, expires_in=18000):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.commit()
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        db.session.commit()
        

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), nullable=False)
    word_length = db.Column(db.Integer, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "word": self.word,
            "word_length": self.word_length
        }


class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.String(200), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "prompt": self.prompt
        }
    

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(300))                         # this will be the url for an image
    line1 = db.Column(db.String(200))                            # these 6 are for each line of player's response, saved as a string of words
    line2 = db.Column(db.String(200))
    line3 = db.Column(db.String(200))
    line4 = db.Column(db.String(200))
    line5 = db.Column(db.String(200))
    line6 = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "line1": self.line1,
            "line2": self.line2,
            "line3": self.line3,
            "line4": self.line4,
            "line5": self.line5,
            "line6": self.line6,
            "user_id": self.user_id,
            "prompt_id": self.prompt_id
        }