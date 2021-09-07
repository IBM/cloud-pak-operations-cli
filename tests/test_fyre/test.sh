#!/bin/bash

echo "Installing Db2 Data Gate CLI"
python3 -m pip install --user .

echo "Executing tests"
python3 -m unittest discover tests.test_fyre
