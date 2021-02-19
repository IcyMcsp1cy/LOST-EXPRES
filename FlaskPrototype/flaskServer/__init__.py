from flask import Flask

from .extensions import mongo

def create_app(config_objects='flaskServer.settings'):
    app = Flask(__name__)

    app.config.from_object(config_object)

    mongo.init_app(app, MONGO_URI = "mongodb+srv://TestUser:Password123@cluster0.kjbxb.mongodb.net")

    return app