# -*- coding: utf-8 -*-
#
# DWaveNetworkX documentation build configuration file, created by
# sphinx-quickstart on Wed Jul 26 10:55:26 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# This file contains function linkcode_resolve, based on 
# https://github.com/numpy/numpy/blob/main/doc/source/conf.py, 
# which is licensed under the BSD 3-Clause "New" or "Revised" 
# license: ./licenses/numpy.rst  

import os
import sys
import subprocess
import inspect      
import pkg_resources

config_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.system('dwave install --yes inspector')   # To run doctests on examples with inspector

# -- General configuration ------------------------------------------------
# import sphinx
# if sphinx.__version__  # can check here

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autosummary',
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.linkcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.ifconfig',
    'breathe',
    'sphinx_panels'
]

autosummary_generate = True

# templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = ['.rst', '.md']

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Ocean Documentation'
copyright = u'D-Wave Systems Inc'
author = u'D-Wave Systems Inc'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
import dwaveoceansdk.package_info as sdk

version = sdk.__version__
# The full version, including alpha/beta/rc tags.
release = version

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None


add_module_names = False
# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

linkcheck_ignore=[r'.clang-format',                   # would need symlink
                  r'https://cloud.dwavesys.com/leap', # redirects, many checks
                  r'https://scipy.org',               # ignores robots
                  r'LICENSE',                         # would need symlink, checked by submodule
                  r'CONTRIBUTING',                    # would need symlink, checked by submodule
                  ]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

doctest_global_setup = """
from __future__ import print_function, division
import operator         # Used by dwave-binarycsp

# Set up mocking for DWaveSampler 
from dwave.system.testing import MockDWaveSampler
import dwave.system
import hybrid
dwave.system.DWaveSampler = MockDWaveSampler
hybrid.samplers.DWaveSampler = MockDWaveSampler

from dwave.system import *
from dwave.embedding import *

import networkx as nx
import dwave_networkx as dnx

import dimod
import dwavebinarycsp

from hybrid.samplers import *
from hybrid.core import *
from hybrid.utils import *
from hybrid.decomposers import *
from hybrid.composers import *
from hybrid.flow import *

import penaltymodel.core as pm
import penaltymodel.cache as pmc
#import penaltymodel.maxgap as maxgap
import penaltymodel.mip as mip
import penaltymodel.lp as lp

import dwave.inspector
"""


# Path to the cpp xml files
breathe_projects = {"minorminer": os.path.join(
    config_directory, '../minorminer/docs/build-cpp/xml/')}

breathe_default_project = "minorminer"

breathe_default_members = ('members', )

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
import sphinx_rtd_theme
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Joel December 11, 2017: added for mathjax operator \vc
# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = ["."]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Joel April 2018: table widths bug in Read The Docs
# html_context = {
#     'css_files': [
#         '_static/theme_overrides.css',  # override wide tables in RTD theme
#         ],
#      }
def setup(app):
   #app.add_javascript("custom.js")
   app.add_css_file('theme_overrides.css')
   app.add_css_file('cookie_notice.css')
   app.add_js_file('cookie_notice.js')
   app.add_config_value('target', 'sdk', 'env')


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'docs'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).

latex_preamble = r"""
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsbsy}
\usepackage{braket}
\usepackage{circuitikz}

\newcommand{\vc}[1]{\pmb{#1}}
"""

latex_documents = [
    (master_doc, 'docs.tex', u'docs Documentation',
     u'D-Wave Systems Inc', 'manual'),
]

#
# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'docs', u'dock Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'dock', u'dock Documentation',
     author, 'dock', 'One line description of project.',
     'Miscellaneous'),
]


# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']


# Joel May 16: WARNING: failed to reach any of the inventories with the following issues:
# WARNING: intersphinx inventory 'http://networkx.readthedocs.io/en/latest/objects.inv' not
# fetchable due to <class 'requests.exceptions.HTTPError'>: ('intersphinx inventory %r not
# fetchable due to %s: %s', 'http://networkx.readthedocs.io/en/latest/objects.inv', <class
# 'requests.exceptions.HTTPError'>, HTTPError(...))

# Example configuration for intersphinx: refer to the Python standard library.
#intersphinx_mapping = {'https://docs.python.org/': None,
#                       'http://networkx.readthedocs.io/en/latest/': None}
intersphinx_mapping = {'python': ('https://docs.python.org/3/', None),
    'numpy': ('http://docs.scipy.org/doc/numpy/', None),
    'bson': ('https://api.mongodb.com/python/current/', None),
    'networkx': ('https://networkx.github.io/documentation/stable/', None),
    'sysdocs_gettingstarted': ('https://docs.dwavesys.com/docs/latest/', None),
    'oceandocs': ('https://docs.ocean.dwavesys.com/en/stable/', None),
    }

# sort documentation they way the appear in the source file
autodoc_member_order = 'bysource'

# show inherited members
# autodoc_default_flags = ['members', 'undoc-members', 'inherited-members', 'show-inheritance']

read_the_docs_build = os.environ.get('READTHEDOCS', None) == 'True'

if read_the_docs_build:

    subprocess.call('cd ../minorminer/docs/; make cpp', shell=True)

# Link to GitHub source
github_map = {'dwavebinarycsp': 'dwavebinarycsp',
              'cloud': 'dwave-cloud-client',
              'dimod':  'dimod',
              'dwave_networkx': 'dwave-networkx',
              'greedy': 'dwave-greedy',
              'hybrid': 'dwave-hybrid',
              'inspector': 'dwave-inspector',
              'minorminer': 'minorminer',
              'neal': 'dwave-neal',
              'penaltymodel': {'cache': 'penaltymodel_cache',
                               'core': 'penaltymodel_core',
                               'lp': 'penaltymodel_lp',
                               'maxgap': 'penaltymodel_maxgap',
                               'mip': 'penaltymodel_mip'},
              'preprocessing': 'dwave-preprocessing',
              'system': 'dwave-system',
              'embedding': 'dwave-system',
              'tabu': 'dwave-tabu'}

reqs = pkg_resources.get_distribution('dwave-ocean-sdk').requires(extras=['all'])
pkgs = [pkg_resources.get_distribution(req) for req in reqs]
versions = {pkg.project_name: pkg.version for pkg in pkgs}
versions['penaltymodel-core'] = versions.pop('penaltymodel')

def linkcode_resolve(domain, info):
    """
    Find the URL of the GitHub source for dwave-ocean-sdk objects.
    """
    # Based on https://github.com/numpy/numpy/blob/main/doc/source/conf.py
    # Updated to work on multiple submodules and fall back to next-level 
    # module for objects such as properties

    if domain != 'py':
        return None

    obj={}
    obj_inx = 0
    obj[obj_inx] = sys.modules.get(info['module'])
    for part in info['fullname'].split('.'):
        obj_inx += 1
        try:
            obj[obj_inx] = getattr(obj[obj_inx - 1], part)
        except Exception:
            pass

    # strip decorators, which would resolve to the source of the decorator
    # https://bugs.python.org/issue34305
    for i in range(len(obj)):
           obj[i] = inspect.unwrap(obj[i])

    fn = None
    for i in range(len(obj)-1, -1, -1): 
        try: 
           fn = inspect.getsourcefile(obj[i]) 
           if fn: 
              obj_inx = i
              break 
        except:
           pass 

    linespec = ""
    try:
        source, lineno = inspect.getsourcelines(obj[obj_inx])
        if obj_inx != 0:
           linespec = "#L%d" % (lineno) 
    except Exception:
        linespec = ""

    if not fn or not "site-packages" in fn:
       return None
    
    if ".egg" in fn:
       fn = fn.replace(fn[:fn.index("egg")+len("egg")], "")   
    else:
       fn = fn.replace(fn[:fn.index("site-packages")+len("site-packages")], "") 

    repo = fn.split("/")[1] if  \
           (fn.split("/")[1] != "dwave") and (fn.split("/")[1] != "penaltymodel") \
           else fn.split("/")[2]

    if fn.split("/")[1] == 'penaltymodel':
        pm_module = github_map['penaltymodel'][repo] 
        pm_ver = versions[github_map['penaltymodel'][repo].replace('_', '-')]
        fn = "https://github.com/dwavesystems/penaltymodel/tree/{}-{}/{}{}".format( \
             repo, pm_ver, pm_module, fn)
    else:
        pm_module = github_map[repo] 
        pm_ver = versions[github_map[repo]]
        fn = "https://github.com/dwavesystems/{}/blob/{}{}".format(pm_module, pm_ver, fn) 
 
    return fn + linespec
