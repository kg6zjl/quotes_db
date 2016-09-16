# -*- coding: utf-8 -*

import os
from flask import Flask, render_template, request, json, abort, make_response, jsonify
from werkzeug import generate_password_hash, check_password_hash
try:
	from flask.ext.mysql import MySQL
except:
	from flask_mysql import MySQL

app = Flask(__name__)
mysql = MySQL()

# MySQL configurations/ENV Vars
app.config['MYSQL_DATABASE_USER'] = os.environ['QUOTES_DB_USER']
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ['QUOTES_DB_PASS']
app.config['MYSQL_DATABASE_DB'] = os.environ['QUOTES_DB_NAME']
app.config['MYSQL_DATABASE_HOST'] = os.environ['QUOTES_DB_HOST']
mysql.init_app(app)



@app.route("/")
def main():
	return render_template('index.html')

@app.route("/submitQuote")
def submitRecipe():
	return render_template('add_quote.html')

@app.route("/thanks")
def thanks():
	return render_template('thanks.html')

@app.route("/recent")
def recent():
	conn = mysql.connect()
	cursor = conn.cursor()
	query = ("select * from quotes.quotes order by id DESC limit 10;")
	cursor.execute(query)
	data = cursor.fetchall()
	
	return render_template('recent.html',data=(data))

@app.route('/addQuote',methods=['POST','GET'])
def addRecipe(): # read the posted values from the UI
	_quote = request.form['quoteText']
	_author = request.form['quoteAuthor']

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
