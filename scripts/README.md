# Version Management Scripts

This directory contains scripts to automate version bumping and changelog updates for DICOM Fabricator.

## Overview

The version management system automatically:
- Bumps version numbers according to semantic versioning
- Updates the CHANGELOG.md with new version entries
- Updates version references in source files
- Commits version changes to git

## Scripts

### `bump_version.py`

The core Python script that handles version bumping logic.

**Usage:**
```bash
python3 scripts/bump_version.py [patch|minor|major]
```

**Bump Types:**
- `patch` (default): 1.0.1 → 1.0.2 (bug fixes, small changes)
- `minor`: 1.0.1 → 1.1.0 (new features)
- `major`: 1.0.1 → 2.0.0 (breaking changes)

**What it does:**
1. Reads current version from `VERSION` file
2. Calculates new version based on bump type
3. Updates `VERSION` file
4. Adds new entry to `CHANGELOG.md`
5. Updates version references in source files
6. Provides git commit commands

### `post-merge-version-bump.sh`

A bash script designed to be run after merging feature branches into develop.

**Usage:**
```bash
./scripts/post-merge-version-bump.sh [patch|minor|major]
```

**What it does:**
1. Checks if you're on the develop branch
2. Runs the version bump script
3. Shows git status
4. Prompts to commit changes
5. Automatically commits version bump if approved

## Workflow

### Standard Development Workflow

1. **Create feature branch:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit:**
   ```bash
   # Make your changes
   git add .
   git commit -m "feat: Add new feature"
   ```

3. **Merge to develop:**
   ```bash
   git checkout develop
   git merge feature/your-feature-name
   ```

4. **Bump version:**
   ```bash
   ./scripts/post-merge-version-bump.sh patch
   ```

5. **Push changes:**
   ```bash
   git push origin develop
   ```

### Version Bump Types

Choose the appropriate bump type based on your changes:

- **Patch (1.0.1 → 1.0.2):**
  - Bug fixes
  - Documentation updates
  - Minor improvements
  - Security patches

- **Minor (1.0.1 → 1.1.0):**
  - New features
  - Enhancements
  - Non-breaking changes

- **Major (1.0.1 → 2.0.0):**
  - Breaking changes
  - Major refactoring
  - Incompatible API changes

## Files Updated

The version bumping process updates these files:

1. **`VERSION`** - Central version number
2. **`CHANGELOG.md`** - Version history and change log
3. **`src/dicom_fabricator.py`** - Software version reference
4. **`docs/CLAUDE.md`** - Documentation version reference

## Manual Version Bumping

If you need to bump the version manually:

```bash
# Bump patch version (default)
python3 scripts/bump_version.py

# Bump minor version
python3 scripts/bump_version.py minor

# Bump major version
python3 scripts/bump_version.py major
```

## Troubleshooting

### Common Issues

1. **Script not executable:**
   ```bash
   chmod +x scripts/bump_version.py
   chmod +x scripts/post-merge-version-bump.sh
   ```

2. **Python not found:**
   ```bash
   # Use python3 explicitly
   python3 scripts/bump_version.py
   ```

3. **Not on develop branch:**
   ```bash
   git checkout develop
   ./scripts/post-merge-version-bump.sh
   ```

### Git Hooks (Optional)

To automatically run version bumping on merge, you can set up a git hook:

```bash
# Create post-merge hook
cp scripts/post-merge-version-bump.sh .git/hooks/post-merge
chmod +x .git/hooks/post-merge
```

**Note:** Git hooks are local to each repository and won't be shared with other developers.

## Best Practices

1. **Always bump version after merging to develop**
2. **Use appropriate bump type for your changes**
3. **Review changelog entries before committing**
4. **Push version changes with your feature changes**
5. **Keep version numbers consistent across all files**

## Examples

### Patch Version Bump
```bash
./scripts/post-merge-version-bump.sh patch
# Result: 1.0.1 → 1.0.2
```

### Minor Version Bump
```bash
./scripts/post-merge-version-bump.sh minor
# Result: 1.0.1 → 1.1.0
```

### Major Version Bump
```bash
./scripts/post-merge-version-bump.sh major
# Result: 1.0.1 → 2.0.0
```
