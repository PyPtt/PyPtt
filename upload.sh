#!/bin/sh

echo PyPtt uploader v 1.0.1

rm dist/*
python3 setup.py sdist bdist_wheel --universal

case $1 in
release)
    twine upload dist/*
    ;;
test)
    echo upload to testpypi
    python3 -m twine upload --repository testpypi dist/*
    ;;

*)
    echo "unknown command [$@]"
    ;;
esac

echo Upload finish