"""
**Introduction**


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
    '''
    Id
    Primary Key - Auto assigned
    '''
    account_id = db.Column(db.String(100))
    '''
    account_id
    Account owner of the record. Restricts viewing from other users.
    '''
    name = db.Column(db.String)
    '''
    name
    Name of the project
    '''
    description = db.Column(db.String(120))
    '''
    description
    Description of the project
    '''

    modelType = db.Column(db.String(20))
    '''
    modelType:
        TRAIN_CLASSIFICATION = 'Classification'
        TRAIN_REGRESSION = 'Regression'
        TRAIN_CLUSTERING = 'Clustering'
    '''

    trainingType = db.Column(db.String(20))
    '''
        kaggle, train-only, predict, cluster
    '''

    trainingFile = db.Column(db.String(120))
    '''
    Training file.
    CSV file to be loaded for training as uploaded in the upload folder.
    It stored in the project record in 'savedTrainingFile' as a python pickle.
    '''
    testingFile = db.Column(db.String(120))
    '''
    Testing file.
    CSV file to be loaded for testing the trained model as uploaded in the
    upload folder. The testing file is designed for Kaggle comperition
    submissions. It is stored in the project record in 'savedTestingFile'
    as a python pickle
    '''
    savedTrainingFile = db.Column(db.PickleType)
    '''
    savedTrainingFile file.
    The saved training file stored as a python pickle.
    Generated automatically.
    '''
    savedTestingFile = db.Column(db.PickleType)
    '''
    savedTestingFile file.
    The saved testing file stored as a python pickle. Generated automatically.
    '''
    columns = db.Column(db.ARRAY(db.String))
    '''
    The columns of the training table. Used to populate picklist
    in the UI. Generated automatically.
    '''
    runs = db.relationship('Run', backref='project', lazy=True)
    '''
    Runs associated with the project.
    Runs have a many to one relationship to projects.
    '''

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
    '''
    Id
    Primary Key - Auto assigned
    '''

    name = db.Column(db.String)
    '''
    name
    Name of the run.
    '''

    description = db.Column(db.String(120))
    '''
    description
    Description of the projerunct
    '''

    results = db.Column(db.PickleType)
    '''
    results
    The results data for a run. This contains the output of a run. This
    includes the feature evaluation, feature engineering, and model training
    stats.
    '''

    account_id = db.Column(db.String(100))
    '''
    account_id
    Account owner of the record. Restricts viewing from other users.
    '''

    project_id = db.Column(db.Integer,
                           db.ForeignKey('Project.id', ondelete='CASCADE'),
                           nullable=False)
    '''
    project_id
    Parent record of the run.
    '''

    targetVariable = db.Column(db.String(120))
    '''
    targetVariable
    The variable that is to be predicted.
    '''

    clusterDimensionThreshold = db.Column(db.Integer)
    '''
    clusterDimensionThreshold
    The max number of clusters to evaluate
    '''

    key = db.Column(db.String(120))
    '''
    key
    The unique key that defines the training record.
    '''

    # example:predictSetOut=['Survived','PassengerId'],
    predictSetOut = db.Column(db.ARRAY(db.String))
    '''
    predictSetOut
    Defines the sheet columns to be used in the predict file.
    Usually two, the target variable and key. This is designed
    to be used for Kaggle competition submissions.
    '''

    predictFile = db.Column(db.PickleType)
    '''
    predictFile
    Stores the results of the prediction for the test file.
    Used for downloads.
    '''

    # confusionMatrixLabels=[(0,'Not'), (1, 'Survived')],
    modelList = db.Column(db.ARRAY(db.String))
    '''
    modelList
    List of models used in training. Best is evaluated on the scoreing
    choice. Valid models can include: l2, rfc, gbc, decisiontree,
    kneighbors, sgd, bagging, adaboost, gaussiannb, etc, svc, xgbc,
    stack, vote
    '''

    scoring = db.Column(db.String(120), default='f1')
    '''
    scoring
    Scoring methods for model evaluation.
    Options include f1, r2, Perecision, Recall, and Accuracy
    '''

    # Booleans
    basicAutoMethod = db.Column(db.Boolean(), default=True)
    '''
    basicAutoMethod
    There are two algorithems for feature engineering and attribute
    evaliuation. This selects between the two models. True for Model
    I False for model II
    '''

    Project = db.relationship('Project',
                              backref=db.backref(
                                  'Run',
                                  cascade='all, delete-orphan'))
    '''
    Project
    Back reference to the parent project
    '''

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
