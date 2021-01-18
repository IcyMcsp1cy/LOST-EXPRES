 #* Run this app with `python app.py` and
 #* visit http://127.0.0.1:8050/ in your web browser



from flask import Flask, render_template, abort

#~ Flask Server Setup
#~=============================================================================
server = Flask(__name__)

#~ Error Handling
@server.errorhandler(404)
def not_found(e):
    return '<h1>404 not found</h1>', 404

#~ Server Routing
@server.route('/')
def index():
    return render_template('index.html')

#~ serve file named in extension
@server.route('/<string:page_name>/')
def render_static(page_name):
    try:
        page = render_template('%s.html' % page_name)
    except:
        abort(404, not_found)

    return page
#~=============================================================================

#! Run Server
#!=============================================================================
if __name__ == '__main__':
    server.run(debug=True)
#!=============================================================================