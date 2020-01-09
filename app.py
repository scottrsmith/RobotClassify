"""
**Introduction**
----------------
Robot Classify does stuff...

- GET /XXX
- GET /XXX-detail
- POST /XXX
- PATCH /XXX/<id>
- DELETE /XXX/<id>

With the following API permissions:
- `get:drinks-detail` (Barista and Manager)
- `post:drinks` (Manager)
- `patch:drinks` (Manager)
- `delete:drinks` (Manager)

"""

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv
from authlib.flask.client import OAuth

import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect
from flask import url_for, abort, session, jsonify, Blueprint, Request
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_cors import CORS


from six.moves.urllib.parse import urlencode

from functools import wraps
from jose import jwt
from urllib.request import urlopen


from forms import *
from models import *

import config


#----------------------------------------------------------------------------#
# Helper Functions
#    dump: print out the contents of an object
#----------------------------------------------------------------------------#

def dumpObj(obj, name='None'):
  print ('\n\nDump of object...{}'.format(name))
  for attr in dir(obj):
    print("    obj.%s = %r" % (attr, getattr(obj, attr)))

def dumpData(obj, name='None'):
  print ('\n\nDump of data...{}'.format(name))
  for attr in obj:
    print("    data.%s = %r" % (attr, obj[attr]))


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
CORS(app)


# CORS Headers

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Auth0 security setup


AUTH0_DOMAIN = 'dev-p35ewo73.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'robotclassify'


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = str(env.get(config.AUTH0_CALLBACK_URL))
AUTH0_CLIENT_ID = str(env.get(config.AUTH0_CLIENT_ID))
AUTH0_CLIENT_SECRET = str(env.get(config.AUTH0_CLIENT_SECRET))
AUTH0_DOMAIN = str(env.get(config.AUTH0_DOMAIN))
AUTH0_BASE_URL = 'https://dev-p35ewo73.auth0.com'
AUTH0_AUDIENCE = str(env.get(config.AUTH0_AUDIENCE))


oauth = OAuth(app)

auth0= oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

#----------------------------------------------------------------------------#
# auth setup
#----------------------------------------------------------------------------#



# Auth Header

# def get_token_auth_header():
#   raise Exception('Not Implemented')

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """

    # auth = request.headers.get('Authorization', None)
    auth = session.get('token', None)
    

    if not auth:
        abort(401, 'Authorization header is expected.')

    if 'access_token' not in auth:
        abort(401, 'Token not found.')

    elif auth['token_type'] != 'Bearer':
        abort(401, 'Authorization header must start with "Bearer".')

    return auth['access_token']


# ----------------------------------------------------------------------------#
#  Raise an AuthError if permissions are not included in the payload
#
#  INPUTS
#     permission: string permission (i.e. 'post:admin')
#        payload: decoded jwt payload
# ----------------------------------------------------------------------------#

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        abort(400, 'Permissions not included in JWT.')

    if permission not in payload['permissions']:
        abort(401, 'Permission not found.')

    return True


# ----------------------------------------------------------------------------#
# verify_decode_jwt(token) method
# INPUTS
#    token: a json web token (string)
# Returns:
#     decoded payload
# ----------------------------------------------------------------------------#

def verify_decode_jwt(token):
    jsonurl = urlopen('https://' + AUTH0_DOMAIN + '/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}

    if 'kid' not in unverified_header:
        raise AuthError({'code': 'invalid_header',
                        'description': 'Authorization malformed.'}, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e'],
                }
    if rsa_key:
        try:
            payload = jwt.decode(token, rsa_key, algorithms=ALGORITHMS,
                                 audience=API_AUDIENCE,
                                 issuer='https://' + AUTH0_DOMAIN + '/')

            return payload
        except jwt.ExpiredSignatureError:

            abort(401, 'Token expired.')
        except jwt.JWTClaimsError:

            abort(401,
                  'Incorrect claims. Please, check the audience and issuer.'
                  )
        except Exception:

            abort(400, 'Unable to parse authentication token.')

    abort(400, 'Unable to find the appropriate key.')


# ----------------------------------------------------------------------------#
#  @requires_auth(permission) decorator method
#  INPUTS
#     permission: string permission (i.e. 'post:admin')
#
# ----------------------------------------------------------------------------#

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        
        @wraps(f)
        def wrapper(*args, **kwargs):

            
            # Save the URL 'state' for redirects
            session['state'] = request.full_path

            if config.PROFILE_KEY not in session:
                return redirect('/login')
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except Exception:
                abort(401)
            check_permissions(permission, payload)
            
            return f( *args, **kwargs)
            #return f(payload, *args, **kwargs)
        return wrapper

    return requires_auth_decorator




#----------------------------------------------------------------------------#
# Filters..
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
#----------------------------------------------------------------------------
#  Account and Session security
#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    
    session[config.JWT_PAYLOAD] = userinfo
    session[config.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    session['token'] = auth0.token

    # Check to see of the redirected URL was saved to redirect back after login
    if 'state' in session:
        return redirect(session['state'])
    else:
        return redirect('/')


@app.route('/login')
def login():
    # print (dumpObj(session))
    # print (dumpData(session))
    print ('AUTH0_CALLBACK_URL=',AUTH0_CALLBACK_URL)
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))



#----------------------------------------------------------------------------
# Home Page
#----------------------------------------------------------------------------
@app.route('/')
def index():
    """
        **Home Page**

        Display the home page

        - Sample Call::

            curl -X GET http://localhost:5000/
0

        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

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
@requires_auth('get:admin')
def venues():
    """
        **List Venues**

        Display a list of venues

        - Sample Call::

            curl -X GET http://localhost:5000/venues


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>



        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """  
    # List the venues grouped by city/state
    uniqueCityStates = Venue.query.distinct(Venue.city, Venue.state).all()
    data = [cs.filterCityState for cs in uniqueCityStates]
    return render_template('pages/venues.html', areas=data)


#  ----------------------------------------------------------------
#  Search Venues
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
@requires_auth('get:admin')
def search_venues():
    """
        **Search Venues**

        Display the hoime page

        - Sample Call::

            curl -X GET http://localhost:5000/venues/search


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>



        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """ 
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
@requires_auth('get:admin')
def show_venue(venue_id):
    """
        **Venue**

        Display a single venue

        - Sample Call::

            curl -X GET http://localhost:5000/venues/<id>


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """
    # Query and show a single venue
    theVenue = Venue.query.get(venue_id)
    data = theVenue.venueShowsCount
    return render_template('pages/show_venue.html', venue=data)



#----------------------------------------------------------------------------
#  Create Venue
#----------------------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
@requires_auth('get:admin')
def create_venue_form():
    """
        **Create Venue**

        Create a venue

        - Sample Call::

            curl -X GET http://localhost:5000/venues/create


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

    # Display an empty venue form for create
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


# Process the create request
@app.route('/venues/create', methods=['POST'])
@requires_auth('post:admin')
def create_venue_submission():
    """
        **Create Venue**

        Create Venue

        - Sample Call::

            curl -X POST http://localhost:5000/venues/create


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """
 
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
@requires_auth('get:admin')
def delete_venue(venue_id):
    """
        **Delete Venue**

        Delete Venue

        - Sample Call::

            curl -X GET http://localhost:5000/venues/<venue_id>/delete


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

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
@requires_auth('get:admin')
def edit_venue_submission(venue_id):
    """
        **Edit Venue**

        Edit Venue

        - Sample Call to edit::

            curl -X POST http://localhost:5000/venues/<int:venue_id>/edit

       - Sample Call to display::

            curl -X GET http://localhost:5000/venues/<int:venue_id>/edit



        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

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
@requires_auth('get:admin')
def artists():
    """
        ** List Artists**

        List Artists

        - Sample Call::

            curl -X GET http://localhost:5000/artists


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)



#  ----------------------------------------------------------------
#  Search Artists
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
@requires_auth('get:admin')
def search_artists():
    """
        **Search Artists**

        Search Artists

        - Sample Call::

            curl -X GET http://localhost:5000/artists/search 


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

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
@requires_auth('get:admin')
def show_artist(artist_id):
    """
        **Show single Artistt**

        Show single artist details

        - Sample Call::

            curl -X GET http://localhost:5000/artists/<int:artist_id>


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

    theArtist = Artist.query.get(artist_id)
    data = theArtist.artistShowsCount
    return render_template('pages/show_artist.html', artist=data)


#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
@requires_auth('get:admin')
def create_artist_form():
    """
        **Get Artist**

        Display an Artist's info

        - Sample Call::

            curl -X GET http://localhost:5000/artists/create


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

    # Display an empty artist form for create
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form) 


@app.route('/artists/create', methods=['POST'])
@requires_auth('post:admin')
def create_artist_submission():
    """
        **Create an Artist**

        Create an Artist

        - Sample Call::

            curl -X POST http://localhost:5000/artists/create


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

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
@requires_auth('get:admin')
def edit_artist_submission(artist_id):
    """
        **Edit Artists Information**

        Edit Artists Information

        - Sample Call to display::

            curl -X GET http://localhost:5000/artists/<int:artist_id>/edit


        - Sample Call to edit::

            curl -X POST http://localhost:5000/artists/<int:artist_id>/edit


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

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
@requires_auth('get:admin')
def delete_artist(artist_id):
    """
        **Delete an artist**

        Delete an artist

        - Sample Call::

            curl -X GET http://localhost:5000/artists/<artist_id>/delete


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

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
@requires_auth('get:admin')
def shows():
    """
        **List of Shows**

        Display a list of shows

        - Sample Call::

            curl -X POST http://localhost:5000/shows


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

    data = Show.query.all()
    return render_template('pages/shows.html', shows=data)



#----------------------------------------------------------------------------
#  Create Show
#----------------------------------------------------------------------------
@app.route('/shows/create', methods=['GET'])
@requires_auth('get:admin')
def create_shows():
    """
        **Show a show**

        Display a show

        - Sample Call::

            curl -X GET http://localhost:5000/shows/create


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
@requires_auth('get:admin')
def create_show_submission():
    """
        **Create Show submission**

        Create a new show submission

        - Sample Call::

            curl -X POST http://localhost:5000/shows/create


        - Expected Success Response::

            HTTP Status Code: 200

            <!doctype html>...</html>


        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401: Authorization header is expected.",
                "error": 401,
                "message": "Unauthorized",
                "success": false
            }

    """

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

@app.errorhandler(400)
def bad_request(error):
    return (jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request',
        'description': str(error),
        }), 400)

@app.errorhandler(401)
def unauthorized_user(error):
    return (jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized',
        'description': str(error),
        }), 401)



@app.errorhandler(405)
def not_found(error):
    return (jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed',
        'description': str(error),
        }), 405)


@app.errorhandler(422)
def unprocessable(error):
    return (jsonify({
        'success': False,
        'error': 422,
        'message': 'Unprocessable',
        'description': str(error),
        }), 422)



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
