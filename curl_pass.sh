echo "Set Flask Environment Variables"
export FLASK_ENV=development
export FLASK_DEBUG=true
export FLASK_APP=app.py

#
# Set the env variables for the Auth0 API test user
echo
echo "Set Auth0 Environment Variables for testing"
export DATABASE_URL="postgresql://localhost:5432/robotclassify_test"
export AUTH0_CLIENT_ID=XbF8BXBWausifCDdGz9fgh3slknCjrQx
export AUTH0_DOMAIN=dev-p35ewo73.auth0.com
export AUTH0_CLIENT_SECRET=VBGhyl47Gww_XEqV5A3r_N4LltUlbjcHTIYjFYxPISJPKcvYOk-7xw-xdcbvRL5l
export AUTH0_CALLBACK_URL=http://127.0.0.1:5000/callback
export AUTH0_AUDIENCE=https://dev-p35ewo73.auth0.com/api/v2/
export APP_TESTING=True
export WTF_CSRF_ENABLED=False
echo 
echo "Set Bearer Token and API userid Envoronment variables:"
export `python3 get_credentials.py | grep 'APP_TESTING_USERID'`
export `python3 get_credentials.py | grep 'TOKEN'`

# 
# Set the env variables with the updated
echo 
echo "Updated UserID and Token environment variables:"
echo "APP_TESTING_USERID=$APP_TESTING_USERID"
echo
echo "TOKEN=$TOKEN"

echo "Home Page"
curl http://localhost:5000/

echo "Docs"
curl -X GET http://localhost:5000/docs/index.html

echo "Projects"
curl -X GET http://localhost:5000/projects \
     -H "Authorization: Bearer $TOKEN"

curl -X GET http://localhost:5000/projects/1 \
                 -H "Authorization: Bearer $TOKEN"

curl -X POST http://localhost:5000/projects/create \
                 -H "Authorization: Bearer $TOKEN" \
                 -F "form-project-name=New Test Project" \
                 -F "form-project-description=Testing Project Create" \
                 -F "form-project-trainingFile=@examples/titanic_train.csv" \
                 -F "form-project-testingFile=@examples/titanic_test.csv"

curl -X PATCH http://localhost:5000/projects/1/edit \
                 -H "Authorization: Bearer $TOKEN" \
                 -F "form-project-name=Titanic Disaster Patch"

curl -X POST http://localhost:5000/projects/search \
                 -H "Authorization: Bearer $TOKEN" \
                 -F "search_term=Titanic"

curl -X DELETE http://localhost:5000/projects/3/delete \
                 -H "Authorization: Bearer $TOKEN"

echo "Runs"

curl -X GET http://localhost:5000/runs/1 \
                 -H "Authorization: Bearer $TOKEN"

curl -X POST http://localhost:5000/runs/create/1 \
                 -H "Authorization: Bearer $TOKEN" \
                 -F "form-run-name=New Curl Run" \
                 -F "form-run-description=Via curl" \
                 -F "form-run-targetVariable=Survived" \
                 -F "form-run-key=PassengerId"\
                 -F "form-run-predictSetOut=PassengerId" \
                 -F "form-run-predictSetOut=Survived" \
                 -F "form-run-scoring=f1"\
                 -F "form-run-modelList=xgbc" \
                 -F "form-run-basicAutoMethod=True"

curl -X DELETE http://localhost:5000/runs/5/delete \
                 -H "Authorization: Bearer $TOKEN"






