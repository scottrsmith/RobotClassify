RobotClassify allows for non-data scientists such as citizen developers and other operational people involved with analyzing and
reporting on business data.  The goal is to automate the entire ML process (feature-engineering, training, prediction). 

This version of the app is optimized for loading data files to train with, and test files for predictions. Prediction files are optimized for submission in Kaggle competitions. Currently, we only support Machine Learning classification problems. The Machine Learning component is based upon mlLib, a library that I created, put into code techniques I have learning during my ML studies.

My motivation for RobotClassify centers around my interest in making machine learning accessible for citizen developers. Taking the complicated task of feature engineering, model selection, and training and making it a simple point and click exercise without any prior machine learning training. 

Using RobotClassify requires four simple steps that can all be accomplished via the RobotClassify.herokuapp.com.

* Load a CSV data file. This is done by creating a project and specifying the training and test files (examples are found in the examples folder)
* Create a Run. The run record defines the file attributes and the nature of the training. For this, we need to specify:
    - The target variable that is to be predicted
    - Record Key column 
    - Predict set out. These are the columns that are used to create the predict file in a format that can be used to submit the test results in a Kaggle competition
    - Classification model to train 
    - Scoring method
    - Algorithm type (There are two approaches used to automate feature engineering)
* Run the training
* Review the results

# Running and Testing Instructions #

RobotClassify can be accessed from the URL: https://robotclassify.herokuapp.com/.

## Running on the Web ###
The web interface provides a 4 step approach to completing training and getting a result:
* Load the training and test files by creating a project
* Create a run record. The run record describes the test attributes
* Run the training
* Download the results file from the predictions

For example, the Titanic Kaggle competition (https://www.kaggle.com/c/titanic) provides two data sets, the training set and a test set. Loading these into RobotClassify, we would set the run parameters as follows:
- Target Variable: Survived
- Record Key: PassengerID
- Predict set out: Survived, PassengerID
- Classification model: xgbc
- Scoring method: f1
- Use Algorithm I for feature engineering: True

Following these instructions will give a training result that would put you in the top 8% of competitors.

# Implementation Overview #

The application was written with Flask as the backend and Flask What-the-forms for the frontend. 

## Roles ##

DISABLED FOR NOW - ALL PERMISSIONS AVAILABLE FOR ALL USERS.

There are two roles:
- Viewer Role: Viewers can only view projects, runs, and their results.
- Editor Role: Editors can create projects, runs, and perform training

| permissions |  Editor  | Viewer | Description | 
| ----------- | --------- | ---------- | --------------------------------| 
| get:project | Yes | Yes | get a single, or list of projects |
| post:project | Yes |  | Create a new project or search |
| patch:project | Yes | | Update a project attributes |
| delete:project | Yes |  | Delete a project and its runs |
| get:run | Yes | Yes | Get a run or download run results |
| post:run | Yes |  | Create a new run |
| patch:run | Yes |  | Update a run's attributes |
| delete:run | Yes |  | Delete a run |
| get:train | Yes |  | Run ML Training  |


## API End Points ##

The following APIs endpoints are available. Detailed HTML documentation on these end points,
including this file, can be found at https://robotclassify.herokuapp.com/docs/index.html

These are the end-points, with the short description and role.

-- Home Page --
- GET / (home)

-- Documentation Page --
- GET /docs/index.html

--- Projects ---
- GET /projects (List all projects) - get:project
- GET /projects/<int:project_id> (List a single project) - get:project
- POST/GET /projects/create (create a new project) - post:project
- PATCH /projects/<int:project_id>/edit (edit a project) - patch:project
- DELETE /projects/<project_id>/delete (Delete a project) - delete:project

--- Runs ---
- GET /runs/<int:run_id>  (Display a run results) - get:run
- GET/POST /runs/create/<int:project_id> (Create a run) - get:post
- DELETE /runs/<int:run_id>/delete (Delete a run) - delete:post
- PATCH /run/<int:run_id>/edit (edit a run) - patch:run

--- Train ---
- GET /train/<int:run_id>  (run ML training for a run) get:train
- GET /train/<int:run_id>/download  (download testing results file,
      kaggle file) get:run


# Installation and Dependencies #

RobotClassify source is loacted at: https://github.com/scottrsmith/RobotClassify

## Python ##

This project uses python 3.7

To Install [Python](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

## PIP Dependencies ##

Once you have your virtual environment setup and running, install dependencies by navigating to the root directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

## Key Dependencies ##

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. 

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension used to handle cross-origin requests from the frontend server. 

- [Auth0](https://auth0.com/docs/getting-started/overview) Provides authentication and authorization as a service

- [Postgres](https://www.postgresql.org/download/) Postgres SQL database

- [Heroku](http://heroku.com) App Hosting

- [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/install.html) Flask What-the-forms

- [mlLib](https://github.com/scottrsmith/mllib) Machine Learning Training lib. Included in robot classify

- [InitTest](https://docs.python.org/3/library/unittest.html) Test automation for Python

- [FlaskMigrate](https://flask-migrate.readthedocs.io/en/latest/) Manages SQLAlchemy database migrations for Flask applications using Alembic

- [scikit-learn](https://scikit-learn.org/stable/) Simple and efficient tools for predictive data analysis

## Database Setup ##

The UnitTest is running Postgres SQL as the local souce database.

How to start/stop:
https://stackoverflow.com/questions/7975556/how-to-start-postgresql-server-on-mac-os-x

## Running the flask server ##

On a local machine, from within the `root` directory to run the server, execute `dev.sh`

# Documentation #

## HTML Documentation ##

Live documentation, including this readme, can be found at https://robotclassify.herokuapp.com/docs/index.html

## PDF Documentation ##

The PDF version of the documentation is located in the root project directory. Named robotclassify.pdf

## Generating documentation ##

Documentation is generated with Sphinx.

### Installing Sphinx and support tools ###

To install Sphinx, reference the documents at https://www.sphinx-doc.org/en/master/usage/installation.html

### Generating documentation ###

Documentation is generated with Sphinx. Use `docs.sh` in the docs folder to generate the documentation.
Generated docs are located at https://robotclassify.herokuapp.com/docs/index.html

# Error Handling

Errors are returned as JSON objects in the following format:

```bash
{
    "success": False, 
    "error": 401,
    "message": "Premission Error"
    "description": "401: Authorization header is expected."
}
```

The API returns multiple error types when requests fail:
- 400: Bad Request
- 401: Permission Error
- 404: Resource Not Found
- 405: Method Not Allowed
- 422: Not Processable 
- 500: Server Error


# Testing

Testing is done with UnitTest and curl.  UnitTest is set up to create and use a local Postgres database while Curl is set up to  run commands against the


# Development Notes

- Flask Sessions are maintained between REST Calls for Web-based use of the API. The implementation is based upon Flask Sessions and the quickstart example app from Auth0 for Web applications.
- CSRF protection is disabled for certain REST calls to facilitate testing via CuRL.
- Patch and Delete functions are only available via API calls
- UnitTest uses a local Postgres database
- UnitTest uses Auth0 API App credentials (verses using Auth0 Web App quickstart code)
Auth0 Management API (Test Application)
- Tokens in the headers are used for API authentication
