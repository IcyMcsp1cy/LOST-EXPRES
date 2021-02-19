from flask import Flask







def create_app():
    server = Flask(__name__, static_folder="./static")