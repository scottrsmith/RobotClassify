export TOKEN="$USER_VIEW_TOKEN"
echo "TOKEN=$USER_VIEW_TOKEN"

export HOST='http://robotclassify.herokuapp.com'


echo "Home Page"
curl http://robotclassify.herokuapp.com/

echo "Docs"
curl -X GET http://robotclassify.herokuapp.com/docs/index.html


echo "Projects"
curl -X GET http://robotclassify.herokuapp.com/projects \
     -H "Authorization: Bearer $USER_VIEW_TOKEN"

curl -X GET http://robotclassify.herokuapp.com/projects/7 \
                 -H "Authorization: Bearer $USER_VIEW_TOKEN"


curl -X POST http://robotclassify.herokuapp.com/projects/search \
                 -H "Authorization: Bearer $USER_VIEW_TOKEN" \
                 -F "search_term=Titanic"

echo "Runs"

curl -X GET http://robotclassify.herokuapp.com/runs/12 \
                 -H "Authorization: Bearer $USER_VIEW_TOKEN"


echo "Training"


curl -X GET http://robotclassify.herokuapp.com/train/12/download \
                 -H "Authorization: Bearer $USER_VIEW_TOKEN"



