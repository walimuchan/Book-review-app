import os, psycopg2, csv


DATABASE_URL = os.getenv('DATABASE_URL')
# conn = psycopg2.connect(host="ec2-54-204-41-109.compute-1.amazonaws.com",database="d1n7l3kagabmad", user="uwkbqqgeyazbdh", password="c5647dbf653b7bdab68452b7c6dc23c3c57bef1b6a54ba3c749e6e4fbdcfb23d")




csvfile = open("books.csv") 
reader = csv.reader(csvfile,delimiter=',')
print("Creating books table!")

cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS books ( id SERIAL PRIMARY KEY, \
								   isbn VARCHAR NOT NULL, \
								   title VARCHAR NOT NULL, \
								   author VARCHAR NOT NULL, \
								   year VARCHAR NOT NULL );")

print("Created!")

print("Adding values to table.")

for isbn, title, author, year in reader:
	cur.execute("INSERT INTO books (isbn, title, author, year) VALUES (%s, %s, %s, %s)",(isbn,title,author,year))

conn.commit()
print("Insert Completed!")


cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR(100) NOT NULL, email VARCHAR(100) NOT NULL, password VARCHAR NOT NULL, create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
conn.commit()
print("user table created successfully")


cur.execute("CREATE TABLE IF NOT EXISTS reviews (id SERIAL PRIMARY KEY, review VARCHAR NOT NULL,book_id INTEGER NOT NULL,user_id INTEGER REFERENCES users);")
conn.commit()
print("Reviews table created successfully!")




