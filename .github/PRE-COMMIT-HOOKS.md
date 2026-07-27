# Pre-commit Hooks Setup Guide 🔧

Pre-commit hooks ensure code quality and consistency before each commit. This guide explains how to set up and use them for the OpenClaw Gateway Provisioning CLI Library.

---

## 📋 What Are Pre-commit Hooks?

**Pre-commit hooks** are scripts that run automatically before you make a commit. They:
- ✅ Check code quality (linting, formatting)
- ✅ Detect issues early (type errors, security problems)
- ✅ Enforce coding standards consistently
- ✅ Catch mistakes before they reach the repository
- ✅ Save time by running locally instead of waiting for CI

---

## 🎯 What This Project Checks

The pre-commit hooks in this project verify:

### Code Quality & Style

1. **Trailing Whitespace**: Removes accidental spaces at end of lines
2. **End-of-file Newlines**: Ensures all files end with newline character
3. **Large Files**: Warns about files >500KB (prevents performance issues)
4. **Merge Conflicts**: Detects unmerged conflict markers
5. **Symlinks**: Checks for broken symbolic links
6. **YAML Syntax**: Validates `.yaml`/`.yml` configuration files
7. **JSON Syntax**: Validates JSON files

### Code Style & Linting

8. **Ruff Linting**: Fast Python code analysis
   - Detects bugs, unused imports, unreachable code
   - Enforces PEP 8 style guidelines
   - Checks for type hints compliance

9. **Black Formatting**: Consistent code formatting
   - Standardizes indentation and line breaks
   - Ensures uniform spacing and brackets
   - Handles multi-line statements gracefully

### Security Scanning (Optional)

10. **MyPy Type Checking**: Static type validation
    - Catches type mismatches before runtime
    - Provides detailed error messages
    - Requires `types-requests`, `types-python-dotenv` packages

11. **Bandit Security Scan**: Vulnerability detection
    - Scans for common security issues
    - Checks for hardcoded secrets
    - Detects dangerous code patterns

---

## 🚀 Quick Setup (3 Commands)

### Step 1: Install Pre-commit Tools

```bash
# Install pre-commit globally
pip install pre-commit
```

OR with uv (recommended):

```bash
uv add pre-commit
```

### Step 2: Run Initial Check

```bash
# Check all hooks against your codebase once
pre-commit run --all-files
```

This shows what would be checked on each commit and fixes auto-fixable issues.

### Step 3: Install Hooks Automatically

```bash
# Register hooks with Git (run once per machine/clone)
git pre-commit install

# Or use pip to register globally
pre-commit install
```

**Done!** Now every `git commit` will automatically run these checks.

---

## 📝 Detailed Setup Guide

### Option 1: Automatic Installation (Recommended)

```bash
cd /home/manager/tom-first-project

# Install pre-commit from pip or uv
pip install pre-commit
# OR: uv add pre-commit

# Install hooks for this repository
pre-commit install

# Run all hooks on current changes
pre-commit run --from-merge

# Or run once to see all checks
pre-commit run --all-files
```

### Option 2: Manual Hook Management

To install/uninstall specific hooks:

```bash
# Install only ruff and black (skip type checking)
pre-commit install --hook-type pre-commit

# Uninstall all hooks
pre-commit uninstall

# Run only on Python files
pre-commit run --files "src/**/*.py" "scripts/*.py"
```

---

## 🔧 Configuring Hook Behavior

### Customizing `.pre-commit-config.yaml`

The configuration file at `.pre-commit-config.yaml` controls:

1. **Which tools to use**: Each `repo:` block specifies a tool and its version
2. **When to run**: Different hook types (commit, push, post-checkout)
3. **Where to check**: File patterns that are checked or ignored

#### Example: Modify Check Behavior

```yaml
# In .pre-commit-config.yaml

repos:
  # Run ruff only on Python files (not tests/examples)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.1
    hooks:
      - id: ruff
        args: [--fix]  # Auto-fix what it can
        exclude: '^tests/'  # Skip test files

  # Run Black only on src/ and scripts/ directories
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        args: [--line-length, '88']
        exclude: '^examples/'
```

### Skipping Specific Hooks Temporarily

If you need to bypass a check temporarily (e.g., for work in progress):

```bash
# Commit without running pre-commit checks
git commit -m "feat: work in progress" --no-verify

# OR skip only ruff hook
pre-commit run --all-files --files src/main.py

# Commit with specific files, skipping hooks for them
git add src/utils.py
git commit -m "fix: update utils" --no-verify
```

**⚠️ Warning**: Never bypass hooks in production code! Use `--no-verify` only for:
- Work-in-progress commits
- Large experimental changes
- Initial repository setup

---

## 📊 Hook Types and Triggers

Pre-commit supports different hook types with different triggers:

| Hook Type | Trigger | Best For |
|-----------|---------|----------|
| `pre-commit` | Every commit (default) | Most checks - formatting, linting, security |
| `pre-push` | Before pushing to remote | Performance checks, integration tests |
| `post-commit` | After successful commit | Git history cleanup, changelog updates |
| `post-checkout` | When switching branches | Updating environment variables |

### Current Project Hooks

This project currently uses **pre-commit** hooks only. The configuration:

```yaml
# Runs before every git commit
# Checks code quality and formatting
repos:
  - ruff: linting and bug detection
  - black: consistent formatting
  - mypy: type checking (optional)
  - bandit: security scanning (optional)
```

---

## 🎓 Understanding Hook Results

When you run `pre-commit run --all-files`, you'll see output like this:

### ✅ Passed Check
```
ruff.....................................................................Passed
black...............................................................Passed
```

The tool found no issues or auto-fixed them.

### ⚠️ Needs Fixing (Manual)
```
mypy...................................................Failing
  - src/gateway_provisioning/auth.py:15: error: Incompatible types in assignment [assignment]
    
  Hint: Add type annotation to fix:
    from typing import Optional
    
    def validate_auth_config(config_path: str, auth_mgr: AuthenticationManager) -> bool:
        # ...
```

The tool found an issue you need to fix manually.

### 🔧 Auto-fixed Issues
```
ruff............................................................Fixed
  - Fixed 3 issues
  - Trailing whitespace removed from src/utils.py:5-12
  - Unnecessary parentheses removed
```

Ruff automatically fixed some issues!

---

## 🚀 Advanced Setup: Custom Hooks

### Adding a Custom Hook for Coverage

If you want to check test coverage before commit:

```yaml
# In .pre-commit-config.yaml

repos:
  # ... existing hooks ...
  
  # Add coverage check (optional)
  - repo: local
    hooks:
      - id: coverage-check
        name: Test Coverage Check (>80% required)
        entry: >-
          bash -c '
            uv run pytest tests/ --cov=src/gateway_provisioning \
            --cov-report=term-missing | grep "Total:"
          '
        language: system
        pass_filenames: false
        always_run: true
        stages: [commit]
```

### Adding a Hook for Documentation

To ensure docs stay updated:

```yaml
repos:
  # ... existing hooks ...
  
  - repo: local
    hooks:
      - id: update-docs-check
        name: Check Documentation Exists
        entry: bash -c 'if [ ! -f README.md ]; then echo "❌ README.md missing"; exit 1; fi'
        language: system
        pass_filenames: false
        always_run: true
```

---

## 🐛 Troubleshooting Common Issues

### Issue: "No pre-commit installed"

**Solution**: Install pre-commit globally or in project dependencies:

```bash
# Global installation
pip install pre-commit

# Or with uv (project-specific)
uv add pre-commit
```

### Issue: Hook fails on large file

The hook has a 500KB limit to prevent performance issues:

```bash
# Check for large files
pre-commit run --files large-file.txt

# Either split the file or disable that check temporarily
git config --global core.bigFileThreshold 1M
```

### Issue: Pre-commit too strict

If hooks are rejecting valid code, adjust the configuration:

```yaml
# In .pre-commit-config.yaml

repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports]  # Less strict on missing types
```

### Issue: "Could not find python" after installing hooks

**Solution**: Add Python to PATH or use full path:

```bash
# Option 1: Set up Python in .bashrc
export PATH="$HOME/.local/bin:$PATH"

# Option 2: Use full path to pre-commit
python -m pre_commit run --all-files
```

### Issue: Hooks running too slowly

The hooks are designed for fast feedback, but large repositories can be slow. To speed up:

```yaml
# In .pre-commit-config.yaml

repos:
  # Exclude tests directory from some checks
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.1
    hooks:
      - id: ruff
        exclude: 'tests/|examples/'  # Skip these directories
```

---

## 📚 Best Practices

### When to Run Pre-commit Hooks

✅ **Always** run before committing production code  
✅ **Before** Pull Request reviews (catch issues early)  
❌ **Don't** bypass for work-in-progress commits without note  
❌ **Don't** disable hooks on shared team repositories  

### Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
# Good commit messages:
git commit -m "feat: add authentication setup CLI command"
git commit -m "fix: resolve type checking errors in auth.py"
git commit -m "docs: update README with quick start guide"
git commit -m "test: add unit tests for config initialization"

# Bad commit messages:
git commit -m "update stuff"           # Too vague
git commit -m "fixed things"            # Incomplete (was it a bug?)
git commit -m "WIP"                     # Don't use work-in-progress commits
```

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] All pre-commit hooks pass locally (`pre-commit run --all-files`)
- [ ] Tests pass (`uv run pytest tests/ -v`)
- [ ] Code follows team conventions (PEP 8, Black formatting)
- [ ] No sensitive data committed (no tokens, secrets, passwords)
- [ ] Documentation updated where needed
- [ ] Git history is clean (no `WIP` or empty commits)

---

## 🔍 What Each Hook Does

### Trailing Whitespace Remover

Removes accidental spaces and tabs at end of lines:

```bash
# Before (wrong):
echo "Hello world  "  # Notice trailing spaces

# After (correct):
echo "Hello world"    # No trailing spaces
```

**Why important**: Trailing whitespace can cause issues in diff viewing and merge conflicts.

### End-of-file Fixer

Ensures all files end with a newline character:

```bash
# Before (wrong):
# File without final newline

# After (correct):
# File ends with newline
```

**Why important**: Some editors expect this; prevents accidental diffs on save.

### Ruff Linter

Fast Python linter that checks for common bugs:

```python
# Detected by ruff (would fail check):

def process_data(data, invalid_param=None):  # Unused parameter warning
    return data.lower()

if "text" in x and "text":  # Dead code warning
    pass
```

**Why important**: Catches bugs before runtime.

### Black Formatter

Consistent code formatting:

```python
# Before (messy):
def calculate_total(prices, tax_rate=0.1) -> float:
    total = sum(prices) + sum(prices)*tax_rate
    return round(total,2)

# After (formatted by black):
def calculate_total(prices, tax_rate: float = 0.1) -> float:
    """Calculate the total price including tax."""
    total = sum(prices) * (1 + tax_rate)
    return round(total, 2)
```

**Why important**: Uniform style makes code easier to read and review.

### MyPy Type Checker (Optional)

Static type checking:

```python
# Detected by mypy (would fail):

def greet(name: str) -> str:
    if name == "":  # Empty string is valid, not None
        return "Hello!"
    else:
        return f"Hello {name}"  # Type mismatch warning here
```

**Why important**: Catches errors before runtime; enables better autocomplete.

### Bandit Security Scanner (Optional)

Security vulnerability detection:

```python
# Detected by bandit (would warn):

password = "secret123"  # Hardcoded secret!
import os
os.popen("command")  # Command injection risk!
```

**Why important**: Prevents security vulnerabilities from being introduced.

---

## 📖 Additional Resources

- [Pre-commit documentation](https://pre-commit.com/)
- [Ruff official guide](https://docs.astral.sh/ruff/)
- [Black formatting guide](https://black.readthedocs.io/)
- [MyPy type hints guide](https://mypy.readthedocs.io/)
- [Bandit security scanning](https://bandit.readthedocs.io/)

---

## 🎯 Summary

Pre-commit hooks are your first line of defense against:

✅ Code quality issues (trailing whitespace, formatting)  
✅ Security vulnerabilities (hardcoded secrets, dangerous commands)  
✅ Type errors (MyPy checks)  
✅ Style violations (PEP 8 compliance)  
✅ Performance problems (large files, merge conflicts)  

**Setup once, benefit always!** By automating these checks before each commit, you ensure:
- Clean, consistent codebase
- Faster code reviews (issues caught early)
- Higher code quality over time
- Less time debugging runtime errors

---

**Ready to keep your code clean!** 🚀
