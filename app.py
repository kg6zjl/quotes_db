# -*- coding: utf-8 -*

import os
from flask import Flask, render_template, request, json, abort, make_response, jsonify
from werkzeug import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////quotes.db'
db = SQLAlchemy(app)

class Quote(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	quote = db.Column(db.String(255), unique=True)
	contributor = db.Column(db.String(120))
	private = db.Column(db.String(5))
	created_at = db.Column(db.String(120))
	updated_at = db.Column(db.String(120))

	def __init__(self, quote, contributor, private):
		self.quote = quote 
		self.contributor = contributor
		self.private = private

	def __repr__(self):
		return '<Quote %r>' % self.quote


@app.route("/")
def main():
	return render_template('index.html')

@app.route("/submit")
def submitRecipe():
	return render_template('add_quote.html')

@app.route("/thanks")
def thanks():
	return render_template('thanks.html')

@app.route("/recent")
def recentRecipes():
	conn = mysql.connect()
	cursor = conn.cursor()
	query = ("select * from ridiculous.quotes order by created_at DESC limit 10;")
	cursor.execute(query)
	data = cursor.fetchall()
	
	return render_template('recent.html',data=(data))

@app.route('/addQuote',methods=['POST','GET'])
def addRecipe(): # read the posted values from the UI
	_quote = request.form['quoteText']
	_description = request.form['quote']
	_contributor = request.form['recipeContributor']

	# validate the received values
	if _title and _description and _contributor:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('sp_createRecipe',(_title,_description,_contributor))
		data = cursor.fetchall()
		if len(data) is 0:
			conn.commit()
			#return json.dumps({'html':'<span>All fields good !!</span>'})
			main()
			return redirect(url_for('thanks'))
		else:
			return json.dumps({'error':str(data[0])})
	else:
		return json.dumps({'html':'<span>Enter the required fields</span>'})

@app.errorhandler(404)
def not_found(error):
	#to use, call: abort(404)
	return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "__main__":
	app.run(debug=True)
