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
import os
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
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
from flask_modus import Modus
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_cors import CORS
from flask_session import Session
from flask_uploads import UploadSet, configure_uploads, DATA, IMAGES, patch_request_class, send_from_directory
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import pandas as pd
import pickle

# Machine learning libraries
from xgboost import XGBClassifier
from mlLib.project import autoEvaluateClassifier, autoFlaskEvaluateClassifier

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

def makePickList(columns):
    return [(c,c) for c in columns]


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
#modus = Modus(app)

# app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
moment = Moment(app)
app.secret_key = config.SECRET_KEY
app.config.from_object('config')
#app.config['WTF_CSRF_CHECK_DEFAULT'] = False
app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken', 'X-CSRF-Token']

# define file uploadss
configure_uploads(app, config.dataFiles)
patch_request_class(app, 1024 * 1024)  # set maximum file size to 1 mb
app.secret_key = config.SECRET_KEY
#app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_TYPE'] = 'filesystem'

# Setup for mllib
os.environ['KMP_DUPLICATE_LIB_OK']='True'


# open/Connect to a local postgresql database
db = connectToDB(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
# CORS(app, supports_credentials=True)
CORS(app)
Session(app)



# CORS Headers

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS,PATCH')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Auth0 security setup




def getEnvVars(first=None, second=None, third=None):
    # print ('first={}, second={}, third={}'.format(first,second,third))
    if first is None:
        if second is None:
            return third
        else:
            return second
    else:
        return first
    
# Get environment variables, priority order: OS Env, .env, config.opy
AUTH0_CALLBACK_URL = getEnvVars(os.getenv('AUTH0_CALLBACK_URL'), \
                                env.get('AUTH0_CALLBACK_URL'), \
                                config.AUTH0_CALLBACK_URL)

AUTH0_CLIENT_ID = getEnvVars(os.getenv('AUTH0_CLIENT_ID'), \
                                env.get('AUTH0_CLIENT_ID'), \
                                config.AUTH0_CLIENT_ID)

AUTH0_DOMAIN = getEnvVars(os.getenv('AUTH0_DOMAIN'), \
                                env.get('AUTH0_DOMAIN'), \
                                config.AUTH0_DOMAIN)

AUTH0_AUDIENCE = getEnvVars(os.getenv('AUTH0_AUDIENCE'), \
                                env.get('AUTH0_AUDIENCE'), \
                                config.AUTH0_AUDIENCE)


AUTH0_CLIENT_SECRET = getEnvVars(os.getenv('AUTH0_CLIENT_SECRET'), \
                                env.get('AUTH0_CLIENT_SECRET'), \
                                config.AUTH0_CLIENT_SECRET)


AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN


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

            # Save the URL 'redirect_url' 
            session['redirect_url'] = request.path
            session.modified = True
                       
            if config.PROFILE_KEY not in session:
                return redirect('/login')

            return f(None, *args, **kwargs)
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
    tries = 0
    failed = False
    while tries < 10:
        try:
            auth0.authorize_access_token()
            tries = 10
            failed = False
        except:
            tries += 1
            failed = True
    if failed:
        abort(500)

    resp = auth0.get('userinfo')
    userinfo = resp.json()
    
    session[config.JWT_PAYLOAD] = userinfo
    session[config.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    session['account_id'] = userinfo['sub']
    #dumpObj(session, 'Dump of Session afer callback')
    #session['token'] = auth0.token
    #session.modified = True

    # Check to see of the redirected URL was saved to redirect back after login
    if 'redirect_url' in session:
        return redirect(session.get('redirect_url'))
    else:
        return redirect('/')


@app.route('/login')
def login():
    flash('You are now logged in!')
    session['request_uri'] = AUTH0_CALLBACK_URL
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
    flash('You are now logged out')
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


#----------------------------------------------------------------------------
#  List Projects
#----------------------------------------------------------------------------
@app.route('/projects', methods=['GET'])
@requires_auth('get:project')
def projects(payload):
    """
        **List Proejcts**

        Display a list of projects
        - Sample Call::

            curl -X GET http://localhost:5000/projects


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
    # List the projects 
    projectList = Project.query.filter_by(account_id=session['account_id']).all()
    data = [p.projectPage for p in projectList]
    return render_template('pages/projects.html', projects=data, count=len(data))



#  ----------------------------------------------------------------
#  Show single project
#  ----------------------------------------------------------------
@app.route('/projects/<int:project_id>', methods=['GET'])
@requires_auth('get:project')
def show_project(payload, project_id):
    """
        **Project**

        Display a single projects

        - Sample Call::

            curl -X GET http://localhost:5000/projects/<id>


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
    # Query and show a single project
    project = Project.query.filter(Project.id == project_id).one_or_none()
    if project is None:
        abort(404)

    data = project.projectPage
    return render_template('pages/show_project.html', project=data)



# upload and parse the file data
def populateProjectFiles(project, form):
    # Get the filenames
    project.trainingFile = config.dataFiles.save(form.trainingFile.data)
    project.testingFile = config.dataFiles.save(form.testingFile.data)

    print ('Populate proejct files.project.trainingFile =',project.trainingFile, project.testingFile)
    #dumpObj(form.trainingFile.data,'form.trainingFile.data')

    # pickle the testing/training data for later runs
    # The data will be in the form of a
    
    training=pd.read_csv(app.config['UPLOADED_DATA_DEST'] + '/' + project.trainingFile, 
                            low_memory=False)
    testing=pd.read_csv(app.config['UPLOADED_DATA_DEST'] + '/' + project.testingFile, 
                            low_memory=False)
    project.savedTrainingFile = pickle.dumps(training)
    project.savedTestingFile = pickle.dumps(testing)

    # Last, get the column namesto be saved (from the training file)
    # These are to be used later in the runs to help select attributes.
    project.columns = [c for c in training.columns.tolist()]


#  ----------------------------------------------------------------
#  Create project
#  ----------------------------------------------------------------

@app.route('/projects/create', methods=['POST', 'GET'])
@requires_auth('post:project')
def create_projects_submission(payload):
    """
        **Create Project**

        Create Project

        - Sample Call::

            curl -X POST http://localhost:5000/project/create


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
    

    form = ProjectForm() # request.form
    
    if form.validate_on_submit():
        project = Project()
        form.populate_obj(project)

        # load the files and column data into the project record
        populateProjectFiles(project, form)

        # Now insert
        project.insert()

        # on successful db insert, flash success
        flash('Project ' + form['name'].data + ' was successfully added!')
    else:
        return render_template('forms/new_project.html', form=form)

    return render_template('pages/index.html')


# ----------------------------------------------------------------
#  Edit Project
# ----------------------------------------------------------------
@app.route('/projects/<int:project_id>/edit', methods=['GET','POST','PATCH'])
@csrf.exempt
@requires_auth('patch:project')
def edit_project_submission(payload, project_id):
    """
        **Edit Project**

        Edit Project

        - Sample Call to edit::

            curl -X POST http://localhost:5000/projects/<int:project_id>/edit

       - Sample Call to display::

            curl -X GET http://localhost:5000/projects/<int:project_id>/edit

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

    project = Project.query.filter(Project.id == project_id).one_or_none()
    if project is None:
        abort(404)
    form = ProjectFormEdit(obj=project)
    

    if request.method=='POST':
      if form.is_submitted() and form.validate():
        # form data is posted to venue object for update
        form.populate_obj(project)

        # load the files and column data into the project record
        # populateProjectFiles(project, form)

        project.update()
        # on successful db update, flash success
        
        flash('Project ' + form['name'].data + ' was successfully Updated!')

        return redirect(url_for('show_project', project_id=project_id))

        #except:
        #  db.session.rollback()
        #  flash('An DB error occurred. Project ' + form['name'].data + ' could not be Updated.')
      else:
        print (form.errors.items())
        flash('An error occurred. Project ' + form['name'].data + ' could not be Updated.')

      return redirect(url_for('show_project', project_id=project_id))
    
    return render_template('forms/edit_project.html', form=form, project=project)



#----------------------------------------------------------------------------
#  Delete Project
#----------------------------------------------------------------------------
@app.route('/projects/<project_id>/delete', methods=['GET','DELETE'])
@requires_auth('delete:project')
def delete_project(payload, project_id):
    """
        **Delete Project**

        Delete Project

        - Sample Call::

            curl -X GET http://localhost:5000/project/<project_id>/delete


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
        Project.query.filter_by(id=project_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        flash('Oh Snap! Project with ID of "' + project_id + '" was not deleted')
        return redirect(url_for('index'))

    flash('Project with ID of "' + project_id + '" was successfully deleted!')
    return redirect(url_for('index'))


# ----------------------------------------------------------------
# ----------------------------------------------------------------
#  R U N S
# ----------------------------------------------------------------
# ----------------------------------------------------------------


#  ----------------------------------------------------------------
#  Show single run
#  ----------------------------------------------------------------
@app.route('/runs/<int:run_id>', methods=['GET'])
@requires_auth('get:run')
def show_run(payload, run_id):
    """
        **Runs**

        Display a single run

        - Sample Call::

            curl -X GET http://localhost:5000/runs/<id>


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
    # Query and show a single project
    run = Run.query.filter(Run.id == run_id).one_or_none()
 
    if run is None:
        abort(404)


    if isinstance(run.results, type(None)):
        flash ('No Run Results for '+run.name)
        redirect(url_for('show_project', project_id=run.Project.id))
    else:
        return render_template('pages/results.html', run=run, results=pickle.loads(run.results))
    


#----------------------------------------------------------------------------
#  Create Run
#----------------------------------------------------------------------------


# Process the create request
@app.route('/runs/create/<int:project_id>', methods=['GET','POST'])
@requires_auth('post:run')
def create_run_submission(payload, project_id):
    """
        **Create Run**

        Create Run

        - Sample Call::

            curl -X POST http://localhost:5000/run/create


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

    project = Project.query.filter(Project.id == project_id).one_or_none()
    if project is None:
        abort(404)
    form = RunForm()
    pickList = makePickList(project.columns)
    form.targetVariable.choices=pickList
    form.key.choices=pickList
    form.predictSetOut.choices=pickList
    
    if form.validate_on_submit():
        run = Run()
        form.populate_obj(run)
        run.project_id = project_id
        run.insert()
        # on successful db insert, flash success
        flash('Run ' + form['name'].data + ' was successfully added!')
    else:
        return render_template('forms/new_run.html', form=form)
        # flash('An error occurred. Run ' + form['name'].data + ' could not be added.')
    
    return redirect(url_for('show_project', project_id=project_id)) 


#----------------------------------------------------------------------------
#  Delete Runs
#----------------------------------------------------------------------------

@app.route('/runs/<int:run_id>/delete', methods=['GET','DELETE'])
@requires_auth('delete:run')
def delete_run(payload, run_id):
    run = Run.query.filter(Run.id == run_id).one_or_none()
    if run is None:
        abort(404)

    try:
        project_id = run.project_id
        run.delete()
    except:
        db.session.rollback()
        flash('Oh Snap! Run with ID of "' + str(run_id) + '" was not deleted')
        return redirect(url_for('show_project', project_id=project_id))

    flash('Run with ID of "' + str(run_id) + '" was successfully deleted!')
    return redirect(url_for('show_project', project_id=project_id)) 



# ----------------------------------------------------------------
#  Edit Runs
# ----------------------------------------------------------------
@app.route('/runs/<int:run_id>/edit', methods=['GET', 'POST', 'PATCH'])
@requires_auth('patch:run')
@csrf.exempt
def edit_run_submission(payload, run_id):
    """
        **Edit Run**

        Edit Run

        - Sample Call to edit::

            curl -X POST http://localhost:5000/runs/<int:run_id>/edit

       - Sample Call to display::

            curl -X GET http://localhost:5000/runs/<int:run_id>/edit



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
    run = Run.query.filter(Run.id == run_id).one_or_none()
    if run is None:
        abort(404)

    form = RunForm(obj=run)
    pickList = makePickList(run.Project.columns)
    form.targetVariable.choices=pickList
    form.key.choices=pickList
    form.predictSetOut.choices=pickList

    print (">>>>> request.method, form.is_submitted() , form.validate()",request.method, form.is_submitted() , form.validate())
    if request.method=='POST':
       
      if form.is_submitted() and form.validate():
        # form data is posted to venue object for update
        try:
          form.populate_obj(run)
          run.update()
          # on successful db update, flash success
          flash('Run ' + form['name'].data + ' was successfully Updated!')
        except:
          db.session.rollback()
          flash('An DB error occurred. Run ' + form['name'].data + ' could not be Updated.')
      else:
        print (form.errors.items())
        flash('An error occurred. Run ' + form['name'].data + ' could not be Updated.')

      return redirect(url_for('show_project', project_id=run.Project.id)) 
    
    return render_template('forms/edit_run.html', form=form, run=run)


# ----------------------------------------------------------------
#  Run ML training
# ----------------------------------------------------------------
@app.route('/train/<int:run_id>', methods=['GET'])
# requires_auth('post:train')
def run_submission(run_id):
    """
        **Exec Run**

        Run ML Training based upon run record attributes

        

        - Sample Call to display::

            curl -X POST http://localhost:5000/rutrainns/<int:run_id>



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

    run = Run.query.filter(Run.id == run_id).one_or_none()
    if run is None:
        abort(404)
   
    results = autoFlaskEvaluateClassifier(projectName=run.name,
                        trainingFile = run.Project.trainingFile,
                        testingFile = run.Project.testingFile,
                        trainingFileDF = run.Project.savedTrainingFile,
                        testingFileDF = run.Project.savedTestingFile,
                        targetVariable = run.targetVariable,
                        key = run.key,
                        predictSetOut=run.predictSetOut,

                        logFileOut = None,
                        transcriptFile = None,
                        trainingFileOut= None,
                        predictFileOut= None,

                        #logFileOut = './examples/resultsFile.csv',
                        #transcriptFile = './examples/AutoRunTransscript.txt',
                        #trainingFileOut='./examples/AutoReadyToTrain.csv',
                        #predictFileOut= './examples/ReadyToPredict.csv',
                        resultsFile='KaggleSubmitFile.csv',
                        modelList = run.modelList,
                        confusionMatrixLabels=None,
                        scoring = run.scoring,
                        setProjectGoals={'f1': (0.9,'>')},
                        runVerbose = 0,
                        recommendOnly=True,
                        basicAutoMethod = True,
                        skewFactor=40.0,
                        doExplore=True,
                        doTrain=True,
                        doPredict=True,
                        toTerminal=True
                        )
    run.results = pickle.dumps(results)
    run.update()

    return render_template('pages/results.html', run=run, results=results)



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
    return render_template('pages/index.html')


@app.route('/downloads/<path:filename>', methods=['GET'])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config['DOWNLOAD_DATA_DEST'])
    return send_from_directory(directory=uploads, filename=filename)


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
