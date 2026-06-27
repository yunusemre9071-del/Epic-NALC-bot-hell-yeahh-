#!/bin/bash

# Exit if a command fails
set -e

# Check if there are any changes
if git diff --quiet && git diff --cached --quiet; then
    echo "✅ No changes to commit."
    exit 0
fi

echo "📦 Adding changes..."
git add .

echo "📝 Creating commit..."
git commit -m "Update $(date '+%Y-%m-%d %H:%M:%S')"

echo "🚀 Pushing to GitHub..."
git push

echo "✅ Done!"
