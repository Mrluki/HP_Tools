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
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath("../.."))
sys.path.append(os.path.abspath(".."))


# -- Project information -----------------------------------------------------

project = "Hugo Potin tool"
copyright = "2021, Hugo potin. Theme based on Godot dark theme"
author = "Hugo potin"

# The full version, including alpha/beta/rc tags
release = "0.0.1"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinxemoji.sphinxemoji",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autosummary",
]

autosummary_generate = True
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []
global long
autodoc_mock_imports = [
    "PySide2",
    "shiboken2",
    "maya",
    "icon_rc",
    "pymel",
    "Qt",
    "Maya",
    "Sculpt_anim",
    "Reference_manager",
]
todo_include_todos = True
pygments_style = "monokai"
# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_logo = "h_tool_logo.png"
html_theme_options = {
    "logo_only": True,
    "display_version": True,
}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
