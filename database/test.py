import sqlite3
import requests

#Connect ot the db
conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

#My personnal API key to TMDb
api_key = "8c20949924e21c12e725af3432345313"


url = f"https://api.themoviedb.org/3/discover/movie?language=en-US&api_key={api_key}&page=1&primary_release_year=2022&sort_by=popularity.desc"

response = requests.get(url)

movies = response.json()
movies = movies["results"]

print(movies)