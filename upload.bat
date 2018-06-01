@echo off
cls

rmdir /s /q dist
rmdir /s /q PTTLibrary.egg-info

python setup.py sdist
twine upload dist/*

echo Upload finish