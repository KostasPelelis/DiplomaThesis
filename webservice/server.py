from flask import Flask, render_template

app = Flask('netmode-backend', static_path='/static', static_folder='./webservice/frontend2/dist/')

@app.route('/')
def index():
	return render_template("static/index.html")
