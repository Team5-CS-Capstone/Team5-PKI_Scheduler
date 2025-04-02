import os
import sys
sys.path.insert(0, os.path.abspath('../python-db'))

project = 'PKI Scheduler - Team 5'
copyright = '2025, Charlie, Zaid, Brian, John, Brady'
author = 'Charlie, Zaid, Brian, John, Brady'
release = '0.0.1'

extensions = [
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']