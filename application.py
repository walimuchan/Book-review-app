import os
import psycopg2


from flask import Flask, render_template, url_for, flash, redirect, request, redirect, Markup, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_login import current_user, LoginManager, login_required, login_user, logout_user, UserMixin
from forms import RegistrationForm, LoginForm
from flask_bcrypt import Bcrypt
import requests
from xml.etree import ElementTree
app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"]= '70d146d487dfd571dc7b'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

Session(app)


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=['GET', 'POST'])
def home():
	if request.method == "GET":
	 	return render_template('home.html')
	else:
		query = request.form.get('query').lower()
		query_like = '%' + query + '%'
		books = db.execute('SELECT * FROM books WHERE (LOWER(isbn) LIKE :query) OR 						(LOWER(title) LIKE :query)' 'OR (LOWER(author) 							LIKE :query)',{'query': query_like}).fetchall()
		if not books:
			flash(f"no book found!")
	return render_template('result.html', query=query, books=books)


 
@app.route("/signup", methods=['POST', 'GET'])
def signup():
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		db.execute("INSERT INTO users(username, email, password) VALUES(:username, :email, :password)",{"username":form.username.data, "email":form.email.data, "password":hashed_password})
		db.commit()
		flash (f"{form.username.data}  you have successfully created an account! Please login", 'success')
		return redirect(url_for('login'))
	return render_template('signup.html',form=form)


@app.route("/login", methods=['POST', 'GET'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = db.execute("SELECT * FROM users WHERE (email=:email)",{'email': form.email.data}).fetchone()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			flash(f"Welcome start searching for your favorite books.", 'success')
			return redirect(url_for('home'))
		else:
			flash("Invalid email or password. Try again", 'danger')			
	return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('home'))



@app.route('/books/<string:isbn>')
def book(isbn):
	book = db.execute('SELECT * FROM books WHERE isbn=:isbn',{'isbn': isbn}).fetchone()

	if book is None:
		flash(f"no book found!")

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
		return render_template('book.html', book=book, link=None)
	description_markup = Markup(description)

	return render_template('book.html', book=book, link=link, 											description=description_markup, image_url=image_url, 						review_count=review_count, avg_score=avg_score)									


@app.route('/api/<isbn>')
def book_api(isbn):
	book = db.execute('SELECT * FROM books WHERE isbn=:isbn',{'isbn': isbn}).fetchone()
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
