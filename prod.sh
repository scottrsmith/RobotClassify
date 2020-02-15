export FLASK_ENV=production
export FLASK_DEBUG=False
export FLASK_APP=app.py

export DATABASE_URL=postgres://aufhyymyagwkob:ab8afcf071e31c3a3ec92ec9a14c5155d8ff25c243598b75399bd12c718c026c@ec2-52-203-160-194.compute-1.amazonaws.com:5432/d4vsnpfh6qmqt1
export AUTH0_CLIENT_ID=924mOUHAkgolmjZN1hT30dpkUYQl8EU9
export AUTH0_DOMAIN=dev-p35ewo73.auth0.com
export AUTH0_CLIENT_SECRET=1TRVqfE_oVC1yzVKW8rtm1gAWjpBeHxjtKO8qVr21ZlCL0bO4hr_m6jGkiJ3fpwQ
export AUTH0_CALLBACK_URL=http://127.0.0.1:5000/callback
export AUTH0_AUDIENCE=robotclassify
export APP_TESTING=False
export APP_TESTING_USERID="XbF8BXBWausifCDdGz9fgh3slknCjrQx@clients"
export WTF_CSRF_ENABLED=True


cd ~/Udacity\ Nanodegree/Full\ Stack\ Developer/robotClassify
flask run
