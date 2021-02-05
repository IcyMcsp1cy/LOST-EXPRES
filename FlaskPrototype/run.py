from flask import Flask
from flaskServer.views import homepage_plot, init_views
from flaskServer.dashApp import init_dash

server = Flask(__name__, static_folder="./static")

init_views(server)

dash = init_dash( server )

if __name__ == '__main__':
    server.run(debug=True)
