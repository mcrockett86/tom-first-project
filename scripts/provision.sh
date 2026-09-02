#!/bin/bash
# ============================================================================
# OpenClaw Gateway Provisioning CLI
# 
# This script provides command-line interfaces for each provisioning stage.
# Use this to run individual stages of the provisioning workflow.
# ============================================================================

set -euo pipefail

# Add project source to path
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_PATH="$PROJECT_ROOT/src/gateway_provisioning"

# Ensure Python environment is set up
if [ ! -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    echo "⚠️  Virtual environment not found. Run:"
    echo "   cd $PROJECT_ROOT"
    echo "   uv venv --python 3.10"
    echo "   source .venv/bin/activate"
    echo ""
    exit 1
fi

# Activate virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Change to project directory
cd "$PROJECT_ROOT"

# ============================================================================
# Usage Information
# ============================================================================

usage() {
    cat << EOF
OpenClaw Gateway Provisioning CLI v0.1.0

Usage: $(basename "$0") <command> [options]

Available Commands:
  config:init              Initialize gateway configuration (interactive)
  config:show             Display current configuration
  config:update           Update a configuration field
  auth:create             Create authentication setup
  auth:validate           Validate authentication configuration
  provision:setup         Run complete provisioning wizard
  provision:config        Setup only - create config file
  provision:auth          Setup only - configure authentication
  provision:migrate       Migrate existing skills to project repository
  provision:check-system  Run system checks (Python, uv, directories)

Options:
  --help, -h              Show this help message

Examples:
  # Interactive configuration setup
  $(basename "$0") config:init
  
  # View current configuration
  $(basename "$0") config:show
  
  # Create authentication template
  $(basename "$0") auth:create
  
  # Validate authentication is configured
  $(basename "$0") auth:validate

  # Run complete provisioning wizard
  $(basename "$0") provision:setup

EOF
}

# ============================================================================
# Main Command Handler
# ============================================================================

command="config:init"
interactive=true

while [[ $# -gt 0 ]]; do
    case $1 in
        config:init)
            command="config:init"
            shift
            ;;
        config:show)
            command="config:show"
            shift
            ;;
        config:update)
            command="config:update"
            shift
            ;;
        auth:create)
            command="auth:create"
            shift
            ;;
        auth:validate)
            command="auth:validate"
            shift
            ;;
        provision:setup)
            command="provision:setup"
            shift
            ;;
        provision:config)
            command="provision:config"
            shift
            ;;
        provision:auth)
            command="provision:auth"
            shift
            ;;
        provision:migrate)
            command="provision:migrate"
            shift
            ;;
        provision:check-system)
            command="provision:check-system"
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "❌ Unknown command: $1"
            echo ""
            usage
            exit 1
            ;;
    esac
done

echo ""
echo "═══════════════════════════════════════════════════════"
echo "   OpenClaw Gateway Provisioning CLI"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Executing: $command"
echo ""

# ============================================================================
# Command Implementations
# ============================================================================

case $command in
    config:init)
        python3 "$SRC_PATH/main.py" init-config
        
        if [ $? -eq 0 ]; then
            echo "✅ Configuration initialized successfully!"
            echo ""
            echo "View your config with: $(basename "$0") config:show"
        else
            echo "❌ Configuration initialization failed"
            exit 1
        fi
        ;;
    
    config:show)
        CONFIG_FILE="$PROJECT_ROOT/.openclaw/config.json"
        
        if [ ! -f "$CONFIG_FILE" ]; then
            echo "❌ Configuration file not found."
            echo ""
            echo "Run: $(basename "$0") config:init"
            exit 1
        fi
        
        echo "═══════════════════════════════════════════════════════"
        echo "   Current Configuration"
        echo "═══════════════════════════════════════════════════════"
        echo ""
        
        cat "$CONFIG_FILE" | python3 -m json.tool 2>/dev/null || \
            echo "Could not display config (not valid JSON or missing dependencies)"
        
        ;;
    
    config:update)
        CONFIG_FILE="$PROJECT_ROOT/.openclaw/config.json"
        
        if [ ! -f "$CONFIG_FILE" ]; then
            echo "❌ Configuration file not found. Run config:init first."
            exit 1
        fi
        
        echo "═══════════════════════════════════════════════════════"
        echo "   Update Configuration Field"
        echo "═══════════════════════════════════════════════════════"
        echo ""
        
        echo "Available fields:"
        echo "  gateway.host              - Gateway host URL"
        echo "  gateway.api_endpoint      - API endpoint path"
        echo "  auth.use_pat              - Use PAT authentication"
        echo "  security.allow_elevated_ops - Allow elevated operations"
        echo "  security.dangerous_commands - Dangerous command patterns to block"
        echo "  logging.log_level         - Log level (DEBUG/INFO/ERROR)"
        echo ""
        
        read -p "Enter field name: " field_name
        
        if [ -z "$field_name" ]; then
            echo "❌ Field name is required"
            exit 1
        fi
        
        read -s -p "Enter new value: " new_value
        
        if [ -z "$new_value" ]; then
            echo "❌ New value is required"
            exit 1
        fi
        
        # Python script to update config field
        python3 << PYSCRIPT
import json
with open("$CONFIG_FILE", 'r') as f:
    config = json.load(f)

# Parse field name and get the value
field_path = "$field_name"
parts = field_path.split('.')

section = '.'.join(parts[:-1])
subfield = parts[-1]

if section in config and subfield in config[section]:
    # Update if user wants to update
    import sys
    old_value = config[section][subfield]
    
    # For security, we won't auto-update
    print(f"\nCurrent value: {old_value}")
    print(f"New value: $new_value")
    print("\nEnter 'yes' to confirm update, or press Ctrl+C to cancel:")
    sys.stdout.flush()
    
    while True:
        response = input("> ").strip().lower()
        if response == "yes":
            config[section][subfield] = "$new_value"
            with open("$CONFIG_FILE", 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Configuration updated successfully!")
            break
        elif response == "" or response == "cancel":
            break
        else:
            print("Please enter 'yes' to confirm or press Ctrl+C to cancel")
else:
    print(f"❌ Field '{field_path}' not found in configuration")
PYSCRIPT
        
        ;;
    
    auth:create)
        echo "═══════════════════════════════════════════════════════"
        echo "   Create Authentication Setup"
        echo "═══════════════════════════════════════════════════════"
        echo ""
        
        python3 "$SRC_PATH/main.py" auth-setup
        
        ;;
    
    auth:validate)
        echo "═══════════════════════════════════════════════════════"
        echo "   Validate Authentication Configuration"
        echo "═══════════════════════════════════════════════════════"
        echo ""
        
        python3 "$SRC_PATH/main.py" auth-validate
        
        ;;
    
    provision:setup)
        echo "═══════════════════════════════════════════════════════"
        echo "   Complete Provisioning Wizard"
        echo "═══════════════════════════════════════════════════════"
        echo ""
        
        python3 "$SRC_PATH/main.py" setup
        
        ;;
    
    provision:config)
        echo "═══════════════════════════════════════════════════════"
        echo "   Configure Gateway (Configuration Only)"
        echo "═══════════════════════════════════════════════════════"
        echo ""
        
        python3 "$SRC_PATH/main.py" config
        
        ;;
    
    provision:auth)
        echo "═══════════════════════════════════════════════════════"
        echo "   Configure Authentication (Auth Only)"
        echo "═══════════════════════════════════════════════════════"
        echo ""
        
        python3 "$SRC_PATH/main.py" auth
        
        ;;
    
    provision:migrate)
        echo "═══════════════════════════════════════════════════════"
        echo "   Migrate Skills to Project Repository"
        echo "═══════════════════════════════════════════════════════"
        echo ""
        
        python3 "$SRC_PATH/main.py" migrate
        
        ;;
    
    provision:check-system)
        echo "═══════════════════════════════════════════════════════"
        echo "   Run System Checks"
        echo "═══════════════════════════════════════════════════════"
        echo ""
        
        python3 "$SRC_PATH/main.py" check-system
        
        ;;
    
    *)
        usage
        ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════"
