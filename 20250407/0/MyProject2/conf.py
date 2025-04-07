# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Testik'
copyright = '2025, Bagrov'
author = 'Bagrov'
release = '02.04.2025'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

import os
import sys
import subprocess

year, month = 2025, 9
output_file = f"restcalend-{year}-{month}.rst"
if not os.path.exists(output_file):
    subprocess.run(
            ["python3", "-m", "restcalend", str(year), str(month)], check=True, text=True)

# Включаем расширение для автодокументации
extensions = [
    'sphinx.ext.autodoc',  # Автодокументация
    'sphinx.ext.napoleon',  # Поддержка Google и NumPy стилей docstrings
]


sys.path.insert(0, os.path.abspath('.'))
