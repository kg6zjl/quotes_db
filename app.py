# -*- coding: utf-8 -*

import os
from flask import Flask, render_template, request, json, abort, make_response, jsonify, Blueprint
from flask.views import View
from flask_paginate import Pagination
from werkzeug import generate_password_hash, check_password_hash
try:
	from flask.ext.mysql import MySQL
except:
	from flask_mysql import MySQL

app = Flask(__name__)
application = Flask(__name__)
mysql = MySQL()

# MySQL configurations/ENV Vars
app.config['MYSQL_DATABASE_USER'] = os.environ['QUOTES_DB_USER']
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ['QUOTES_DB_PASS']
app.config['MYSQL_DATABASE_DB'] = os.environ['QUOTES_DB_NAME']
app.config['MYSQL_DATABASE_HOST'] = os.environ['QUOTES_DB_HOST']
mysql.init_app(app)

@app.route('/all')
def index():
    #use this if adding in search features
    search = False
    q = request.args.get('q')
    if q:
        search = True
    
    page = request.args.get('page', type=int, default=1)
    
    if page == 1:
        per_page = 1
    else:
        per_page = 10

    conn = mysql.connect()
    cursor = conn.cursor()
    query = ("select * from quotes.quotes where private = 0 ORDER BY id ASC LIMIT 10 OFFSET %s;") % (int(page)*int(per_page)-1)
    cursor.execute(query)
    data = cursor.fetchall()

    total=cursor.rowcount

    #page=request.args.get('page')
    #if not page:
    #	page = 1

    pagination = Pagination(page=page, total=total, search=search)#, record_name='quotes')
    return render_template('viewall.html',
                           data=data,
                           pagination=pagination,
                           page=page
                           )

@app.route("/all_dep")
def main():
	conn = mysql.connect()
	cursor = conn.cursor()
	query = ("select * from quotes.quotes where private = 0 ORDER BY RAND() LIMIT 50;")
	cursor.execute(query)
	data = cursor.fetchall()
	
	return render_template('recent.html',data=(data))
	#return render_template('index.html')

@app.route("/darkside")
@app.route("/darkside/")
@app.route("/darkside/<quoteID>")
def darkside(quoteID=None):
	if quoteID:
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("select * from quotes.quotes where private = 1 AND id = '%s' LIMIT 1;") % str(quoteID)
		cursor.execute(query)
		data = cursor.fetchall()
	else:
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("select * from quotes.quotes where private = 1 order by RAND() ASC;")
		cursor.execute(query)
		data = cursor.fetchall()	
	return render_template('recent.html',data=data,darkside=True)

@app.route('/quote/<quoteID>')
def singleQuote(quoteID=None):
	if quoteID:
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("select * from quotes.quotes where private = 0 AND id = '%s' LIMIT 1;") % str(quoteID)
		cursor.execute(query)
		data = cursor.fetchall()
	else:
		data=None
	return render_template('recent.html',data=(data))

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
	query = ("select * from quotes.quotes where private = 0 order by id DESC limit 10;")
	cursor.execute(query)
	data = cursor.fetchall()
	
	return render_template('recent.html',data=(data))

@app.route("/author/<name>")
def author(name=None):
	if name:
		name = name.replace("'", "\\'")
		try:
			conn = mysql.connect()
			cursor = conn.cursor()
			query = ("select * from quotes.quotes q where private = 0 and name like '%s' order by id DESC;") % name
			cursor.execute(query)
			data = cursor.fetchall()
			
			return render_template('recent.html',data=(data))
		except:
			data=[('404',"Something broke.","Webserver")]
			return render_template('recent.html',data=data)

@app.route("/search")
@app.route("/search/")
@app.route("/search/<searchString>")
def search(searchString=None):
	if searchString:
		searchString = searchString.replace("'", "\\'")
		searchString = ('%'+searchString+'%')
		try:
			conn = mysql.connect()
			cursor = conn.cursor()
			query = ("select * from quotes.quotes q where private = 0 and quote like '%s' order by id DESC;") % searchString
			cursor.execute(query)
			data = cursor.fetchall()
			
			return render_template('recent.html',data=(data))
		except:
			data=[('404',"Something broke.","Webserver")]
			return render_template('recent.html',data=None)
	else:
		data=[('404',"Something broke.","Webserver")]
		return render_template('recent.html',data=data)

@app.route('/')
@app.route("/random")
@app.route("/random/")
def random():
	conn = mysql.connect()
	cursor = conn.cursor()
	query = ("select * from quotes.quotes where private = 0 ORDER BY (RAND()*hour(now())) limit 1;")
	cursor.execute(query)
	data = cursor.fetchall()
	
	return render_template('recent.html',data=(data))

#@app.route('/addQuote',methods=['POST','GET']) # for future api?
@app.route('/addQuote')
def addRecipe(): # read the posted values from the UI
	_quote = request.form['quoteText']
	_author = request.form['quoteAuthor']

	# validate the received values
	if _title and _description and _contributor:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('sp_createQuote',(_title,_description,_contributor))
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
	data=[('404',"Something broke.","Webserver")]
	return render_template('recent.html',data=data)
	#return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "__main__":
	#app.debug = True
	app.run(host='0.0.0.0', port=5000)
