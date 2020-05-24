##### THIS IS FOR TRAVIS BUILDS, DO NOT RUN THIS ON YOUR COMPUTER! #####

choco install python --version=$PYVER
export PATH="/c/$PYDIR:/c/$PYDIR/Scripts:$PATH"
refreshenv
