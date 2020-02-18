echo "Set Flask Environment Variables"
export FLASK_ENV=development
export FLASK_DEBUG=true
export FLASK_APP=app.py

echo "Set Host"
# export HOST='http://localhost:5000'
export HOST='http://robotclassify.herokuapp.com'

#
# Set the env variables for the Auth0 API test user

export DATABASE_URL=postgres://aufhyymyagwkob:ab8afcf071e31c3a3ec92ec9a14c5155d8ff25c243598b75399bd12c718c026c@ec2-52-203-160-194.compute-1.amazonaws.com:5432/d4vsnpfh6qmqt1
export AUTH0_CLIENT_ID=924mOUHAkgolmjZN1hT30dpkUYQl8EU9
export AUTH0_DOMAIN=dev-p35ewo73.auth0.com
export AUTH0_CLIENT_SECRET=1TRVqfE_oVC1yzVKW8rtm1gAWjpBeHxjtKO8qVr21ZlCL0bO4hr_m6jGkiJ3fpwQ
export AUTH0_CALLBACK_URL=http://127.0.0.1:5000/callback
export AUTH0_AUDIENCE=robotclassify
export APP_TESTING=False
export APP_TESTING_USERID="XbF8BXBWausifCDdGz9fgh3slknCjrQx@clients"
export WTF_CSRF_ENABLED=True

# Use the following URLS to get the Tokens

export USER_EDIT_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1rUkdRalkyUVRNNU56UTVNemt4UkRZM09UQTFOREU1UXpBeVJUTTNSVGxFUlVZNU9URkZOQSJ9.eyJpc3MiOiJodHRwczovL2Rldi1wMzVld283My5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWUyYjRiZDdjYzJkYTgwZTk4MTNmM2UzIiwiYXVkIjpbInJvYm90Y2xhc3NpZnkiLCJodHRwczovL2Rldi1wMzVld283My5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNTgyMDA2NjM0LCJleHAiOjE1ODIwOTMwMzQsImF6cCI6IjkyNG1PVUhBa2dvbG1qWk4xaFQzMGRwa1VZUWw4RVU5Iiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTpwcm9qZWN0IiwiZGVsZXRlOnJ1biIsImdldDpwcm9qZWN0IiwiZ2V0OnJ1biIsImdldDp0cmFpbiIsInBhdGNoOnByb2plY3QiLCJwYXRjaDpydW4iLCJwb3N0OnByb2plY3QiLCJwb3N0OnJ1biJdfQ.F90COO7vpsOIEuVnm2Zj1S43PqxM6B9yKiSTH5KLrL85w7uFe63V0kEIfOuubSFjwwqRqra_7MFGqueaGGnmCLqKuoq2vwNV9WXOyVr11HjFtpwowesC7iPBcABKnZEYkh8v0TQRauLUuxvpP2INbxwgvuc2mU7FICGD8w2qPCB1lfw7z8C2hs7RmXiUKXpdT_N5pDcDkD33fkSKwicXhT6TyxAW_dHzLfCYm2_EfslkNguuK5jwH_Y4G1oJww3zP3h2LtaBHaXBe1Jsy10DCIBHAPLDXHIwx0WMV91KkJudCnsHHj_--T2gBYqN9SzNRLcnR_gV9TF6bfk97EMJKA"
export USER_VIEW_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1rUkdRalkyUVRNNU56UTVNemt4UkRZM09UQTFOREU1UXpBeVJUTTNSVGxFUlVZNU9URkZOQSJ9.eyJpc3MiOiJodHRwczovL2Rldi1wMzVld283My5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWUyYjRjMjAxZDFmZDgwZjAzMjVkOWY5IiwiYXVkIjpbInJvYm90Y2xhc3NpZnkiLCJodHRwczovL2Rldi1wMzVld283My5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNTgyMDA2Njc5LCJleHAiOjE1ODIwOTMwNzksImF6cCI6IjkyNG1PVUhBa2dvbG1qWk4xaFQzMGRwa1VZUWw4RVU5Iiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTpwcm9qZWN0IiwiZGVsZXRlOnJ1biIsImdldDpwcm9qZWN0IiwiZ2V0OnJ1biIsImdldDp0cmFpbiIsInBhdGNoOnByb2plY3QiLCJwYXRjaDpydW4iLCJwb3N0OnByb2plY3QiLCJwb3N0OnJ1biJdfQ.m9HPAg0INhV1vY9Zgq_PJF59uoWC67BzO_O7xnU0PmhT9DJsIzvYFoCpszHw-t_UnnuXYqIVedVTR4DR_e9owzlRlRovxjD43Zx5MRsxEPt67RD3ifHBh7gmdxlYWWM7kHjxQTeB8tFqmEG1J60fu_7aW90kdTI0DuDbwoRu7gf-xa8ABChKy4a8qDmxJx2WM7rhBkgn8Cwin3T831yKLgFIp7Mc5K-xit8E--VBsUmOQjU7oXp9VL2ephPNiK94E5LCKyhPjRaNzHzRr-w4rZvAFFtk8wdIhTdtjMAaOd4SfjZoMAaiXzmSsVvnhqTuEgUr0whIiRWod1RprkTtNg"