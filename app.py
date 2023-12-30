from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, check_pw


app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Function to get genre information
def get_genres():
    cursor = get_db()
    genres = cursor.execute("SELECT * FROM genres").fetchall()
    genres_dict = {genre[0]: genre[1] for genre in genres}
    return genres_dict

@app.template_filter('convert')
def convert(value):
    hours = value // 60
    minutes = value % 60
    return f"{hours}h{minutes}"

@app.template_filter('year')
def convert(date):
    year = date[:4]
    return f"{year}"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("movies.db")
    return db.cursor()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Your research route
@app.before_request
def before_request():
    if not hasattr(g, 'genres'):
        g.genres = get_genres()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_to_watchlist", methods=["POST"])
def add_to_watchlist():
    if "user_id" in session:
        user_id = session["user_id"]
        movie_id = request.form.get("movie_id")

        # Assuming you have a table named 'watchlist' with columns 'user_id' and 'movie_id'
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        
        in_watchlist = cursor.execute("SELECT * FROM watchlist WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)).fetchone()
        if not in_watchlist:
            cursor.execute("INSERT INTO watchlist (user_id, movie_id) VALUES (?, ?)", (user_id, movie_id))
            conn.commit()
            conn.close()
            return "Successfully added to watchlist"
        else:
            return "Already in watchlist", 401

    return "User not authenticated", 401

@app.route("/remove_from_watchlist", methods=["POST"])
def remove_from_watchlist():
    if "user_id" in session:
        user_id = session["user_id"]
        movie_id = request.form.get("movie_id")

        # Assuming you have a table named 'watchlist' with columns 'user_id' and 'movie_id'
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        
        in_watchlist = cursor.execute("SELECT * FROM watchlist WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)).fetchone()
        if in_watchlist:
            cursor.execute("DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
            conn.commit()
            conn.close()
            return "Successfully removed from watchlist"
        else:
            return "Already not in watchlist", 401

    return "User not authenticated", 401

@app.route("/add_to_liked", methods=["POST"])
def add_to_liked():
    if "user_id" in session:
        user_id = session["user_id"]
        movie_id = request.form.get("movie_id")

        # Assuming you have a table named 'liked' with columns 'user_id' and 'movie_id'
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()

        in_watchlist = cursor.execute("SELECT * FROM watchlist WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)).fetchone()
        if in_watchlist:
            cursor.execute("DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
            conn.commit()

        in_disliked = cursor.execute("SELECT * FROM disliked WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)).fetchone()
        if in_disliked:
            cursor.execute("DELETE FROM disliked WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
            conn.commit()
        
        in_liked = cursor.execute("SELECT * FROM liked WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)).fetchone()
        if not in_liked:
            cursor.execute("INSERT INTO liked (user_id, movie_id) VALUES (?, ?)", (user_id, movie_id))
            conn.commit()
            conn.close()
            return "Successfully added to liked"
        else:
            return "Already in liked", 401

    return "User not authenticated", 401

@app.route("/add_to_disliked", methods=["POST"])
def add_to_disliked():
    if "user_id" in session:
        user_id = session["user_id"]
        movie_id = request.form.get("movie_id")

        # Assuming you have a table named 'disliked' with columns 'user_id' and 'movie_id'
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()

        in_watchlist = cursor.execute("SELECT * FROM watchlist WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)).fetchone()
        if in_watchlist:
            cursor.execute("DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
            conn.commit()

        in_liked = cursor.execute("SELECT * FROM liked WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)).fetchone()
        if in_liked:
            cursor.execute("DELETE FROM liked WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
            conn.commit()
        
        in_disliked = cursor.execute("SELECT * FROM disliked WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)).fetchone()
        if not in_disliked:
            cursor.execute("INSERT INTO disliked (user_id, movie_id) VALUES (?, ?)", (user_id, movie_id))
            conn.commit()
            conn.close()
            return "Successfully added to disliked"
        else:
            return "Already in disliked", 401

    return "User not authenticated", 401

@app.route("/research", methods=["GET", "POST"])
def research():
    if request.method == "POST":
        title = request.form.get("title")

        min_year = request.form.get("min-year")
        max_year = request.form.get("max-year")

        if not min_year:
            min_year = "1900"
        if not max_year:
            max_year = "2100"

        min_duration = request.form.get("min-duration")
        max_duration = request.form.get("max-duration")

        if not min_duration:
            min_duration = "0"
        if not max_duration:
            max_duration = "600"

        min_rating = request.form.get("min-rating")
        max_rating = request.form.get("max-rating")

        if not min_rating:
            min_rating = "0"
        if not max_rating:
            max_rating = "10"

        cursor = get_db()

        genre = request.form.get("genres")

        # Initialize variables for genre-related conditions
        genre_condition = ""
        genre_params = ()

        # Check if a genre is selected
        if genre:
            genre_id_result = cursor.execute("SELECT genre_id FROM genres WHERE genre = ?", (genre,)).fetchone()
            
            # Check if the genre exists in the database
            if genre_id_result:
                genre_id = genre_id_result[0]
                genre_condition = "AND movie_genres.genre_id = ?"
                genre_params = (genre_id,)

        director = request.form.get("director")

        # Now use these conditions in your main query
        rows = cursor.execute(
            f"SELECT * FROM movies JOIN movie_genres ON movies.movie_id = movie_genres.movie_id JOIN genres ON genres.genre_id = movie_genres.genre_id JOIN movie_directors ON movie_directors.movie_id = movies.movie_id WHERE movies.title LIKE ? AND strftime('%Y', movies.release_date) >= ? AND strftime('%Y', movies.release_date) <= ? AND movies.runtime >= ? AND movies.runtime <= ? AND movies.rating >= ? AND movies.rating <= ? AND movie_directors.director LIKE ? {genre_condition} GROUP BY movies.title ORDER BY movies.rating DESC",
            ('%' + title + '%', min_year, max_year, min_duration, max_duration, min_rating, max_rating, '%' + director + '%', *genre_params)
        ).fetchall()

        columns = [column[0] for column in cursor.description]
        movie_dict = [dict(zip(columns, row)) for row in rows]

        # Access genres from g object
        genres_dict = g.genres

        movie_count = 0

        for movie in movie_dict:
            genres = []
            directors = []
            db_genres = cursor.execute("SELECT * FROM movie_genres WHERE movie_id = ?", (movie["movie_id"],)).fetchall()
            db_directors = cursor.execute("SELECT * FROM movie_directors WHERE movie_id = ?", (movie["movie_id"],)).fetchall()
            for genre in db_genres:
                genre_id = genre[1]
                genres.append(genres_dict.get(genre_id))
            for director in db_directors:
                director_name = director[2]
                directors.append(director_name)
            movie_dict[movie_count]["genres"] = genres
            movie_dict[movie_count]["directors"] = directors
            movie_count += 1
            

        return render_template("searched.html", movies=movie_dict)

    return render_template("research.html")

@app.route("/profile")
def profile():

    user_id = session["user_id"]
    cursor = get_db()
    watchlist = cursor.execute("SELECT * FROM movies JOIN watchlist ON movies.movie_id = watchlist.movie_id WHERE watchlist.user_id = ?", (user_id, )).fetchall()
    columns = [column[0] for column in cursor.description]
    watchlist_dict = [dict(zip(columns, movie)) for movie in watchlist]

    watchlist_count = 0

    for movie in watchlist_dict:
        directors = []
        db_directors = cursor.execute("SELECT * FROM movie_directors WHERE movie_id = ?", (movie["movie_id"],)).fetchall()
        for director in db_directors:
            director_name = director[2]
            directors.append(director_name)
        watchlist_dict[watchlist_count]["directors"] = directors
        watchlist_count += 1

    liked = cursor.execute("SELECT * FROM movies JOIN liked ON movies.movie_id = liked.movie_id WHERE liked.user_id = ?", (user_id, )).fetchall()
    columns = [column[0] for column in cursor.description]
    liked_dict = [dict(zip(columns, movie)) for movie in liked]

    liked_count = 0

    for movie in liked_dict:
        directors = []
        db_directors = cursor.execute("SELECT * FROM movie_directors WHERE movie_id = ?", (movie["movie_id"],)).fetchall()
        for director in db_directors:
            director_name = director[2]
            directors.append(director_name)
        liked_dict[liked_count]["directors"] = directors
        liked_count += 1

    disliked = cursor.execute("SELECT * FROM movies JOIN disliked ON movies.movie_id = disliked.movie_id WHERE disliked.user_id = ?", (user_id, )).fetchall()
    columns = [column[0] for column in cursor.description]
    disliked_dict = [dict(zip(columns, movie)) for movie in disliked]

    disliked_count = 0

    for movie in disliked_dict:
        directors = []
        db_directors = cursor.execute("SELECT * FROM movie_directors WHERE movie_id = ?", (movie["movie_id"],)).fetchall()
        for director in db_directors:
            director_name = director[2]
            directors.append(director_name)
        disliked_dict[disliked_count]["directors"] = directors
        disliked_count += 1
    

    return render_template("profile.html", watchlist=watchlist_dict, liked=liked_dict, disliked=disliked_dict)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", username="incorrect", password="correct", match="correct")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", username="correct", password="incorrect", match="correct")

        # Query database for username
        cursor = get_db()
        rows = cursor.execute(
            "SELECT * FROM users WHERE user = ?", (request.form.get("username"),)
        ).fetchone()

        # Ensure username exists and password is correct
        if rows is None or not check_password_hash(
            rows[2], request.form.get("password")
        ):
            return render_template("login.html", username="correct", password="correct", match="incorrect")

        # Remember which user has logged in
        session["user_id"] = rows[0]

        # Redirect user to home page
        return redirect("/")
    return render_template("login.html", username="correct", password="correct", match="correct")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        if not request.form.get("username"):
            return render_template("signup.html", username="incorrect", used="correct", password="correct", confirmation="correct", pw_format="correct")

        # Query database for username
        cursor = get_db()
        rows = cursor.execute(
            "SELECT * FROM users WHERE user = ?", (request.form.get("username"),)
        ).fetchall()

        # Ensure username not exists
        if len(rows) == 1:
            return render_template("signup.html", username="correct", used="incorrect", password="correct", confirmation="correct", pw_format="correct")

        # Ensure username was submitted
        if not request.form.get("password"):
            return render_template("signup.html", username="correct", used="correct", password="incorrect", confirmation="correct", pw_format="correct")

        # Ensure password given has the good format
        password = request.form.get("password")
        if not check_pw(password):
            return render_template("signup.html", username="correct", used="correct", password="correct", confirmation="correct", pw_format="incorrect")
        if not request.form.get("confirmation") or request.form.get("confirmation") != password:
            return render_template("signup.html", username="correct", used="correct", password="correct", confirmation="incorrect", pw_format="correct")


        hashed_pw = generate_password_hash(password)
        cursor.execute("INSERT INTO users (user, password) VALUES (?, ?)", (username, hashed_pw))
        user_id = cursor.lastrowid
        cursor.connection.commit()
        session["user_id"] = user_id
        return redirect("/") #Change to /home when its done
    return render_template("signup.html", username="correct", used="correct", password="correct", confirmation="correct", pw_format="correct")

@app.route("/logout")
def logout():
    # Clear the session variables
    session.clear()
    return redirect("/")


