@echo off
cls

@rmdir /s /q dist
@rmdir /s /q PTTLibrary.egg-info

python setup.py sdist

@rmdir /s /q PTTLibrary\__pycache__

twine upload dist/*

echo Upload finish