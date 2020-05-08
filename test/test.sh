#!/usr/bin/env bash

coverage run --source=./manimlib -m unittest discover
echo -e "\ngenerating report..."
coverage html -d test/report
