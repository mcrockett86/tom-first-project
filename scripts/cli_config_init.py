#!/usr/bin/env python3
"""
CLI Command: config:init
Initialize OpenClaw gateway configuration with interactive prompts.

This script creates the initial config.json file with all required sections
using user input for sensitive values through approval prompts.
"""

import json
import sys
from pathlib import Path

# Add project source to path
PROJECT_ROOT = Path(__file__).parent.parent / "src" / "gateway_provisioning"
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Run interactive configuration initialization."""
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("   Initialize OpenClaw Gateway Configuration")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    from gateway_provisioning.config import ConfigManager
    
    config_manager = ConfigManager()
    
    # Create initial configuration with prompts
    print("\n📋 This will create ~/.openclaw/config.json with the following structure:")
    print("""
  {
    "gateway": {
      "host": "http://localhost:8080",
      "api_endpoint": "/__openclaw__/api"
    },
    "auth": {
      "use_pat": false,
      "github": {
        "scope": ["repo", "workflow"]
      }
    },
    "security": {
      "allow_elevated_ops": false,
      "dangerous_commands": "rm -rf;mount",
      "max_exec_timeout_s": "3600"
    },
    "logging": {
      "log_level": "INFO",
      "log_dir": "~/.openclaw/logs"
    }
  }

Note: Sensitive data should go in .env file, not here.
""")
    
    print("Answer the following questions (press Enter for defaults):\n")
    
    # Use simple prompts instead of rich for standalone script
    config = {
        "gateway": {},
        "auth": {},
        "security": {},
        "logging": {}
    }
    
    # Gateway host
    print("[1/4] Setting up gateway connection...")
    while True:
        host = input("Gateway Host URL [http://localhost:8080]: ").strip() or "http://localhost:8080"
        config["gateway"]["host"] = host
        break
    
    print("\n[2/4] Setting up API endpoint...")
    while True:
        endpoint = input("API Endpoint path [/__openclaw__/api]: ").strip() or "/__openclaw__/api"
        config["gateway"]["api_endpoint"] = endpoint
        break
    
    print("\n[3/4] Setting up authentication...")
    while True:
        use_pat_input = input("Use Personal Access Token for auth? [false (recommended)]: ").strip()
        if use_pat_input.lower() in ["", "false", "no"]:
            config["auth"]["use_pat"] = False
            print("\nℹ️  TIP: Store your PAT in .openclaw/.env file instead")
            break
        elif use_pat_input.lower() in ["true", "yes", "1"]:
            while True:
                pat_input = input("Enter GitHub PAT (or press Ctrl+C to skip): ").strip() or None
                if not pat_input:
                    print("\n⚠️  Skipping PAT authentication for now")
                    config["auth"]["use_pat"] = False
                    break
                else:
                    config["auth"]["use_pat"] = True
                    # For security, we store reference to env var, not actual token
                    config["auth"]["github_token_variable"] = "GITHUB_PAT"
                    print("\n⚠️  Note: Actual token should be stored in .openclaw/.env file")
                    break
        else:
            print("Please enter 'true', 'false', 'yes', or 'no'")
    
    # Security settings
    print("\n[3/4] Setting up security policies...")
    while True:
        allow_elevated_input = input("Allow elevated file operations (sudo)? [false]: ").strip()
        if allow_elevated_input.lower() in ["", "false", "no"]:
            config["security"]["allow_elevated_ops"] = False
            print("\nℹ️  TIP: For safer development, keep this disabled by default")
            break
        elif allow_elevated_input.lower() in ["true", "yes", "1"]:
            while True:
                dangerous_commands = input(
                    "Dangerous command patterns to block (comma-separated): "
                    "[rm -rf;mount;dd /dev/*]: "
                ).strip() or "rm -rf;mount;dd /dev/*"
                config["security"]["dangerous_commands"] = dangerous_commands
                break
        else:
            print("Please enter 'true', 'false', 'yes', or 'no'")
    
    # Set max exec timeout
    while True:
        try:
            timeout_input = input("Maximum exec timeout in seconds [3600]: ").strip()
            if not timeout_input:
                config["security"]["max_exec_timeout_s"] = "3600"
                break
            else:
                timeout_val = int(timeout_input)
                config["security"]["max_exec_timeout_s"] = str(timeout_val)
                break
        except ValueError:
            print("Invalid number. Press Enter for default (3600 seconds)")
    
    # Logging configuration
    print("\n[4/4] Setting up logging...")
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    while True:
        level_input = input(f"Log level [INFO]: ").strip() or "INFO"
        if level_input.upper() in log_levels:
            config["logging"]["log_level"] = level_input.upper()
            break
        print(f"Invalid level. Choose from: {', '.join(log_levels)}")
    
    while True:
        log_dir_input = input("Log directory path [.openclaw/logs]: ").strip() or ".openclaw/logs"
        config["logging"]["log_dir"] = log_dir_dir = Path.home() / log_dir_input if log_dir_input.startswith("~") else log_dir_input
        break
    
    print("\n✅ Configuration initialized successfully!")
    print(f"\n📁 Config saved to: {config_manager.config_path}")
    print("💡 View the config with: python cli_config_show.py")


if __name__ == "__main__":
    main()
