from setuptools import setup, find_packages
import sys, os
"""
打包的用的setup必须引入
"""

VERSION = '0.3.170717'

with open('README.md') as f:
    long_description = f.read()

setup(
    name = 'PTT',
    packages = ['request', 'BeautifulSoup4', 'progressbar2'],
    scripts = [],
    version = VERSION,
    description = long_description,
    author = 'Truth0906',
    author_email = 'thetruth0906@livemail.tw',
    url = 'https://github.com/Truth0906/PTTCrawlerLibrary',
    download_url = 'https://github.com/dokelung/MyProject/tarball/v1.0',
    keywords = ['PTT', 'Crawler'],
    classifiers = [],
)