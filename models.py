"""
**Introduction**

There are three models:
- Venue
- Artists
- Shows

"""

#----------------------------------------------------------------------------#
# Models..
#----------------------------------------------------------------------------#
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
    return db

# ----- Define the Project Table Class
class Project(db.Model):
    '''
    Project
    An ML Project. Projects are the top-orginizing layer for running ML problems
    '''
    __tablename__ = 'Project'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(100))
    name = db.Column(db.String)
    description = db.Column(db.String(120))
    trainingFile = db.Column(db.String(120)) # './Data/titanic_train.csv',
    testingFile = db.Column(db.String(120)) #'./Data/titanic_test.csv',
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
                'description': self.description,
                'runCount': 
                    Run.query.filter(Run.project_id == self.id).count(),
                'runs': [r.runList for r in Run.query.filter(
                    Run.project_id == self.id,
                    Run.account_id == session['account_id'])],
            }

    @property
    def projectList(self):
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
            }


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
    project_id = db.Column(db.Integer, db.ForeignKey('Project.id', ondelete='CASCADE'),  nullable=False)
   

    targetVariable= db.Column(db.String(120)) #'Survived',
    key= db.Column(db.String(120)) #'PassengerId',
    predictSetOut = db.Column(db.ARRAY(db.String)) # predictSetOut=['Survived','PassengerId'],


    #confusionMatrixLabels=[(0,'Not'), (1, 'Survived')],
    scoring = db.Column(db.String(120), default='f1')
    setProjectGoals=db.Column(db.Float, default=0.9)     # {'F1': (0.9,'>')},
   
    # Booleans
    basicAutoMethod = db.Column(db.Boolean(), default=True)
    
    Project = db.relationship('Project', backref=db.backref('Run', cascade='all, delete-orphan'))
 
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
                "setProjectGoals" : self.setProjectGoals,
                "results": results
                }

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

