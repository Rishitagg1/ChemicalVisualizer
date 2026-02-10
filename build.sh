#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies from the backend folder
pip install -r backend/requirements.txt

# Run Django commands (pointing to the backend folder)
python backend/manage.py collectstatic --no-input
python backend/manage.py migrate
