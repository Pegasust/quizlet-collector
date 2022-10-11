#!/usr/bin/env bash

CHROME_VERSION="$(google-chrome --version | cut -d' ' -f3 | cut -d'.' -f1).*"

python3 -m pip install -r requirements.txt
# install chrome web driver
python3 -m pip install chromedriver-binary==${CHROME_VERSION}

