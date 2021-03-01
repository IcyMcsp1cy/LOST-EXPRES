from flask_pymongo import PyMongo
from flask_mail import Mail
from flask import render_template, abort, request, Flask

mongo = PyMongo()
mail= Mail()