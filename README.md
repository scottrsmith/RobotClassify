## Introduction

The RobotClassify app allows for non-data scientest such as citizen developers and other operational people incolced with analizing and
reporting on numbers.  THe goal is to automate the entire ML process (featwure-engineering, training, perediction). This cversion of the app
is optimized for loading datafiles to train with, and test files for predctiona, optimzed for submission in Kaggle comoetitions

MymMotivation for project centers around my interest in machine learning for citizen developers. Taking the complecated tasked of feature engineering, model selection, and training and makeing it a simple point anc click excersie 2without any prior ML Training.


## Project dependencies, local development and hosting instructions,


- Detailed instructions for scripts to install any project dependencies, and to run the development server.
- Documentation of API behavior and RBAC controls

## Runing and Testing instrunctions:

URL:
Auth:
Testing:
https://robotclassify.herokuapp.com/



## Getting Started - Backend

### Installing Dependencies

#### Python 3.7 ####

This project uses python 3.7.

To Install: [Python](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by navigating to the root directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies


- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. 

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension used to handle cross-origin requests from the frontend server. 

- [Auth0](https://auth0.com/docs/getting-started/overview) Provides authentication and authorization as a service

## Database Setup

The app is running with SQLite. No setup needs to be performed.

## Running the server

From within the `backend/src` directory to run the server, execute:

```bash
export FLASK_APP=api.py
export FLASK_ENV=development
flask run
```

## Documentation

### Opening the API Documentation

Documentation is generated with Sphinx.

#### HTML Documentation
From the root folder, open the index file in a browser

```bash
./docs/build/html/index.html
```

#### PDF Documentation

The PDF version of the documentation is located in the root project directory. Named RobotClassifyapi.pdf

### Generating documentation

Documentation is generated with Sphinx.

#### Installing Sphinx and support tools

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


#### Generating the documentation
Generate the documentation with the following commands:

```bash
# From the root project directory
# Convert readme to rst to be included in generated docs
m2r README.md README.rst --overwrite
cp -R README.rst ./docs/source
cd ./docs
make html
# Make pdf
make latexpdf
cd ..
cp -R ./docs/build/latex/RobotClassifyaapi.pdf .
```


## API End Points

The following APIs are available. Detailed html documentation can be found in the 'docs/source' folder.

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
- POST /train/<int:run_id>  (run ML training for a run) post:train



## Error Handling

Errors are returned as JSON objects in the following format:
```bash

{
    "success": False, 
    "error": 400,
    "message": "Bad Request"
}
```

The API will return three error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 405: Method Not Allowed
- 422: Not Processable 
- 500: Internal Server Error


## Testing

Testing is done with Postman. Load and run the test collection: 
.backend/udacity-fsnd-udaspicelatte.postman_collection.json


## Full Stack RobotClassify API Frontend

### Installing Dependencies

#### Installing Node and NPM

This app depends on Nodejs and Node Package Manager (NPM). Before continuing, you must download and install Node (the download includes NPM) from [https://nodejs.com/en/download](https://nodejs.org/en/download/).

#### Installing Ionic Client

The Ionic Command Line Interface is required to serve and build the frontend. Instructions for installing the CLI  is in the [Ionic Framework Docs](https://ionicframework.com/docs/installation/cli).


#### Installing project dependencies

This project uses NPM to manage software dependencies. NPM Relies on the package.json file located in the `frontend` directory of this repository. After cloning, open your terminal and run:

```bash

npm install
```


## Running the Frontend 

To run Ionic from the `frontend` directory run:

```bash

ionic serve
```