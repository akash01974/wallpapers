#!/bin/bash
cd "$(dirname "$0")"
# Try to run the python script and keep window open if it fails
python3 repo-update.py || (echo "Error starting script. Press Enter to close."; read)
