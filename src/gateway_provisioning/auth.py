"""Authentication management for OpenClaw gateway."""

import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from typing import Optional, Dict
from dotenv import load_dotenv

console = Console()


class AuthenticationManager:
    """Manages authentication configuration without storing sensitive tokens in config."""

    def __init__(self):
        self.config_dir = Path.home() / ".openclaw"
        self._ensure_auth_dirs()
        
    def _ensure_auth_dirs(self):
        """Create necessary directories for auth artifacts."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        (self.config_dir / "secrets").mkdir(exist_ok=True)
        (self.config_dir / "tokens").mkdir(exist_ok=True)
    
    def create_auth_config(self) -> dict:
        """Create authentication configuration template.
        
        Returns:
            Dictionary with auth settings (without actual tokens)
        """
        console.print("[green]Creating authentication configuration...[/green]")
        
        auth_config = {
            "github": {
                "user": "",  # Will be filled during setup
                "scope": ["repo", "workflow", "read:org"],  # Standard repo access
                "token_variable": "GITHUB_PAT",  # Reference env var, not actual token
                "note": "Store your PAT in environment variable or secure vault"
            },
            "scopes": [
                "operator.admin",  # Gateway admin capabilities
                "operator.approvals",  # Request approvals on behalf of user
                "operator.read",  # Read gateway state
                "operator.write",  # Write to gateway config
                "operator.talk.secrets"  # Handle sensitive operations
            ],
            "deny_commands": [
                "rm -rf *",      # Dangerous bulk delete
                "rm -rf /*",     # Root deletion
                "dd /dev/*",     # Direct block device access
                "mount",         # Mount filesystems (security risk)
                "mkfs",          # Filesystem creation
            ],
            "exec_approval_policy": {
                "enabled": True,
                "log_path": str(self.config_dir / "exec-approvals.json"),
                "dangerous_patterns": [
                    "rm -rf",
                    "dd ",
                    "mv /*",
                    "chmod.*root"
                ]
            }
        }
        
        # Print what needs to be set up
        console.print("[yellow]⚠️  Authentication Setup Required[/yellow]")
        console.print("""
Next steps:

1. GitHub PAT (from your browser or GitHub settings):
   - Go to: https://github.com/username/settings/tokens
   - Create a Personal Access Token with scopes: repo, workflow
   - Store it in environment variable: export GITHUB_PAT='ghp_xxx'
   
2. Add this env var to ~/.bashrc or ~/.zshrc:
   export GITHUB_PAT='your_token_here'
""")
        
        return auth_config
    
    def load_env_variables(self) -> Dict[str, str]:
        """Load environment variables from .env file if it exists."""
        env_file = self.config_dir / ".env"
        
        if env_file.exists():
            load_dotenv(env_file)
            
            console.print("[green]Loaded environment variables from .env[/green]")
            return {
                "github_pat": os.getenv("GITHUB_PAT", ""),
                "gateway_host": os.getenv("GATEWAY_HOST", ""),
            }
        
        console.print("[yellow]No .env file found. Create one with sensitive values.[/yellow]")
        return {}
    
    def validate_auth_setup(self) -> bool:
        """Validate that authentication is properly configured."""
        pat = os.getenv("GITHUB_PAT")
        
        if not pat:
            console.print("[red]❌ GitHub PAT not found in environment variables[/red]")
            console.print("[yellow]Create your token at: https://github.com/settings/tokens[/yellow]")
            return False
        
        # Basic validation (not full API check to avoid unnecessary requests)
        if len(pat) < 10:
            console.print("[red]❌ PAT appears invalid (too short)[/red]")
            return False
        
        console.print("[green]✅ GitHub PAT found and validated[/green]")
        console.print(f"📁 Auth config at: {self.config_dir / '.env.example'}")
        return True
    
    def create_env_template(self) -> None:
        """Create .env.example template for sensitive configuration."""
        template = """# OpenClaw Gateway Environment Variables
# Copy this file to .env and fill in your values
# NEVER commit .env to git!

# GitHub Personal Access Token
# Create at: https://github.com/settings/tokens
# Scopes needed: repo, workflow
GITHUB_PAT=ghp_your_token_here

# Gateway Host (optional, defaults to localhost)
GATEWAY_HOST=http://localhost:8080

# For advanced deployments
# GATEWAY_API_KEY=your_api_key  # If using API key auth
"""
        
        env_file = self.config_dir / ".env"
        template_file = self.config_dir / ".env.example"
        
        with open(template_file, 'w') as f:
            f.write(template)
        
        console.print(f"[green]Created .env.example template[/green]")
        console.print("[yellow]👉 Copy it to .env and add your tokens![/yellow]")
