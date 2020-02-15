#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from flask_uploads import UploadSet, DATA

# Grabs the folder where the script runs.
# basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.

DEBUG = False

# setup flask uploads

dataFiles = UploadSet('data', DATA)
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOADED_DATA_DEST = os.path.join(basedir, 'uploads')
DOWNLOAD_DATA_DEST = os.path.join(basedir, 'download')

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
AUTH0_CLIENT_ID = os.environ['AUTH0_CLIENT_ID']
AUTH0_CLIENT_SECRET = os.environ['AUTH0_CLIENT_SECRET']
AUTH0_CALLBACK_URL = os.environ['AUTH0_CALLBACK_URL']
AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
AUTH0_AUDIENCE = os.environ['AUTH0_AUDIENCE']
APP_TESTING = os.environ['APP_TESTING']
WTF_CSRF_ENABLED = os.environ['WTF_CSRF_ENABLED']
if 'APP_TESTING_USERID' in os.environ:
    APP_TESTING_USERID = os.environ['APP_TESTING_USERID']
else:
    APP_TESTING_USERID = None

PROFILE_KEY = 'profile'
SECRET_KEY = os.urandom(32)
JWT_PAYLOAD = 'jwt_payload'
ALGORITHMS = ['RS256']

# WTF_CSRF_CHECK_DEFAULT = False
# WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token']
