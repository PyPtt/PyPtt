import os
import subprocess
import time

from setuptools import setup


def version_automation_script():
    is_merged = os.environ.get('GITHUB_EVENT_NAME') == 'pull_request'
    branch = os.environ.get('GITHUB_REF_NAME')
    print('is_merged:', is_merged)
    print('branch:', branch)

    # read the main version from __init__.py
    with open('PyPtt/__init__.py', 'r', encoding='utf-8') as f:
        data = f.read().strip()
        main_version = data.split('_main_version = ')[1].split('\n')[0].strip().strip('\'')
        print('main_version version:', main_version)

    version = None
    pypi_version = None
    for i in range(5):
        try:
            # Use wget to retrieve the PyPI version information
            subprocess.run(['wget', '-q', '-O', 'pypi_version.json', 'https://pypi.org/pypi/PyPtt/json'], check=True)
            with open('pypi_version.json', 'r', encoding='utf-8') as f:
                pypi_data = f.read()
            pypi_version = pypi_data.split('"version":')[1].split('"')[1]
            if pypi_version.startswith(main_version):
                min_pypi_version = pypi_version.split('.')[-1]
                # the next version
                version = f"{main_version}.{int(min_pypi_version) + 1}"
            else:
                version = f"{main_version}.0"
            break
        except subprocess.CalledProcessError:
            time.sleep(1)

    if version is None or pypi_version is None:
        raise ValueError('Can not get version from pypi')

    if 'master' not in branch:
        commit_file = '/tmp/commit_hash.txt'
        if os.path.exists(commit_file):
            with open(commit_file, 'r', encoding='utf-8') as f:
                commit_hash = f.read().strip()
        else:
            max_hash_length = 5
            try:
                commit_hash = subprocess.check_output(['git', 'rev-parse', '--long', 'HEAD']).decode('utf-8').strip()
            except subprocess.CalledProcessError:
                commit_hash = '0' * max_hash_length

            commit_hash = ''.join([x for x in list(commit_hash) if x.isdigit()])

            if len(commit_hash) < max_hash_length:
                commit_hash = commit_hash + '0' * (max_hash_length - len(commit_hash))
            commit_hash = commit_hash[:max_hash_length]

            with open(commit_file, 'w', encoding='utf-8') as f:
                f.write(commit_hash)

        version = f"{version}.dev{commit_hash}"

    if '__version__' in data:
        current_version = data.split('__version__ = ')[1].split('\n')[0].strip().strip('\'')
        data = data.replace(f"__version__ = '{current_version}'", f"__version__ = '{version}'")
    else:
        data += f'\n\n__version__ = \'{version}\''

    with open('PyPtt/__init__.py', 'w', encoding='utf-8') as f:
        f.write(data)
        f.write('\n')

    return version


version = version_automation_script()
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
        'requests',
        'AutoStrEnum',
        'PyYAML',
    ],
    package_data={
        'PyPtt': [
            'ssl/*.pem',
        ],
    }
)
