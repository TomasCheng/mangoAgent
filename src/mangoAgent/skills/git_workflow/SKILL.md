---
name: git_workflow
description: Standard Git workflow for the project.
---

# Git Workflow

## Branching Strategy
- **main**: Production-ready code.
- **develop**: Integration branch for features.
- **feature/**: New features (e.g., `feature/login`).
- **fix/**: Bug fixes (e.g., `fix/typo`).

## Commit Messages
- Use Conventional Commits.
- `feat: add login`
- `fix: resolve crash on startup`
- `docs: update readme`

## Pull Requests
- Keep PRs small and focused.
- Require at least one approval.
- Ensure CI passes before merging.
