#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Introduction
============

RobotClassify has a number of APIs that are under RBAC control. These APIs
generally return HTML data (web pages) for human interaction. These APIs
can also be called machine-to-machine.

"""

# ---------------------------------------------------------------------------#
# Imports
# ---------------------------------------------------------------------------#

import os
import json
from os import environ as env
# from werkzeug.exceptions import HTTPException
# from werkzeug.utils import secure_filename
from dotenv import load_dotenv, find_dotenv
from authlib.integrations.flask_client import OAuth

# import dateutil.parser
# import babel
# System libraries
import sys
import pandas as pd
import pickle
import http.client

# Flask
from flask import Flask, render_template, request, Response, flash, \
    redirect, make_response, send_from_directory
from flask import url_for, abort, session, jsonify, Blueprint, Request
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_wtf import Form
from flask_cors import CORS

from flask_wtf.file import FileField, FileRequired, FileAllowed

# Machine learning libraries
from xgboost import XGBClassifier
from mlLib.project import autoFlaskEvaluateClassifier, getMLScoringFunctions
import mlLib.trainModels as tm

# System libraries
import logging
from logging import Formatter, FileHandler
from six.moves.urllib.parse import urlencode
from functools import wraps
from jose import jwt
from urllib.request import urlopen, Request

# Robot Classify Libraries
from forms import *
from models import *
import config

import flask_uploads as fu
from flask_session import Session


# ---------------------------------------------------------------------------#
# Helper Functions
#    dump: print out the contents of an object
# ---------------------------------------------------------------------------#

def dumpObj(obj, name='None'):
    print('\n\nDump of object...{}'.format(name))
    for attr in dir(obj):
        print("    obj.%s = %r" % (attr, getattr(obj, attr)))


def dumpData(obj, name='None'):
    print('\n\nDump of data...{}'.format(name))
    for attr in obj:
        print("    data.%s = %r" % (attr, obj[attr]))


def makePickList(columns, add=None):
    if add is not None:
        columns.append(add)
    return [(c, c) for c in columns]


def makeModelPickList(model):
    if model is None:
        columns = tm.availableModels[tm.TRAIN_CLASSIFICATION]
    else:
        columns = tm.availableModels[model]

    return makePickList(columns)


def makeScorerPickList(model):
    if model is None:
        scorers = tm.availableScorers[tm.TRAIN_CLASSIFICATION]
    else:
        scorers = tm.availableScorers[model]

    return makePickList(scorers)


def dumpSession(name=None):
    print('\n\nDump of the session Object at location: ', name)
    print('  SESSION_COOKIE_NAME={}'.format(app.config['SESSION_COOKIE_NAME']))
    print('  session.sid={}'.format(session.sid))
    print('  SESSION_TYPE={}'.format(app.config['SESSION_TYPE']))
    print('  Session dump..', session)
    print('\n\n')


def dumpHeader(name=None):
    print('\nHeader Object dump at location: ', name)
    # dumpObj(request,'request')
    dumpObj(request.headers, 'request.headers')
    # print('  request.header={}'.format(request))
    print('\n')
    pass


def dumpProjectForm(form):
    print('\n\nProject Form Validate on submit=', form.validate_on_submit())
    print('is_submitted=', form.is_submitted())
    print('validate=', form.validate())
    print('form.name.data=', form.name.data)
    print('form.description.data=', form.description.data)
    print('form.trainingFile.data=', form.trainingFile.data)
    print('form.testingFile.data=', form.testingFile.data)


def dumpRunForm(form):
    print('\n\nRun Form Validate on submit=', form.validate_on_submit())
    print('is_submitted=', form.is_submitted())
    print('validate=', form.validate())
    print('form.name.data=', form.name.data)
    print('form.description.data=', form.description.data)


# ---------------------------------------------------------------------------#
# App Config.
# ---------------------------------------------------------------------------#
# def create_app(testing=False):
app = Flask(__name__)

moment = Moment(app)
app.secret_key = config.SECRET_KEY
app.config.from_object('config')
app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken', 'X-CSRF-Token']

# define file uploads
fu.configure_uploads(app, config.dataFiles)

# set maximum file size to 1 mb
fu.patch_request_class(app, 1024 * 1024 * config.MAX_FILE_SIZE_MB)
app.secret_key = config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'


# Setup for mllib
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# open/Connect to a postgresql database
CORS(app)
Session(app)
db = connectToDB(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS,PATCH')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# Function to get the values for UnitTests
def return_app():
    return app, db


# Register Auth0 for user authentication
AUTH0_BASE_URL = 'https://' + config.AUTH0_DOMAIN
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=config.AUTH0_CLIENT_ID,
    client_secret=config.AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={'scope': 'openid profile email'},
)


# Obtains the Access Token from the oAuth object
# When using auth0's implementation for web apps, the token is
# in the Oauth object (auth0 object)
def get_token_from_auth0():
    auth = auth0.token
    if not auth:
        abort(401, 'Authorization header is expected.')

    if 'access_token' not in auth:
        abort(401, 'Token not found.')

    elif auth['token_type'] != 'Bearer':
        abort(401, 'Authorization header must start with "Bearer".')

    return auth['access_token']


# Obtains the Access Token from the Authorization Header
# Use this to check for authentication via Curl or UnitTest Calls
def get_token_from_header():
    auth = request.headers.get('Authorization', None)
    if not auth:
        abort(401, 'Authorization header is expected.')

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        abort(401, 'Authorization header must start with "Bearer".')
    elif len(parts) == 1:

        abort(401, 'Token not found.')
    elif len(parts) > 2:

        abort(401, 'Authorization header must be bearer token.')

    token = parts[1]
    return token


# When authenticated, set the user's session data for later reference
def set_session_at_auth(userinfo, payload):

    session[config.JWT_PAYLOAD] = userinfo
    session[config.PROFILE_KEY] = {'user_id': userinfo['sub'],
                                   'name': userinfo['name']}
    session['account_id'] = userinfo['sub']
    session['username'] = userinfo['name']
    session['payload'] = payload
    session['editor_role'] = test_permissions('post:project', payload)
    session.modified = True


# ---------------------------------------------------------------------------#
#  Raise an AuthError if permissions are not included in the payload
#
#  INPUTS
#     permission: string permission (i.e. 'post:admin')
#        payload: decoded jwt payload
# ---------------------------------------------------------------------------#

def check_permissions(permission, payload):
    # print('\n\n\nEnter check_permisions.permission=', permission)
    # if 'permissions' not in payload:
    #    abort(400, 'Permissions not included in JWT.')

    # print('payload[permissions]=',payload['permissions'])
    # if permission not in payload['permissions']:
    #    abort(401, 'Permission not found.')

    return True


# Test permissions
def test_permissions(permission, payload):
    # if 'permissions' not in payload:
    #    return False
    # if permission not in payload['permissions']:
    #    return False
    return True


# ---------------------------------------------------------------------------#
# verify_decode_jwt(token) method
# INPUTS
#    token: a json web token (string)
# Returns:
#     decoded payload
# ---------------------------------------------------------------------------#

def verify_decode_jwt(token):

    unverified_header = jwt.get_unverified_header(token)
    jsonurl = \
        urlopen(AUTH0_BASE_URL + '/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
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
            payload = jwt.decode(token, rsa_key,
                                 algorithms=config.ALGORITHMS,
                                 audience=config.AUTH0_AUDIENCE,
                                 issuer='https://' + config.AUTH0_DOMAIN + '/')
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


# ---------------------------------------------------------------------------#
#  @requires_auth(permission) decorator method
#  INPUTS
#     permission: string permission (i.e. 'post:admin')
#
# ---------------------------------------------------------------------------#

def requires_auth(permission=''):

    def requires_auth_decorator(f):

        @wraps(f)
        def wrapper(*args, **kwargs):

            # Save the URL for redirect & premissions for auth check
            session['redirect_url'] = request.path
            session['permission'] = permission
            WebSession = False  # get web friendly error messages
            session.modified = True

            # Test if a session is active
            # tokens are verified in the /callback api for logins
            # This is the default method provided by Auth0
            if config.PROFILE_KEY not in session:
                # Machine to machine API (testing/curl/etc) look for the token
                # in the header since it will not be in the sessions
                if 'Authorization' in request.headers:
                    token = get_token_from_header()
                    payload = verify_decode_jwt(token)
                    check_permissions(permission, payload)
                    session['account_id'] = payload['sub']
                    session['username'] = payload['sub']
                    session['payload'] = payload
                    session['editor_role'] = test_permissions('post:project',
                                                              payload)
                    session.modified = True
                    app.config['WTF_CSRF_ENABLED'] = False
                else:
                    return redirect('/login')
            else:
                # check premissions in an active session
                payload = session['payload']
                check_permissions(permission, payload)

            return f(None, *args, **kwargs)
        return wrapper

    return requires_auth_decorator


# ---------------------------------------------------------------------------
# Controllers.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
#  Account and Session security
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


@app.route('/callback')
def callback_handling():

    auth0.authorize_access_token()
    token = get_token_from_auth0()
    try:
        payload = verify_decode_jwt(token)
    except Exception:
        abort(401)

    # Get the premission from requires_auth (which will call the callback
    # in a redirect)
    # Pages that do not have redirercts will go to the unprotected home page,
    # so no need to check permissions
    if 'redirect_url' in session:
        permission = session['permission']
        check_permissions(permission, payload)

    # Get the user info and update session attributes

    resp = auth0.get('userinfo')
    userinfo = resp.json()
    set_session_at_auth(userinfo, payload)
    session['jwttoken'] = token

    # Check to see of the redirected URL was saved to redirect back after login

    flash('You are now logged in!')
    if 'redirect_url' in session:
        return redirect(session.get('redirect_url'))
    else:
        return redirect('/projects')


@app.route('/login')
def login():
    if 'permission' not in session:
        session['permission'] = None
    session['request_uri'] = config.AUTH0_CALLBACK_URL
    return auth0.authorize_redirect(redirect_uri=config.AUTH0_CALLBACK_URL,
                                    audience=config.AUTH0_AUDIENCE)


@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('index', _external=True),
              'client_id': config.AUTH0_CLIENT_ID}
    flash('You are now logged out')
    return redirect(auth0.api_base_url + '/v2/logout?'
                    + urlencode(params))


@app.route('/jwt')
@requires_auth('get:project')
def getjwttoken(payload):
    if 'jwttoken' in session:
        return session['jwttoken']
    else:
        return 'None'


# Get user data
def userData():
    if 'username' in session:
        un = session['username']
    else:
        un = None

    if 'editor_role' in session:
        er = session['editor_role']
    else:
        er = True

    return {'username': un, 'editor': er}


# ----------------------------------------------------------------------------
# Home Page
# ----------------------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    """
        **Home Page**

        Display the home page. No access restrictions.

        - Sample Call::
            curl https://robotclassify.herokuapp.com/

        - Expected Success Response::

            HTTP Status Code: 200
            <!doctype html>...</html>

        - Expected Fail Response::

            HTTP Status Code: 405
            {
             "description":"405 Method Not Allowed: .... requested URL.",
             "error":405,
             "message":"Method Not Allowed",
             "success":false
            }

    """

    return render_template('pages/index.html', user=userData())

# ----------------------------------------------------------------------------
# Display Documentation Pages (Generated from sphinx)
# ----------------------------------------------------------------------------
@app.route('/docs/<path:path>')
def send_documents(path):
    """
        **Documentation Page**

        Display the documetnation pages. No access restrictions.

        - Sample Call::

            curl -X GET https://robotclassify.herokuapp.com/docs/index.html

        - Expected Success Response::

            HTTP Status Code: 200
            <!doctype html>...</html>

        - Expected Fail Response::

            HTTP Status Code: 404
            {
             "description": "404 Not Found: The requested URL..."
             "error": 404,
             "message": "Not Found",
             "success": false
            }

     """
    return send_from_directory('docs/build/html', path)


def projects_list_page():
    projectList = \
            Project.query.filter_by(account_id=session['account_id']).all()
    data = [p.projectPage for p in projectList]
    return render_template('pages/projects.html',
                           projects=data,
                           count=len(data),
                           user=userData())


def projects_show_page(project):
    data = project.projectPage
    return render_template('pages/show_project.html',
                           project=data,
                           user=userData())


# ----------------------------------------------------------------------------
#  List Projects
# ----------------------------------------------------------------------------

@app.route('/projects', methods=['GET'])
@requires_auth('get:project')
def projects(payload):
    """
        **List Projects**

        Display a list of projects for the current user. Returns as a web page.
        Requires get:project auth (Editor or viewer roles.)

        - Sample Call::

            export TOKEN=...
            curl -X GET https://robotclassify.herokuapp.com/projects
                 -H "Authorization: Bearer $TOKEN"

        - Expected Success Response::

            HTTP Status Code: 200
            <!doctype html>...</html>

        - Expected Fail Response::

            HTTP Status Code: 302
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
            <title>Redirecting...</title>

        - Expected Fail Response::

            HTTP Status Code: 405
            {
             "description": "405 Method Not Allowed...",
             "error": 405,
             "message": "Method Not Allowed",
             "success": false
            }

    """

    # List the projects

    return projects_list_page()


# ----------------------------------------------------------------------------
#  Show single project
# ----------------------------------------------------------------------------

@app.route('/projects/<int:project_id>', methods=['GET'])
@requires_auth('get:project')
def show_project(payload, project_id):
    """
        **Project**

        Display a single project. Must be owned by the user.

        Requires get:project auth (Editor or viewer roles.)

        - Sample Call::
            curl -X GET https://robotclassify.herokuapp.com/projects/4
                 -H "Authorization: Bearer $TOKEN"

        - Expected Success Response::

            HTTP Status Code: 200
            <!doctype html>...</html>

        - Expected Fail Response::

             HTTP Status Code: 404
            {
             "description": "404 Not Found: The requested URL..."
             "error": 404,
             "message": "Not Found",
             "success": false
            }

    """

    # Query and show a single project

    project = Project.query.filter(Project.id == project_id,
                                   Project.account_id ==
                                   session['account_id']).one_or_none()
    if project is None:
        abort(404)

    return projects_show_page(project)


# ----------------------------------------------------------------------------
# upload and parse the file data
# ----------------------------------------------------------------------------

def populateProjectFiles(project, form):

    # Get the filenames

    project.trainingFile = config.dataFiles.save(form.trainingFile.data)
    project.testingFile = config.dataFiles.save(form.testingFile.data)

    training = pd.read_csv(app.config['UPLOADED_DATA_DEST'] + '/'
                           + project.trainingFile, low_memory=False)
    testing = pd.read_csv(app.config['UPLOADED_DATA_DEST'] + '/'
                          + project.testingFile, low_memory=False)
    project.savedTrainingFile = pickle.dumps(training)
    project.savedTestingFile = pickle.dumps(testing)

    # Last, get the column namesto be saved (from the training file)
    # These are to be used later in the runs to help select attributes.
    project.columns = [c for c in training.columns.tolist()]


# ----------------------------------------------------------------------------
#  Create project
# ----------------------------------------------------------------------------

@app.route('/projects/create', methods=['GET', 'POST'])
@csrf.exempt
@requires_auth('post:project')
def create_projects_submission(payload):
    """
        **Create Project**

        Create Project for the current user. Uploads the files and stores the
        uploaded files in the database.

        Requires post:project auth (Editors Only). Data is sent as a form.

        - Sample Call::

            export TOKEN="edfgdfgd..."
            curl -X POST https://robotclassify.herokuapp.com/projects/create
                 -H "Authorization: Bearer $TOKEN"
                 -F "form-project-name=New Test Project"
                 -F "form-project-description=Testing Project Create"
                 -F "form-project-trainingFile=@examples/titanic_train.csv"
                 -F "form-project-testingFile=@examples/titanic_test.csv"

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

    form = ProjectForm(prefix='form-project-')  # request.form
    if form.is_submitted() and request.method == 'POST':
        project = Project()
        form.populate_obj(project)

        # load the files and column data into the project record

        populateProjectFiles(project, form)

        # Now insert

        project.insert()

        # on successful db insert, flash success

        flash('Project ' + form['name'].data
              + ' was successfully added!')
        return projects_show_page(project)

    else:
        return render_template('forms/new_project.html',
                               form=form,
                               user=userData())

    return projects_list_page()


# ----------------------------------------------------------------------------
#  Edit Project
# ----------------------------------------------------------------------------

@app.route('/projects/<int:project_id>/edit', methods=['GET', 'PATCH', 'POST'])
@csrf.exempt
@requires_auth('patch:project')
def edit_project_submission(payload, project_id):
    """
        **Edit Project**

        Edit Project. Data is passed as a form.
        Requires pacht:project auth (Editors Only). Data is sent as a form.

        - Sample Call to edit::

            curl -X PATCH https://robotclassify.herokuapp.com/projects/4/edit
                 -H "Authorization: Bearer $TOKEN"
                 -F "form-project-name=Titanic Disaster Patch"

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

        - Expected Fail Response::

            HTTP Status Code: 405
            {
             "description":
             "405 Method Not Allowed: The method is not allowed...",
             "error":405,
             "message":"Method Not Allowed",
             "success":false
            }

    """

    project = Project.query.filter(Project.id == project_id,
                                   Project.account_id ==
                                   session['account_id']).one_or_none()
    if project is None:
        abort(404)
    form = ProjectFormEdit(obj=project, prefix='form-project-')

    if request.method == 'PATCH' or request.method == 'POST':
        if form.is_submitted():

            # form data is posted to venue object for update
            form.populate_obj(project)

            # load the files and column data into the project record
            # populateProjectFiles(project, form)

            project.update()

            # on successful db update, flash success

            flash('Project ' + form['name'].data
                  + ' was successfully Updated!')
        else:

            flash('An error occurred. Project ' + form['name'].data
                  + ' could not be Updated.')

        return projects_show_page(project)

    return render_template('forms/edit_project.html',
                           form=form,
                           project=project,
                           user=userData())

# ----------------------------------------------------------------------------
#  Search projects
# ----------------------------------------------------------------------------
@app.route('/projects/search', methods=['POST'])
@csrf.exempt
@requires_auth('post:project')
def search_projects(payload):
    """
        **Search Projects**

        Search Projects, returning a list of projects with matching criteria.
        Requires post:project auth (Editors Only). Search is sent as a form
        post.

        - Sample Call to search::

            curl -X POST https://robotclassify.herokuapp.com/projects/search
                 -H "Authorization: Bearer $TOKEN"
                 -F "search_term=Titanic"

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

    search_term = request.form.get('search_term', None)

    # Search for an included string, case sensitive
    searchResults = Project.query.filter(Project.name.ilike('%{}%'.
                                         format(search_term)),
                                         Project.account_id ==
                                         session['account_id']).all()
    count_items = len(searchResults)

    # List and format the search results using venueShowCount property
    response = {"count": count_items,
                "data": [p.projectSearch for p in searchResults]}

    return render_template('pages/search_projects.html',
                           results=response,
                           search_term=request.form.get('search_term', ''),
                           user=userData())


# ----------------------------------------------------------------------------
#  Delete Project
# ----------------------------------------------------------------------------
@app.route('/projects/<project_id>/delete', methods=['DELETE', 'POST'])
@csrf.exempt
@requires_auth('delete:project')
def delete_project(payload, project_id):
    """
        **Delete Project**

        Delete Project

        - Sample Call::

            curl -X DELETE https://robotclassify.herokuapp.com/\
                           projects/15/delete\
                 -H "Authorization: Bearer $TOKEN"

        - Expected Success Response::

            HTTP Status Code: 200
            {"success"}

        - Expected Fail Response::

            HTTP Status Code: 404
            {
             "description": "404 Not Found:  If you entered....",
             "error": 404,
             "message": "Not Found",
             "success": false
            }

    """

    project = Project.query.filter(Project.id == project_id,
                                   Project.account_id ==
                                   session['account_id']).one_or_none()

    if project is None:
        abort(404)

    try:
        project.delete()
    except Exception as e:
        db.session.rollback()
        abort(405)
        flash('Oh Snap! Project with ID of "' + str(run_id)
              + '" was not deleted')
        return projects_show_page(project)

    flash('Project with ID of "' + str(project_id)
          + '" was successfully deleted!')
    return projects_list_page()


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
#  R U N S
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
#  Show single run
# ----------------------------------------------------------------------------
@app.route('/runs/<int:run_id>', methods=['GET'])
@requires_auth('get:run')
def show_run(payload, run_id):
    """
        **Runs**

        Display a single run result.
        Requires get:run auth (Editors and Viewers).

        - Sample Call::

            curl -X GET https://robotclassify.herokuapp.com/runs/8
                 -H "Authorization: Bearer $TOKEN"

        - Expected Success Response::

            HTTP Status Code: 200
            <!doctype html>...</html>

        - Expected Fail Response::

            HTTP Status Code: 404
            {
             "description": "404 Not Found:  If you entered....",
             "error": 404,
             "message": "Not Found",
             "success": false
            }

        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401 Unauthorized: Token not found.",
                "error": 401,
                "message": "Premission Error",
                "success": false
            }
    """

    # Query and show a single project

    run = Run.query.filter(Run.id == run_id,
                           Run.account_id ==
                           session['account_id']).one_or_none()

    if run is None:
        abort(404)

    if isinstance(run.results, type(None)):

        flash('No Run Results for ' + run.name)
        return projects_show_page(run.Project)
    else:
        return render_template('pages/results.html', run=run,
                               results=pickle.loads(run.results),
                               user=userData())


# ----------------------------------------------------------------------------
#  Create Run
# ----------------------------------------------------------------------------
@app.route('/runs/create/<int:project_id>', methods=['GET', 'POST'])
@csrf.exempt
@requires_auth('post:run')
def create_run_submission(payload, project_id):
    """
        **Create Run**

        Create Run for a project.
        Requires post:run auth (Editors Only). Data is sent as a form.

        - Sample Call::

            curl -X POST https://robotclassify.herokuapp.com/runs/create/4
                 -H "Authorization: Bearer $TOKEN"
                 -F "form-run-name=New Curl Run"
                 -F "form-run-description=Via curl"
                 -F "form-run-targetVariable=Survived"
                 -F "form-run-key=PassengerId"
                 -F "form-run-predictSetOut=PassengerId"
                 -F "form-run-predictSetOut=Survived"
                 -F "form-run-scoring=f1"
                 -F "form-run-modelList=xgbc"
                 -F "form-run-basicAutoMethod=True"

        - Expected Success Response::

            HTTP Status Code: 200
            <!doctype html>...</html>

        - Expected Fail Response::

            HTTP Status Code: 404
            {
             "description": "404 Not Found:  If you entered....",
             "error": 404,
             "message": "Not Found",
             "success": false
            }

        - Expected Fail Response::

            HTTP Status Code: 401
            {
                "description": "401 Unauthorized: Token not found.",
                "error": 401,
                "message": "Premission Error",
                "success": false
            }


    """

    project = Project.query.filter(Project.id
                                   == project_id).one_or_none()
    if project is None:
        abort(404)
    form = RunForm(prefix='form-run-')
    pickList = makePickList(project.columns)
    form.targetVariable.choices = pickList
    form.predictSetOut.choices = pickList
    form.key.choices = makePickList(project.columns, add='None')

    # set the available models based upon selected model for the project
    form.modelList.choices = makeModelPickList(project.modelType)
    form.scoring.choices = makeScorerPickList(project.modelType)

    if form.is_submitted() and request.method == 'POST':
        run = Run()
        form.populate_obj(run)
        run.project_id = project_id
        run.insert()

        # on successful db insert, flash success
        flash('Run ' + form['name'].data + ' was successfully added!')
    else:
        return render_template('forms/new_run.html',
                               form=form,
                               user=userData(),
                               project=project)

    return projects_show_page(project)


# ----------------------------------------------------------------------------
#  Delete Runs
# ----------------------------------------------------------------------------
@app.route('/runs/<int:run_id>/delete', methods=['DELETE', 'GET'])
@csrf.exempt
@requires_auth('delete:run')
def delete_run(payload, run_id):
    """
        **Delete Run**

        Delete a Run.
        Requires delete:run auth (Editors Only).

        - Sample Call::

            curl -X DELETE https://robotclassify.herokuapp.com/runs/17/delete
                 -H "Authorization: Bearer $TOKEN"

        - Expected Success Response::

            HTTP Status Code: 200
           {'success'}

        - Expected Fail Response::

            HTTP Status Code: 404
            {
             "description": "404 Not Found: The requested URL was....",
             "error": 404,
             "message": "Not Found",
             "success": false
            }

    """

    run = Run.query.filter(Run.id == run_id,
                           Run.account_id ==
                           session['account_id']).one_or_none()
    project = run.Project
    if run is None:
        abort(404)

    try:
        run.delete()
    except Exception as e:
        db.session.rollback()
        abort(405)
        flash('Oh Snap! Run with ID of "' + str(run_id)
              + '" was not deleted')
        return projects_show_page(project)

    flash('Run with ID of "' + str(run_id)
          + '" was successfully deleted!')
    return projects_show_page(project)


# ----------------------------------------------------------------------------
#  Edit Runs
# ----------------------------------------------------------------------------

@app.route('/runs/<int:run_id>/edit', methods=['GET', 'PATCH', 'POST'])
@csrf.exempt
@requires_auth('patch:run')
def edit_run_submission(payload, run_id):
    """
        **Edit Run**

        Edit Run record.
        Requires pacht:run auth (Editors Only). Data is sent as a form.

        - Sample Call to edit::

            curl -X PATCH https://robotclassify.herokuapp.com/runs/15/edit
                 -H "Authorization: Bearer $TOKEN"
                 -F "form-run-name=Updated Curl Run Patch"

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

        - Expected Fail Response::

            HTTP Status Code: 404
            {
             "description": "404 Not Found: The requested URL was....",
             "error": 404,
             "message": "Not Found",
             "success": false
            }

    """

    run = Run.query.filter(Run.id == run_id,
                           Run.account_id
                           == session['account_id']).one_or_none()

    if run is None:
        abort(404)

    form = RunForm(obj=run, prefix='form-run-')
    pickList = makePickList(run.Project.columns)
    form.targetVariable.choices = pickList
    form.predictSetOut.choices = pickList
    form.key.choices = makePickList(run.Project.columns, add='None')

    project = run.Project
    # form.scoring.choices = makePickList(getMLScoringFunctions())

    # set the available models based upon selected model for the project
    form.modelList.choices = makeModelPickList(project.modelType)
    form.scoring.choices = makeScorerPickList(project.modelType)

    if request.method == 'PATCH' or request.method == 'POST':
        if form.is_submitted():
            # form data is posted to run object for update
            try:
                form.populate_obj(run)
                run.update()

                # on successful db update, flash success
                flash('Run ' + form['name'].data
                      + ' was successfully Updated!')
            except Exception as e:
                db.session.rollback()
                flash('An DB error occurred. Run ' + form['name'].data
                      + ' could not be Updated.')
        else:
            flash('An error occurred. Run ' + form['name'].data
                  + ' could not be Updated.')

        return projects_show_page(project)

    return render_template('forms/edit_run.html',
                           form=form,
                           run=run,
                           project=project,
                           user=userData())


# ----------------------------------------------------------------------------
#  Run ML training
# ----------------------------------------------------------------------------


@app.route('/train/<int:run_id>', methods=['GET'])
@requires_auth('get:train')
def run_submission(payload, run_id):
    """
        **Exec Run**

        Run ML Training based upon run record attributes.
        Requires get:train auth (Editors and viewers).

        - Sample Call to display::

            curl -X GET https://robotclassify.herokuapp.com/train/13
                 -H "Authorization: Bearer $TOKEN"

        - Expected Success Response::

            HTTP Status Code: 200
            <!doctype html>...</html>

        - Expected Fail Response::

            HTTP Status Code: 404
            {
             "description": "404 Not Found: The requested URL... try again.",
             "error": 404,
             "message": "Not Found",
             "success": false
            }

    """

    run = Run.query.filter(Run.id == run_id,
                           Run.account_id ==
                           session['account_id']).one_or_none()

    if run is None:
        abort(404)

    results, pred = autoFlaskEvaluateClassifier(
        projectName=run.name,
        trainingFile=run.Project.trainingFile,
        testingFile=run.Project.testingFile,
        trainingFileDF=run.Project.savedTrainingFile,
        testingFileDF=run.Project.savedTestingFile,
        targetVariable=run.targetVariable,
        key=run.key,
        predictSetOut=run.predictSetOut,
        logFileOut=None,
        transcriptFile=None,
        trainingFileOut=None,
        predictFileOut=None,
        resultsFile='KaggleSubmitFile.csv',
        modelType=run.Project.modelType,
        modelList=run.modelList,
        confusionMatrixLabels=None,
        scoring=run.scoring,
        setProjectGoals=None,
        runVerbose=0,
        recommendOnly=True,
        basicAutoMethod=True,
        clusterDimensionThreshold=run.clusterDimensionThreshold,
        skewFactor=40.0,
        doExplore=True,
        doTrain=True,
        doPredict=True,
        toTerminal=True,
    )

    run.results = pickle.dumps(results)
    run.predictFile = pickle.dumps(pred)
    run.update()

    return render_template('pages/results.html',
                           run=run,
                           results=results,
                           user=userData())


@app.route('/train/<int:run_id>/download', methods=['GET'])
@requires_auth('get:run')
def download(payload, run_id):
    """
        **download results file**
        Run ML Training based upon run record attributes

        - Sample Call to display::

            curl -X GET https://robotclassify.herokuapp.com//train/13/download
                 -H "Authorization: Bearer $TOKEN"

        - Expected Success Response::

            HTTP Status Code: 200
            File Download. Example:
                PassengerId,Survived
                892,0
                893,0
                894,1

        - Expected Fail Response::

            HTTP Status Code: 404
            {
             "description": "404 Not Found: The requested URL... try again.",
             "error": 404,
             "message": "Not Found",
             "success": false
            }

    """
    run = Run.query.filter(Run.id == run_id,
                           Run.account_id ==
                           session['account_id']).one_or_none()
    if run is None:
        abort(404)

    if run.predictFile is None:
        flash("No Results file to download")
        run.results = pickle.dumps(results)
        return render_template('pages/results.html', run=run,
                               results=results)
    predict = pickle.loads(run.predictFile)
    resp = make_response(predict.to_csv(index=False))
    resp.headers["Content-Disposition"] =\
        "attachment; filename=kaggleSubmit.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp


# ----------------------------------------------------------------------------
#  error handlers and other support code
# ----------------------------------------------------------------------------
@app.errorhandler(400)
def bad_request(error):
    return (jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request',
        'description': str(error),
    }), 400)


@app.errorhandler(401)
def premission_error(error):

    # return (jsonify({
    #    'success': False,
    #    'error': 401,
    #    'message': 'Permission Error',
    #    'description': str(error),
    # }), 401)
    return (render_template('errors/500.html', user=userData()), 401)


@app.errorhandler(404)
def not_found_error(error):
    # return (jsonify({
    #    'success': False,
    #    'error': 404,
    #    'message': 'Not Found',
    #   'description': str(error),
    # }), 404)
    return (render_template('errors/404.html', user=userData()), 404)


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


@app.errorhandler(500)
def server_error(error):

    # return (jsonify({
    #    'success': False,
    #    'error': 500,
    #    'message': 'Server Error',
    #    'description': str(error),
    # }), 500)
    return (render_template('errors/500.html', user=userData()), 500)


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


# ---------------------------------------------------------------------------#
# Launch.
# ---------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
