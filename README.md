# Popcorn Picks
#### Video Demo:  https://youtu.be/_1aIB8_GFTU
#### Description:
This Webapp is a bank of movies. I've imported data from The Movie Database (https://www.themoviedb.org). 40 movies per year since 1960, with title, release date, runtime, genres, directors, overview and ratings.
The goal of this webapp was to look for movies in this imported db, according to certain criteria.
Each user have its own watchlist, liked list and disliked list.
For this project, I've used different languages:
- Python, Flask and Jinja: for the interactivity of the Web App
- HTML, CSS, JS: for the look of the page
- SQLite: for the construction of the database
#### Explanation of each file:
In the database folder, there is the scripts that permit me to build my database, using the API from THDM.
In the static folder, I got my background image for my home page and the different .css sheets. I have not used bootstrap or any technologies, just vanilla CSS.
In the tempates folder, there are my html pages.
The app.py defines all the routes of my App.
In the helpers.py, I have two functions: one to require a login, and one to check if the password is strong enough.
In the requirements.txt, all the updates and libraries required for the app.
In the movies.db, there is my database which contains 8 tables:
- users: links a user_id to a hased password
- movies: contains all the data from each movies (title, runtime, rating, release date, overview and poster path)
- genres: links all genres to an id
- movie-genres: links movies to its different genres
- movie-directors: links movies to its directors
- watchlist: links a user id and its watchlist
- liked: links a user id and its liked movies
- disliked: links a user id and its disliked movies
#### What did I do this particular project?
I wanted to create a complete project. A webapp seemed to be a good solution because I had to handle Python, HTML, CSS (without bootstrap, I wanted to try vanilla CSS), (a bit of) JS and a Database.
I love watching movies, so to build a webapp on something I personnally enjoy seemed like a good idea.
#### What did I learned?
Building something from scratch is complicated. I found the PSET from CS50 not too difficult, even without a great background in programming, because I've had some context in what to build.
Here, it was different. Everything need to come from me and online resources. No context, no template. So I've learned about VS Code, Github.
After this project, I feel good about Jinja and Python for a web app, but I don't really enjoy HTML and CSS. Web app is probably not for me. You'll see how it is not beautiful. But it works as intended.
I also learned a lot on how to use database and SQLITE.
#### What to improve?
First, the design would need to be better. Then, I would have liked to have a recommendation algorithm based on the lists of the user. I would also have liked a system of ratings inside the webapp, where each user can rate and review a movie.
