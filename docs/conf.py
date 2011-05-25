# -*- coding: utf-8 -*-
import sys, os, pkginfo, datetime

pkg_info = pkginfo.Develop(os.path.join(os.path.dirname(__file__),'..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx'
    ]

intersphinx_mapping = dict(
    python=('http://docs.python.org/dev',None),
    )

# General
source_suffix = '.txt'
master_doc = 'index'
project = pkg_info.name
copyright = '2011-%s Simplistix Ltd' % datetime.datetime.now().year
version = release = pkg_info.version
exclude_trees = ['_build']
unused_docs = ['description','ideas']
pygments_style = 'sphinx'

# Options for HTML output
html_theme = 'default'
htmlhelp_basename = project+'doc'

# Options for LaTeX output
latex_documents = [
  ('index',project+'.tex', project+u' Documentation',
   'Simplistix Ltd', 'manual'),
]

