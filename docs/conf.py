# flake8: noqa
# pylint: skip-file
# Configuration file for the Sphinx documentation builder.

#
# -- Path setup --------------------------------------------------------------
#

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))


#
# -- Project information -----------------------------------------------------
#

project = "Flask APScheduler"
copyright = "2015, Vinicius Chiele"


#
# -- General configuration ---------------------------------------------------
#

extensions = [
    "sphinx.ext.extlinks",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
    "sphinx_panels",
    "myst_parser",
]

templates_path = ["_templates"]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "venv"]

pygments_style = "colorful"

#
# -- Options for HTML output -------------------------------------------------
#

html_theme = "furo"
html_title = "Flask APScheduler"
#html_logo = "images/icon-512x512.png"
#html_favicon = "images/favicon.ico"

html_theme_options = {
    #"sidebar_hide_name": True,
}
