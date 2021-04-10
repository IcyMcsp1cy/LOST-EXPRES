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
import pymongo

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
        post = mongo.db.news.find_one({ 'locationtype': "homepage"})
        return render_template('index.html', plot=rv_plot.result, post = post)


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
            addUser = "http://127.0.0.1:5000/addUser/" + user.email
            messageBody = "Hello, " + fullname + " has requested researcher access for the LOST telescope.\n" + "Email: " + user.email + "\nInstitution: " + user.institution + "\nAdd user with this link: " + addUser

            sendMail(server.config['ADMIN_EMAIL'], "Request Access Submission from " + fullname,
                messageBody)

            sendMail(user.email, "Request Access Submission from " + fullname,
                messageBody)

            return render_template('successRegister.html')
        else:
            flash('Please choose a different email')
        return render_template('register.html', form=form)

    @server.route('/addUser/<email_id>', methods=['GET', 'POST'])
    def addUser(email_id):
        current_email = email_id
        current_user = User.get_user(current_email)
        mongo.db.user.update_one({'_id': ObjectId(current_user.get_id())}, {'$set': {'type': "researcher"}})
        return render_template('successAddUser.html')

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

    @server.route("/deleteNews/")
    def deleteNews():
            selectedPosts = mongo.db.news.find().sort('_id', pymongo.DESCENDING)
            return render_template('deleteNews.html', selectedPosts=selectedPosts)

    @server.route('/deletePost/', methods=['POST'])
    def deletePost():
        deleted = request.form.getlist('deleted')
        for x in deleted:
            print(x)
            mongo.db.news.delete_one({"title": x})
        return redirect(url_for('news'))

    @server.route("/setNewsHomePage/")
    def setNewsHomePage():
            selectedPosts = mongo.db.news.find().sort('_id', pymongo.DESCENDING)
            return render_template('setNewsHomePage.html', selectedPosts=selectedPosts)

    @server.route('/setNewsPost/', methods=['POST'])
    def setNewsPost():
        mongo.db.news.update_many(
            {},
            { '$set': { "locationtype": "default" } },
        )
        setNews = request.form.getlist('setNews')
        for x in setNews:
            print(x)
            mongo.db.news.update_one({'title': x}, {'$set': {'locationtype': "homepage"}})
        return redirect(url_for('index'))

    @server.route("/deleteGlossary/")
    def deleteGlossary():
        glossaryItems = mongo.db.glossary.find().sort('_id', pymongo.DESCENDING)
        return render_template('deleteGlossary.html', glossaryItems=glossaryItems)

    @server.route('/deleteItem/', methods=['POST'])
    def deleteItem():
        deleted = request.form.getlist('deleted')
        for x in deleted:
            print(x)
            mongo.db.glossary.delete_one({"entry": x})
        return redirect(url_for('glossary'))

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
