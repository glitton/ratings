"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect, request,
                   flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "suefgbkuzyfbaidfhalieufhaefh"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # a = jsonify([1,3])
    # return a
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/users/<user_id>")
def show_user_info(user_id):
    """Shows information about the user."""

    user = User.query.filter(User.user_id == user_id).first()
    user_ratings = user.ratings

    return render_template("/user_info.html", user=user,
                            ratings=user_ratings)    


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<movie_id>")
def show_movie_info(movie_id):
    """Shows information about the movie."""

    movie = Movie.query.filter(Movie.movie_id == movie_id).first()
    movie_ratings = movie.ratings

    return render_template("/movie_info.html", movie=movie,
                            ratings=movie_ratings)


@app.route("/add-rating", methods=["POST"])
def add_rating_to_db():
    """Add user rating to database"""

    user_rating = request.form.get("rating")
    user_id = session["logged_in_user_id"]
    movie_id = request.form.get("movie_id")

    # Check to see if rating already exists in the database
    # If it's not there, .first() will return None
    rating = Rating.query.filter(Rating.user_id == user_id, 
                                 Rating.movie_id == movie_id).first()

    # If the rating does not already exist, add it to the database
    if not rating:
        rating = Rating(user_id=user_id, movie_id=movie_id, score=user_rating)
        db.session.add(rating)
        db.session.commit()
        flash("Added rating.")
        return redirect("/movies/" + movie_id)

    #  If the rating already exists in the database for that user
    #  update the rating to reflect the new score
    else:
        rating.score = user_rating
        db.session.commit()
        flash("Updated rating.")
        return redirect("/movies/" + movie_id)


@app.route("/register", methods=["GET"])
def show_registration_form():
    """Show registration form"""

    return render_template("registration_form.html")
   

@app.route("/register", methods=["POST"])
def process_registration_form():
    """Process registration form"""

    user_email = request.form.get("email")
    user_password = request.form.get("password")

    user = User.query.filter(User.email == user_email).first()
    if not user:
        new_user = User(email=user_email, password=user_password)
        db.session.add(new_user)
        db.session.commit()
        session["logged_in_user_id"] = new_user.user_id
        flash("Successfully created new account! Welcome %s" % (user_email))
        return redirect("/")
    else:
        flash("Account already exists. Please log in")
        return redirect("/login")


@app.route("/login", methods=["GET"])
def show_login_form():
    """Show login form"""

    return render_template("login_form.html")


@app.route("/login", methods=["POST"])
def process_login_form():
    """Process login form"""

    user_email = request.form.get("email")
    user_password = request.form.get("password")

    user = User.query.filter(User.email == user_email).first()
    # If the user does not exist, we'll send them to the registration page
    if not user:
        flash("User does not exist. Please create an account")
        return redirect("/register")

    # Checks to see if password is correct
    if user.password != user_password:
        flash("Password incorrect, please try again.")
        return redirect("/login")
    else:
        session["logged_in_user_id"] = user.user_id
        flash("Successfully logged in as %s" % (user_email))
        return redirect("/users/" + str(user.user_id))


@app.route("/logout")
def logout_user():
    """Removes session and logs user out"""

    del session["logged_in_user_id"]
    flash("Successfully logged out.")

    return redirect("/")


 



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
