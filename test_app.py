#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Tests for jwt flask app

-- Home Page
- GET / (home)

-- Documentation Page
- GET /docs/index.html

--- Projects ---
- GET /projects (List all projects) - get:project
- GET /projects/<int:project_id> (Project page) - get:project
- POST/GET /projects/create (create a new project) - post:project
- PATCH /projects/<int:project_id>/edit (edit a project) - patch:project
- DELETE /projects/<project_id>/delete (Delete a project) - delete:project

--- Runs ---
- GET /runs/<int:run_id>  (Display a run results) - get:run
- GET/POST /runs/create/<int:project_id> (Create a run) - get:post
- DELETE /runs/<int:run_id>/delete (Delete a run) - delete:post
- PATCH /run/<int:run_id>/edit (edit a run) - patch:run

--- Train ---
- GET /train/<int:run_id>  (run ML training for a run) post:train
- GET /train/<int:run_id>/download  (download testing results file,
      kaggle file) get:train

'''

import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase

from app import return_app
from models import Project, Run
from forms import ProjectForm, RunForm, ProjectFormEdit
from werkzeug.datastructures import FileStorage
from flask_session import Session
from flask import session, jsonify
import http.client
import config

# ----------------------------------------------------------------------------#
# helper functions
# ----------------------------------------------------------------------------#


def dumpObj(obj, name='None'):
    print('\n\nDump of object...{}'.format(name))
    for attr in dir(obj):
        print("    obj.%s = %r" % (attr, getattr(obj, attr)))


# Used to authenticate a user and create the header
def testing_auth(editorRole=True, multiPart=False):
    conn = http.client.HTTPSConnection("dev-p35ewo73.auth0.com")
    if editorRole:
        CLIENT_ID = config.AUTH0_CLIENT_ID
        CLIENT_SECRET = config.AUTH0_CLIENT_SECRET
    else:
        CLIENT_ID = os.environ['AUTH0_CLIENT_ID_VIEW']
        CLIENT_SECRET = os.environ['AUTH0_CLIENT_SECRET_VIEW']

    payload = "{\"client_id\":\"" +\
              CLIENT_ID +\
              "\",\"client_secret\":\"" +\
              CLIENT_SECRET +\
              "\",\"audience\":\"" + config.AUTH0_AUDIENCE +\
              "\",\"grant_type\":\"client_credentials\"}"

    headers = {'content-type': "application/json"}
    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    token = data['access_token']

    if multiPart:
        return {'Authorization': 'Bearer ' + token,
                'content-type': "multipart/form-data"}
    else:
        return {'Authorization': 'Bearer ' + token}


def getCSVFile(filePath):
    file = None
    fp = open(filePath, 'rb')

    if fp is None:
        print('File {} Not Found'.format(filePath))
    return fp


def isHTML(s):
    if str(s).count('<!doctype html>') > 0:
        return True
    else:
        return False


def isFound(s, sub):
    if str(s).count(sub) > 0:
        return True
    else:
        return False


# ----------------------------------------------------------------------------#
# Create UnitTest class
# ----------------------------------------------------------------------------#
class RobotClassifyTestCase(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app."""
        self.app, self.db = return_app()
        self.app.testing = True
        self.client = self.app.test_client
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.header = None

    def tearDown(self):
        """Executed after each test"""
        self.header = None
        pass

    # ------------------------------------------------------------------------#
    # Home Page (Get /)
    # ------------------------------------------------------------------------#
    def test_home_page(self):
        res = self.client().get('/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isHTML(res.data))

    def test_home_page_fail(self):
        res = self.client().post('/')
        self.assertEqual(res.status_code, 405)

    # ------------------------------------------------------------------------#
    # Documentation Page (Get /docs)
    # ------------------------------------------------------------------------#

    def test_docs_page(self):
        # dumpObj(self)
        res = self.client().get('/docs/index.html')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isHTML(res.data))

    def test_docs_page_fail(self):
        # dumpObj(self)
        res = self.client().get('/docs/badurl')
        self.assertEqual(res.status_code, 404)

    # ------------------------------------------------------------------------#
    # Role-based access control
    #
    #   There are two roles:
    #     1. Viewer Role can only view projects, runs, & results
    #           - get:project  get a single, or list of projects
    #           - get:run Get a run or download run results
    #     2. Editor Role can create projects, runs, & perform training
    #           - get:project  get a single, or list of projects
    #           - post:project  Create a new project or search
    #           - patch:project  Update a project attributes
    #           - delete:project  Delete a project and its runs
    #           - get:run Get a run or download run results
    #           - post:run  Create a new run
    #           - patch:run  Update a run's attributes
    #           - delete:run  Delete a run
    #           - get:train Run ML Training
    # ------------------------------------------------------------------------#

    # ------------------------------------------------------------------------#
    #   Test Viewer Role
    #
    # ------------------------------------------------------------------------#

    # Viewer should be able to see projects
    def test_get_multiple_projects_viewer(self):
        self.header = testing_auth(editorRole=False)
        res = self.client().get('/projects', headers=self.header)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isHTML(res.data))

    # Viewer should not be able to post a new project
    def test_post_projects_viewer_fail(self):

        # Get auth
        self.header = testing_auth(editorRole=False, multiPart=True)

        # get datafiles
        trainingFile = getCSVFile('examples/titanic_train.csv')
        testingFile = getCSVFile('examples/titanic_test.csv')
        theName = 'UnitTest Project Create Viewer'
        res = self.client().post(
            '/projects/create',
            headers=self.header,
            data={
                'form-project-name': theName,
                'form-project-description': 'Testing Project Create',
                'form-project-trainingFile': trainingFile,
                'form-project-testingFile': testingFile},
            content_type='multipart/form-data',
            follow_redirects=True)

        self.assertEqual(res.status_code, 401)

    # Viewers should not be able to delete projects
    def test_delete_project_fail(self):
        self.header = testing_auth(editorRole=False)
        project_id = 3
        path = '/projects/{}/delete'.format(project_id)
        res = self.client().delete(path, headers=self.header)
        self.assertEqual(res.status_code, 401)

    # Viewers should not be able to post runs
    def test_post_run_fail(self):
        self.header = testing_auth(editorRole=False)
        project_id = 1
        path = '/runs/create/{}'.format(project_id)
        theName = 'UnitTest Run Create Viewer'
        res = self.client().post(
            path,
            headers=self.header,
            data={
                'form-run-name': theName,
                'form-run-description': 'Testing Run Create Viedw',
                'form-run-targetVariable': 'Survived',
                'form-run-key': 'PassengerId',
                'form-run-predictSetOut': ['PassengerId', 'Survived'],
                'form-run-scoring': 'f1',
                'form-run-modelList': ['xgbc'],
                'form-run-basicAutoMethod': True},
            follow_redirects=True)
        self.assertEqual(res.status_code, 401)
        run = Run.query.filter(Run.name == theName).one_or_none()
        self.assertIsNone(run)

    # ------------------------------------------------------------------------#
    # Projects (All as editor role)
    #   - GET /projects (List all projects) - get:project
    #   - GET /projects/<int:project_id> (Project page) - get:project
    #   - POST/GET /projects/create (create a new project) - post:project
    #   - PATCH /projects/<int:project_id>/edit (edit a project) patch:project
    #   - DELETE /projects/<project_id>/delete  delete:project
    # ------------------------------------------------------------------------#

    # ------------------------------------------------------------------------#
    #   - GET /projects (List all projects for user) - get:project
    #
    # ------------------------------------------------------------------------#

    def test_get_multiple_projects(self):
        self.header = testing_auth(editorRole=True)
        res = self.client().get('/projects', headers=self.header)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isHTML(res.data))

        # Test we got correct number of projects records
        c = Project.query.filter(Project.account_id ==
                                 config.APP_TESTING_USERID).count()
        self.assertTrue(isFound(res.data, '{} PROJECTS'.format(c)))

    def test_get_multiple_projects_fail(self):
        self.header = testing_auth(editorRole=True)
        res = self.client().post('/projects', headers=self.header)
        self.assertEqual(res.status_code, 405)

    # ------------------------------------------------------------------------#
    #   - GET /projects/<int:project_id> (Project page) - get:project
    #
    # ------------------------------------------------------------------------#

    def test_get_single_project(self):
        self.header = testing_auth(editorRole=True)
        project_id = 2
        path = '/projects/{}'.format(project_id)
        res = self.client().get(path, headers=self.header)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isHTML(res.data))

        # Test that we got the correct contents
        self.assertTrue(isFound(res.data, 'Survey'))

    def test_get_single_project_not_found(self):
        self.header = testing_auth(editorRole=True)
        project_id = 2000
        path = '/projects/{}'.format(project_id)
        res = self.client().get(path, headers=self.header)
        self.assertEqual(res.status_code, 404)

    # ------------------------------------------------------------------------#
    #   - POST /projects/search (search projects for user) - post:project
    #
    # ------------------------------------------------------------------------#

    def test_post_search_projects(self):

        search_term = 'Titanic'
        self.header = testing_auth(editorRole=True)
        res = self.client().post('/projects/search',
                                 data={'search_term': search_term},
                                 headers=self.header)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(isHTML(res.data))

        # Test we got the correct search results
        searchCount = Project.query.filter(Project.name.ilike('%{}%'.
                                           format(search_term)),
                                           Project.account_id ==
                                           config.APP_TESTING_USERID).count()
        sub = 'Number of search results for "Titanic": {}'.format(searchCount)
        self.assertTrue(isFound(res.data, sub))

    def test_post_search_projects_fail(self):

        search_term = 'Titanic'
        self.header = testing_auth(editorRole=True)
        res = self.client().get('/projects/search',
                                data={'search_term': search_term},
                                headers=self.header)

        self.assertEqual(res.status_code, 405)

    # ------------------------------------------------------------------------#
    #   - POST/GET /projects/create (create a new project) - post:project
    #
    # ------------------------------------------------------------------------#

    def test_post_projects(self):

        # Get auth
        self.header = testing_auth(editorRole=True, multiPart=True)

        # get datafiles
        trainingFile = getCSVFile('examples/titanic_train.csv')
        testingFile = getCSVFile('examples/titanic_test.csv')
        theName = 'UnitTest Project Create'
        res = self.client().post(
            '/projects/create',
            headers=self.header,
            data={
                'form-project-name': theName,
                'form-project-description': 'Testing Project Create',
                'form-project-trainingFile': trainingFile,
                'form-project-testingFile': testingFile},
            content_type='multipart/form-data',
            follow_redirects=True)

        # Test that the record was created
        proj = Project.query.filter(Project.name == theName).one_or_none()
        self.assertIsNotNone(proj)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(isHTML(res.data))

    def test_post_projects_bad_content_type(self):

        # Get auth
        self.header = testing_auth(editorRole=True, multiPart=True)

        # get datafiles
        trainingFile = getCSVFile('examples/titanic_train.csv')
        testingFile = getCSVFile('examples/titanic_test.csv')
        theName = 'UnitTest Project Create'
        res = self.client().post(
            '/projects/create',
            headers=self.header,
            data={
                'form-project-name': theName,
                'form-project-description': 'Testing Project Create',
                'form-project-trainingFile': trainingFile,
                'form-project-testingFile': testingFile},
            follow_redirects=True)

        self.assertEqual(res.status_code, 200)

    # ------------------------------------------------------------------------#
    #   - PATCH /projects/<int:project_id>/edit (edit a project) patch:project
    #
    # ------------------------------------------------------------------------#
    def test_patch_projects(self):
        self.header = testing_auth(editorRole=True)
        project_id = 2

        project = Project.query.filter_by(id=project_id).one_or_none()
        self.assertIsNotNone(project)
        patchName = project.name + ' Patched'

        path = '/projects/{}/edit'.format(project_id)
        res = self.client().patch(
            path,
            headers=self.header,
            data={
                'form-project-name': patchName,
                'form-project-description': project.description + ' Patched'},
            follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isHTML(res.data))

        # Test that the record was patched
        proj = Project.query.filter(Project.name == patchName).one_or_none()
        self.assertIsNotNone(proj)

        # Test flask message
        self.assertTrue(isFound(res.data, 'successfully Updated!'))

    def test_patch_projects_fail(self):
        self.header = testing_auth(editorRole=True)
        project_id = 2

        project = Project.query.filter_by(id=project_id).one_or_none()
        self.assertIsNotNone(project)
        patchName = project.name + ' Patched'

        path = '/projects/{}/edit'.format(project_id)
        res = self.client().post(
            path,
            headers=self.header,
            data={
                'form-project-name': patchName,
                'form-project-description': project.description + ' Patched'},
            follow_redirects=True)
        self.assertEqual(res.status_code, 405)

    # ------------------------------------------------------------------------#
    #   - DELETE /projects/<project_id>/delete  delete:project
    #
    # ------------------------------------------------------------------------#
    def test_delete_project(self):
        self.header = testing_auth(editorRole=True)
        project_id = 3
        path = '/projects/{}/delete'.format(project_id)
        res = self.client().delete(path, headers=self.header)
        self.assertEqual(res.status_code, 200)

        # Test that the record was actually deleted
        self.assertEqual(Project.query.filter_by(id=project_id).count(), 0)

    def test_delete_project_not_Found(self):
        self.header = testing_auth(editorRole=True)
        project_id = 3000
        path = '/projects/{}/delete'.format(project_id)
        res = self.client().delete(path, headers=self.header)
        self.assertEqual(res.status_code, 404)

    # ------------------------------------------------------------------------#
    # Runs
    # - GET /runs/<int:run_id>  (Display a run results) - get:run
    # - GET/POST /runs/create/<int:project_id> (Create a run) - get:post
    # - PATCH /run/<int:run_id>/edit (edit a run) - patch:run
    # - DELETE /runs/<int:run_id>/delete (Delete a run) - delete:post
    # ------------------------------------------------------------------------#

    # ------------------------------------------------------------------------#
    # - GET /runs/<int:run_id>  (Display a run results) - get:run
    #
    # ------------------------------------------------------------------------#
    def test_get_run(self):
        self.header = testing_auth(editorRole=True)
        run_id = 1
        path = '/runs/{}'.format(run_id)
        res = self.client().get(path, headers=self.header)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isHTML(res.data))

    def test_get_run_not_found(self):
        self.header = testing_auth(editorRole=True)
        run_id = 1000
        path = '/runs/{}'.format(run_id)
        res = self.client().get(path, headers=self.header)
        self.assertEqual(res.status_code, 404)

    # ------------------------------------------------------------------------#
    # - GET/POST /runs/create/<int:project_id> (Create a run) - get:post
    #
    # ------------------------------------------------------------------------#
    def test_post_run(self):
        self.header = testing_auth(editorRole=True)
        project_id = 1
        path = '/runs/create/{}'.format(project_id)
        theName = 'UnitTest Run Create'
        res = self.client().post(
            path,
            headers=self.header,
            data={
                'form-run-name': theName,
                'form-run-description': 'Testing Run Create',
                'form-run-targetVariable': 'Survived',
                'form-run-key': 'PassengerId',
                'form-run-predictSetOut': ['PassengerId', 'Survived'],
                'form-run-scoring': 'f1',
                'form-run-modelList': ['xgbc'],
                'form-run-basicAutoMethod': True},
            follow_redirects=True)

        run = Run.query.filter(Run.name == theName).one_or_none()
        self.assertIsNotNone(run)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isHTML(res.data))

    def test_post_run_project_not_found(self):
        self.header = testing_auth(editorRole=True)
        project_id = 10000
        path = '/runs/create/{}'.format(project_id)
        theName = 'UnitTest Run Create'
        res = self.client().post(
            path,
            headers=self.header,
            data={
                'form-run-name': theName,
                'form-run-description': 'Testing Run Create',
                'form-run-targetVariable': 'Survived',
                'form-run-key': 'PassengerId',
                'form-run-predictSetOut': ['PassengerId', 'Survived'],
                'form-run-scoring': 'f1',
                'form-run-modelList': ['xgbc'],
                'form-run-basicAutoMethod': True},
            follow_redirects=True)

        self.assertEqual(res.status_code, 404)

    # ------------------------------------------------------------------------#
    # - PATCH /run/<int:run_id>/edit (edit a run) - patch:run
    #
    # ------------------------------------------------------------------------#
    def test_patch_run(self):
        self.header = testing_auth(editorRole=True)

        run_id = 1
        run = Run.query.filter_by(id=run_id).one_or_none()
        self.assertIsNotNone(run)
        patchName = run.name + ' Patched'
        # print ('Run=', run)

        path = '/runs/{}/edit'.format(run_id)
        res = self.client().patch(
            path,
            headers=self.header,
            data={
                'form-run-name': patchName,
                'form-run-description': run.description + ' Patched',
                'form-run-results': run.results,
                'form-run-account_id': run.account_id,
                'form-run-project_id': run.project_id,
                'form-run-targetVariable': run.targetVariable,
                'form-run-key': run.key,
                'form-run-predictSetOut': run.predictSetOut,
                'form-run-predictFile': run.predictFile,
                'form-run-modelList': run.modelList,
                'form-run-scoring': run.scoring,
                'form-run-basicAutoMethod': run.basicAutoMethod,
            },
            follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isHTML(res.data))

        # Test that the record was patched
        run = Run.query.filter(Run.name == patchName).one_or_none()
        self.assertIsNotNone(run)

        # Test flask message
        self.assertTrue(isFound(res.data, 'successfully Updated!'))

    def test_patch_run_fail(self):
        self.header = testing_auth(editorRole=True)

        run_id = 1
        run = Run.query.filter_by(id=run_id).one_or_none()
        self.assertIsNotNone(run)
        patchName = run.name + ' Patched'
        # print ('Run=', run)

        path = '/runs/{}/edit'.format(run_id)
        res = self.client().post(
            path,
            headers=self.header,
            data={
                'form-run-name': patchName,
                'form-run-description': run.description + ' Patched',
                'form-run-results': run.results,
                'form-run-account_id': run.account_id,
                'form-run-project_id': run.project_id,
                'form-run-targetVariable': run.targetVariable,
                'form-run-key': run.key,
                'form-run-predictSetOut': run.predictSetOut,
                'form-run-predictFile': run.predictFile,
                'form-run-modelList': run.modelList,
                'form-run-scoring': run.scoring,
                'form-run-basicAutoMethod': run.basicAutoMethod,
            },
            follow_redirects=True)
        self.assertEqual(res.status_code, 405)

    # ------------------------------------------------------------------------#
    # - DELETE /runs/<int:run_id>/delete (Delete a run) - delete:post
    #
    # ------------------------------------------------------------------------#
    def test_delete_run(self):
        self.header = testing_auth(editorRole=True)
        run_id = 6
        path = '/runs/{}/delete'.format(run_id)
        res = self.client().delete(path, headers=self.header)
        self.assertEqual(res.status_code, 200)

        # Test that the record was actually deleted
        self.assertEqual(Run.query.filter_by(id=run_id).count(), 0)

    def test_delete_run_not_found(self):
        self.header = testing_auth(editorRole=True)
        run_id = 6000
        path = '/runs/{}/delete'.format(run_id)
        res = self.client().delete(path, headers=self.header)
        self.assertEqual(res.status_code, 404)

    # ------------------------------------------------------------------------#
    # Train
    # - GET /train/<int:run_id>  (run ML training for a run) post:train
    # - GET /train/<int:run_id>/download  (download testing results file -
    #       kaggle file) get:train
    # ------------------------------------------------------------------------#

    # ------------------------------------------------------------------------#
    # - GET /train/<int:run_id>  (run ML training for a run) post:train
    #
    # ------------------------------------------------------------------------#
    def test_get_train(self):
        self.header = testing_auth(editorRole=True)
        run_id = 3
        path = '/train/{}'.format(run_id)
        res = self.client().get(path, headers=self.header)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isHTML(res.data))
        self.assertTrue(isFound(res.data, '0.877'))

    def test_get_train_not_found(self):
        self.header = testing_auth(editorRole=True)
        run_id = 3000
        path = '/train/{}'.format(run_id)
        res = self.client().get(path, headers=self.header)
        self.assertEqual(res.status_code, 404)

    # ------------------------------------------------------------------------#
    # - GET /train/<int:run_id>/download  (download testing results file -
    #       kaggle file) get:train
    #
    # ------------------------------------------------------------------------#

    def test_get_train_download(self):
        self.header = testing_auth(editorRole=True)
        run_id = 3
        path = '/train/{}/download'.format(run_id)
        res = self.client().get(path, headers=self.header)
        self.assertEqual(res.status_code, 200)
        # Download file is a sheer with 'recommend' as a column
        self.assertTrue(isFound(res.data, 'Recommend'))

    def test_get_train_download_fail(self):
        self.header = testing_auth(editorRole=True)
        run_id = 30000
        path = '/train/{}/download'.format(run_id)
        res = self.client().get(path, headers=self.header)
        self.assertEqual(res.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
