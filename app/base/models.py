# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String, Boolean

from app import db, login_manager

from app.base.util import hash_pass
import jwt
import datetime
import os

class User(db.Model, UserMixin):

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Binary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass( value ) # we need bytes here (not plain str)
                
            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None

class Response(db.Model):
    
    __tablename__ = 'Response'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    age = Column(Integer)
    gender = Column(String)
    grade = Column(Integer)
    race = Column(String)
    isHispanic = Column(Boolean)
    is4HMember = Column(Boolean)
    question_1 = Column(String)
    question_2 = Column(String)
    answer_1 = Column(String)
    answer_2 = Column(String)
    country = Column(String)
    programType = Column(String)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            setattr(self, property, value)

    def __repr__(self):
        dic = vars(self)
        EXCLUDED = ["id", "_sa_instance_state"]
        for key in EXCLUDED:
            dic.pop(key, None)
        return dic

    def __str__(self):
        dic = vars(self)
        EXCLUDED = ["id", "_sa_instance_state"]
        separator = "|"
        return separator.join([str(dic[key]) for key in dic.keys() if key not in EXCLUDED])

    def getHeaders(self):
        keys = vars(self).keys()
        EXCLUDED = ["id", "_sa_instance_state"]
        separator = "|"
        return separator.join([key for key in keys if key not in EXCLUDED])

class MobileUser(db.Model):

    __tablename__ = 'MobileUser'
    id = Column(Integer, primary_key=True)
    sent = Column(Integer)
    isBanned = Column(Boolean)

    def __init__(self):
        sent = 0
        isBanned = False
    
    def encode_auth_token(self):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
                'iat': datetime.datetime.utcnow(),
                'sub': self.id
            }
            return str(jwt.encode(
                payload,
                os.environ.get('PRIVATE_KEY'),
                algorithm='HS256'
            ).decode('UTF-8'))
        except Exception as e:
            return str(e)

    @staticmethod
    def decode_auth_token(auth_token):
        print(auth_token)
        try:
            payload = jwt.decode(auth_token,  os.environ.get('PRIVATE_KEY'))
            print(payload)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return -1
        except jwt.InvalidTokenError:
            return -2
        except:
            return -3