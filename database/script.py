import sqlite3
import requests
from datetime import datetime
from dateutil import parser

#Connect ot the db
conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

#My personnal API key to TMDb
api_key = "8c20949924e21c12e725af3432345313"

#Get the genres list
url = f"https://api.themoviedb.org/3/genre/movie/list?language=en-US&api_key={api_key}"
response = requests.get(url)

#Make it to a readable dict
genres = response.json()
genres = genres["genres"]

cursor.execute("DROP TABLE IF EXISTS genres")
cursor.execute("DROP TABLE IF EXISTS movies")
cursor.execute("DROP TABLE IF EXISTS movie_genres")
cursor.execute("DROP TABLE IF EXISTS movie_directors")

#Create the genres table if not exists that link a genre to an id
cursor.execute("CREATE TABLE IF NOT EXISTS genres (genre_id INT NOT NULL PRIMARY KEY, genre TEXT NOT NULL)")

#Put in the genres table every genre and their id
for genre in genres:
    id = genre["id"]
    name = genre["name"]
    cursor.execute("SELECT * FROM genres WHERE genre_id = ?", (id,))
    in_table = cursor.fetchone()
    if not in_table: 
        cursor.execute("INSERT INTO genres (genre_id, genre) VALUES (?, ?)", (id, name))

conn.commit()

#Create the movies table if not exists
cursor.execute("CREATE TABLE IF NOT EXISTS movies (movie_id INT NOT NULL PRIMARY KEY, title TEXT NOT NULL, overview TEXT NOT NULL, release_date DATE NOT NULL, rating REAL DEFAULT NULL, runtime INTc)")

#Create the movies-genres table if not exists
cursor.execute("CREATE TABLE IF NOT EXISTS movie_genres (movie_id INT, genre_id INT, FOREIGN KEY (movie_id) REFERENCES movies(movie_id), FOREIGN KEY (genre_id) REFERENCES genres(genre_id))")

#Create the movies-directors table if not exists
cursor.execute("CREATE TABLE IF NOT EXISTS movie_directors (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, movie_id INT, director TEXT NOT NULL, FOREIGN KEY (movie_id) REFERENCES movies(movie_id))")

#Initialise the thresholds
start_year = 1960
end_year = 2023
max_page = 2

#Add into movies and movie_genres the data imported from TMDb
for year in range(start_year, end_year + 1):
    for page in range(1, max_page + 1):
        url = f"https://api.themoviedb.org/3/discover/movie?language=en-US&api_key={api_key}&page={page}&primary_release_year={year}&sort_by=popularity.desc"

        response = requests.get(url)

        movies = response.json()
        movies = movies["results"]

        for movie in movies:
            movie_id = movie["id"]
            title = movie["title"]
            try:
                date = movie["release_date"]
                release_date = parser.parse(date).date()
            except KeyError:
                release_date = ""
            genre_ids = movie["genre_ids"]
            overview = movie["overview"]
            rating = movie["vote_average"]

            url_duration = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
            response_duration = requests.get(url_duration)
            duration = response_duration.json()
            runtime = duration["runtime"]

            url_director = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}"
            response_director = requests.get(url_director)
            movie_credits = response_director.json()
            crew = movie_credits.get("crew", [])
            directors = [member for member in crew if member.get("job", "") == "Director"]
            director_names = [director.get("name") for director in directors]
            

            cursor.execute("SELECT * FROM movies WHERE movie_id = ?", (movie_id,))
            in_table = cursor.fetchone()
            if not in_table: 
                cursor.execute("INSERT INTO movies (movie_id, title, overview, release_date, rating, runtime) VALUES (?, ?, ?, ?, ?, ?)", (movie_id, title, overview, release_date, rating, runtime))
                for genre_id in genre_ids:
                    cursor.execute("INSERT INTO movie_genres (movie_id, genre_id) VALUES (?, ?)", (movie_id, genre_id))
                for director_name in director_names:
                    cursor.execute("INSERT INTO movie_directors (movie_id, director) VALUES (?, ?)", (movie_id, director_name))
                conn.commit()

conn.close()
