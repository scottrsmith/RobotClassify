"""
**Introduction**

There are three models:
- Venue
- Artists
- Shows

"""

#----------------------------------------------------------------------------#
# Models..
#----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime

db = SQLAlchemy()

# ------- Commect and configure the connection to the DB ----------
def connectToDB(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    return db


# ----- Define the Venue Table Class
class Venue(db.Model):
    '''
    Venue
    A list of venues that artist can play at.
    '''
    
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    '''*id* is the auto assigned primary key.
        Type: Integer, Primary key. Required.
    '''
    name = db.Column(db.String)
    '''
    name, String, Required
    The name of the venue
    '''
    city = db.Column(db.String(120))
    '''
    City, String, Required
    The name of the city
    '''
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500), default='')
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #shows = db.relationship('Show', backref='Venue', lazy='dynamic', cascade="all, delete-orphan")
    
    #----------------------------------------------------------------------------#
    # serialize Venues
    #    - Return the venue with lists of upcomming/past shows plus counts
    #----------------------------------------------------------------------------#

    @property
    def venueShowsCount(self):
            return {
                'id': self.id,
                'name': self.name,
                'address': self.address,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'website': self.website,
                'genres': self.genres,
                'facebook_link': self.facebook_link,
                'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description,
                'image_link': self.image_link,
                'upcoming_shows_count': Show.query.filter(
                    Show.start_time >= datetime.datetime.now(),
                    Show.venue_id == self.id).count(),
                'upcoming_shows': [s.showDetails for s in Show.query.filter(
                    Show.start_time >= datetime.datetime.now(),
                    Show.venue_id == self.id)],
                'past_shows_count': Show.query.filter(
                    Show.start_time < datetime.datetime.now(),
                    Show.venue_id == self.id).count(),
                'past_shows': [s.showDetails for s in Show.query.filter(
                    Show.start_time < datetime.datetime.now(),
                    Show.venue_id == self.id)]
            }

    # query for list of venues by city/state
    @property
    def filterCityState(self):
            return {'city': self.city,
                    'state': self.state,
                    'venues': [v.venueShowsCount
                            for v in Venue.query.filter(Venue.city == self.city,
                                        Venue.state == self.state).all()]}
    
    @property
    def theShows(self):
            return {'artist_image_link': Artist.image_link,
                    'artist_name ': Artist.name,
                    'start_time': self.start_time}
   

class Artist(db.Model):
    '''
    Artist
    A list of Artist that can play at venues.
    '''
 
    __tablename__ = 'Artist'
 
    id = db.Column(db.Integer, primary_key=True)
    '''*id* is the auto assigned primary key.
        Type: Integer, Primary key. Required.
    '''
    
    name = db.Column(db.String)
    '''
    name, String, Required
    The name of the Artist
    '''
 
    city = db.Column(db.String(120))
    '''
    city, String, Required
    The city of the artist
    '''
 
    state = db.Column(db.String(120))
    '''
    state, String, Required
    The state of the artist
    '''
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500), default='')
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #shows = db.relationship('Show', cascade="all, delete-orphan")
    
    @property
    def artistShowsCount(self):
            return {
                'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'website': self.website,
                'genres': self.genres,
                'facebook_link': self.facebook_link,
                'seeking_venue': self.seeking_venue,
                'seeking_description': self.seeking_description,
                'image_link': self.image_link,
                'upcoming_shows_count': Show.query.filter(
                    Show.start_time >= datetime.datetime.now(),
                    Show.artist_id == self.id).count(),
                'upcoming_shows': [s.showDetails for s in Show.query.filter(
                    Show.start_time >= datetime.datetime.now(),
                    Show.artist_id == self.id)],
                'past_shows_count': Show.query.filter(
                    Show.start_time < datetime.datetime.now(),
                    Show.artist_id == self.id).count(),
                'past_shows': [s.showDetails for s in Show.query.filter(
                    Show.start_time < datetime.datetime.now(),
                    Show.artist_id == self.id)]
            }


# Define the show class
# Show records are dependent upon their parent records of venue and artist IDs. 
# There can be no Show records on their own
class Show(db.Model):
    '''
    Show
    A list of Shows for venues and artists.
    '''
  
    __tablename__ = 'Show'
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    '''
    venue_id, Integer, Required, part of the primary key
    The auto-assigned id of the venue
    '''
 
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    '''
    artist_id, Integer, Required, part of the primary key
    The auto-assigned id of the artist
    '''

    start_time = db.Column(db.DateTime, primary_key=True, nullable=False)
    Venue = db.relationship('Venue', backref=db.backref('Shows', cascade='all, delete-orphan'))
    Artist = db.relationship('Artist', backref=db.backref('Shows', cascade='all, delete-orphan'))


    @property
    def venue_name(self):
        return self.Venue.name

    @property
    def artist_name (self):
        return self.Artist.name

    @property
    def artist_image_link (self):
        return self.Artist.image_link

    @property
    def start_time_str (self):
        return self.start_time.strftime("%Y-%m-%dT%H:%M:%S")

    # Show the expanded details on the show records (getting venue and artist names & links)
    @property
    def showDetails(self):
        return {"artist_id": self.Artist.id,
                "artist_name": self.Artist.name,
                "artist_image_link": self.Artist.image_link,
                "venue_id": self.Venue.id,
                "venue_name": self.Venue.name,
                "venue_image_link": self.Venue.image_link,
                "start_time": self.start_time_str
                }
