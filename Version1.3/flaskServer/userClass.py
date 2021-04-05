from flask import session
from flask_login import UserMixin
from werkzeug.security import (
    generate_password_hash, 
    check_password_hash)
from uuid import uuid4
from bson.objectid import ObjectId
import json
import random

from .extensions import mongo, mail, login, JSONEncoder


class User(UserMixin):
    def __init__(self, 
    firstName, 
    lastName, 
    email, 
    institution,
    password,
    accountType,
    _id=None):
        self._id = uuid4().hex if _id is None else _id
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.institution = institution
        self.accountType = accountType
        self.password = password


    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self._id

    def check_password(self, password_hash): #, password):\
        return password_hash == self.password
        # return check_password_hash(password_hash, password)


    def to_json(self):
        return {
            "_id": str(self._id),
            "email": self.email,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "institution": self.institution,
            "type": self.accountType
        }

    @staticmethod
    def get_user(email):
        u = json.loads(JSONEncoder().encode(mongo.db.user.find_one({"email": email})))
        print(u)
        if not u:
            return None
        return User(
            u['firstName'],
            u['lastName'],
            u['email'],
            u['institution'],
            u['password'],
            u['type'],
            u['_id'])

    @staticmethod
    def new_user(firstName, lastName, email, institution):

        password = "xxxxxxxxxxxx"

        for char in range(12):
            password[char] = chr(random.randrange(65, 123, 1)) # 12 alphabetic and cased characters

        return User(
            firstName,
            lastName,
            email,
            institution,
            password,
            "registeree",)




    @login.user_loader
    def load_user(id):
        u = json.loads(JSONEncoder().encode(mongo.db.user.find_one({"_id": ObjectId(id)})))
        if not u:
            return None
        return User(
            u['firstName'],
            u['lastName'],
            u['email'],
            u['institution'],
            u['password'],
            u['type'],
            u['_id'])

