import os


from flask import Flask, render_template, request, session, redirect, Markup,jsonify, flash, url_for
from flask_session import Session
from sqlalchemy import create_engine
from functools import wraps
from sqlalchemy.orm import scoped_session, sessionmaker

import requests
from xml.etree import ElementTree


app = Flask(__name__)

app.config["SECRET_KEY"]= '70d146d487dfd571dc7b'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


# # Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'logged_in' not in session:
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function

#home
@app.route('/', methods=['GET', 'POST'])
def home():
	if session.get('username') is None:
		return redirect('/login')
	if request.method == "GET":
		return render_template('home.html', menu=True)
	else:
		query = request.form.get('query').lower()
		query_like = '%' + query + '%'
		books = db.execute('SELECT * FROM books WHERE (LOWER(isbn) LIKE :query) 					OR (LOWER(title) LIKE :query) '
                           'OR (LOWER(author) LIKE :query)',
                           {'query': query_like}).fetchall()
		if not books:
			return render_template('error.html', menu=True)
		return render_template('result.html', query=query, books=books, menu=True)

# signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    session.clear()

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # check if passwords are the same

        if not password == confirm_password:
            return render_template('error.html', message='Passwords do not match')

        # check if user is available

        avail = db.execute('SELECT username FROM users WHERE username=:username',
                           {'username': username}).fetchone()

        if avail:
            return render_template('error.html', message='Username Already Exists')

        # Write username and password to database

        db.execute('INSERT INTO users(username, password) VALUES(:username, 				:password)',
                   {'username': username, 'password': password})
        db.commit()
		

        session['username'] = username

        return redirect('/login')

    else:
        return render_template('signup.html', menu=False)

	
# login
@app.route('/login', methods=['GET', 'POST'])
def login():
	session.clear()
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

		

		user = db.execute("SELECT * FROM users WHERE (username=:username and 						password=:password)",
                             {'username': username, 'password': password}).fetchone()
		if user is None or username!=user.username:
			return render_template('error.html')
		else:
			session[ 'username' ] = username
			return redirect('/')
	
	return render_template('login.html', menu=False)

# logout
@app.route('/logout')
@login_required
def logout():
	session.clear()
	return redirect('/')


@app.route('/books/<isbn>')
def book(isbn):

    book = db.execute('SELECT * FROM books WHERE isbn=:isbn',
                      {'isbn': isbn}).fetchone()

    if book is None:
        return render_template('error.html', message='This book is not available', menu=True)

    url = "https://www.goodreads.com/book/isbn/{}?key=dcaxcbB83QsR3RHGr7QEyw".format(isbn)
    res = requests.get(url)
    tree = ElementTree.fromstring(res.content)

    try:
        description = tree[1][16].text
        image_url = tree[1][8].text
        review_count = tree[1][17][3].text
        avg_score = tree[1][18].text
        link = tree[1][24].text

    except IndexError:
        return render_template('book.html', book=book, link=None, menu=True)

    description_markup = Markup(description)

    return render_template('book.html', book=book, link=link, 										   description=description_markup,
                           image_url=image_url, review_count=review_count, avg_score=avg_score, menu=True)

@app.route('/api/<isbn>')
def book_api(isbn):

    book = db.execute('SELECT * FROM books WHERE isbn=:isbn',
                      {'isbn': isbn}).fetchone()

    if book is None:
        api = jsonify({'error': 'This book is not available'})
        return api

    url = "https://www.goodreads.com/book/isbn/{}?key=dcaxcbB83QsR3RHGr7QEyw".format(isbn)
    res = requests.get(url)
    tree = ElementTree.fromstring(res.content)

    try:
        description = tree[1][16].text
        image_url = tree[1][8].text
        review_count = tree[1][17][3].text
        avg_score = tree[1][18].text
        link = tree[1][24].text

    except IndexError:
        api = jsonify({
            'title': book.title,
            'author': book.author,
            'year': book.year,
            'isbn': book.isbn,
            'link': '',
            'description': '',
            'book_cover': '',
            'review_count': '',
            'average_rating': ''
        })

        return api

    api = jsonify({
        'title': book.title,
        'author': book.author,
        'year': book.year,
        'isbn': book.isbn,
        'link': link,
        'description': description,
        'book_cover': image_url,
        'review_count': review_count,
        'average_rating': avg_score
    })

    return api

@app.route('/review', methods=['GET', 'POST'])
def review():

    if request.method == 'POST':

        isbn = request.form.get('isbn')
        review = request.form.get('review')

        username = session['username']

        book = db.execute('SELECT * FROM books WHERE isbn=:isbn ',
                          {'isbn': isbn}).fetchone()

        if book is None:
            return render_template('error.html', message='Book ISBN Invalid', menu=True)

        db.execute('INSERT INTO reviews(title, isbn, review, user_name) VALUES(:title, :isbn, :review, :username)',
                   {'title': book.title, 'isbn': isbn, 'review': review, 'username': username})
        db.commit()
        

        

    else:
        return render_template('book.html', menu=True)
