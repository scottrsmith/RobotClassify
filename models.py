"""
**Introduction**

There are three models:
- Venue
- Artists
- Shows

"""

# ---------------------------------------------------------------------------#
# Models..
# ---------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import session
import datetime
import pickle

db = SQLAlchemy()


# ------- Commect and configure the connection to the DB ----------
def connectToDB(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    # db.create_all()
    return db


# ----- Define the Project Table Class
class Project(db.Model):
    '''
    Project
    An ML Project. Projects are the top-orginizing layer for
    running ML problems
    '''
    __tablename__ = 'Project'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(100))
    name = db.Column(db.String)
    description = db.Column(db.String(120))
    trainingFile = db.Column(db.String(120))
    testingFile = db.Column(db.String(120))
    savedTrainingFile = db.Column(db.PickleType)
    savedTestingFile = db.Column(db.PickleType)
    columns = db.Column(db.ARRAY(db.String))
    runs = db.relationship('Run', backref='project', lazy=True)

    @property
    def projectPage(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'trainingFile': self.trainingFile,
            'testingFile': self.testingFile,
            'runCount':
                Run.query.filter(Run.project_id == self.id).count(),
            'runs': [r.runList for r in Run.query.filter(
                Run.project_id == self.id,
                Run.account_id == session['account_id'])],
        }

    @property
    def projectSearch(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    def __str__(self):
        return 'Project Record\n' +\
               '  id={}\n'.format(self.id) +\
               '  name={}\n'.format(self.name) +\
               '  description={}\n'.format(self.description) +\
               '  trainingFile={}\n'.format(self.trainingFile) +\
               '  testingFile={}\n'.format(self.testingFile) 


    def insert(self):
        '''
        insert()
            Inserts a new model into a database.
            The model must have a unique id and title.

            EXAMPLE::

                p = Project()
                p.insert()

        '''
        self.account_id = session['account_id']
        db.session.add(self)
        db.session.commit()

    def delete(self):
        '''
        delete()
            deletes a new model into a database
            the model must exist in the database

            EXAMPLE::

                p = Project()
                p.delete()

        '''

        db.session.delete(self)
        db.session.commit()

    def update(self):
        '''
        update()
            updates a new model into a database
            the model must exist in the database

            EXAMPLE::

                p = Project.query.filter(p.id == id).one_or_none()
                p.name = 'Regression Test'
                p.update()

        '''
        db.session.commit()


# ----- Define the Run Table Class
class Run(db.Model):
    '''
    Run
    '''
    __tablename__ = 'Run'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String(120))
    results = db.Column(db.PickleType)
    account_id = db.Column(db.String(100))
    project_id = db.Column(db.Integer,
                           db.ForeignKey('Project.id', ondelete='CASCADE'),
                           nullable=False)

    targetVariable = db.Column(db.String(120))
    key = db.Column(db.String(120))

    # example:predictSetOut=['Survived','PassengerId'],
    predictSetOut = db.Column(db.ARRAY(db.String))
    predictFile = db.Column(db.PickleType)

    # confusionMatrixLabels=[(0,'Not'), (1, 'Survived')],
    modelList = db.Column(db.ARRAY(db.String))

    scoring = db.Column(db.String(120), default='f1')

    # Booleans
    basicAutoMethod = db.Column(db.Boolean(), default=True)

    Project = db.relationship('Project',
                              backref=db.backref(
                                  'Run',
                                  cascade='all, delete-orphan'))

    # List out the runs for display on the project page
    @property
    def runList(self):
        if self.results is None:
            results = None
        else:
            results = pickle.loads(self.results)

        return {"id": self.id,
                "name": self.name,
                "description": self.description,
                "trainingFile": self.Project.trainingFile,
                "testingFile": self.Project.testingFile,
                "targetVariable": self.targetVariable,
                "basicAutoMethod": self.basicAutoMethod,
                "scoring": self.scoring,
                "modelList": self.modelList,
                "results": results
                }

    def __str__(self):
        return "Run Record\n" +\
               "  id={}\n".format(self.id) +\
               "  name={}\n".format(self.name) +\
               "  description={}\n".format(self.description) +\
               "  account_id={}\n".format(self.account_id) +\
               "  project_id={}\n".format(self.project_id) +\
               "  targetVariable={}\n".format(self.targetVariable) +\
               "  basicAutoMethod={}\n".format(self.basicAutoMethod) +\
               "  scoring={}\n".format(self.scoring) +\
               "  modelList={}\n".format(self.modelList)  
                
       
        

    def insert(self):
        '''
        insert()
            Inserts a new model into a database.
            The model must have a unique id and title.

            EXAMPLE::

                p = Project()
                p.insert()

        '''
        self.account_id = session['account_id']
        db.session.add(self)
        db.session.commit()

    def delete(self):
        '''
        delete()
            deletes a new model into a database
            the model must exist in the database

            EXAMPLE::

                p = Project()
                p.delete()

        '''

        db.session.delete(self)
        db.session.commit()

    def update(self):
        '''
        update()
            updates a new model into a database
            the model must exist in the database

            EXAMPLE::

                p = Project.query.filter(p.id == id).one_or_none()
                p.name = 'Regression Test'
                p.update()

        '''
        db.session.commit()
