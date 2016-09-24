from flask import Flask, jsonify
from flask import Flask, render_template, request, json, abort, make_response, jsonify, Blueprint, redirect, url_for, session
import mysql.connector, os
try:
	from flask.ext.mysql import MySQL
except:
	from flask_mysql import MySQL

app = Flask(__name__)
application = app

#mysql = MySQL()
#sess = Session()

# sql envs
app.config['MYSQL_DATABASE_USER'] = os.environ['QUOTES_DB_USER']
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ['QUOTES_DB_PASS']
app.config['MYSQL_DATABASE_DB'] = os.environ['QUOTES_DB_NAME']
app.config['MYSQL_DATABASE_HOST'] = os.environ['QUOTES_DB_HOST']

sqlUser = os.environ['QUOTES_DB_USER']
sqlPass = os.environ['QUOTES_DB_PASS']
sqlDb = os.environ['QUOTES_DB_NAME']
sqlHost = os.environ['QUOTES_DB_HOST']


@app.route('/api/v1.0/quotes', methods=['GET'])
@app.route('/api/v1.0/quote/<quoteID>', methods=['GET'])
def get_all_quotes(quoteID=None):
	#conn = mysql.connect()
	#cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	conn = mysql.connector.connect(user=sqlUser, password=sqlPass, host=sqlHost, database=sqlDb)
	cursor = conn.cursor(dictionary=True)
	if quoteID:
		query = ("select * from quotes.quotes where private = 0 and remove is NULL and id = '%s' ORDER BY ID DESC LIMIT 1;") % quoteID
	else:
		query = ("select * from quotes.quotes where private = 0 and remove is NULL ORDER BY ID DESC LIMIT 50;")
	cursor.execute(query)
	data = cursor.fetchall()
	#return jsonify({'quotes': data})
	return jsonify(quote=data)

@app.route('/api', methods=['GET'])
@app.route('/api/v1.0/random', methods=['GET'])
def get_all_quotes(quoteID=None):
	#conn = mysql.connect()
	#cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	conn = mysql.connector.connect(user=sqlUser, password=sqlPass, host=sqlHost, database=sqlDb)
	cursor = conn.cursor(dictionary=True)
	query = ("select * from quotes.quotes where private = 0 and remove is NULL ORDER BY RAND() LIMIT 1;")
	cursor.execute(query)
	data = cursor.fetchall()
	#return jsonify({'quotes': data})
	return jsonify(quote=data)

if __name__ == '__main__':
	app.debug=True
	app.run(host='0.0.0.0', port=5050)