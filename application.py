import os
import psycopg2
import ssl

from flask import Flask, render_template, url_for, flash, redirect, request, redirect, Markup, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_login import current_user, LoginManager, login_required, login_user
from forms import RegistrationForm, LoginForm, SearchForm
from flask_bcrypt import Bcrypt
import requests
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

Session(app)


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/signup", methods=['POST', 'GET'])
def signup():
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		cur.execute("INSERT INTO users(username, email, password) VALUES(:username, :email, :password)",{"username":form.username.data, "email":form.email.data, "password":hashed_password})
		conn.commit()
		flash (f"user {form.username.data} have successfully created an account! Please login", 'success')
		return redirect(url_for('login'))
	return render_template('signup.html',form=form)


@app.route("/login", methods=['POST', 'GET'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = db.execute("SELECT * FROM users WHERE (email=:email)",{'email': form.email.data}).fetchone()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			flash(f"Welcome start searching for your favorite books.", 'success')
			return redirect(url_for('home'))
		else:
			flash("Invalid email or password. Try again", 'danger')			
	return render_template('login.html', form=form)

# search
@app.route("/search", methods=['POST', 'GET'])
def search():
	form = SearchForm()
	if request.method == "GET":
		return render_template("search.html", form=form)
	else:
		title=request.form.get("title")
		author=request.form.get("author")
		isbn=request.form.get("isbn")
		data=[]
		if title:
			title=db.execute("SELECT * from books where title :title",
								{"title":"%"+title+"%"}).fetchall()
			data.append(title)

		if author:
			author=db.execute("SELECT * from books where author :author",
								{"author":"%"+author+"%"}).fetchall()
			data.append(author)

		if isbn:
			isbn=db.execute("SELECT * from books where isbn :isbn",
								{"isbn":"%"+isbn+"%"}).fetchall()
			data.append(isbn)
		
		if not data:
			return render_template("search.html")
		else:
			return render_template("search.html", data=data)
		
	


    # form = SearchForm()
    # if form.validate_on_submit():
    #     results = db.execute("SELECT * FROM books WHERE author LIKE  '%a%' ORDER BY id OFFSET 10 ROWS FETCH NEXT 10 ROWS ONLY ")
    #     print(results)
    #     return render_template('results.html', results=results)
	# 	# return redirect(url_for('home'))
    # return render_template('search.html', form=form)
    