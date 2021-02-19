from flask import Flask
from .views import init_views
from .dashApp import init_dash
from .extensions import mongo

def create_app(config):
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    app.config.from_pyfile(config)

    mongo.init_app(app)
    init_views(app)
    init_dash(app)

    return app