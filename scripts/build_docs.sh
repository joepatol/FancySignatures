#!/bin/bash

# Install required packages
pip install click
pip install markdown

VERSION=$(python fancy_signatures/__version__.py)

# Build the release notes
python scripts/compile_release_notes.py --version=$VERSION

# Build docs using pdoc, output to docs folder
pdoc ./fancy_signatures -o ./docs

# Commit and push to git
git add *
git commit -a -m "workflow docs build"
git push
