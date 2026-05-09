#!/bin/bash

# Navigate to the wallpaper directory
cd "$(dirname "$0")"

# 1. Count new wallpapers before staging
# This looks for untracked files (??) with image extensions
NEW_COUNT=$(git status --porcelain | grep -E "^\?\? .*\.(png|jpg|jpeg|gif|webp)$" | wc -l)

# 2. Update the README gallery
echo "Refreshing README gallery..."
python3 auto_readme.py

# 3. Check if there are any changes (including README updates)
if [[ -z $(git status -s) ]]; then
    notify-send "Wallpapers" "No new changes to upload." --icon=folder-pictures
    exit 0
fi

# 4. Stage, Commit, and Push
echo "Uploading $NEW_COUNT new wallpapers to GitHub..."
git add .
git commit -m "Auto-update: Added $NEW_COUNT new wallpapers on $(date '+%Y-%m-%d')"
git push origin main

# 5. Notify user of success
if [ $? -eq 0 ]; then
    if [ "$NEW_COUNT" -gt 0 ]; then
        MESSAGE="Successfully pushed $NEW_COUNT new wallpapers!"
    else
        MESSAGE="Successfully updated repository!"
    fi
    notify-send "Wallpapers" "$MESSAGE" --icon=vcs-normal
else
    notify-send "Wallpapers" "Failed to push updates. Check your connection." --icon=dialog-error
fi
