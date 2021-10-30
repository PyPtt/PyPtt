#!/bin/sh

echo PyPtt uploader v 1.0.1

rm dist/*

python3 setup.py sdist bdist_wheel
twine upload dist/*

echo Upload finish