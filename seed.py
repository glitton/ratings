"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User, Movie, Rating
# from model import Rating
# from model import Movie

from model import connect_to_db, db
from server import app
from datetime import datetime


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""
    print "Movies"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate movies
    Movie.query.delete()

    # Read u.item file and insert data
    for row in open("seed_data/u.item"):
        row = row.rstrip().split("|")
        movie_id = row[0]  # movie_id is the first item in each row
        
        # This step removes the movie year from each title
        movie_title = row[1].split(" ")
        movie_title.pop(-1)
        movie_title = " ".join(movie_title)

        # Converts string date to a datetime object
        released_at = row[2]
        if released_at:
            released_at = datetime.strptime(released_at, "%d-%b-%Y")
        else:
            released_at = None

        imdb = row[3]  # IMDB url is the 4th item in each row    

        # Instantiating the Movie object so we can add to our database
        movie = Movie(movie_id=movie_id,
                      title=movie_title,
                      released_at=released_at,
                      imdb_url=imdb)

        db.session.add(movie)  # Adds move to the database

    db.session.commit()  # Commits after all data has been added to the db


def load_ratings():
    """Load ratings from u.data into database."""
    print "Ratings"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate ratings
    Rating.query.delete()   

    # Read u.item file and insert data
    for row in open("seed_data/u.data"):
        row = row.rstrip().split("\t")
        user_id = row[0]  # user_id is the first item in each row
        
        movie_id = row[1]  # movie_id is the second item in each row

        score = row[2] # score is the third item in each row
        
        #Instantiating the Rating object so we can add to our database
        rating = Rating(user_id=user_id,
                        movie_id=movie_id,
                        score=score)

        db.session.add(rating)

    db.session.commit()  # Commits after all data has been added to the db 


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
