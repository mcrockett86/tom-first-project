# Provisioning Scripts README 🚀

This directory contains command-line interfaces (CLIs) for each main provisioning stage. Each script is designed to be called individually, making it easy to run specific stages when needed.

---

## 📋 Available Commands

### 1. Configuration Initialization
**File:** `cli_config_init.py`  
**Usage:** `python scripts/cli_config_init.py`  
**Purpose:** Create initial gateway configuration with approval prompts

```bash
# Interactive setup
python scripts/cli_config_init.py

# Or use the combined script
python scripts/cli_provision_setup.py config
```

#### What it does:
- ✅ Creates `.openclaw/config.json` with all required sections
- ✅ Uses interactive prompts for sensitive values
- ✅ Shows warnings about security best practices
- ✅ Never stores actual API tokens in config file

#### Output example:
```bash
╔═══════════════════════════════════════════════════════╗
   Initialize OpenClaw Gateway Configuration
╚═══════════════════════════════════════════════════════╝

📋 This will create ~/.openclaw/config.json with the following structure:
  {
    "gateway": {...},
    "auth": {...},
    ...
  }
```

---

### 2. Authentication Setup
**File:** `cli_auth_setup.py`  
**Usage:** `python scripts/cli_auth_setup.py <command>`  
**Purpose:** Configure authentication (create .env file, validate setup)

#### Available subcommands:

```bash
# Create .env.example template
python scripts/cli_auth_setup.py create-template

# Validate current authentication configuration
python scripts/cli_auth_setup.py validate

# Show authentication configuration structure
python scripts/cli_auth_setup.py config
```

#### What it does:
- ✅ Creates `.openclaw/.env.example` template
- ✅ Validates that PAT is configured in environment variables
- ✅ Shows default authentication scopes
- ✅ Displays dangerous commands blocked by default

---

### 3. Provisioning Setup (Combined Wizard)
**File:** `cli_provision_setup.py`  
**Usage:** `python scripts/cli_provision_setup.py <command>`  
**Purpose:** Run complete provisioning wizard or individual stages

#### Available subcommands:

```bash
# Full setup wizard (all stages)
python scripts/cli_provision_setup.py setup

# Configure only
python scripts/cli_provision_setup.py config

# Authentication only
python scripts/cli_provision_setup.py auth

# System checks only
python scripts/cli_provision_setup.py system

# Migrate skills only
python scripts/cli_provision_setup.py migrate
```

#### What it does:
- ✅ Orchestrates complete provisioning workflow
- ✅ Runs all four stages sequentially
- ✅ Provides status and progress updates
- ✅ Handles errors gracefully

---

### 4. Configuration Management
**File:** `cli_provision_config.py`  
**Usage:** `python scripts/cli_provision_config.py <command>`  
**Purpose:** Manage configuration with approval prompts

#### Available subcommands:

```bash
# Initialize configuration (interactive)
python scripts/cli_provision_config.py init

# Validate and display current configuration
python scripts/cli_provision_config.py validate

# Example with output:
python scripts/cli_provision_config.py validate
```

---

### 5. Skills Migration
**File:** `cli_provision_migrate.py`  
**Usage:** `python scripts/cli_provision_migrate.py <command>`  
**Purpose:** Migrate existing skills to project repository (sanitized)

#### Available subcommands:

```bash
# Run migration (copy with sanitization)
python scripts/cli_provision_migrate.py run

# Check which skills exist in project
python scripts/cli_provision_migrate.py check

# Example output:
╔═══════════════════════════════════════════════════════╗
   Skills Migration CLI
╚═══════════════════════════════════════════════════════╝

Commands:
  run       - Run migration (copy skills with sanitization)
  check     - Check which skills exist in project
```

#### What it does:
- ✅ Copies skills from previous locations
- ✅ Removes all sensitive data (tokens, passwords, etc.)
- ✅ Creates organized skill repository structure
- ✅ Uses pattern-based redaction for security

---

## 🎯 Quick Start Guide

### Complete Setup Flow

```bash
cd /home/manager/tom-first-project

# Step 1: Initialize configuration
python scripts/cli_provision_config.py init

# Step 2: Create authentication template
python scripts/cli_auth_setup.py create-template

# Step 3: Validate setup (optional)
python scripts/cli_auth_setup.py validate

# Step 4: Run full provisioning wizard
python scripts/cli_provision_setup.py setup

# Step 5: Migrate skills to project
python scripts/cli_provision_migrate.py run

# Step 6: Check system status
python scripts/cli_provision_setup.py system
```

### Individual Stage Setup

```bash
cd /home/manager/tom-first-project

# Just configure without full wizard
python scripts/cli_provision_config.py init

# Configure authentication separately
python scripts/cli_auth_setup.py create-template
echo "GITHUB_PAT=your_token_here" > .openclaw/.env

# Migrate skills only (if needed)
python scripts/cli_provision_migrate.py run

# Verify system checks
python scripts/cli_provision_setup.py system
```

---

## 🔐 Security Best Practices

### 1. Never Store Tokens in Config Files

All provisioning scripts follow this principle:

```bash
# ✅ CORRECT - Use .env file
echo "GITHUB_PAT=your_token_here" > .openclaw/.env

# ❌ WRONG - Don't do this!
python scripts/cli_provision_config.py init  # Without approval prompts
```

### 2. Approval Prompts for Sensitive Operations

Each script requires explicit user approval:

```bash
# Config file created with approval prompts
[3/4] Authentication...
Use Personal Access Token (store in .env file)? [yes/no]: no

Security policies...
Allow elevated file operations (sudo)? [false/true]: false
```

### 3. Sensitive Data Sanitization

Skills are migrated without sensitive data:

```bash
# Original skill might contain:
ghp_vxpw8q1234567890abcdef

# After migration:
[REDACTED_GITHUB_PAT]
```

### 4. Environment Variables for Secrets

```bash
# Store sensitive data in .env, not config.json
cat .openclaw/.env.example
# GITHUB_PAT=ghp_your_token_here

# Load before running scripts
source .openclaw/.env
python scripts/cli_provision_setup.py setup
```

---

## 📝 Unit Tests Location

Comprehensive unit tests are located in:

```bash
tests/
├── __init__.py
├── test_helpers.py              # Utility functions for testing
└── tests_gateway_provisioning/
    ├── __init__.py
    ├── test_config.py           # Tests for config module
    ├── test_auth.py             # Tests for auth module  
    └── test_provisioner.py      # Tests for provisioner module
```

### Running Tests

```bash
cd /home/manager/tom-first-project

# Install test dependencies (via uv)
uv add pytest pydantic

# Run all tests
uv run pytest tests/ -v

# Run specific test module
uv run pytest tests/tests_gateway_provisioning/test_config.py -v

# Run with coverage
uv run pytest tests/ --cov=src/gateway_provisioning --cov-report=term-missing
```

### Test Coverage Areas

- ✅ **Configuration Management:**
  - Loading/saving config files
  - Validating required sections
  - Atomic write operations
  
- ✅ **Authentication:**
  - Template creation
  - Environment variable loading
  - PAT validation
  
- ✅ **Provisioner:**
  - System checks (Python, uv, directories)
  - Skills migration with sanitization
  - Report generation

---

## 🛠️ Troubleshooting

### Issue: "Config file already exists"

```bash
# View current config
python scripts/cli_provision_config.py validate

# Or clear and reinitialize
rm .openclaw/config.json
python scripts/cli_provision_config.py init
```

### Issue: ".env file not found"

```bash
# Create template first
python scripts/cli_auth_setup.py create-template

# Copy and edit
cp .openclaw/.env.example .openclaw/.env
echo "GITHUB_PAT=your_token_here" >> .openclaw/.env
```

### Issue: "Skills not found to migrate"

```bash
# Check source locations
find ~ -name "SKILL.md" 2>/dev/null | head -20

# Migration will work from any of these locations:
# - /home/manager/skills/git-operations/SKILL.md
# - ~/.npm-global/lib/node_modules/openclaw/skills/software-developer/SKILL.md
```

---

## 📚 Git Operations Skill Reference

The skills are organized following best practices:

### Branching Strategy

We use **trunk-based development** for rapid iteration:

```bash
# Feature branches from main/develop
git checkout -b feat/configuration-setup

# Commit with conventional commits
git commit -m "feat: add configuration CLI scripts"

# Push to GitHub
git push -u origin feat/configuration-setup

# When ready, create Pull Request:
# https://github.com/mcrockett86/tom-first-project/pull/new/feat/configuration-setup
```

### PR Template Checklist

When creating a PR for these changes:

- [ ] Code follows team conventions
- [ ] All CI checks pass (linting, typing, tests)
- [ ] Documentation updated where needed
- [ ] No sensitive data exposed in commit diff
- [ ] Git operations skill consulted on structure

---

## 🎯 Summary

This directory provides:

1. **`cli_config_init.py`** - Interactive configuration setup with approval prompts
2. **`cli_auth_setup.py`** - Authentication management (create .env, validate)
3. **`cli_provision_setup.py`** - Full provisioning wizard and system checks
4. **`cli_provision_migrate.py`** - Skills migration with sanitization
5. **Comprehensive unit tests** covering all modules

All scripts follow Git Operations skill best practices:
- ✅ Conventional commits for documentation
- ✅ Security-first design (no tokens in config)
- ✅ Interactive approval prompts
- ✅ Clean, maintainable code structure

**Ready to provision!** 🚀
