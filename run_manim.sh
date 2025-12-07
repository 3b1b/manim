#!/usr/bin/env bash
# Quick helper to create a venv, install dependencies, and render the example
set -euo pipefail
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Render the SimpleTransform scene (low quality, preview)
manim -pql Animation.py SimpleTransform
