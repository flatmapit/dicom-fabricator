#!/bin/bash
"""
Post-Merge Version Bump Hook for DICOM Fabricator

This script automatically bumps the version number and updates the changelog
when changes are merged into the develop branch.

Usage:
    ./scripts/post-merge-version-bump.sh [patch|minor|major]
    
    patch: 1.0.1 -> 1.0.2 (default, for bug fixes and small changes)
    minor: 1.0.1 -> 1.1.0 (for new features)
    major: 1.0.1 -> 2.0.0 (for breaking changes)

This script should be run after merging feature branches into develop.
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "This script must be run from a git repository"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

# Check if we're on develop branch
if [ "$CURRENT_BRANCH" != "develop" ]; then
    print_warning "Not on develop branch (current: $CURRENT_BRANCH)"
    print_warning "This script is designed to run after merging to develop"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Determine bump type
BUMP_TYPE=${1:-patch}

if [[ ! "$BUMP_TYPE" =~ ^(patch|minor|major)$ ]]; then
    print_error "Invalid bump type: $BUMP_TYPE"
    print_error "Use: patch, minor, or major"
    exit 1
fi

print_header "Post-Merge Version Bump"
print_status "Current branch: $CURRENT_BRANCH"
print_status "Bump type: $BUMP_TYPE"

# Check if scripts directory exists
if [ ! -d "scripts" ]; then
    print_error "Scripts directory not found"
    exit 1
fi

# Check if bump_version.py exists
if [ ! -f "scripts/bump_version.py" ]; then
    print_error "bump_version.py script not found"
    exit 1
fi

# Make sure the script is executable
chmod +x scripts/bump_version.py

# Run the version bump script
print_status "Running version bump script..."
python3 scripts/bump_version.py "$BUMP_TYPE"

if [ $? -eq 0 ]; then
    print_status "Version bump completed successfully!"
    
    # Show git status
    print_status "Git status:"
    git status --porcelain
    
    # Prompt to commit changes
    echo
    read -p "Commit version bump changes? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_warning "Version bump changes not committed"
        print_warning "You can commit them manually later"
    else
        # Get new version from VERSION file
        NEW_VERSION=$(cat VERSION)
        
        # Commit the changes
        git add VERSION CHANGELOG.md
        git commit -m "chore: Bump version to $NEW_VERSION after merge to develop"
        
        print_status "Version bump changes committed successfully!"
        print_status "New version: $NEW_VERSION"
    fi
else
    print_error "Version bump failed!"
    exit 1
fi

print_header "Post-Merge Version Bump Complete"
print_status "Don't forget to push the changes:"
print_status "  git push origin develop"
