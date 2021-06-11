#!/bin/bash

export PYTHON_VERSION="3.8.10"

echo "Compiling and installing Python $PYTHON_VERSION"
wget "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"
tar -xf "Python-$PYTHON_VERSION.tgz"
cd "Python-$PYTHON_VERSION"
./configure
make
make install
cd ..

echo "Installing Data Gate CLI"
python3 -m pip install .

echo "Executing tests"
python3 -m unittest discover tests.test_fyre
