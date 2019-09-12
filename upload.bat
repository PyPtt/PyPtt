@echo off
cls

@rmdir /s /q dist
@rmdir /s /q PTTLibrary.egg-info
@rmdir /s /q PTTLibrary\__pycache__

python setup.py sdist
twine upload dist/*

echo Upload finish