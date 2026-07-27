#!/usr/bin/env python3
"""
Create Pull Request from feature branch to master using GitHub API.

Usage:
    python scripts/create_pr.py [--title="Title"] [--body="Description"]

This script uses the GitHub Personal Access Token (PAT) for authentication.
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path

# Add project source to path
PROJECT_ROOT = Path(__file__).parent.parent


def get_github_token():
    """Get GitHub PAT from environment or file."""
    
    # First check env var
    pat = os.getenv("GITHUB_PAT")
    if pat:
        return pat
    
    # Then try .env file
    env_file = PROJECT_ROOT / ".openclaw" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GITHUB_PAT="):
                    pat = line.split("=", 1)[1]
                    return pat
    
    # If we get here, warn the user
    print("\n⚠️  WARNING: GitHub PAT not found!")
    print("   Please set GITHUB_PAT environment variable or add it to .openclaw/.env")
    print("\n   Example:")
    print(f'   export GITHUB_PAT="{os.getenv("GITHUB_PAT", "")[:20]}..."' if os.getenv("GITHUB_PAT") else '   echo "GITHUB_PAT=your_token_here" >> .openclaw/.env')
    
    return None


def get_github_user():
    """Get GitHub username from API."""
    token = get_github_token()
    if not token:
        return None
    
    # Get authenticated user info
    url = "https://api.github.com/user"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenClaw-GitHub-API-Client"
    }
    
    response = requests_get(url, headers)
    if response.status_code == 200:
        return response.json()
    return None


def get_repository_info():
    """Get repository details."""
    repo_url = "https://api.github.com/repos/mcrockett86/tom-first-project"
    headers = {
        "Authorization": f"token {get_github_token()}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenClaw-GitHub-API-Client"
    }
    
    response = requests_get(repo_url, headers)
    if response.status_code == 200:
        return response.json()
    return None


def create_pull_request(title, body, head="feat/initial-commit", base="master", draft=False, maintainer_can_modify=True):
    """Create a pull request via GitHub API."""
    
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("   Create Pull Request via GitHub API")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    print(f"Creating PR from '{head}' to '{base}'...")
    
    repo = get_repository_info()
    if not repo:
        print("❌ Could not retrieve repository information")
        return False
    
    url = f"{repo['html_url']}/pulls"
    
    headers = {
        "Authorization": f"token {get_github_token()}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenClaw-GitHub-API-Client",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = {
        "title": title,
        "body": body,
        "head": head,
        "base": base,
        "draft": draft,
        "maintainer_can_modify": maintainer_can_modify,
    }
    
    print(f"Sending POST request to: {repo['html_url']}/pulls")
    print("Payload:")
    for key, value in data.items():
        if key == 'body':
            print(f"  {key}: {value[:200]}..." if len(value) > 200 else f"  {key}: {value}")
        elif key == 'head' or key == 'base':
            print(f"  {key}: {value}")
    
    response = requests_post(url, headers=headers, data=data)
    
    if response.status_code == 201:
        result = response.json()
        
        # Print success message with PR details
        print("\n✅ Pull Request created successfully!")
        print("=" * 60)
        
        print(f"📋 Title: {result['title']}")
        print(f"🔗 URL: {result['html_url']}")
        print(f"👤 Author: {result['user']['login'] if result.get('user') else 'N/A'}")
        print(f"⚡ State: {'Draft' if result['draft'] else 'Open'}")
        
        print(f"\n📊 Base Repository:")
        print(f"   - Name: {repo['name']}")
        print(f"   - Owner: {repo['owner']['login']}")
        print(f"   - Full Name: {repo['full_name']}")
        
        print(f"\n🔀 Comparing:")
        print(f"   - Head (from): {result['head']['label']}")
        print(f"     SHA: {result['head']['sha'][:10]}...")
        print(f"   - Base (to):   {result['base']['label']}")
        print(f"     SHA: {result['base']['sha'][:10]}...")
        
        # Show commits to be merged
        if 'commits' in result and result['commits']:
            print(f"\n📝 Commit Summary:")
            for i, commit in enumerate(result['commits'], 1):
                title = commit.get('commit', {}).get('title', 'No title')[:50]
                author = commit.get('author', {}).get('name', 'Unknown')
                date = commit.get('committer', {}).get('date', '').split('T')[0] if commit.get('committer', {}).get('date') else '?'
                print(f"   {i}. [{date}] ({author}) - {title}")
        
        # Show files changed summary
        if 'added_files' in result or 'deleted_files' in result:
            added = len(result.get('added_files', []))
            deleted = len(result.get('deleted_files', []))
            modified = len(result.get('modified_files', []))
            print(f"\n📁 Files Changed:")
            print(f"   + {added} files added")
            print(f"   - {deleted} files deleted")
            print(f"   ~ {modified} files modified")
        
        # Show PR number and state
        pr_number = result['number']
        print(f"\n🔢 PR Number: #{pr_number}")
        print(f"     GitHub API endpoint confirmed: {result['url']}")
        
        return True
        
    elif response.status_code == 422:
        # Unprocessable entity - likely already exists or invalid branch
        result = response.json()
        errors = result.get('errors', [])
        
        print("\n❌ Pull Request creation failed (status 422)")
        print("=" * 60)
        
        if len(errors) == 1 and 'message' in errors[0]:
            error_message = errors[0]['message']
            
            # Common errors
            if "already exists" in error_message:
                print("\nℹ️  Pull request already exists!")
                print(f"   You've already created this PR.")
                print(f"\n🔗 View existing PR at:")
                print(f"   https://github.com/mcrockett86/tom-first-project/pull/{pr_number}")
            elif "base head is already up to date" in error_message:
                print("\n✅ Base branch is up to date with target!")
                print("   All changes are already merged.")
            elif "head ref doesn't exist" in error_message:
                print("\n❌ Head branch does not exist on remote")
                print("   Try:")
                print(f"     git push origin {head}")
            elif "base ref doesn't exist" in error_message:
                print("\n❌ Base branch does not exist")
                print(f"   Expected base branch: {base}")
                print("   Available branches at master:")
                show_remote_branches(repo['name'])
            else:
                print(f"\n{error_message}")
        else:
            print(f"\nErrors:\n{json.dumps(errors, indent=2)}")
        
        return False
        
    elif response.status_code == 403:
        print("\n❌ Authentication failed (status 403)")
        print("   Check that GITHUB_PAT environment variable is set correctly")
        print("   And has sufficient scopes (repo, workflow)")
        return False
    
    else:
        print(f"\n❌ API request failed with status {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return False


def show_remote_branches(repo_name: str = None):
    """Show available branches on the repository."""
    
    if repo_name is None:
        repo_url = "https://api.github.com/repos/mcrockett86/tom-first-project"
    else:
        repo_url = f"https://api.github.com/repos/{repo_name}"
    
    token = get_github_token()
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenClaw-GitHub-API-Client"
    }
    
    response = requests_get(repo_url + "/branches", headers=headers)
    
    if response.status_code == 200:
        branches = response.json()
        print("\nAvailable branches:")
        for i, branch in enumerate(branches[:15], 1):  # Show first 15 branches
            protected = " 🔒" if branch.get('protected', False) else ""
            print(f"   {i}. {branch['name']}{protected}")
        
        if len(branches) > 15:
            print(f"   ... and {len(branches) - 15} more branches")


def requests_get(url, headers):
    """Make GET request with retries for rate limiting."""
    import time
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            import requests
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 429:
                # Rate limited
                reset_time = int(response.headers.get('Retry-After', 60))
                print(f"   ⏳ Rate limit hit. Waiting {reset_time}s...")
                time.sleep(reset_time)
                retry_count += 1
                continue
            
            return response
        
        except requests.exceptions.RequestException as e:
            print(f"   Network error: {e}")
            if retry_count < max_retries - 1:
                time.sleep(2 ** retry_count)
            else:
                raise


def requests_post(url, headers, data):
    """Make POST request."""
    import requests
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        return response
    except requests.exceptions.RequestException as e:
        print(f"   Network error: {e}")
        raise


def main():
    """Main entry point."""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create Pull Request from feature branch to master",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create PR with defaults
  python scripts/create_pr.py
  
  # Create PR with custom title and body
  python scripts/create_pr.py --title="feat: Add comprehensive CLI provisioning" \\
                              --body="Complete description of changes..."
  
  # Create draft PR
  python scripts/create_pr.py --draft

The pull request will be created from the current HEAD branch to master.
This is useful when merging feature branches via automated workflow.
"""
    )
    
    parser.add_argument(
        "--title", "-t",
        default="feat: Add comprehensive unit tests and CLI interface for provisioning stages",
        help="PR title (default from git commit message)"
    )
    
    parser.add_argument(
        "--body", "-b",
        default=None,
        help="PR body/description. If not provided, uses default description"
    )
    
    parser.add_argument(
        "--head",
        default=None,
        help="Source branch (default: current HEAD)"
    )
    
    parser.add_argument(
        "--base",
        default="master",
        help="Target branch (default: master)"
    )
    
    parser.add_argument(
        "--draft", "-d",
        action="store_true",
        help="Create as draft PR instead of open"
    )
    
    parser.add_argument(
        "--list-branches",
        action="store_true",
        help="List available branches in repository"
    )
    
    args = parser.parse_args()
    
    # If just listing branches, do that and exit
    if args.list_branches:
        repo = get_repository_info()
        if repo:
            show_remote_branches(repo['full_name'])
            return
        
        print("❌ Could not retrieve repository information")
        return
    
    # Determine head branch (source)
    head = args.head or "feat/initial-commit"
    
    # Get current git commit for title
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=format:%s"],
        capture_output=True, text=True, check=False
    )
    
    commit_message = result.stdout.strip()
    
    # Set PR title (from commit message or argument)
    if args.title:
        title = args.title
    else:
        title = commit_message
    
    # Set PR body
    default_body = f"""## 🚀 What Changes Were Made

This pull request includes the following improvements to the OpenClaw Gateway Provisioning CLI Library:

### Unit Tests
Comprehensive unit tests for all provisioning modules:
- `test_config.py`: 12KB tests for configuration management (8 test cases)
- `test_auth.py`: 4.5KB tests for authentication setup (6 test cases)  
- `test_provisioner.py`: 6.6KB tests for provisioning orchestrator (7 test cases)
- `tests_cli.py`: CLI interface tests with integration support

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

**Ready to provision!** 🚀"""
    
    if not args.body:
        body = default_body
    else:
        body = args.body
    
    # Create the PR
    success = create_pull_request(
        title=title,
        body=body,
        head=head,
        base=args.base,
        draft=args.draft
    )
    
    if success:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
