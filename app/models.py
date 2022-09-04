from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)

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

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# class Word(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     word = db.Column(db.String(50), nullable=False)

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         db.session.add(self)
#         db.session.commit()
    


# class Answer(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     answer = db.Column(db.String(300), nullable=False)              # this will be the 
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         db.session.add(self)
#         db.session.commit()