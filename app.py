#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *


#----------------------------------------------------------------------------#
# Helper Functions
#    dump: print out the contents of an object
#----------------------------------------------------------------------------#

def dumpObj(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

def dumpData(obj):
  for attr in obj:
    print("data.%s = %r" % (attr, obj[attr]))


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# open/Connect to a local postgresql database
db = connectToDB(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------
# Controllers.
#----------------------------------------------------------------------------


#----------------------------------------------------------------------------
# Home Page
#----------------------------------------------------------------------------
@app.route('/')
def index():
  return render_template('pages/home.html')


#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
#  Venues
#----------------------------------------------------------------------------
#----------------------------------------------------------------------------


#----------------------------------------------------------------------------
#  List Venues
#----------------------------------------------------------------------------
@app.route('/venues')
def venues():
  
  # List the venues grouped by city/state
  uniqueCityStates = Venue.query.distinct(Venue.city, Venue.state).all()
  data = [cs.filterCityState for cs in uniqueCityStates]
  return render_template('pages/venues.html', areas=data)


#  ----------------------------------------------------------------
#  Search Venues
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
 
  search_term = request.form.get('search_term', None )

  # Search for an included string, case sensitive
  searchResults = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  count_items = len(searchResults)

  # List and format the search results using venueShowCount property
  response = {"count": count_items, 
              "data": [v.venueShowsCount for v in searchResults]}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))



#  ----------------------------------------------------------------
#  Show single Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # Query and show a single venue
  theVenue = Venue.query.get(venue_id)
  data = theVenue.venueShowsCount
  return render_template('pages/show_venue.html', venue=data)



#----------------------------------------------------------------------------
#  Create Venue
#----------------------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  # Display an empty venue form for create
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

# Process the create request
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
 
  form = VenueForm(request.form)
  venue = Venue()
  
  
  if form.validate():
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + form['name'].data + ' was successfully listed!')
  else:
      flash('An error occurred. Venue ' + form['name'].data + ' could not be listed.')
  
  return render_template('pages/home.html')


#----------------------------------------------------------------------------
#  Delete Venue
#----------------------------------------------------------------------------
@app.route('/venues/<venue_id>/delete', methods=['get'])
def delete_venue(venue_id):
  try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
  except:
      db.session.rollback()
      flash('Oh Snap! Venue with ID of "' + venue_id + '" was not deleted')
      return redirect(url_for('index'))

  flash('Venue with ID of "' + venue_id + '" was successfully deleted!')
  return redirect(url_for('index'))

# ----------------------------------------------------------------
#  Edit Venue
# ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET','POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)

  if request.method=='POST':
    if form.is_submitted() and form.validate():
      # form data is posted to venue object for update
      try:
        form.populate_obj(venue)
        db.session.commit()
        # on successful db update, flash success
        flash('Venue ' + form['name'].data + ' was successfully Updated!')
      except:
        db.session.rollback()
        flash('An DB error occurred. Venue ' + form['name'].data + ' could not be Updated.')
    else:
      print (form.errors.items())
      flash('An error occurred. Venue ' + form['name'].data + ' could not be Updated.')

    return redirect(url_for('show_venue', venue_id=venue_id))
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)



#  ----------------------------------------------------------------
#  List Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)



#  ----------------------------------------------------------------
#  Search Artists
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', None )
  searchResults = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  count_items = len(searchResults)
  response = {"count": count_items, 
              "data": [a.artistShowsCount for a in searchResults]}

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#  ----------------------------------------------------------------
#  Show single Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  theArtist = Artist.query.get(artist_id)
  data = theArtist.artistShowsCount
  return render_template('pages/show_artist.html', artist=data)


#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  # Display an empty artist form for create
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form) 


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form = ArtistForm(request.form)
  artist = Artist()
  
  if form.validate():
      form.populate_obj(artist)
      try:
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
      except:
        db.session.rollback()
        flash('An DB error occurred. Artist ' + form['name'].data + ' could not be listed.')
  else:
      print (form.errors.items())
      flash('An error occurred. Artist ' + form['name'].data + ' could not be listed.')
  return render_template('pages/home.html')


#  ----------------------------------------------------------------
#  Edit Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET','POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)

  if request.method=='POST':
    if form.is_submitted() and form.validate():
      # The form is submitted and valid, get the form data into the artist object for updates
      form.populate_obj(artist)
      try:
        db.session.commit()
        # on successful db update, flash success
        flash('Artist ' + form['name'].data + ' was successfully Updated!')
      except:
        db.session.rollback()
        flash('An database error occurred. Artist ' + form['name'].data + ' could not be Updated.')
    else:
      print (form.errors.items())
      flash('An error occurred. Artist ' + form['name'].data + ' could not be Updated.')

    return redirect(url_for('show_artist', artist_id=artist_id))
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)



#----------------------------------------------------------------------------
#  Delete Artist
#----------------------------------------------------------------------------
@app.route('/artists/<artist_id>/delete', methods=['get'])
def delete_artist(artist_id):
  try:
      Artist.query.filter_by(id=artist_id).delete()
      db.session.commit()
  except:
      db.session.rollback()
      flash('Oh Snap! Artist with ID of "' + artist_id + '" was not deleted')
      return redirect(url_for('index'))


  flash('Artist with ID of "' + artist_id + '" was successfully deleted!')
  return redirect(url_for('index'))


#  ----------------------------------------------------------------
#  ----------------------------------------------------------------
#  SHOWS
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------


#  ----------------------------------------------------------------
#  List Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)



#----------------------------------------------------------------------------
#  Create Show
#----------------------------------------------------------------------------
@app.route('/shows/create', methods=['GET'])
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # create the form and show record object
  form = ShowForm()
  show = Show()
  
  if form.validate():
      form.populate_obj(show)
      try:
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
      except:
        db.session.rollback()
        flash('There was an database error submitting show')
  else:
      flash('There was an error submitting show')
  
  return render_template('pages/home.html')




#----------------------------------------------------------------------------
#  error handlers and other support code
#----------------------------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')



#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
