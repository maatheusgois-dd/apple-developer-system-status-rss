#!/bin/bash

# Change to the script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the feed generator
python3 .github/scripts/generate_all_status_rss.py

# Add changes to git if they exist
if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "chore: update Apple system status RSS feeds [skip ci]"
    git push
fi

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 