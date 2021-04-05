from flask_pymongo import PyMongo
from flask_mail import Mail
from flask_login import LoginManager
from bson.objectid import ObjectId
import json
from datetime import datetime

mongo = PyMongo()


mail= Mail()
login=LoginManager()
login.login_view = 'login'



class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,ObjectId) or isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self,o)