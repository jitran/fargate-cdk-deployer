#!/bin/bash -e

venv=${1:-.env}

rm -rf .pytest_cache
python3 -m venv $venv
source $venv/bin/activate
pip install -r requirements.txt
pycodestyle --ignore=E501 modules tests *.py
pytest -vv
