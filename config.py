#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from flask_uploads import UploadSet, DATA

# Grabs the folder where the script runs.
# basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.

DEBUG = True

# setup flask uploads

dataFiles = UploadSet('data', DATA)
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOADED_DATA_DEST = os.path.join(basedir, 'uploads')
DOWNLOAD_DATA_DEST = os.path.join(basedir, 'download')

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
AUTH0_CLIENT_ID = 'AUTH0_CLIENT_ID'
AUTH0_CLIENT_SECRET = 'AUTH0_CLIENT_SECRET'
AUTH0_CALLBACK_URL = 'AUTH0_CALLBACK_URL'
AUTH0_DOMAIN = 'AUTH0_DOMAIN'
AUTH0_AUDIENCE = 'AUTH0_AUDIENCE'
PROFILE_KEY = 'profile'
SECRET_KEY = os.urandom(32)
JWT_PAYLOAD = 'jwt_payload'

# WTF_CSRF_CHECK_DEFAULT = False
# WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token']

AUTH0_DOMAIN = 'dev-p35ewo73.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'robotclassify'
