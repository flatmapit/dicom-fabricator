# Git Workflow and Branching Strategy

## Overview
This project follows a Git Flow branching strategy with the following main branches:

- **`main`** - Production-ready code, stable releases
- **`develop`** - Integration branch for features, main development work
- **`feature/*`** - Feature branches for individual development work

## Branch Structure

```
main
├── develop
│   ├── feature/user-authentication
│   ├── feature/dicom-viewer-enhancement
│   ├── feature/pacs-integration
│   └── ...
```

## Workflow

### Starting New Feature Development

1. **Ensure you're on develop branch:**
   ```bash
   git checkout develop
   git pull origin develop
   ```

2. **Create a new feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Work on your feature:**
   - Make commits with clear, descriptive messages
   - Keep commits atomic and focused
   - Update CHANGELOG.md for significant changes

4. **Complete the feature:**
   - Ensure all tests pass
   - Update documentation if needed
   - Update CHANGELOG.md

### Merging Feature Back to Develop

1. **Switch to develop and pull latest changes:**
   ```bash
   git checkout develop
   git pull origin develop
   ```

2. **Merge your feature branch:**
   ```bash
   git merge feature/your-feature-name
   ```

3. **Push to remote develop:**
   ```bash
   git push origin develop
   ```

4. **Clean up feature branch:**
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

### Releasing to Main

When develop is stable and ready for production:

1. **Create a release branch from develop:**
   ```bash
   git checkout develop
   git checkout -b release/v1.x.x
   ```

2. **Make any final adjustments:**
   - Update version numbers
   - Finalize CHANGELOG.md
   - Update any release-specific documentation

3. **Merge to main:**
   ```bash
   git checkout main
   git merge release/v1.x.x
   git tag v1.x.x
   git push origin main --tags
   ```

4. **Merge back to develop:**
   ```bash
   git checkout develop
   git merge release/v1.x.x
   git push origin develop
   ```

5. **Clean up release branch:**
   ```bash
   git branch -d release/v1.x.x
   git push origin --delete release/v1.x.x
   ```

## Commit Message Convention

Use clear, descriptive commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(auth): add user authentication system`
- `fix(viewer): resolve DICOM image display issue`
- `docs(readme): update installation instructions`
- `refactor(core): optimize DICOM processing logic`

## Best Practices

1. **Never commit directly to main** - always go through develop
2. **Keep feature branches focused** - one feature per branch
3. **Pull latest develop before creating feature branches**
4. **Update CHANGELOG.md for all significant changes**
5. **Test thoroughly before merging to develop**
6. **Use descriptive branch names** (e.g., `feature/user-dashboard`, `fix/login-bug`)

## Emergency Hotfixes

For critical production issues:

1. **Create hotfix branch from main:**
   ```bash
   git checkout main
   git checkout -b hotfix/critical-fix
   ```

2. **Fix the issue and commit:**
   ```bash
   git commit -m "fix: resolve critical production issue"
   ```

3. **Merge to main and tag:**
   ```bash
   git checkout main
   git merge hotfix/critical-fix
   git tag v1.x.x+1
   git push origin main --tags
   ```

4. **Merge to develop:**
   ```bash
   git checkout develop
   git merge hotfix/critical-fix
   git push origin develop
   ```

5. **Clean up hotfix branch:**
   ```bash
   git branch -d hotfix/critical-fix
   git push origin --delete hotfix/critical-fix
   ```
