from flask import render_template, abort, request, redirect, url_for
from flask_mail import Message
from .indexPlot import homepage_plot
from .extensions import mongo, mail
import datetime


def init_views( server ):

    #~ Error Handling
    @server.errorhandler(404)
    def not_found(e):
        return '<h1>404 not found</h1>', 404

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

    @server.route("/admin/")
    def admin():
        # RV = mongo.db.radialvelocity.find({}, {"_id": 0, "FILENAME": 1, "MJD": 1})
        # return render_template('admin.html', RV=RV)

        RV = mongo.db.radialvelocity.find({"PUBLIC":"FALSE"}, {"_id": 0, "FILENAME": 1, "MJD": 1})
        return render_template('admin.html', RV=RV)

    @server.route("/news/")
    def news():
        posts = mongo.db.news.find({})
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
        return redirect(url_for('admin.html'))

    @server.route('/post/<int:post_id>')
    def post(post_id):
        post = mongo.db.news.find_one()
        return render_template('post.html', post=post)


        return '<h1>Title: {} Subtitle: {} Author: {} Content: {}</h1>'.format(title, subtitle, author, content)



    #Called from requestAccess.html when the form is submitted
    @server.route('/requestEmail', methods=['POST'])
    def requestEmail():
        #save the form inputs as variables
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
        return "Request access form has been sent."

    @server.route('/forgotPasswordRequest', methods=['GET', 'POST'])
    def forgotPasswordRequest():
        #save the form input as a variable
        email = request.form['email']
        #send an email using the input parameters in the header and message
        msg = Message("Forgot Password Email", sender = 'LOSTEXPRES1@gmail.com', recipients = [email])
        msg.body = "Hello, follow this link to reset your password: WIP"
        mail.send(msg)
        return "Forgot password form has been sent."

    @server.route('/loginAttempt', methods=['GET', 'POST'])
    def loginAttempt():
        return "<h1>Login Successful.</h1> <a href='/'>home</a>"
        

    #~ serve file named in extension
    @server.route('/<string:page_name>/')
    def render_static(page_name):
        try:
            page = render_template('%s.html' % page_name)
        except:
            abort(404, not_found)

        return page
