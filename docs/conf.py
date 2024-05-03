# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------

import os
import sys
sys.path.insert(0, os.path.abspath('../src/griml/'))

project = 'GrIML'
copyright = '2024, Penelope How'
author = 'Penelope How'
release = '0.0.2'

# -- General configuration ---------------------------------------------------

extensions = [    
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',	  
    'sphinx.ext.mathjax',     
    'sphinx.ext.napoleon',
    'myst_parser',
    'sphinx_design' 
]

napoleon_google_docstring = False 
napoleon_numpy_docstring = True   
napoleon_use_ivar = True 

autodoc_mock_imports = ['griml']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------

html_theme = 'renku'
html_static_path = ['_static']
