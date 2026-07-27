#!/usr/bin/env bash
# Create Pull Request from feature branch to master using GitHub API
# Usage: ./scripts/create_pr.sh --title="PR Title"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load GitHub PAT from environment or .env file
if [[ -n "${GITHUB_PAT:-}" ]]; then
    echo "✅ Using GITHUB_PAT from environment variable"
elif [[ -f "$PROJECT_ROOT/.openclaw/.env" ]]; then
    export GITHUB_PAT=$(grep '^GITHUB_PAT=' "$PROJECT_ROOT/.openclaw/.env" | cut -d'=' -f2 | tr -d '"')
    echo "✅ Loaded GITHUB_PAT from .openclaw/.env"
else
    echo "❌ GITHUB_PAT not found in environment or .openclaw/.env"
    echo "   Please set it with: export GITHUB_PAT='your_token_here'"
    exit 1
fi

# Default values
DEFAULT_TITLE="feat: Add comprehensive unit tests and CLI interface for provisioning stages"
DEFAULT_BODY=$(cat << 'EOF'
## 🚀 What Changes Were Made

This pull request includes the following improvements to the OpenClaw Gateway Provisioning CLI Library:

### Unit Tests
Comprehensive unit tests for all provisioning modules:
- **test_config.py**: 12KB tests for configuration management (8 test cases)
- **test_auth.py**: 4.5KB tests for authentication setup (6 test cases)  
- **test_provisioner.py**: 6.6KB tests for provisioning orchestrator (7 test cases)
- **tests_cli.py**: CLI interface tests with integration support

### CLI Interface Scripts
Complete CLI interface for each main provisioning stage:
1. `cli_config_init.py` - Interactive configuration setup with approval prompts
2. `cli_auth_setup.py` - Authentication management (create .env, validate)
3. `cli_provision_setup.py` - Full provisioning wizard and system checks
4. `cli_provision_migrate.py` - Skills migration with sanitization

### Documentation
- Comprehensive README for all CLI scripts
- Quick start guide with examples
- Security best practices documentation
- Git Operations skill references
- Troubleshooting section

### GitHub Actions CI/CD Pipeline
Automated workflows for building, testing, and releasing:
- Linting and code quality checks (ruff, black, flake8)
- Type checking with MyPy
- Unit tests with pytest coverage reporting
- Integration tests for CLI scripts
- Security scanning for dependencies
- Automatic package building

### Pre-commit Hooks
Automated code quality checks before each commit:
- Trailing whitespace removal
- End-of-file newline enforcement
- Large file detection (>500KB warnings)
- YAML/JSON syntax validation
- Ruff linting and Black formatting

## 🔐 Security Features

The implementation follows security best practices:

✅ No API tokens in config files (use .env instead)  
✅ Interactive approval prompts for sensitive operations  
✅ Pattern-based sanitization of skills during migration  
✅ Comprehensive CI/CD pipeline checks  
✅ Dangerous command patterns blocked  

## 🧪 Testing Coverage

```bash
uv add pytest pydantic coverage
uv run pytest tests/ -v --cov=src/gateway_provisioning --cov-report=term-missing
```

Coverage is tracked for:
- Configuration management module
- Authentication setup module
- Provisioner orchestrator module
- CLI script validation

## 🛠️ Development Commands

See `scripts/README.md` for usage guide.

## 🔗 Related Documentation

- [Git Operations Skill](skills/git-operations/SKILL.md)
- [Software Developer Skill](skills/software-developer/SKILL.md)
- [Advanced Browser Automation Skill](skills/advanced-browser-automation/SKILL.md)

---

**Ready to provision!** 🚀
EOF
)

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --title|-t)
            DEFAULT_TITLE="$2"
            shift 2
            ;;
        --body|-b)
            DEFAULT_BODY="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Get current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "🔍 Current branch: $CURRENT_BRANCH"

# Validate head branch exists
if [[ "$CURRENT_BRANCH" != "feat/initial-commit" ]]; then
    echo "⚠️  Warning: Current branch is '$CURRENT_BRANCH', but expected 'feat/initial-commit'"
    read -p "Continue with current branch? (y/n): " -n 1 -r
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        exit 1
    fi
fi

# Get repository details
echo "📦 Retrieving repository information..."
REPO_INFO=$(curl -s -H "Authorization: token $GITHUB_PAT" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/mcrockett86/tom-first-project")

if [[ $? -ne 0 ]]; then
    echo "❌ Failed to retrieve repository info"
    exit 1
fi

# Get PR number if exists (to avoid duplicates)
EXISTING_PR=$(curl -s -H "Authorization: token $GITHUB_PAT" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/mcrockett86/tom-first-project/pulls?state=open&head=feat%2Finitial-commit&base=master")

if [[ -n "$EXISTING_PR" ]] && [[ "$EXISTING_PR" != "[]" ]]; then
    # Parse first PR number
    PR_NUMBER=$(echo "$EXISTING_PR" | jq -r '.[0].number' 2>/dev/null || echo "")
    
    if [[ -n "$PR_NUMBER" ]]; then
        echo ""
        echo "⚠️  Pull request already exists! Number: #$PR_NUMBER"
        echo "🔗 View existing PR at:"
        echo "   https://github.com/mcrockett86/tom-first-project/pull/$PR_NUMBER"
        echo ""
        
        read -p "Create duplicate PR anyway? (y/n): " -n 1 -r
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "⚠️  WARNING: Creating duplicate PR may cause conflicts!"
            read -p "Continue? (y/n): " -n 1 -r
            if [[ $REPLY =~ ^[Nn]$ ]]; then
                exit 0
            fi
        else
            echo "Cancelled."
            exit 0
        fi
    fi
fi

# Create the pull request
echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "   Creating Pull Request via GitHub API"
echo "╚═══════════════════════════════════════════════════════╝"

echo "Creating PR from '$CURRENT_BRANCH' to 'master'..."
echo "📝 Title: $DEFAULT_TITLE"

RESPONSE=$(curl -s -X POST \
    -H "Authorization: token $GITHUB_PAT" \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Content-Type: application/json; charset=utf-8" \
    --data "{\"title\":\"$DEFAULT_TITLE\",\"body\":\"$(echo "$DEFAULT_BODY" | jq -Rs .)\" , \"head\":\"$CURRENT_BRANCH\", \"base\":\"master\", \"draft\":false, \"maintainer_can_modify\":true}" \
    "https://api.github.com/repos/mcrockett86/tom-first-project/pulls")

if [[ $? -eq 0 ]]; then
    PR_NUMBER=$(echo "$RESPONSE" | jq -r '.number')
    PR_HTML_URL=$(echo "$RESPONSE" | jq -r '.html_url')
    PR_TITLE=$(echo "$RESPONSE" | jq -r '.title')
    
    echo ""
    echo "✅ Pull Request created successfully!"
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "   📋 Title: $PR_TITLE"
    echo "   🔗 URL: $PR_HTML_URL"
    echo "   👤 Author: $(echo "$RESPONSE" | jq -r '.user.login // "N/A"')"
    echo "   ⚡ State: Open"
    echo ════════════════════════════════════════════════════════╗"
    
    # Show commits
    if [[ $(echo "$RESPONSE" | jq '.commits | length') -gt 0 ]]; then
        echo ""
        echo "📝 Commit Summary:"
        for commit in $(echo "$RESPONSE" | jq -c '.commits[]'); do
            title=$(echo "$commit" | jq -r '.commit.title')
            author=$(echo "$commit" | jq -r '.author.name')
            date=$(echo "$commit" | jq -r '.committer.date' | cut -dT -f1)
            echo "   • [$date] ($author) - ${title:0:60}"
        done
    fi
    
    # Show files changed summary
    added=$(echo "$RESPONSE" | jq '.added_files // [] | length')
    deleted=$(echo "$RESPONSE" | jq '.deleted_files // [] | length' 2>/dev/null || echo "0")
    modified=$(echo "$RESPONSE" | jq '.modified_files // [] | length' 2>/dev/null || echo "0")
    
    echo ""
    echo "📁 Files Changed:"
    echo "   + $added files added"
    echo "   - $deleted files deleted (if any)"
    echo "   ~ $modified files modified"
    
    echo ""
    echo "🔢 PR Number: #$PR_NUMBER"
else
    RESPONSE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: token $GITHUB_PAT" \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Content-Type: application/json; charset=utf-8" \
        --data "{\"title\":\"$DEFAULT_TITLE\",\"body\":\"$(echo "$DEFAULT_BODY" | jq -Rs .)\" , \"head\":\"$CURRENT_BRANCH\", \"base\":\"master\", \"draft\":false, \"maintainer_can_modify\":true}" \
        "https://api.github.com/repos/mcrockett86/tom-first-project/pulls")
    
    echo ""
    echo "❌ Pull Request creation failed with status: $RESPONSE_STATUS"
    echo ""
    if [[ "$RESPONSE_STATUS" == "422" ]]; then
        # Try to get error message
        ERROR_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_PAT" \
            -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/repos/mcrockett86/tom-first-project/pulls?state=open&head=feat%2Finitial-commit&base=master")
        if [[ -n "$ERROR_RESPONSE" ]] && [[ "$ERROR_RESPONSE" != "[]" ]]; then
            PR_NUMBER=$(echo "$ERROR_RESPONSE" | jq -r '.[0].number' 2>/dev/null)
            echo ""
            echo "Existing pull request found. View at:"
            echo "   https://github.com/mcrockett86/tom-first-project/pull/$PR_NUMBER"
        fi
    fi
fi

echo ""
echo "✅ Pull Request creation complete!"
exit 0
