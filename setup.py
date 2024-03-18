# Always prefer setuptools over distlib_utils
import time

import requests
from setuptools import setup

# read the main version from __init__.py
with open('PyPtt/__init__.py', 'r', encoding='utf-8') as f:
    data = f.read().strip()
    main_version = data.split('_main_version = ')[1].split('\n')[0].strip().strip('\'')
    print('main_version version:', main_version)

version = None
pypi_version = None
for i in range(5):
    response = requests.get('https://pypi.org/pypi/PyPtt/json')

    if response.status_code == 200:
        pypi_version = response.json()['info']['version']
        if pypi_version.startswith(main_version):
            min_pypi_version = pypi_version.split('.')[-1]
            # the next version
            version = f"{main_version}.{int(min_pypi_version) + 1}"
        else:
            version = f"{main_version}.0"
        break
    time.sleep(1)

if version is None or pypi_version is None:
    raise ValueError('Can not get version from pypi')

print('the next version:', version)

if '__version__' in data:
    current_version = data.split('__version__ = ')[1].split('\n')[0].strip().strip('\'')
    data = data.replace(f"__version__ = '{current_version}'", f"__version__ = '{version}'")
else:
    data += f'\n\n__version__ = \'{version}\''

with open('PyPtt/__init__.py', 'w', encoding='utf-8') as f:
    f.write(data)
    f.write('\n')

setup(
    name='PyPtt',  # Required
    version=version,  # Required
    description='PyPtt\ngithub: https://github.com/PyPtt/PyPtt',  # Required
    long_description=open('README.md', encoding="utf-8").read(),  # Optional
    long_description_content_type='text/markdown',
    url='https://github.com/PyPtt/PyPtt',  # Optional

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

        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',

        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: English',
    ],
    keywords=['PTT', 'crawler', 'bot', 'library', 'websockets'],  # Optional

    python_requires='>=3.8',
    packages=['PyPtt'],
    install_requires=[
        'progressbar2',
        'websockets',
        'uao',
        'SingleLog',
        'requests',
        'AutoStrEnum'
    ],
)
