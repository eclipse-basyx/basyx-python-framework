# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import datetime

# Add the root directory of the project to sys.path
sys.path.insert(0, os.path.abspath('../..'))



# -- Project information -----------------------------------------------------

project = 'Eclipse BaSyx Python Framework'
project_copyright = str(datetime.datetime.now().year) + ', the Eclipse BaSyx Authors'
author = 'The Eclipse BaSyx Authors'

# The full version, including alpha/beta/rc tags
release = "none"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme',
    'sphinxarg.ext',
    'sphinx_autodoc_typehints'  # Allow TypeVars to be compiled properly.
]

# Add any paths that contain templates here, relative to this directory.
templates_path = []

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# Don't prepend the name of the current module to all classes.
add_module_names = False

# Include all public documented and undocumented members by default.
autodoc_default_options = {
    'members': True,
    'undoc-members': True
}

# Mapping for correctly linking other module documentations.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'dateutil': ('https://dateutil.readthedocs.io/en/stable/', None),
    'lxml': ('https://lxml.de/apidoc/', None),
    'aas_core3': ('https://aas-core30-python.readthedocs.io/en/latest/', None),
}


def on_missing_reference(app, env, node, contnode):
    path = node["reftarget"].split(".")
    # TODO: pyecma376_2 doesn't have a documentation we can link to, so suppress missing reference warnings.
    #  see: https://github.com/rwth-iat/PyECMA376-2/issues/3
    if path[0] == "pyecma376_2":
        return contnode
    return None


def setup(app):
    app.connect("missing-reference", on_missing_reference)


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Fix white-space wrapping in tables. css files specified here will be applied on top of the selected theme.
# See https://github.com/readthedocs/sphinx_rtd_theme/issues/1505
# Once fixed, this can be removed and '_static' can be removed from html_static_path.
html_css_files = ["custom.css"]

# Configuration of the 'Edit on GitHub' button at the top right.
html_context = {
    'display_github': True,
    'github_user': 'eclipse-basyx',
    'github_repo': 'basyx-python-framework',
    'github_version': 'docs',
    'conf_py_path': '/docs/source/'
}
