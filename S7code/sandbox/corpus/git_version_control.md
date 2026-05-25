# Git: Version Control Best Practices

Git is a distributed version control system designed for speed, data integrity, and support for non-linear workflows. Understanding Git's internal model enables confident use of its powerful features.

## Git's Object Model

Every object in Git is content-addressed by its SHA-1 hash:

- **Blob**: File content (no name or path)
- **Tree**: Directory structure (blob names + permissions + references)
- **Commit**: Points to a tree, parent commits, metadata (author, message, timestamp)
- **Tag**: Named pointer to a commit

```bash
git cat-file -t abc123    # Shows object type
git cat-file -p abc123    # Shows object content
```

## Branching and Merging

```bash
# Create and switch to branch
git checkout -b feature/auth-improvements

# Push branch to remote
git push -u origin feature/auth-improvements

# Merge into main (creates merge commit)
git checkout main
git merge feature/auth-improvements

# Rebase onto main (linear history)
git rebase main feature/auth-improvements
git checkout main
git merge feature/auth-improvements --ff-only
```

**Merge vs Rebase**:
- Merge preserves historical branching topology
- Rebase creates linear history but rewrites commits — never rebase shared branches

## Interactive Rebase for Clean History

```bash
git rebase -i HEAD~5  # Edit last 5 commits

# Commands:
# pick = keep commit
# reword = keep commit, edit message
# squash = squash into previous commit
# fixup = squash, discard message
# drop = delete commit
```

## Useful Workflows

**GitFlow**: main + develop + feature/release/hotfix branches
**GitHub Flow**: main + short-lived feature branches with PRs
**Trunk-Based Development**: All developers commit to main daily; use feature flags for incomplete features

## Undoing Mistakes

```bash
# Undo last commit, keep changes staged
git reset --soft HEAD~1

# Undo last commit, keep changes unstaged
git reset --mixed HEAD~1

# DANGER: Undo last commit, discard changes
git reset --hard HEAD~1

# Undo a commit that's already pushed (creates new undo commit)
git revert abc123

# Restore a deleted file
git checkout HEAD -- deleted_file.py

# Find when a bug was introduced
git bisect start
git bisect bad                          # Current commit is bad
git bisect good v2.0.0                  # Last known good commit
# Git checks out midpoint; you test and mark good/bad
git bisect good / git bisect bad
git bisect reset                        # Return to HEAD
```

## Stashing

```bash
git stash                               # Save uncommitted changes
git stash push -m "WIP: auth fix"      # Named stash
git stash list                          # Show stashes
git stash pop                           # Apply and remove latest stash
git stash apply stash@{2}              # Apply specific stash
```

## Git Hooks

Automate checks at key points:

```bash
# .git/hooks/pre-commit (must be executable)
#!/bin/bash
ruff check src/           # Lint check
mypy src/ --no-error-summary  # Type check
exit $?                   # Non-zero exit blocks the commit
```

## Aliases for Productivity

```bash
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.st "status -sb"
git config --global alias.cm "commit -m"
git config --global alias.ac "!git add -A && git commit"
```

## Signed Commits

```bash
git config --global user.signingkey YOUR_GPG_KEY_ID
git config --global commit.gpgsign true
git commit -S -m "Signed commit"
```

GitHub shows "Verified" badge on signed commits, important for supply chain security.
