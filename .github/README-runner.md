# CI/CD Pipeline - GitHub Actions Runner 🚀

This repository uses GitHub Actions for automated building, testing, and releasing of the OpenClaw Gateway Provisioning CLI Library.

---

## 📋 Overview

The CI/CD pipeline includes:

- **CI Pipeline** (`.github/workflows/ci.yml`): Runs on every push/PR
- **Deploy Pipeline** (`.github/workflows/deploy.yml`): Releases on master branch
- **Pre-commit hooks** (`.pre-commit-config.yaml`): Automated code quality checks
- **Release notes**: Automatic generation from commit history

---

## 🎯 CI Pipeline Features

### What Gets Checked

1. **Linting & Code Quality**
   - ✅ Ruff linting for Python code
   - ✅ Black formatting checks
   - ✅ isort import ordering
   - ✅ Flake8 additional checks
   - ✅ Trailing whitespace removal
   - ✅ End-of-file newline enforcement

2. **Type Checking**
   - ✅ MyPy static type checking
   - ✅ Ignore missing imports (for optional dependencies)
   - ✅ Python 3.10+ type hints validation

3. **Unit Testing**
   - ✅ pytest with coverage reporting
   - ✅ Branch coverage tracking
   - ✅ HTML coverage reports generated
   - ✅ All test modules validated
   - ✅ CLI script existence and help commands

4. **Integration Tests**
   - ✅ CLI scripts executable and properly documented
   - ✅ Configuration module validation
   - ✅ Authentication setup validation
   - ✅ Provisioner initialization checks
   - ✅ Skills migration sanitization tests

5. **Security Scanning**
   - ✅ Dependency vulnerability checks
   - ✅ Broken dependencies detection
   - ✅ No sensitive data in commits
   - ✅ Dangerous command patterns blocked

---

## 📦 Deploy Pipeline Features

### Release Process

The deploy workflow:

1. **Builds wheel package**: Creates distributable Python package
2. **Creates GitHub Release**: Auto-generated release notes from git log
3. **Uploads artifacts**: Stores build artifacts for 7 days
4. **Publishes to PyPI** (optional): Can be configured for PyPI uploads

### Tagged Releases

When pushing a new tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

This will automatically:
- Create GitHub Release at `tom-first-project/releases`
- Upload release artifacts
- Update CHANGELOG.md (if configured)

---

## 🔧 Pre-commit Hooks Setup

### Install Pre-commit Hooks

To run code quality checks automatically before each commit:

```bash
cd /home/manager/tom-first-project
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Run once to verify everything works
```

### What Gets Checked on Commit

- ✅ **Trailing whitespace**: Removed from all Python files
- ✅ **End-of-file newlines**: Ensured for all source files
- ✅ **Large files**: Warns about files >500KB
- ✅ **Merge conflicts**: Detects unmerged conflicts
- ✅ **Symlinks**: Checks for broken symlinks
- ✅ **YAML syntax**: Validates configuration files
- ✅ **JSON syntax**: Validates JSON files
- ✅ **Private keys**: Prevents committing private keys
- ✅ **TODO/FIXME**: Warns about unchecked comments
- ✅ **Code linting**: Ruff checks for style issues
- ✅ **Formatting**: Black ensures consistent code style
- ✅ **Type checking**: MyPy validates type hints (optional)

### Configure Pre-commit

To skip specific hooks:

```yaml
# In .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        # Exclude certain directories
        exclude: '^tests/|examples/'
```

---

## 📊 CI/CD Workflow Triggers

### Automatic Triggers

**CI Pipeline** runs on:
- Every push to `master` or `main` branch
- Pull requests to `master` or `main`
- Changes in:
  - `src/**` (source code)
  - `scripts/**` (CLI scripts)
  - `tests/**` (test files)
  - `pyproject.toml` (dependencies)

**Deploy Pipeline** runs on:
- Pushes to `master` branch with release tag (`v*.*.*`)
- Manual workflow dispatch (via GitHub UI)
- Pull requests merged from feature branches

### Concurrent Execution

To save CI time, workflows run concurrently and are cancelled if:
- Multiple pushes/PRs occur in quick succession
- Same job already running for same branch

This ensures builds always use the latest code.

---

## 🎛️ Manual Workflow Dispatch

You can manually trigger releases via GitHub UI:

1. Go to `Actions` tab at https://github.com/mcrockett86/tom-first-project/actions
2. Click **Deploy CLI Library** workflow
3. Choose release type:
   - `patch` (bug fixes)
   - `minor` (new features)
   - `major` (breaking changes)
4. Click **Run workflow**

This will trigger a new release build with the selected type.

---

## 📈 Coverage Reports

### View Coverage Locally

After running tests:

```bash
cd /home/manager/tom-first-project

# Install coverage tool
uv add coverage

# Generate HTML coverage report
uv run pytest tests/ --cov=src/gateway_provisioning --cov-report=html

# Open in browser
python -m http.server 8000
# Navigate to: http://localhost:8000/coverage_html/index.html
```

### Coverage Goals

**Target: >80% branch coverage**

Coverage is tracked for:
- Configuration management module
- Authentication setup module
- Provisioner orchestrator module
- CLI script validation

---

## 🔐 Security Best Practices

### Sensitive Data in Workflows

**NEVER** commit:
- ❌ GitHub PATs in workflow files
- ❌ API keys in configuration
- ❌ Passwords or secrets

**ALWAYS** use:
- ✅ GitHub Secrets (for authentication tokens)
- ✅ Environment variables for local development
- ✅ `.env` file (excluded from git)

### Dangerous Command Detection

The CI pipeline detects and blocks dangerous patterns like:
```bash
rm -rf *
dd /dev/*
mount /tmp/malicious
mkfs /dev/sdX
```

---

## 📚 Workflow Files Reference

### `.github/workflows/ci.yml`

Main CI pipeline with 6 jobs:

| Job Name | Purpose | Trigger |
|----------|---------|---------|
| `lint` | Code quality checks (ruff, black) | All pushes/PRs |
| `type-check` | MyPy type validation | All pushes/PRs |
| `test` | Unit tests with coverage | All pushes/PRs |
| `integration-test` | CLI script validation | All pushes/PRs |
| `build-package` | Build wheel package | Needs other jobs to pass |
| `security-scan` | Dependency vulnerability check | All pushes/PRs |

### `.github/workflows/deploy.yml`

Deployment pipeline with 3 jobs:

| Job Name | Purpose | Trigger |
|----------|---------|---------|
| `build-and-release` | Build and release package | Master push, tags |
| `publish-to-pypi` | PyPI upload (dry-run) | Manual dispatch |
| `notify-on-failure` | Fail-fast on errors | Conditional job |

### `.pre-commit-config.yaml`

Pre-commit hooks for local development:

- Automatically runs before each commit
- Ensures code quality standards
- Catches issues early in development

---

## 🎯 Quick Reference

### Run CI Tests Locally (Equivalent to GitHub Actions)

```bash
cd /home/manager/tom-first-project

# Install uv if not installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev

# Add testing tools
uv add pytest coverage ruff mypy flake8 bandit

# Run linting
uv run ruff check src/ tests/ scripts/*.py

# Run type checking
uv run mypy src/gateway_provisioning/*.py

# Run unit tests with coverage
uv run pytest tests/ -v --cov=src/gateway_provisioning --cov-report=term-missing

# Run integration tests (CLI validation)
python scripts/cli_config_init.py --help
python scripts/cli_auth_setup.py validate
python scripts/cli_provision_setup.py --help
python scripts/cli_provision_migrate.py check

# Security scan
uv run bandit -r src/gateway_provisioning
```

### View Coverage Report

```bash
cd /home/manager/tom-first-project

# Generate HTML coverage report
uv run pytest tests/ --cov=src/gateway_provisioning --cov-report=html:coverage_html

# Open in browser
open coverage_html/index.html  # macOS
xdg-open coverage_html/index.html  # Linux
start coverage_html/index.html  # Windows
```

---

## 🐛 Troubleshooting CI Failures

### "ModuleNotFoundError" in Tests

**Fix:** Install dependencies first:

```bash
uv sync --dev
uv add pytest pydantic
```

### "ruff format" Fails

**Fix:** Format code with Black first:

```bash
uv run black src/ tests/ scripts/*.py
pre-commit run ruff-format --all-files
```

### "MyPy type checking fails"

**Fix:** Add type hints or exclude problematic imports:

```python
from typing import Any  # Add proper type annotations
from pathlib import Path
# For third-party libs with no types, use ignore_missing_imports in mypy config
```

### Pre-commit hooks blocking commits

**Solution 1:** Fix all errors and re-run

```bash
pre-commit run --all-files
git add .
git commit -m "feat: add improvements"
```

**Solution 2:** Skip specific hooks

```bash
git commit -m "fix: ..." --no-verify
# Then fix issues manually
```

---

## 📖 Git Workflow with CI/CD

### Feature Branch Development

```bash
# Create feature branch from master
git checkout -b feat/new-feature-name

# Make changes
git add .

# Run pre-commit checks locally (faster than waiting for CI)
pre-commit run --all-files

# Commit with conventional commit format
git commit -m "feat: add new CLI provisioning stage"

# Push to GitHub
git push -u origin feat/new-feature-name

# Create Pull Request from feature branch to master
```

### Ready for Production

When ready to release a stable version:

```bash
# Ensure all tests pass locally
uv run pytest tests/ -v --cov=src/gateway_provisioning

# Run code quality tools
uv run ruff check src/
uv run black --check src/
uv run mypy src/

# Bump version in pyproject.toml
# v0.1.0 -> v0.2.0 (for new release)

# Tag and push
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0

# Create GitHub Release via UI or CLI:
# https://github.com/mcrockett86/tom-first-project/releases/new
```

---

## 🎓 Best Practices

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add configuration CLI initialization scripts"
git commit -m "fix: resolve type checking errors in auth module"
git commit -m "docs: update README with quick start guide"
git commit -m "test: add unit tests for provisioning orchestrator"
```

### PR Descriptions

When creating Pull Request, include:

- [ ] What changes were made
- [ ] Why these changes are needed
- [ ] Testing performed locally (pytest, ruff, mypy)
- [ ] Security implications of the changes
- [ ] Breaking changes (if any)

### Code Quality Checklist

Before submitting PR:

- [ ] Linting passes (`ruff check`)
- [ ] Formatting is correct (`black`)
- [ ] Type checking passes (`mypy`)
- [ ] All tests pass (`pytest`)
- [ ] No sensitive data committed
- [ ] Documentation updated where needed

---

## 🔗 Useful Resources

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Ruff Linter:** https://docs.astral.sh/ruff/
- **Black Formatter:** https://black.readthedocs.io/
- **MyPy Type Checker:** https://mypy.readthedocs.io/
- **pytest Testing:** https://docs.pytest.org/
- **GitHub Secrets:** https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions

---

**Ready to build and ship!** 🎉

Your CI/CD pipeline is fully configured and will automatically:
- ✅ Run on every push/PR
- ✅ Build wheel packages for release
- ✅ Generate comprehensive coverage reports
- ✅ Enforce code quality standards
- ✅ Scan for security vulnerabilities
- ✅ Create GitHub Releases when ready
