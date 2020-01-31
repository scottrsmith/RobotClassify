'''
Tests for jwt flask app

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
- POST /train/<int:run_id>  (run ML training for a run) post:train

-- Home ---
'''

import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase

from app import create_app
from models import Project, Run

# API_PATH = 'http://127.0.0.1:5000/'

def dumpObj(obj, name='None'):
    print('\n\nDump of object...{}'.format(name))
    for attr in dir(obj):
        print("    obj.%s = %r" % (attr, getattr(obj, attr)))


# ----------------------------------------------------------------------------#
# Create UnitTest class
# ----------------------------------------------------------------------------#
class RobotClassifyTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app, self.db = create_app(testing=True)
        self.app.testing = True
        self.client = self.app.test_client
        self.app.config['WTF_CSRF_ENABLED'] = False

        pass

    def tearDown(self):
        """Executed after reach test"""
        pass

    # ------------------------------------------------------------------------#
    # Get categories
    # ------------------------------------------------------------------------#
    def test_get_all_projects(self):
        # dumpObj(self)
        res = self.client().get('/')
        
        print ('Data....', res.data)
        #dumpObj(res,'res = self.client().post')
        self.assertEqual(res.status_code, 200)
        #self.assertEqual(data['success'], True)
        #self.assertEqual(data['total_categories'], 6)
        #self.assertEqual(len(data['categories']), 6)

# ------------------------------------------------------------------------#
    # Get categories
    # ------------------------------------------------------------------------#
    def test_post_all_projects(self):
        # dumpObj(self)
        res = self.client().post('/')
        
        print ('Data....', res.data)
        #dumpObj(res,'res = self.client().post')
        self.assertEqual(res.status_code, 200)
        #self.assertEqual(data['success'], True)
        #self.assertEqual(data['total_categories'], 6)
        #self.assertEqual(len(data['categories']), 6)


    def test_404_error_bad_paramater(self):
        res = self.client().post('/projects')
        # data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        #self.assertEqual(data['success'], False)
        #self.assertEqual(data['message'], 'Resource Not Found')

   

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
