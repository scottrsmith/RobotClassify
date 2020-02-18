export TOKEN="$USER_EDIT_TOKEN"
echo "TOKEN=$USER_EDIT_TOKEN"

export HOST='http://robotclassify.herokuapp.com'


echo "Home Page"
curl http://robotclassify.herokuapp.com/

echo "Docs"
curl -X GET http://robotclassify.herokuapp.com/docs/index.html


echo "Projects"
curl -X GET http://robotclassify.herokuapp.com/projects \
     -H "Authorization: Bearer $USER_EDIT_TOKEN"

curl -X GET http://robotclassify.herokuapp.com/projects/4 \
                 -H "Authorization: Bearer $USER_EDIT_TOKEN"

curl -X POST http://robotclassify.herokuapp.com/projects/create \
                 -H "Authorization: Bearer $USER_EDIT_TOKEN" \
                 -F "form-project-name=New Test Project" \
                 -F "form-project-description=Testing Project Create" \
                 -F "form-project-trainingFile=@examples/titanic_train.csv" \
                 -F "form-project-testingFile=@examples/titanic_test.csv"

curl -X PATCH http://robotclassify.herokuapp.com/projects/4/edit \
                 -H "Authorization: Bearer $USER_EDIT_TOKEN" \
                 -F "form-project-name=Titanic Disaster Patch"

curl -X POST http://robotclassify.herokuapp.com/projects/search \
                 -H "Authorization: Bearer $USER_EDIT_TOKEN" \
                 -F "search_term=Titanic"

curl -X DELETE http://robotclassify.herokuapp.com/projects/15/delete \
                 -H "Authorization: Bearer $USER_EDIT_TOKEN"

echo "Runs"

curl -X GET http://robotclassify.herokuapp.com/runs/8 \
                 -H "Authorization: Bearer $USER_EDIT_TOKEN"

curl -X POST http://robotclassify.herokuapp.com/runs/create/4 \
                 -H "Authorization: Bearer $USER_EDIT_TOKEN" \
                 -F "form-run-name=New Curl Run" \
                 -F "form-run-description=Via curl" \
                 -F "form-run-targetVariable=Survived" \
                 -F "form-run-key=PassengerId"\
                 -F "form-run-predictSetOut=PassengerId" \
                 -F "form-run-predictSetOut=Survived" \
                 -F "form-run-scoring=f1"\
                 -F "form-run-modelList=xgbc" \
                 -F "form-run-basicAutoMethod=True"

curl -X DELETE http://robotclassify.herokuapp.com/runs/17/delete \
                 -H "Authorization: Bearer $USER_EDIT_TOKEN"

curl -X PATCH http://robotclassify.herokuapp.com/runs/13/edit \
                 -H "Authorization: Bearer $USER_EDIT_TOKEN" \
                 -F "form-run-name=Updated Curl Run Patch"

echo "Training"


curl -X GET http://robotclassify.herokuapp.com/train/13/download \
                 -H "Authorization: Bearer $USER_EDIT_TOKEN"



