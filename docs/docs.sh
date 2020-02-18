cd ..
m2r README.md README.rst --overwrite
cp -R README.rst ./docs/source
cd ./docs
make html
#make latexpdf
#cp -R ./build/latex/robotclassify.pdf .
