#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install libraries from the backend folder
pip install -r backend/requirements.txt

# 2. Go inside the backend folder to run Django commands
cd backend

# 3. Collect static files and migrate database
python manage.py collectstatic --no-input
python manage.py migrate