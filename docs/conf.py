# -*- coding: utf-8 -*-
import datetime, os, pkg_resources

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

intersphinx_mapping = {'http://docs.python.org': None}

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx'
    ]

# General
source_suffix = '.rst'
master_doc = 'index'
project = 'configurator'
copyright = '2011-2014 Simplistix Ltd, 2016-%s Chris Withers' % datetime.datetime.now().year
version = release = pkg_resources.get_distribution(project).version
exclude_patterns = [
    'description.rst',
    '_build'
]
pygments_style = 'sphinx'

# Options for HTML output
html_theme = 'default' if on_rtd else 'sphinx_rtd_theme'
htmlhelp_basename = project+'doc'

# Options for LaTeX output
latex_documents = [
  ('index',project+'.tex', project+u' Documentation',
   'Chris Withers', 'manual'),
]

