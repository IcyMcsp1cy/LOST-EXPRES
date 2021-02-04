
from flask import render_template, abort
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

    #~ serve file named in extension
    @server.route('/<string:page_name>/')
    def render_static(page_name):
        try:
            page = render_template('%s.html' % page_name)
        except:
            abort(404, not_found)

        return page
