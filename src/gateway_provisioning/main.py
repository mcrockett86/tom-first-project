#!/usr/bin/env python3
"""Main entry point for OpenClaw gateway provisioning."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Run the provisioning wizard."""
    from .provisioner import GatewayProvisioner
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║      OpenClaw Gateway Provisioning Wizard                  ║
║  🚀 Setting up agent environment with best practices       ║
╚═══════════════════════════════════════════════════════════╝

This wizard will:
  ✅ Configure gateway connection and authentication
  ✅ Set up security policies for elevated operations
  ✅ Migrate your existing skills to this project repository
  ✅ Create templates for secure environment variables

Notes:
  🔒 Sensitive data (API tokens) are stored in .env file
     - NEVER commit .env to git!
     - Review before adding to source control

Press Ctrl+C anytime to cancel.
""")
    
    print("Starting setup...")
    provisioner = GatewayProvisioner()
    success = provisioner.setup_gateway()
    
    if success:
        print("\n🎉 Provisioning complete! Your environment is ready.\n")
        
        # Suggest next commands
        print("Quick start commands:")
        print("""
  # Add your GitHub PAT to .env file:
  echo "GITHUB_PAT='your_token_here'" >> .openclaw/.env
  
  # Verify installation:
  uv run python -c 'import requests; print("✅ Python + requests working")'
  
  # View available skills in this project:
  ls skills/
  
  # Run the gateway (when configured):
  uv run python src/gateway_provisioning/main.py run
""")
    else:
        print("\n❌ Provisioning failed. Check logs for details.\n")


if __name__ == "__main__":
    main()
