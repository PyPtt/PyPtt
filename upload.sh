#!/bin/sh

echo PTT Library uploader v 1.0.1

rm -r dist build

python3 setup.py sdist
twine upload dist/*


echo Upload finish