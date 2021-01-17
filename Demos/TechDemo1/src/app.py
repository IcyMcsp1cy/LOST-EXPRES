from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/button-link/')
def button_link():
    print ('Button has been clicked!')
	
    return 'Button has been clicked.'

if __name__ == "__main__":
    app.run(debug=True,host='127.0.0.1')