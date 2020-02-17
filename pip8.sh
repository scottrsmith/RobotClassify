# OPTION="--show-source --show-pep8"
OPTION=" "
pycodestyle $OPTION app.py
pycodestyle $OPTION models.py
pycodestyle $OPTION forms.py
pycodestyle $OPTION config.py
pycodestyle $OPTION get_credentials.py
pycodestyle $OPTION test_app.py
pycodestyle $OPTION ./mlLib/cleanData.py
pycodestyle $OPTION ./mlLib/exploreData.py
pycodestyle $OPTION ./mlLib/getData.py
pycodestyle $OPTION ./mlLib/mlUtility.py
pycodestyle $OPTION ./mlLib/prepData.py
pycodestyle $OPTION ./mlLib/project.py
pycodestyle $OPTION ./mlLib/trainModels.py
