# Always prefer setuptools over distlib_utils

from setuptools import setup

# get version from __init__.py
with open('PyPtt/__init__.py') as f:
    text = f.read()

version = [line for line in text.split('\n') if line.startswith('__version__')][0]
version = version[version.find("'") + 1:]
version = version[:version.find("'")]

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
