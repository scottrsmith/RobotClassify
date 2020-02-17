## Introduction ##

RobotClassify allows for non-data scientest such as citizen developers and other operational people involved with analizing and
reporting on business data.  The goal is to automate the entire ML process (feature-engineering, training, prediction). 

This version of the app is optimized for loading datafiles to train with, and test files for predctiona, optimzed for submission in Kaggle competitions. Currently, we only support Machine Learning classification problems. The Machine Learning component is based upon mlLib, a library that I created to put into code, techniques I have learning during my ML course work. T

My motivation for project centers around my interest in machine learning for citizen developers. Taking the complecated tasked of feature engineering, model selection, and training and makeing it a simple point and click excersie without any prior machine learning training. 

Using RobotClassify requires four simple steps that can all be accomplished via the RobotClassify.herokuapp.com.

1. Load a CSV data file. This is done be creating a project and specifing the training and test files (examples are founx in the examples folder)
2. Create a Run. The run record defines the file attributes and the nature of the training. FOr this, we need to specify:
- The target variable that is to be predicted
- Record Key column 
- Predict set out. These are the columns that are used to create the predict file in a format that can be used to submit the test results in a Kaggle comopetition
- Classification model to train 
- Scoring method
- Algoritym type (There are two approaches used to automate feature engineering)
3. Run the training
4. Review the results

## Implementation Ovweview ##

The application is build with Flask and Flask What-the-forms for the frontend. 

Roles
There are two roles:
Editor: Able to create, update, train and delete projects and training runs
Viewer: Only able to view results

### API End Points ###

The following APIs endpoints are available. Detailed html documentation can be found at 
https://robotclassify.herokuapp.com/docs/index.html


-- Home Page --
- GET / (home)

-- Documentation Page --
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



## Project dependencies, local development and hosting instructions ##

- Detailed instructions for scripts to install any project dependencies, and to run the development server.
- Documentation of API behavior and RBAC controls


## Runing and Testing Instrunctions ##

URL: https://robotclassify.herokuapp.com/


There are three approaches to running and evaluating RobotClassify:
1. Web
2. UnitTest
3. Curl

There are scripts to help with each one.


### Running on the Web ####

For example, the Titanic Kaggle competeition (https://www.kaggle.com/c/titanic.com), provides two data sets, the Training set and test set. Loading these into Robot Classify, we would set the run paramatgers as follows:
- Target Variable: Survived
- Record Key: PassengerID
- Predict set out: Survuved, PassengerID
- Classification model: xgbc
- Scoring method: f1
- Use Algorithm I for feature engineering: True

This will give a training result that would put you in the top 8% of competitors.

### UnitTest ###

Unittests are run using the script `test.sh`. This script requires Postgress on the local machine where the test is being run.

The `test.sh` script will:
1. Create the robotclassiy_test database
2. Get a Token and User ID for the API user (placed into environment variables)
3. Populate the test database with data for the API user
4. Run the tests

### Curl ###
The current implementation is enabled for Curl. Curl will allow for operations against the product database (Hosted on Amazon/Heroku)

curl_pass.sh
curl_fail.sh
curl.sh (setup the environment variables to run Curl manually)


### Getting updated tokens ###
If you need to get an updated token, you need to login to the Web app and issue the following URL:

https://robotclassify.herokuapp.com/jwt

This will retrive the current jwt token for the logged in user.


## Installation ##

### Python 3.7 ###

This project uses python 3.7

To Install [Python](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

### PIP Dependencies ###

Once you have your virtual environment setup and running, install dependencies by navigating to the root directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

### Key Dependencies ###

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. 

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension used to handle cross-origin requests from the frontend server. 

- [Auth0](https://auth0.com/docs/getting-started/overview) Provides authentication and authorization as a service

- [Postgres](http://example.com) DOES XXX

- [Heroku](http://example.com) DOES XXX

- [Flask-WTF](http://example.com) DOES XXX

- [mlLib](http://example.com) DOES XXX

- [InitTest](http://example.com) DOES XXX

- [FlaskMigrate](http://example.com) DOES XXX


## Database Setup ##

The app is running Postgres SQL.

## Running the server ##

From within the `root` directory to run the server, execute:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

## Documentation ##

### HTML Documentation ###

Live documentation, including this readme, can be found at https://robotclassify.herokuapp.com/docs/index.html

### PDF Documentation ###

The PDF version of the documentation is located in the root project directory. Named robotclassify.pdf

### Generating documentation ###

Documentation is generated with Sphinx.

#### Installing Sphinx and support tools ####

To install Sphinx, reference the documents at https://www.sphinx-doc.org/en/master/usage/installation.html

For example:

```bash
pip install -U sphinx
```

Install dependencies by navigating to the `root` project directory and running:

```bash
cd docs
pip install m2r
pip install recommonmark
pip install rinohtype
pip install -r requirements.txt
```

#### Generating documentation ####

Documentation is generated with Sphinx. Use `docs.sh` in the docs folder to generate the documentation




## Error Handling

Errors are returned as JSON objects in the following format:

```bash
{
    "success": False, 
    "error": 400,
    "message": "Bad Request"
}
```

The API returns multiple error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 405: Method Not Allowed
- 422: Not Processable 
- 500: Internal Server Error


## Testing

Testing is done with UnitTest and curl.  UnitTest is setup to create and use a local Postgres database while Curl is setup to  run commands against the

### Testing with UnitTest ###

### Testing with Curl ###

## Development Notes

- Flask Sessions are maintained between REST Calls for Web-based use of the API. The implementation is based upon 
- CSRF protection is disabled for certain REST calls to faciliate testing cia CuRL.
- Patch and Delete functions are only avialable via API calls
- UnitTest uses a local postgres database
- UnitTest uses API App Auth0 credentials (verses using Auth0 Web App quickstart code)
Auth0 Management API (Test Application)
- Tokens in the headers are used for API authentication
