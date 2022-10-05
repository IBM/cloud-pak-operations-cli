#!/bin/bash

echo "Installing IBM Cloud Pak Operations CLI"
python3 -m pip install --no-warn-script-location --user .

echo "Executing tests"
python3 -m unittest discover tests.test_fyre
