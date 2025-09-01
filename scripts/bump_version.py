#!/usr/bin/env python3
"""
Version Bumping Script for DICOM Fabricator

This script automatically bumps the version number and updates the changelog
when merging changes into develop branch.

Usage:
    python scripts/bump_version.py [patch|minor|major]
    
    patch: 1.0.1 -> 1.0.2 (default, for bug fixes and small changes)
    minor: 1.0.1 -> 1.1.0 (for new features)
    major: 1.0.1 -> 2.0.0 (for breaking changes)
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path

def read_version():
    """Read current version from VERSION file"""
    version_file = Path("VERSION")
    if not version_file.exists():
        print("❌ VERSION file not found!")
        sys.exit(1)
    
    with open(version_file, 'r') as f:
        version = f.read().strip()
    
    return version

def write_version(version):
    """Write new version to VERSION file"""
    version_file = Path("VERSION")
    with open(version_file, 'w') as f:
        f.write(version + '\n')
    print(f"✅ Updated VERSION file to {version}")

def bump_version(current_version, bump_type="patch"):
    """Bump version according to semantic versioning"""
    parts = current_version.split('.')
    if len(parts) != 3:
        print(f"❌ Invalid version format: {current_version}")
        sys.exit(1)
    
    major, minor, patch = map(int, parts)
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        print(f"❌ Invalid bump type: {bump_type}")
        sys.exit(1)
    
    return f"{major}.{minor}.{patch}"

def update_changelog(new_version, bump_type):
    """Update CHANGELOG.md with new version entry"""
    changelog_file = Path("CHANGELOG.md")
    if not changelog_file.exists():
        print("❌ CHANGELOG.md not found!")
        sys.exit(1)
    
    # Read current changelog
    with open(changelog_file, 'r') as f:
        content = f.read()
    
    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create new version entry
    if bump_type == "major":
        change_type = "🚀 Major Release"
    elif bump_type == "minor":
        change_type = "✨ Feature Release"
    else:
        change_type = "🐛 Bug Fix Release"
    
    new_entry = f"""## [{new_version}] - {current_date}

### {change_type}

#### Recent Changes
- **Version Bump**: Automated version bump to {new_version}
- **Change Summary**: This release includes recent improvements and bug fixes

"""
    
    # Insert new entry after the header
    lines = content.split('\n')
    insert_index = 0
    
    # Find where to insert (after the header section)
    for i, line in enumerate(lines):
        if line.startswith('## [') and '] - ' in line:
            insert_index = i
            break
    
    # Insert new entry
    lines.insert(insert_index, new_entry)
    
    # Write updated changelog
    with open(changelog_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Updated CHANGELOG.md with version {new_version}")

def update_files_with_version(old_version, new_version):
    """Update version references in other files"""
    files_to_update = [
        "src/dicom_fabricator.py",
        "docs/CLAUDE.md"
    ]
    
    for file_path in files_to_update:
        file_obj = Path(file_path)
        if file_obj.exists():
            with open(file_obj, 'r') as f:
                content = f.read()
            
            # Replace version references
            updated_content = content.replace(old_version, new_version)
            
            if content != updated_content:
                with open(file_obj, 'w') as f:
                    f.write(updated_content)
                print(f"✅ Updated {file_path} with new version {new_version}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        bump_type = sys.argv[1].lower()
        # Handle help flags
        if bump_type in ["--help", "-h", "help"]:
            print(__doc__)
            sys.exit(0)
        if bump_type not in ["patch", "minor", "major"]:
            print("❌ Invalid bump type. Use: patch, minor, or major")
            print("Run with --help for usage information")
            sys.exit(1)
    else:
        bump_type = "patch"
    
    print(f"🚀 Bumping version ({bump_type})...")
    
    # Read current version
    current_version = read_version()
    print(f"📋 Current version: {current_version}")
    
    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    print(f"📈 New version: {new_version}")
    
    # Update VERSION file
    write_version(new_version)
    
    # Update CHANGELOG.md
    update_changelog(new_version, bump_type)
    
    # Update other files with version references
    update_files_with_version(current_version, new_version)
    
    print(f"\n🎉 Successfully bumped version from {current_version} to {new_version}")
    print(f"📝 Updated CHANGELOG.md with new entry")
    print(f"💾 Don't forget to commit these changes:")
    print(f"   git add VERSION CHANGELOG.md")
    print(f"   git commit -m 'chore: Bump version to {new_version}'")

if __name__ == "__main__":
    main()
