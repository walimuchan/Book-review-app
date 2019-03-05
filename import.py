import os, psycopg2, csv

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(host="localhost",database="bookreviewapp", user="postgres", password="phiona")
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS books ( id SERIAL PRIMARY KEY, \
								   isbn VARCHAR NOT NULL, \
								   title VARCHAR NOT NULL, \
								   author VARCHAR NOT NULL, \
								   year VARCHAR NOT NULL);")

print("Created!")

csvfile = open("books.csv") 
reader = csv.reader(csvfile,delimiter=',')
print("Creating books table!")
for isbn, title, author, year in reader:
	cur.execute("INSERT INTO books (isbn, title, author, year) VALUES (%s, %s, %s, %s)",(isbn,title,author,year))
	cur.commit()
	print("Adding values to table.")
print("Insert Completed!")


cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR(100) NOT NULL, email VARCHAR(100) NOT NULL, password VARCHAR NOT NULL, create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
cur.commit()
print("user table created successfully")


cur.execute("CREATE TABLE IF NOT EXISTS reviews (id SERIAL PRIMARY KEY, review VARCHAR NOT NULL,book_id INTEGER NOT NULL,user_id INTEGER REFERENCES users);")
cur.commit()
print("Reviews table created successfully!")




