from flask import render_template, abort, request
from flask_mail import Mail, Message
from .indexPlot import homepage_plot

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
        return "<a href='/'>home</a> <h1>Admin Page</h1>"

    #email setup
    mail= Mail(server)
    server.config['MAIL_SERVER']='smtp.gmail.com'
    server.config['MAIL_PORT'] = 465
    server.config['MAIL_USERNAME'] = 'LOSTEXPRES1@gmail.com'
    server.config['MAIL_PASSWORD'] = 'Lost2021'
    server.config['MAIL_USE_TLS'] = False
    server.config['MAIL_USE_SSL'] = True
    mail = Mail(server)
    #Called from requestAccess.html when the form is submitted
    @server.route("/requestEmail", methods=['POST'])
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

    #~ serve file named in extension
    @server.route('/<string:page_name>/')
    def render_static(page_name):
        try:
            page = render_template('%s.html' % page_name)
        except:
            abort(404, not_found)

        return page
