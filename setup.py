from setuptools import setup
import re
import os

def get_version():
    """
    Read version from __init__.py
    """
    # read the main version from __init__.py
    with open('PyPtt/__init__.py', 'r', encoding='utf-8') as f:
        data = f.read().strip()
        cur_version = data.split('__version__ = ')[1].split('\n')[0].strip().strip('\'')
        print('version:', cur_version)

    return cur_version

version = get_version()

# Append dev version for non-master branches in GitHub Actions
github_ref = os.environ.get("GITHUB_REF")
github_run_number = os.environ.get("GITHUB_RUN_NUMBER")

if github_ref and github_run_number and github_ref != 'refs/heads/master':
    version = f"{version}.dev{github_run_number}"

# output the version
with open('version.txt', 'w', encoding='utf-8') as f:
    f.write(version)
print('version:', version)

setup(
    name='PyPtt',  # Required
    version=version,  # Required
    description='PyPtt\ngithub: https://github.com/PyPtt/PyPtt',  # Required
    long_description=open('README.md', encoding="utf-8").read(),  # Optional
    long_description_content_type='text/markdown',
    url='https://pyptt.cc/',  # Optional

    author='CodingMan',  # Optional
    author_email='pttcodingman@gmail.com',  # Optional
    # https://pypi.org/classifiers/
    classifiers=[  # Optional

        'Development Status :: 5 - Production/Stable',

        'Operating System :: OS Independent',

        'Intended Audience :: Developers',
        'Topic :: Communications :: BBS',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',

        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',

        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: English',
    ],
    keywords=['PTT', 'crawler', 'bot', 'library', 'websockets'],  # Optional

    python_requires='>=3.11',
    packages=['PyPtt'],
    install_requires=[
        'progressbar2',
        'websockets',
        'uao',
        'requests',
        'AutoStrEnum',
        'PyYAML',
    ],
    extras_require={
        'api': [
            'fastapi',
            'uvicorn[standard]',
        ]
    },
    package_data={
        'PyPtt': [
            'ssl/*.pem',
        ],
    }
)