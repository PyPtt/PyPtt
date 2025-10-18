import os

from setuptools import setup

# read the main version from __init__.py
with open('PyPtt/__init__.py', 'r', encoding='utf-8') as f:
    data = f.read().strip()
    version = data.split('__version__ = ')[1].split('\n')[0].strip().strip('\'')
    print('main_version:', version)

# Append dev version for non-master branches in GitHub Actions
github_ref = os.environ.get("GITHUB_REF")
github_run_number = os.environ.get("GITHUB_RUN_NUMBER")

if github_ref and github_run_number and not github_ref.endswith('/master'):
    version = f"{version}.dev{github_run_number}"

print('final version:', version)

with open('version.txt', 'w', encoding='utf-8') as f:
    f.write(version)

# This setup.py is needed for editable installs and for the dynamic version.
setup(version=version)
