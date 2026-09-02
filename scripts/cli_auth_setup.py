#!/usr/bin/env python3
"""
CLI Command: auth:set-up
Configure OpenClaw authentication without storing sensitive tokens.

This script creates the .env.example template and validates authentication setup.
It demonstrates best practice of using environment variables for sensitive data.
"""

import os
import sys
from pathlib import Path

# Add project source to path
PROJECT_ROOT = Path(__file__).parent.parent / "src" / "gateway_provisioning"
sys.path.insert(0, str(PROJECT_ROOT))


def create_env_template():
    """Create .env.example template file."""
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("   Create Authentication Template")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    from gateway_provisioning.auth import AuthenticationManager
    
    manager = AuthenticationManager()
    
    # Create the .env.example file
    template_path = PROJECT_ROOT / ".openclaw" / ".env.example"
    if not Path(template_path).parent.exists():
        (template_path.parent).mkdir(parents=True, exist_ok=True)
    
    template_content = """# OpenClaw Gateway Environment Variables
# Copy this file to .env and fill in your values
# NEVER commit .env to git!

# GitHub Personal Access Token
# Create at: https://github.com/settings/tokens
# Required scopes: repo, workflow  
# Optional: read:org, public_repo (depending on use case)
GITHUB_PAT=ghp_your_token_here

# Gateway Host (optional, defaults to localhost)
# Use http:// for local development or your gateway URL for production
GATEWAY_HOST=http://localhost:8080

# For advanced deployments with API key authentication
# GATEWAY_API_KEY=***  # If using API key auth

# Custom log directory (optional)
LOG_DIR=.openclaw/logs

# Enable debug logging (for troubleshooting only)
DEBUG_MODE=false
"""
    
    with open(template_path, 'w') as f:
        f.write(template_content)
    
    print(f"✅ Created template at: {template_path}")
    print("\n📋 Instructions:")
    print("   1. Copy to .env: cp .openclaw/.env.example .openclaw/.env")
    print("   2. Add your GitHub PAT: echo 'GITHUB_PAT=your_token_here' >> .openclaw/.env")
    print("   3. Set gateway host if needed: GATEWAY_HOST=https://your-gateway.com")
    print("\n⚠️  IMPORTANT:")
    print("   - NEVER commit .env to git!")
    print("   - Never include your actual token in example files!")
    
    return template_path


def validate_auth_setup():
    """Validate that authentication is configured."""
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("   Validate Authentication Configuration")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    from gateway_provisioning.auth import AuthenticationManager
    
    manager = AuthenticationManager()
    
    # Check if .env file exists and is loaded
    env_file = PROJECT_ROOT / ".openclaw" / ".env"
    
    if env_file.exists():
        print("✅ .env file found")
        
        # Try to load it (will work if dotenv is installed)
        from dotenv import load_dotenv
        try:
            load_dotenv(str(env_file))
            
            pat = os.getenv("GITHUB_PAT")
            if pat and len(pat) >= 10:
                print(f"✅ GitHub PAT configured ({len(pat)} characters)")
            else:
                print("⚠️  GITHUB_PAT not set or too short")
        except Exception as e:
            print(f"ℹ️  Could not load .env (optional): {type(e).__name__}")
        
        host = os.getenv("GATEWAY_HOST", "not set")
        print(f"📁 Gateway Host: {host or 'using default'}")
    else:
        print("⚠️  .env file not found in .openclaw/")
        print("\n💡 Create one with:")
        print(f"   cd {PROJECT_ROOT}")
        print(f"   cp {PROJECT_ROOT}/.openclaw/.env.example {PROJECT_ROOT}/.openclaw/.env")
        print(f"   echo 'GITHUB_PAT=your_token_here' >> {PROJECT_ROOT}/.openclaw/.env")
    
    # Check if GITHUB_PAT is in environment
    pat = os.getenv("GITHUB_PAT")
    if pat:
        print("\n✅ GITHUB_PAT environment variable set")
        if len(pat) >= 10:
            print(f"   Token length: {len(pat)} chars (minimum recommended)")
    
    # Validate token format (basic check)
    if pat and "ghp_" in pat.lower():
        print("✅ Token appears to be valid GitHub PAT format")
    elif pat:
        print("⚠️  Token format is unclear - verify it's a real GitHub PAT")
    
    # Show what scopes are configured by default
    print("\n🔐 Default authentication scopes:")
    print("   • operator.admin      - Full gateway administration")
    print("   • operator.approvals - Request approvals on behalf of user")
    print("   • operator.read       - Read gateway state and logs")
    print("   • operator.write      - Write to gateway config")
    print("   • operator.talk.secrets - Handle sensitive operations")
    
    # Show dangerous commands blocked by default
    print("\n🛡️  Dangerous commands blocked by default:")
    for cmd in ["rm -rf *", "rm -rf /*", "dd /dev/*", "mount", "mkfs"]:
        print(f"   • {cmd}")


def create_auth_config_template():
    """Create authentication configuration template."""
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("   Create Authentication Configuration Template")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    from gateway_provisioning.auth import AuthenticationManager
    
    manager = AuthenticationManager()
    config = manager.create_auth_config()
    
    # Display the configuration structure (without actual tokens)
    print("📋 Configuration template created with following structure:")
    print("\nGitHub Configuration:")
    print(f"  - user: {config['github'].get('user', '(will be set during setup)')}")
    print(f"  - scope: {', '.join(config['github'].get('scope', ['repo']))}")
    print(f"  - token_variable: {config['github'].get('token_variable', 'GITHUB_PAT')}")
    
    print("\nAuthentication Scopes:")
    for i, scope in enumerate(config['scopes'][:5], 1):
        print(f"   {i}. {scope}")
    if len(config['scopes']) > 5:
        print(f"   ... and {len(config['scopes']) - 5} more")
    
    print("\nSecurity Policies:")
    print("  • Exec approval policy enabled")
    print("  • Dangerous command patterns blocked by default")
    
    # Show deny commands list
    deny_commands = config.get('deny_commands', [])
    print("\n🛡️  Dangerous commands blocked (default):")
    for cmd in deny_commands[:5]:
        print(f"   • {cmd}")
    if len(deny_commands) > 5:
        print(f"   ... and {len(deny_commands) - 5} more")


def main():
    """Main entry point with interactive menu."""
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("   Authentication Setup CLI")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    # Show menu
    print("Available Operations:")
    print("  a) Create .env.example template (recommended first step)")
    print("  v) Validate current authentication setup")
    print("  c) Show authentication configuration template")
    print("  h) Help\n")
    
    while True:
        choice = input("\nSelect operation [a/v/c/h]: ").strip().lower()
        
        if choice == 'a':
            create_env_template()
        elif choice == 'v':
            validate_auth_setup()
        elif choice == 'c':
            create_auth_config_template()
        elif choice == 'h':
            print("\n📖 Help:")
            print("   This CLI manages OpenClaw authentication setup.")
            print("   Best practice: Use environment variables for sensitive data.")
            print("   Never commit .env file to git repository.\n")
        else:
            print("❌ Invalid choice. Press 'a', 'v', 'c', or 'h'")


if __name__ == "__main__":
    main()
