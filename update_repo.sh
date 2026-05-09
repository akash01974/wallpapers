#!/bin/bash

# Navigate to the wallpaper directory (where this script is located)
cd "$(dirname "$0")"

# 1. Update the README gallery
echo "Refreshing README gallery..."
python3 auto_readme.py

# 2. Check if there are any changes to push
if [[ -z $(git status -s) ]]; then
    notify-send "Wallpapers" "No new changes to upload." --icon=folder-pictures
    exit 0
fi

# 3. Stage, Commit, and Push
echo "Uploading changes to GitHub..."
git add .
git commit -m "Auto-update: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

# 4. Notify user of success
if [ $? -eq 0 ]; then
    notify-send "Wallpapers" "Successfully pushed to GitHub!" --icon=vcs-normal
else
    notify-send "Wallpapers" "Failed to push updates. Check your connection." --icon=dialog-error
fi
