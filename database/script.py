import sqlite3

conn = sqlite3.connect("movies.db")
print("DB connected successfully")

cursor = conn.cursor()

