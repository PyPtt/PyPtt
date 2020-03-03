@echo off
cls

@rmdir /s /q dist
@rmdir /s /q PyPtt.egg-info
@rmdir /s /q PyPtt\__pycache__

python setup.py sdist
twine upload dist/*

echo Upload finish