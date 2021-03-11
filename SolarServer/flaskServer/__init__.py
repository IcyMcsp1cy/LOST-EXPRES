from flask import Flask
from .userClass import User
from .routes import init_views
from .dash import init_dash
from .extensions import mongo, mail

def create_app(config):
    app = Flask(__name__,
        static_folder="../static",
        template_folder="../templates"
        )
    app.config.from_pyfile(config)
    
    mongo.init_app(app)
    mail.init_app(app)
    init_views(app)
    init_dash(app)

    return app
