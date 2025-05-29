# Git Commands Cheatsheet for Azure DevOps

## 🚀 Installation & Setup

### Installing Git
**Windows:**
```bash
# Download from https://git-scm.com/download/win
# Or use Chocolatey
choco install git

# Or use Winget
winget install --id Git.Git -e --source winget
```

**macOS:**
```bash
# Using Homebrew
brew install git

# Or download from https://git-scm.com/download/mac
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git
```

### Initial Git Configuration
```bash
# Set your identity
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"

# Set default branch name
git config --global init.defaultBranch main

# Set line ending preferences (Windows)
git config --global core.autocrlf true

# Set line ending preferences (macOS/Linux)
git config --global core.autocrlf input

# Configure VS Code as default editor
git config --global core.editor "code --wait"

# Configure VS Code as merge tool
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'
```

### Azure DevOps Authentication Setup
```bash
# Install Git Credential Manager (recommended)
# Windows: Included with Git for Windows
# macOS: brew install --cask git-credential-manager-core
# Linux: Download from GitHub releases

# Configure credential helper
git config --global credential.helper manager-core

# For Azure DevOps, you can also use Personal Access Token (PAT)
# Generate PAT in Azure DevOps: User Settings > Personal Access Tokens
```

## 📁 Repository Management

### Clone Repository from Azure DevOps
```bash
# HTTPS clone (recommended for most users)
git clone https://dev.azure.com/YourOrg/YourProject/_git/YourRepo

# SSH clone (requires SSH key setup)
git clone git@ssh.dev.azure.com:v3/YourOrg/YourProject/YourRepo

# Clone specific branch
git clone -b feature-branch https://dev.azure.com/YourOrg/YourProject/_git/YourRepo

# Clone with specific directory name
git clone https://dev.azure.com/YourOrg/YourProject/_git/YourRepo my-project
```

### Initialize New Repository
```bash
# Initialize new Git repository
git init

# Add Azure DevOps as remote origin
git remote add origin https://dev.azure.com/YourOrg/YourProject/_git/YourRepo

# Verify remote
git remote -v
```

## 🌿 Branch Management

### Basic Branch Operations
```bash
# List all branches
git branch -a

# Create new branch
git branch feature/new-feature

# Switch to branch
git checkout feature/new-feature

# Create and switch to new branch (shortcut)
git checkout -b feature/new-feature

# Switch to branch (Git 2.23+)
git switch feature/new-feature

# Create and switch to new branch (Git 2.23+)
git switch -c feature/new-feature

# Delete local branch
git branch -d feature/completed-feature

# Force delete local branch
git branch -D feature/abandoned-feature

# Delete remote branch
git push origin --delete feature/old-feature
```

### Advanced Branch Operations
```bash
# Rename current branch
git branch -m new-branch-name

# Track remote branch
git branch -u origin/feature/remote-branch

# Push new branch to remote
git push -u origin feature/new-feature

# List branches with last commit info
git branch -v

# List merged branches
git branch --merged

# List unmerged branches
git branch --no-merged
```

## 📝 Staging & Committing

### Basic Staging
```bash
# Stage specific file
git add filename.txt

# Stage all files
git add .

# Stage all modified files (not new files)
git add -u

# Stage files interactively
git add -i

# Stage parts of files (patch mode)
git add -p

# Unstage file
git reset HEAD filename.txt

# Unstage all files
git reset HEAD
```

### Committing Changes
```bash
# Commit with message
git commit -m "Add new feature implementation"

# Commit with detailed message
git commit -m "Add user authentication" -m "- Implement JWT token validation
- Add password hashing with bcrypt
- Create login/logout endpoints"

# Commit all modified files (skip staging)
git commit -a -m "Quick fix for login bug"

# Amend last commit message
git commit --amend -m "Corrected commit message"

# Amend last commit with new changes
git add forgotten-file.txt
git commit --amend --no-edit
```

## 🔄 Synchronization with Azure DevOps

### Fetching & Pulling
```bash
# Fetch latest changes from remote
git fetch origin

# Fetch all remotes
git fetch --all

# Pull changes from current branch
git pull

# Pull with rebase (cleaner history)
git pull --rebase

# Pull specific branch
git pull origin main

# Pull and prune deleted remote branches
git pull --prune
```

### Pushing Changes
```bash
# Push current branch to remote
git push

# Push and set upstream for new branch
git push -u origin feature/new-feature

# Push specific branch
git push origin feature/branch-name

# Push all branches
git push --all

# Push tags
git push --tags

# Force push (use with caution!)
git push --force

# Safer force push
git push --force-with-lease
```

## 🔧 Working with Changes

### Viewing Changes
```bash
# Show working directory status
git status

# Show changes in working directory
git diff

# Show staged changes
git diff --cached

# Show changes between commits
git diff commit1..commit2

# Show changes in specific file
git diff filename.txt

# Show changes between branches
git diff main..feature/branch
```

### Stashing Changes
```bash
# Stash current changes
git stash

# Stash with message
git stash save "Work in progress on feature X"

# List stashes
git stash list

# Apply latest stash
git stash apply

# Apply specific stash
git stash apply stash@{2}

# Pop latest stash (apply and remove)
git stash pop

# Drop specific stash
git stash drop stash@{1}

# Clear all stashes
git stash clear
```

## 🔍 History & Information

### Viewing History
```bash
# Show commit history
git log

# Show one-line commit history
git log --oneline

# Show graphical commit history
git log --graph --oneline --decorate

# Show commits by author
git log --author="John Doe"

# Show commits in date range
git log --since="2025-01-01" --until="2025-01-31"

# Show file history
git log -- filename.txt

# Show detailed changes in commits
git log -p
```

### Searching & Information
```bash
# Search for commits containing string
git log --grep="bug fix"

# Search for code changes
git log -S "function_name"

# Show specific commit details
git show commit-hash

# Show current commit hash
git rev-parse HEAD

# Show branch information
git show-branch

# Show remote repository information
git remote show origin
```

## 🔀 Merging & Rebasing

### Merging
```bash
# Merge branch into current branch
git merge feature/branch-name

# Merge with no fast-forward (creates merge commit)
git merge --no-ff feature/branch-name

# Merge and squash commits
git merge --squash feature/branch-name

# Abort merge (if conflicts occur)
git merge --abort

# Continue merge after resolving conflicts
git merge --continue
```

### Rebasing
```bash
# Rebase current branch onto main
git rebase main

# Interactive rebase (last 3 commits)
git rebase -i HEAD~3

# Rebase onto specific commit
git rebase commit-hash

# Continue rebase after resolving conflicts
git rebase --continue

# Skip current commit during rebase
git rebase --skip

# Abort rebase
git rebase --abort
```

## ⚡ Merge Conflict Resolution

### Identifying Conflicts
```bash
# Check status during merge conflict
git status

# Show files with conflicts
git diff --name-only --diff-filter=U

# Show conflict details
git diff
```

### Resolving Conflicts in VS Code
1. **Open VS Code in repository directory:**
   ```bash
   code .
   ```

2. **VS Code will show conflicted files with 'C' marker in Source Control panel**

3. **Enable Merge Editor in VS Code:**
   - Go to Settings (Ctrl+,)
   - Search for "git merge editor"
   - Check "Open the merge editor for files that are currently under conflict"

4. **Resolve conflicts using VS Code Merge Editor:**
   - Click "Resolve in Merge Editor" button
   - Use 3-way merge view: Incoming | Current | Result
   - Accept incoming, current, or manually edit the result
   - Click "Complete Merge" when done

### Resolving Conflicts in Visual Studio
1. **Visual Studio will show conflicts in Git Changes window**
2. **Double-click conflicted file or click "Open Merge Editor"**
3. **Use the merge editor to resolve conflicts:**
   - Left pane: Incoming changes
   - Right pane: Current changes
   - Bottom pane: Result
4. **Click checkboxes to accept specific changes**
5. **Click "Accept Merge" when complete**

### Command Line Conflict Resolution
```bash
# Edit conflicted files manually
# Look for conflict markers:
# <<<<<<< HEAD
# Your changes
# =======
# Incoming changes
# >>>>>>> branch-name

# After resolving conflicts, stage the files
git add resolved-file.txt

# Complete the merge
git commit

# Or use merge tools
git mergetool

# Configure merge tool (VS Code)
git config merge.tool vscode
git config mergetool.vscode.cmd 'code --wait $MERGED'
```

## 🏷️ Tagging

### Creating Tags
```bash
# Create lightweight tag
git tag v1.0.0

# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Tag specific commit
git tag -a v1.0.1 commit-hash -m "Hotfix release"

# List tags
git tag

# List tags with pattern
git tag -l "v1.*"

# Show tag information
git show v1.0.0
```

### Managing Tags
```bash
# Push specific tag
git push origin v1.0.0

# Push all tags
git push --tags

# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin --delete v1.0.0
```

## 🔧 Advanced Operations

### Cherry-picking
```bash
# Cherry-pick specific commit
git cherry-pick commit-hash

# Cherry-pick multiple commits
git cherry-pick commit1 commit2 commit3

# Cherry-pick range of commits
git cherry-pick commit1..commit3

# Cherry-pick without committing
git cherry-pick -n commit-hash
```

### Reset & Revert
```bash
# Soft reset (keep changes staged)
git reset --soft HEAD~1

# Mixed reset (keep changes unstaged) - default
git reset HEAD~1

# Hard reset (discard all changes)
git reset --hard HEAD~1

# Reset to specific commit
git reset --hard commit-hash

# Revert commit (creates new commit)
git revert commit-hash

# Revert merge commit
git revert -m 1 merge-commit-hash
```

### Cleaning
```bash
# Show what would be removed
git clean -n

# Remove untracked files
git clean -f

# Remove untracked files and directories
git clean -fd

# Remove ignored files too
git clean -fx
```

## 📋 Azure DevOps Specific Commands

### Pull Requests (via Azure CLI)
```bash
# Install Azure CLI and DevOps extension
az extension add --name azure-devops

# Login to Azure DevOps
az login
az devops configure --defaults organization=https://dev.azure.com/YourOrg project=YourProject

# Create pull request
az repos pr create --source-branch feature/new-feature --target-branch main --title "Add new feature" --description "Detailed description"

# List pull requests
az repos pr list

# Show pull request details
az repos pr show --id 123
```

### Working with Azure Repos
```bash
# List repositories
az repos list

# Show repository details
az repos show --repository YourRepo

# Create new repository
az repos create --name NewRepo --project YourProject
```

## 🎯 Best Practices for Azure DevOps

### Branch Naming Conventions
```bash
# Feature branches
git checkout -b feature/WORK-ITEM-123-add-login-feature

# Bug fix branches
git checkout -b bugfix/WORK-ITEM-456-fix-authentication-error

# Hotfix branches
git checkout -b hotfix/WORK-ITEM-789-critical-security-patch

# Release branches
git checkout -b release/v1.2.0
```

### Commit Message Format
```bash
# Use conventional commits format
git commit -m "feat: add user authentication system

- Implement JWT token validation
- Add password hashing with bcrypt
- Create login/logout endpoints

Closes #123"

# Types: feat, fix, docs, style, refactor, test, chore
git commit -m "fix: resolve login timeout issue"
git commit -m "docs: update API documentation"
git commit -m "refactor: simplify user service logic"
```

### Workflow Commands
```bash
# Daily workflow
git pull --rebase                    # Get latest changes
git switch -c feature/new-work      # Create feature branch
# ... make changes ...
git add .                           # Stage changes
git commit -m "feat: implement feature"  # Commit changes
git push -u origin feature/new-work # Push to remote
# Create pull request in Azure DevOps UI

# Updating feature branch with main
git switch main                     # Switch to main
git pull                           # Get latest changes
git switch feature/new-work        # Switch back to feature
git rebase main                    # Rebase onto main
```

## 🛠️ Troubleshooting Common Issues

### Authentication Issues
```bash
# Clear credential cache
git config --global --unset credential.helper
git config --global credential.helper manager-core

# Manual credential entry
git remote set-url origin https://username@dev.azure.com/YourOrg/YourProject/_git/YourRepo
```

### Line Ending Issues
```bash
# Fix line ending issues
git config core.autocrlf true      # Windows
git config core.autocrlf input     # macOS/Linux

# Refresh repository with correct line endings
git rm --cached -r .
git reset --hard
```

### Large File Handling
```bash
# Install Git LFS for large files
git lfs install

# Track large files
git lfs track "*.psd"
git lfs track "*.zip"

# Add .gitattributes
git add .gitattributes
git commit -m "Configure Git LFS"
```

## 📚 Useful Aliases

Add these to your `.gitconfig` file or use `git config --global alias.name "command"`:

```bash
# Shortcuts
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status

# Advanced aliases
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'
git config --global alias.graph 'log --graph --oneline --decorate --all'
git config --global alias.conflicts 'diff --name-only --diff-filter=U'
```

## 🔧 VS Code Extensions for Git

Recommended extensions for enhanced Git experience:
- **GitLens** - Supercharge Git in VS Code
- **Git Graph** - View Git graph of repository
- **Git History** - View git log, file history, compare branches
- **Azure Repos** - Azure DevOps integration
- **Merge Conflict** - Highlight and resolve merge conflicts

## 📖 Quick Reference Card

| Operation | Command |
|-----------|---------|
| Clone repo | `git clone <url>` |
| Create branch | `git checkout -b <branch>` |
| Switch branch | `git switch <branch>` |
| Stage changes | `git add .` |
| Commit | `git commit -m "message"` |
| Push | `git push` |
| Pull | `git pull` |
| Merge | `git merge <branch>` |
| Status | `git status` |
| History | `git log --oneline` |
| Stash | `git stash` |
| Reset | `git reset --hard HEAD~1` |

---

**Pro Tip:** Use `git help <command>` for detailed help on any Git command, or visit the [official Git documentation](https://git-scm.com/docs) for comprehensive guidance.