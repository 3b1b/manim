#!/bin/bash

pip install sphinx_rtd_theme
make --directory docs/ html
openssl aes-256-cbc -K $encrypted_1b28e850a424_key \
                    -iv $encrypted_1b28e850a424_iv \
                    -in travis/crypt.enc \
                    -out travis/crypt -d
tar xf travis/crypt
travis/deploy_docs.sh
