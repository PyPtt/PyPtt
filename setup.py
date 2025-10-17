from setuptools import setup

import PyPtt

version = PyPtt.__version__
print('the next version:', version)

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
