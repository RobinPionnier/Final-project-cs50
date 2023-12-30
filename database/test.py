import sqlite3

#Connect ot the db
conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS watchlist")
cursor.execute("DROP TABLE IF EXISTS liked")
cursor.execute("DROP TABLE IF EXISTS disliked")

#Create the uses table if not exists that links a username to a pw
cursor.execute("CREATE TABLE IF NOT EXISTS watchlist (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, movie_id INTEGER NOT NULL)")
cursor.execute("CREATE TABLE IF NOT EXISTS liked (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, movie_id INTEGER NOT NULL)")
cursor.execute("CREATE TABLE IF NOT EXISTS disliked (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, movie_id INTEGER NOT NULL)")

conn.commit()

conn.close()