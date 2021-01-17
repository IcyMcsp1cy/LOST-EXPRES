 #* Run this app with `python server.py` and
 #* visit http://127.0.0.1:8050/ in your web browser



from flask import Flask

#~ Default Flask Server
#~=============================================================================
flask_app = Flask(__name__)
#~=============================================================================





from flask_sqlalchemy import SQLAlchemy

#* MySQL Database Connection
#*=============================================================================
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost:3306/users'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
flask_app.secret_key = 'secrets!'
db = SQLAlchemy(flask_app)
#*=============================================================================





from flask_login import (current_user, LoginManager,
                             login_user, logout_user,
                             login_required, UserMixin)

#! Login Authentication
#!=============================================================================
login_manager = LoginManager()
login_manager.init_app(flask_app)

class Userlist(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), unique=True, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Userlist.query.get(int(user_id))
#!=============================================================================





from flask import render_template

#~ Server Routing
#~=============================================================================
@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/login')
def login():
    user = Userlist.query.filter_by(name='admin').first()
    login_user(user)
    return "You're logged in"

@flask_app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'You are now logged out!'

@flask_app.route('/home')
@login_required
def home():
    return 'The current FLASK user is ' + current_user.name
#~=============================================================================





from dash import Dash
import dash_html_components as html

#? Set up Dash Application
#?=============================================================================
dash_app = Dash(__name__,
                server=flask_app,
                url_base_pathname='/dash/')

dash_app.layout = html.H1('MY DASH APP')

for view_func in flask_app.view_functions:            #? require dash app login
    if view_func.startswith('/dash/'):
        flask_app.view_functions[view_func] = login_required(flask_app.view_functions[view_func])
#?=============================================================================





#! Run Server
#!=============================================================================
if __name__ == '__main__':
    dash_app.run_server(debug=True)    #! Any Dash app can run the flask server
#!=============================================================================