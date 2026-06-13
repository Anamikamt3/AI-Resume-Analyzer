#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect all static files into 'staticfiles' directory
python manage.py collectstatic --no-input

# Run database migrations automatically
python manage.py migrate