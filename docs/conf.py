# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from datetime import datetime
sys.path.insert(0, os.path.abspath('../'))

import PyPtt

project = 'PyPtt'
copyright = f'2017 ~ {datetime.now().year}, CodingMan'
author = 'CodingMan'

version = PyPtt.version
release = PyPtt.version

html_title = f'PyPtt.cc'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_copybutton',
    'sphinx.ext.autosectionlabel',
    'sphinx_sitemap',
]
autosectionlabel_prefix_document = True
html_baseurl = 'https://pyptt.cc/'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'zh_TW'

html_extra_path = ['CNAME', 'robots.txt']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_favicon = "https://raw.githubusercontent.com/PyPtt/PyPtt/master/logo/facebook_profile_image.png"
