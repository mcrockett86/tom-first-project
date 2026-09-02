# OpenClaw Gateway Provisioning Scripts 🚀

**Repository:** `tom-first-project`  
**Agent:** Tom  
**Status:** Initial Commit (2026-07-26)  
**Branch:** `feat/initial-commit` → Merge to `master` via PR

---

## 🎯 Purpose

This repository contains OpenClaw gateway provisioning scripts and tools for setting up and managing agent environments. It represents the initial state of the "Tom" agent and serves as a template for future evolution.

### What's Included:

- 🔧 **Python Provisioning Scripts** - Automated setup with approval prompts
- 🛡️ **Security Best Practices** - Safe handling of sensitive data
- 📚 **Git Operations Skills** - Repository management best practices
- 🌐 **Browser Automation Skills** - Advanced web automation capabilities
- 💻 **Software Developer Skills** - Code quality guidance

---

## 📋 Quick Start

### 1. Prerequisites

```bash
# Install uv (recommended package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use pip if uv is not available
pip install uv
```

### 2. Set Up the Project

```bash
cd /home/manager/tom-first-project

# Create virtual environment using uv
uv venv --python 3.10

# Install dependencies
uv sync

# Activate environment
source .venv/bin/activate
```

### 3. Configure Authentication

```bash
# Copy environment template
cp .openclaw/.env.example .openclaw/.env

# Add your GitHub PAT (from: https://github.com/settings/tokens)
echo 'GITHUB_PAT=ghp_your_token_here' >> .openclaw/.env

# Set gateway host if different from default
echo 'GATEWAY_HOST=http://localhost:8080' >> .openclaw/.env
```

### 4. Run Provisioning Wizard

```bash
# Interactive setup with approval prompts
uv run python src/gateway_provisioning/main.py

# Or use provisioning CLI
uv run python src/gateway_provisioning/main.py setup
```

---

## 🎨 User Approval Workflow

This project uses **interactive approval prompts** for sensitive operations:

### Configuration Setup

When running `python main.py`, you'll see prompts like:

```
[1/4] Setting up gateway connection...
Gateway Host URL (leave empty for default) [http://localhost:8080]: 

⚠️  WARNING: Never store API tokens in config files!
Instead, use environment variables (.env file)
```

### Sensitive Data Handling

**NEVER** include API tokens or secrets in:
- ❌ `.openclaw/config.json` (config file)
- ❌ Git repository (never commit sensitive data)

**ALWAYS** use:
- ✅ `.openclaw/.env` (local environment file, never committed)
- ✅ Environment variables (`export GITHUB_PAT='...'`)
- ✅ Secure vault systems for production

---

## 📁 Project Structure

```
tom-first-project/
├── README.md                      # This file
├── pyproject.toml                 # Python project configuration
├── .gitignore                     # Git ignore rules
├── .openclaw/
│   ├── .env.example              # Template for sensitive vars
│   └── config.json               # Main config (created during setup)
├── src/
│   └── gateway_provisioning/
│       ├── __init__.py           # Package exports
│       ├── main.py               # Entry point / CLI
│       ├── provisioner.py        # Main provisioning logic
│       ├── config.py             # Configuration management
│       └── auth.py               # Authentication setup
├── skills/
│   ├── git-operations/           # Git workflow best practices
│   │   └── SKILL.md
│   ├── advanced-browser-auto...  # Web automation capabilities
│   │   └── SKILL.md
│   └── software-developer/       # Code quality guidance
│       └── SKILL.md
├── templates/
│   └── example-config.json       # Example configuration template
├── tests/                        # Test files (add as needed)
└── scripts/                     # Helper scripts
```

---

## 🚀 Usage Examples

### Create New Repository

```bash
# Using the Git Operations skill workflow
cd /home/manager
uv run python -c "from git_operations import create_repo; \
    create_repo('my-new-project', description='New project')"
```

### Provision Gateway Environment

```bash
# Interactive provisioning wizard
uv run python src/gateway_provisioning/main.py

# Or programmatic provisioning
python -c "
from src.gateway_provisioning import GatewayProvisioner
provisioner = GatewayProvisioner()
provisioner.setup_gateway()
"
```

### Validate Configuration

```bash
# Check if environment is properly configured
uv run python -c "
from src.gateway_provisioning import AuthenticationManager
auth = AuthenticationManager()
if auth.validate_auth_setup():
    print('✅ Authentication configured correctly')
else:
    print('❌ Please configure GITHUB_PAT in .env file')
"
```

---

## 🔐 Security Best Practices

### 1. Sensitive Data Handling

```bash
# ✅ CORRECT - Use environment variables
export GITHUB_PAT='ghp_xxx'
python script.py

# ❌ WRONG - Don't store tokens in config files
config.json: { "github_pat": "ghp_xxx" }  # NEVER DO THIS!
```

### 2. Never Commit Sensitive Files

```bash
# .gitignore already excludes these:
.env
*.env
.env.*

# Add any new sensitive files to .gitignore
```

### 3. Use Secure Vault Systems in Production

For production deployments, integrate with:
- HashiCorp Vault
- AWS Secrets Manager  
- Azure Key Vault
- GCP Secret Manager

---

## 📚 Git Workflow (Git Operations Skill)

### Branching Strategy

We use **trunk-based development** for rapid iteration:

```bash
# Feature branches from main
git checkout -b feat/initial-commit

# Commit with conventional commits
git commit -m "feat: add initial provisioning scripts"

# Push to GitHub
git push -u origin feat/initial-commit
```

### Creating a Pull Request

When ready to merge:

```bash
# Complete final changes
git add .
git commit -m "docs: update README with setup instructions"

# Force push if needed (after squash)
git push -f origin feat/initial-commit

# Open PR on GitHub: https://github.com/mcrockett86/tom-first-project/pulls
```

**PR Template:**
- [ ] Code follows team conventions
- [ ] All CI checks pass
- [ ] Documentation updated where needed
- [ ] No sensitive data exposed

---

## 🛠️ Development Commands

```bash
# Install dependencies (uv)
uv sync --dev

# Run tests
uv run pytest

# Lint code
uv run ruff check src/
uv run ruff format src/

# Type check
uv run pyright src/
```

---

## 📖 Documentation

### Git Operations Skill (`skills/git-operations/SKILL.md`)

- Branching strategies (GitFlow, trunk-based)
- Commit message conventions
- PR workflow and review processes
- Conflict resolution patterns

### Software Developer Skill (`skills/software-developer/SKILL.md`)

- Code quality principles
- SOLID design patterns
- Testing best practices
- Refactoring guidelines

### Advanced Browser Automation Skill (`skills/advanced-browser-auto.../SKILL.md`)

- Anti-bot detection evasion
- CAPTCHA handling strategies
- Login form complexity handling
- SPA navigation optimization

---

## 🔧 Troubleshooting

### Issue: "Authentication failed"

**Solution:**
```bash
# Check PAT is set
echo $GITHUB_PAT

# Verify in .env file
cat .openclaw/.env | grep GITHUB_PAT
```

### Issue: "uv not found"

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use pip
pip install uv
```

### Issue: "Permission denied when writing config"

**Solution:**
```bash
# Check permissions
ls -la ~/.openclaw/

# Fix ownership if needed
sudo chown -R \$USER ~/.openclaw
```

---

## 📝 License

MIT License - Same as OpenClaw project

---

## 🔗 Useful Links

- **GitHub:** https://github.com/mcrockett86/tom-first-project
- **Skills Documentation:** https://docs.openclaw.ai/skills
- **Git Best Practices:** `skills/git-operations/SKILL.md`
- **Developer Guidelines:** `skills/software-developer/SKILL.md`

---

**🎉 Happy Coding!** 🚀
