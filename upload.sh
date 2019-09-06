#!/bin/sh

echo PTT Library uploader v 1.0.0

rm dist/*

python3 setup.py sdist
twine upload dist/*


echo Upload finish