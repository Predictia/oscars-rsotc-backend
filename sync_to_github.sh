#!/bin/bash

# Configuration
SOURCE_DIR="/home/pereza/git/oscars-rsotc/backend/"
DEST_DIR="/home/pereza/git/oscars-rsotc/github/oscars-rsotc-backend/"

echo "🚀 Synchronizing changes from $SOURCE_DIR to $DEST_DIR..."

# Sync files using rsync, excluding GitLab and local artifacts
rsync -av --progress \
    --exclude='.git/' \
    --exclude='.gitlab-ci.yml' \
    --exclude='.pixi/' \
    --exclude='.mypy_cache/' \
    --exclude='.pytest_cache/' \
    --exclude='.ruff_cache/' \
    --exclude='__pycache__/' \
    --exclude='htmlcov/' \
    --exclude='.coverage' \
    --exclude='venv/' \
    --exclude='.env' \
    "$SOURCE_DIR" "$DEST_DIR"

echo "✅ Synchronization complete."

# Check for changes in the destination repository
cd "$DEST_DIR" || exit
if [ -n "$(git status --porcelain)" ]; then
    echo "📦 Staging changes in $DEST_DIR..."
    git add .
    
    echo "💾 Committing changes..."
    COMMIT_MSG="Sync backend changes: $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MSG"
    
    echo "✨ Changes committed locally to GitHub repository."
    echo "🔔 Note: Remember to 'git push' to update the remote."
else
    echo "🏖️ No changes to commit in the destination repository."
fi
