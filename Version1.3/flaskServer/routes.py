from flask import (
    render_template, abort,
    request, redirect, g,
    url_for, session, flash)
from flask_login import (current_user,
    login_user, logout_user)
from .extensions import mongo, sendMail
from .userClass import User
from .forms import *
from .dash.graphing import rv_plot
from pymongo import DESCENDING
from bson.objectid import ObjectId

def init_views( server ):

    #! Get current user
    @server.before_request
    def getUser():
        if current_user.is_authenticated:
            g.user = {
                'fname': current_user.firstName,
                'lname': current_user.lastName,
                'atype': current_user.accountType
            }
            if current_user.accountType == 'researcher':
                g.nav = [
                    ['/', 'Home'],
                    ['/data/', 'Data'],
                    ['/news', 'News'],
                    ['/glossary', 'Glossary'],
                ]
                g.drop = [
                    ['/account', 'Account Settings'],
                ]
                g.color = 'primary'
            elif current_user.accountType == 'admin':
                g.nav = [
                    ['/', 'Home'],
                    ['/data/', 'Data'],
                    ['/news', 'News'],
                    ['/glossary', 'Glossary'],
                ]
                g.drop = [
                    ['/account', 'Account Settings'],
                    ['/admin', 'Web Management'],
                ]
                g.color = 'danger'
            else:
                g.nav = [
                    ['/', 'Home'],
                    ['/news', 'News'],
                    ['/data/', 'Data'],
                    ['/glossary', 'Glossary'],
                ]
                g.drop = None
                g.color = 'warning'

        else:
            g.user = {
                'fname': 'Guest',
                'lname': '',
                'atype': 'guest'
            }
            g.nav = [
                ['/', 'Home'],
                ['/news', 'News'],
                ['/data/', 'Data'],
                ['/glossary', 'Glossary'],
                ['/login', 'Sign In'],
            ]
            g.drop = None
            g.color = 'secondary'



    #! Error Handlers
    @server.errorhandler(404)
    def not_found(e):
        return render_template('error.html'), 404

    @server.errorhandler(403)
    def forbidden(e):
        return render_template(
            'error.html',
            code=403,
            message='Access Forbidden'), 403

    @server.errorhandler(500)
    def internal_error(e):
        return render_template(
            'error.html',
            code=500,
            message='Internal Server Error'), 500


    #! Page rendering
    @server.route('/')
    @server.route('/index')
    def index():
        return render_template('index.html', plot=rv_plot.result)


    #! User Management
    @server.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect('/')
        form = LoginForm()
        if form.validate_on_submit():
            user = User.get_user(form.email.data)
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user)

            return redirect(url_for('index'))
        return render_template('login.html', title='Sign In', form=form)


    @server.route('/logout')
    def logout():
        if current_user.is_authenticated:
            logout_user()
        return redirect('/')


    @server.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect('/')
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User.new_user (
                form.firstName.data,
                form.lastName.data,
                form.email.data,
                form.institution.data)
            mongo.db.user.insert_one(user.to_json())

            login_user(user)

            fullname = user.firstName + ' ' + user.lastName

            sendMail(server.config['ADMIN_EMAIL'], "Request Access Submission from " + fullname, 
                "Hello, " + fullname + " has requested researcher access for the LOST telescope.\n" + "Email: " + 
                user.email + "\nInstitution: " + user.institution)

            sendMail(user.email, "Request Access Submission from " + fullname, 
                "Hello, " + fullname + " has requested researcher access for the LOST telescope.\n" + "Email: " + 
                user.email + "\nInstitution: " + user.institution)

            return redirect(url_for('index'))
        else:
            flash('Please choose a different email')
        return render_template('register.html', form=form)


    @server.route("/account", methods=['GET', 'POST'])
    def account():
        if not current_user.is_authenticated:
            abort(403, forbidden)
        form1 = ChangeEmailForm()
        form2 = ChangeInstitutionForm()
        if form1.validate_on_submit():
            mongo.db.user.update_one({'email': form1.old.data}, {'$set': {'email': form1.new.data}})
        elif form2.validate_on_submit():
            mongo.db.user.update_one({'_id': ObjectId(current_user.get_id())}, {'$set': {'institution': form1.new.data}})
        return render_template('account.html', form1=form1, form2=form2)


    @server.route("/forgot", methods=['GET', 'POST'])
    def forgot():
        if current_user.is_authenticated:
            return redirect('/')

        form = ForgotForm()
        if form.validate_on_submit():
            user = User.get_user(form.email.data)
            if user is None:
                flash("This email is not registered, please try registering")
                return redirect("/register")

            sendMail(user.email, "Forgot Password - Lowell Observatory",
                "Hello, you have requested your password.\n Your password is: " + user.password
            )

            return redirect(url_for('login'))

        return render_template('forgot.html', form=form)


    # @server.route('/forgotPasswordRequest', methods=['GET', 'POST'])
    # def forgotPasswordRequest():
    #     #save the form input as a variable
    #     #send an email using the input parameters in the header and message
    #     msg = Message("Forgot Password Email", sender = 'LOSTEXPRES1@gmail.com', recipients = [email])
    #     msg.body = "Hello, follow this link to reset your password: WIP"
    #     mail.send(msg)
    #     return "Forgot password form has been sent."   #! Hi Brooke!




    @server.route("/news/")
    def news():
        posts = mongo.db.news.find().sort('_id', DESCENDING)
        return render_template("news.html",posts=posts)

    @server.route('/post/<post_id>')
    def post(post_id):
        post = mongo.db.news.find_one({ "_id": ObjectId(post_id) })
        return render_template('post.html', post=post)


    @server.route("/glossary")
    def glossary():
        glos = mongo.db.glossary.find()
        return render_template('glossary.html', glos=glos)
