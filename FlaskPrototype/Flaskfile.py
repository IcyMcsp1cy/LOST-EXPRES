from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/graphing")
def graphing():
    return "<a href='/'>home</a> <h1>Graphing Dashboard</h1>"

@app.route("/news")
def news():
    return "<a href='/'>home</a> <h1>News</h1>"

@app.route("/login")
def login():
    return "<a href='/'>home</a> <h1>Login Page</h1>"

@app.route("/search")
def search():
    return "<a href='/'>home</a> <h1>Search Page</h1> "

@app.route("/account")
def accountpage():
    return "<a href='/'>home</a> <h1>Account Page</h1>"

@app.route("/admin")
def admin():
    return "<a href='/'>home</a> <h1>Admin Page</h1>"

@app.route("/appendix")
def appendix():
    return "<a href='/'>home</a> <h1>Appendix</h1>"

if __name__ == "__main__":
    app.run()