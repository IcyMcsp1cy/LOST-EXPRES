from flask import render_template, abort, request, redirect, url_for, session
from functools import wraps
from flask_mail import Message
from .indexPlot import homepage_plot
from .extensions import mongo, mail
from .userClass import User
import pymongo
import datetime
from bson.objectid import ObjectId

def init_views( server ):

    #~ Error Handling
    @server.errorhandler(404)
    def not_found(e):
        return '<h1>404 not found</h1>', 404

    #Login required decorator
    def login_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                return redirect('/')

    #~ Server Routing
    @server.route('/')
    def index():
        graph = homepage_plot()
        return render_template('index.html', plot=graph)

    @server.route("/graphing/")
    def graphing():
        return "<a href='/'>home</a> <h1>Graphing Dashboard</h1>"

    @server.route("/search/")
    def search():
        return "<a href='/'>home</a> <h1>Search Page</h1> "

    @server.route("/adminAddNews/")
    def adminAddNews():
        return render_template('adminAddNews.html')

    @server.route("/adminFileManager/")
    def adminFileManager():
        RV = mongo.db.radialvelocity.find({}, {"_id": 0, "FILENAME": 1, "MJD": 1})
        return render_template('adminFileManager.html', RV=RV)

    @server.route("/adminAddToGlossary/")
    def adminAddToGlossary():
        return render_template('adminAddToGlossary.html')

    @server.route("/glossary/")
    def glossary():
        glos = mongo.db.glossary.find()
        return render_template('glossary.html', glos=glos)

    @server.route("/addTerm/", methods=['POST'])
    def addTerm():

        entry = request.form['term']
        definition = request.form['definition']

        mongo.db.glossary.insert_one({"entry":entry, "definition":definition})

        return redirect(url_for('admin'))

    @server.route("/admin/")
    def admin():
        RV = mongo.db.radialvelocity.find({"PUBLIC":"FALSE"}, {"_id": 0, "FILENAME": 1, "MJD": 1})
        return render_template('adminAddNews.html', RV=RV)

    @server.route("/news/")
    def news():
        posts = mongo.db.news.find().sort('_id', pymongo.DESCENDING)
        return render_template("news.html",posts=posts)


    @server.route('/addPost/', methods=['POST'])
    def addPost():
        title = request.form['title']
        subtitle = request.form['subtitle']
        author = request.form['author']
        content = request.form['content']
        date_posted = datetime.datetime.now()
        final_date = date_posted.strftime('%B %d, %Y')
        post = mongo.db.news.insert_one({"title":title,"subtitle":subtitle,"author":author,"content":content,"datetime":final_date})
        return redirect(url_for('admin'))

    @server.route("/deleteNews/")
    def deleteNews():
        selectedPosts = mongo.db.news.find().sort('_id', pymongo.DESCENDING)
        return render_template('deleteNews.html', selectedPosts=selectedPosts)

    @server.route('/deletePost/', methods=['POST'])
    def deletePost():
        deleted = (request.form['deleted'])
        print(deleted)
        mongo.db.news.delete_one(deleted)
        return redirect(url_for('admin'))


    @server.route('/post/<post_id>')
    def post(post_id):
        post = mongo.db.news.find_one({ "_id": ObjectId(post_id) })
        return render_template('post.html', post=post)


#        return '<h1>Title: {} Subtitle: {} Author: {} Content: {}</h1>'.format(title, subtitle, author, content)


    #Called from requestAccess.html when the form is submitted
    @server.route('/register', methods=['POST'])
    def register():
        #save the form inputs as variables
        try:
            firstName = request.form['fname']
            lastName = request.form['lname']
            fullName = firstName + " " + lastName
            email = request.form['email']
            institution = request.form['institution']
            msgHeader = "Request Access Submission from " + fullName
            #send an email using the input parameters in the header and message
            msg = Message(msgHeader, sender = 'LOSTEXPRES1@gmail.com', recipients = ['LOSTEXPRES2@gmail.com'])
            msg.body = "Hello, " + fullName + " has requested researcher access for the LOST telescope.\n" + "Email: " + email + "\nInstitution: " + institution
            mail.send(msg)
            return render_template('success.html')
        except:
            return render_template('success.html')

    @server.route('/forgotPasswordRequest', methods=['GET', 'POST'])
    def forgotPasswordRequest():
        #save the form input as a variable
        email = request.form['email']
        #send an email using the input parameters in the header and message
        msg = Message("Forgot Password Email", sender = 'LOSTEXPRES1@gmail.com', recipients = [email])
        msg.body = "Hello, follow this link to reset your password: WIP"
        mail.send(msg)
        return "Forgot password form has been sent."

    @server.route('/signup', methods=['GET', 'POST'])
    def signup():
        email = request.form['email']
        firstName = request.form['fname']
        lastName = request.form['lname']
        institution = request.form['institution']
        return User().signup(email, firstName, lastName, institution)

    @server.route('/loginAttempt', methods=['GET', 'POST'])
    def loginAttempt():
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({
            "email": request.form.get('email')
        })
        if mongo.db.user.find({"email":email, "password":password}).count() >= 1:
            User().start_session(user)
            return redirect('/')
        else:
            return "<h1>Login Failed.</h1> <a href='/login'>back</a>"

    @server.route('/logout', methods=['GET', 'POST'])
    def logout():
        return User().signout()

    @server.route('/changeEmail', methods=['POST'])
    def changeEmail():
        oemail = request.form['oemail']
        nemail = request.form['nemail']
        mongo.db.user.update_one({'email':oemail},{"$set":{'email':nemail}})
        return redirect('/account')

    @server.route('/changeInstitution', methods=['POST'])
    def changeInstitution():
        oinstitution = request.form['oinstitution']
        ninstitution = request.form['ninstitution']
        mongo.db.user.update_one({'institution':oinstitution},{"$set":{'institution':ninstitution}})
        return redirect('/account')

    #~ serve file named in extension
    @server.route('/<string:page_name>/')
    def render_static(page_name):
        try:
            page = render_template('%s.html' % page_name)
        except:
            abort(404, not_found)

        return page
