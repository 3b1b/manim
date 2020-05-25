##### THIS IS FOR TRAVIS BUILDS, DO NOT RUN THIS ON YOUR COMPUTER! #####

choco install python --version=$PYVER
export PATH="/c/$PYDIR:/c/$PYDIR/Scripts:$PATH"
cmd.exe //c "RefreshEnv.cmd"
python -m pip install --upgrade pip
python -m pip install --user -r requirements.txt
python -m pip install --user .