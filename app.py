# -*- coding: utf-8 -*

import os, datetime
from flask import Flask, render_template, request, json, abort, make_response, jsonify, Blueprint, redirect, url_for, session
from flask.views import View
from flask_paginate import Pagination
from werkzeug import generate_password_hash, check_password_hash
from werkzeug.contrib.atom import AtomFeed
from flaskext.mysql import MySQL

app = Flask(__name__)
application = Flask(__name__)
mysql = MySQL()
#sess = Session()

# sql envs
app.config['MYSQL_DATABASE_USER'] = os.environ['QUOTES_DB_USER']
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ['QUOTES_DB_PASS']
app.config['MYSQL_DATABASE_DB'] = os.environ['QUOTES_DB_NAME']
app.config['MYSQL_DATABASE_HOST'] = os.environ['QUOTES_DB_HOST']

mysql.init_app(app)
# mailchimp envs
mailchimp_api_key = os.environ['MAILCHIMP_API_KEY']
#upload_api_key
upload_api_key = os.environ['UPLOAD_API_KEY']

@app.route('/feed')
@app.route('/feed/')
def rss_feed():
	#get data for rss feed:
	conn = mysql.connect()
	cursor = conn.cursor()
	query = ("select * from quotes.quotes where private = 0 and remove is NULL having created_at > (DATE(NOW()) - INTERVAL 7 DAY) order by RAND() LIMIT 5;")
	cursor.execute(query)
	data = cursor.fetchall()
	# now process to xml:
	base_url = "http://quotes.stevearnett.com/"
	feed = AtomFeed('Recent Quotes', feed_url=str(base_url+"feed"), url=str(base_url))
	for quote in data:
		title = 'Ridiculous. Quotes. (#'+str(quote[0])+")"
		if quote[2]:
			quote_text = (str(quote[1])+str(" - ")+str(quote[2]))
			author = str(quote[2])
		else:
			author = ' '
			quote_text = str(quote[1])
		feed.add(unicode(title), unicode(quote_text),
				 content_type='html',
				 author=author,
				 id=quote[0],
				 url=("http://quotes.stevearnett.com/quote/"+str(quote[0])),
				 updated=quote[5])
	return feed.get_response()

@app.route('/feed/daily')
@app.route('/feed/daily/')
def rss_feed_random():
	#get data for rss feed:
	conn = mysql.connect()
	cursor = conn.cursor()
	query = ("select * from quotes.quotes where private = 0 and remove is NULL order by RAND() LIMIT 1;")
	cursor.execute(query)
	data = cursor.fetchall()
	# now process to xml:
	base_url = "http://quotes.stevearnett.com/"
	feed = AtomFeed('Random Quote', feed_url=str(base_url+"feed"), url=str(base_url))
	for quote in data:
		title = 'Ridiculous. Quotes. (#'+str(quote[0])+")"
		if quote[2]:
			quote_text = (str(quote[1])+str(" - ")+str(quote[2]))
			author = str(quote[2])
		else:
			author = ' '
			quote_text = str(quote[1])
		feed.add(unicode(title), unicode(quote_text),
				 content_type='html',
				 author=author,
				 id=quote[0],
				 url=("http://quotes.stevearnett.com/quote/"+str(quote[0])),
				 updated=(datetime.datetime.now())) # fool mailchimp into thinking this is new content
				 #updated=quote[5])
	return feed.get_response()	

#write new quote to db
@app.route('/submitquote/<key>',methods=['POST','GET'])
def input(key=None):
	if key == upload_api_key:
		quote = None
		author = None
		private = None
		highdeas = None
		if request.method == 'POST':
			quote, author, private, highdeas = request.form['quoteText'], request.form['quoteAuthor'], request.form['quotePrivate'], request.form['high=quoteHigh']
			conn = mysql.connect()
			cursor = conn.cursor()
			query = ("insert into quotes (quote,name,private,highdeas) values ('%s', '%s', '%s', '%s');") % (quote.replace("'", "\\'"), author.replace("'", "\\'"), private, highdeas)
			print query
			cursor.execute(query)
			print "executed query"
			conn.commit()
			print "commited query"
			return(redirect(url_for('recent'), code=302))
	else:
		data=[('404','"Something broke."',"Webserver")]
		return render_template('recent.html',key=key)

#submit a new quote
@app.route('/submit/<key>')
def new_quote(key=None):
	if key == upload_api_key:
		#session['logged_in'] = True
		return render_template('add_quote.html',key=upload_api_key)
	else:
		data=[('404','"Something broke."',"Webserver")]

#edit the text/author/darkside of a quote
#@app.route('/edit/<quoteID>',methods=['POST','PUT','GET'])
def edit_quote(quoteID=None):
	if session.get('logged_in'):
		if session['logged_in'] == True:
			auth=True
			if request.method == 'POST':
				quote, author, private = request.form['quoteText'], request.form['quoteAuthor'], request.form['quotePrivate']
				conn = mysql.connect()
				cursor = conn.cursor()
				query = ("update quotes.quotes set quote='%s', name='%s', private='%s' where id = '%s';") % (quote.replace("'", "\\'"), author.replace("'", "\\'"), private, quoteID)
				cursor.execute(query)
				conn.commit()
				return redirect("/quote/"+quoteID, code=302)
			else:
				if quoteID:
					conn = mysql.connect()
					cursor = conn.cursor()
					query = ("select * from quotes.quotes where id = '%s' LIMIT 1;") % str(quoteID)
					cursor.execute(query)
					data = cursor.fetchall()
					return render_template('edit_quote.html',data=data,auth=auth)
	else:
		data=[('404','"Something broke."',"Webserver")]
		return render_template('recent.html',data=data)

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
	query = ("select * from quotes.quotes where private = 0 and remove is NULL ORDER BY id ASC LIMIT 10 OFFSET %s;") % (int(page)*int(per_page)-1)
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

@app.route("/darkside")
@app.route("/darkside/")
@app.route("/darkside/<quoteID>")
def darkside(quoteID=None):
	if quoteID:
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("select * from quotes.quotes where private = 1 AND id = '%s' and remove is NULL LIMIT 1;") % str(quoteID)
		cursor.execute(query)
		data = cursor.fetchall()
	else:
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("select * from quotes.quotes where private = 1 and remove is NULL order by id DESC;")
		cursor.execute(query)
		data = cursor.fetchall()	
	return render_template('recent.html',data=data,darkside=True)

@app.route('/quote/<quoteID>')
def singleQuote(quoteID=None):
	darkside=False
	if quoteID:
		darkside=False
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("select * from quotes.quotes where private = '0' and remove is NULL and id = '%s' LIMIT 1;") % str(quoteID)
		#if session.get('logged_in'):
		#	if session['logged_in'] == True:
		#		auth=True
		#		darkside=True
		#		query = ("select * from quotes.quotes where id = '%s' and remove is NULL LIMIT 1;") % str(quoteID)
		cursor.execute(query)
		data = cursor.fetchall()
		return render_template('recent.html',data=(data),darkside=False)

@app.route("/submitQuote")
def submitQuote():
	return render_template('add_quote.html')

@app.route("/thanks")
def thanks():
	return render_template('thanks.html')

@app.route("/recent")
def recent():
	conn = mysql.connect()
	cursor = conn.cursor()
	query = ("select * from quotes.quotes where private = 0 and remove is NULL order by id DESC limit 10;")
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
			query = ("select * from quotes.quotes q where private = 0 and name like '%s' and remove is NULL order by id DESC;") % name
			cursor.execute(query)
			data = cursor.fetchall()
			
			return render_template('recent.html',data=(data))
		except:
			data=[('404','"Something broke."',"Webserver")]
			return render_template('recent.html',data=data)

@app.route('/search/<q>',methods=['GET','POST'])
@app.route('/search/',methods=['GET','POST'])
def search_v2(q=None,darkside=False):
	try:
		if request.method == 'POST': #request.method == 'POST' or 
			if q == None:
				searchString = request.form['q']
			else:
				searchString = q
			searchString = searchString.replace("'", "\\'")
			conn = mysql.connect()
			cursor = conn.cursor()
			query = ("SELECT * FROM quotes.quotes WHERE private = 0 and remove is NULL and MATCH(quote) AGAINST('%s*' IN BOOLEAN MODE) ORDER BY MATCH(quote) AGAINST('%s*') DESC;") % (searchString,searchString)
			cursor.execute(query)
			data = cursor.fetchall()
			if data:
				return render_template('recent.html',data=(data))
			else:
				data=[('','"No results."',"Webserver")]
				return render_template('recent.html',data=data)
		elif request.method == 'GET':
			try:
				if q == None:
					searchString = request.args.get('q')
				else:
					searchString = q
				searchString = searchString.replace("'", "\\'")
				conn = mysql.connect()
				cursor = conn.cursor()
				try:
					darkside = request.args.get('darkside')
				except:
					darkside = False
				if darkside == 'True' or darkside == 'true':
					private = 1
				else:
					private = 0
				
				query = ("SELECT * FROM quotes.quotes WHERE private = '%s' and remove is NULL and MATCH(quote) AGAINST('%s*' IN BOOLEAN MODE) ORDER BY MATCH(quote) AGAINST('%s*') DESC;") % (private,searchString,searchString)
				
				cursor.execute(query)
				data = cursor.fetchall()
				if data:
					return render_template('recent.html',data=(data))
				else:
					data=[('','"No results."',"Webserver")]
					return render_template('recent.html',data=data)
			except:
				return render_template('search.html')
	except:
		return render_template('search.html')	
	return render_template('search.html')

@app.route('/')
@app.route("/random")
@app.route("/random/")
def random():
	conn = mysql.connect()
	cursor = conn.cursor()
	query = ("select * from quotes.quotes where private = 0 and remove is NULL ORDER BY RAND() limit 1;")
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

@app.route("/highdeas")
@app.route("/highdeas/")
@app.route("/highdeas/<quoteID>")
def highdeas(quoteID=None):
	if quoteID:
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("select * from quotes.quotes where highdeas = 1 AND id = '%s' and remove is NULL LIMIT 1;") % str(quoteID)
		cursor.execute(query)
		data = cursor.fetchall()
	else:
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("select * from quotes.quotes where highdeas = 1 and remove is NULL order by id DESC;")
		cursor.execute(query)
		data = cursor.fetchall()	
	return render_template('recent.html',data=data,darkside=True)
	
@app.errorhandler(404)
def not_found(error):
	#to use, call: abort(404)
	data=[('404','"Something broke."',"Webserver")]
	return render_template('recent.html',data=data)
	#return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == "__main__":
	#app.debug = True
	#app.secret_key = upload_api_key
	app.run(host='0.0.0.0', port=5000)
