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
# Create the datebases
echo
echo "Create and populate postgres databases:"

dropdb robotclassify_test
createdb robotclassify_test

#
# updated the sql script with the API username
sed "s/APP_TESTING_USERID/$APP_TESTING_USERID/g" < populate_test.sql > _populate_test.sql
psql robotclassify_test < _populate_test.sql

# 
# Set the env variables with the updated
echo 
echo "Updated UserID and Token environment variables:"
echo "APP_TESTING_USERID=$APP_TESTING_USERID"
echo
echo "TOKEN=$TOKEN"

#
# Run the tests
echo
echo
echo "Run Unit tests:"
python3 test_app.py