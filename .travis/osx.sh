##### THIS IS FOR TRAVIS BUILDS, DO NOT RUN THIS ON YOUR COMPUTER! #####

brew update
brew install openssl readline
brew outdated pyenv || brew upgrade pyenv
brew install ffmpeg
brew install pyenv-virtualenv
pyenv install $PYVER
export PYENV_VERSION=$PYVER
export PATH="/Users/travis/.pyenv/shims:${PATH}"
pyenv virtualenv venv
source ~/.pyenv/versions/venv/bin/activate
python --version
