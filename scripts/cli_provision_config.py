#!/usr/bin/env python3
"""CLI Command: provision:config
Interactive configuration setup with approval prompts.

Usage:
    python scripts/cli_provision_config.py --help
    python scripts/cli_provision_config.py init          # Initialize config
    python scripts/cli_provision_config.py validate      # Validate current config
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project source to path
PROJECT_ROOT = Path(__file__).parent.parent / "src" / "gateway_provisioning"
sys.path.insert(0, str(PROJECT_ROOT))


def init_config(interactive: bool = True) -> dict:
    """Initialize configuration with user approval prompts."""
    
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, Input
    
    console = Console()
    
    # Welcome banner
    console.print("\n[bold green]🔐 OpenClaw Gateway Configuration[/green]")
    console.print("=" * 60)
    
    config_file = PROJECT_ROOT.parent.parent / ".openclaw" / "config.json"
    
    # Check if config exists
    if config_file.exists():
        console.print("[yellow]⚠️  Configuration file already exists![/yellow]")
        console.print("Use 'python scripts/cli_provision_config.py validate' to view it.")
        return None
    
    console.print("\n[blue]This will create ~/.openclaw/config.json[/blue]")
    console.print("[blue]Important: Do NOT store API tokens here![/blue]")
    console.print("[blue]Use .env file for sensitive data instead.[/blue]\n")
    
    config = {
        "gateway": {},
        "auth": {},
        "security": {},
        "logging": {}
    }
    
    # 1. Gateway host
    console.print("\n[bold]Step 1 of 4: Gateway Connection[/bold]")
    
    while True:
        host = Input.ask(
            "[dim]Gateway Host URL[/dim] [cyan](leave empty for default)[/cyan]",
            default="http://localhost:8080"
        ) or "http://localhost:8080"
        config["gateway"]["host"] = host
        break
    
    console.print("\n[bold]Step 2 of 4: API Endpoint[/bold]")
    
    while True:
        endpoint = Input.ask(
            "[dim]API Endpoint path[/dim] [cyan](leave empty for default)[/cyan]",
            default="/__openclaw__/api"
        ) or "/__openclaw__/api"
        config["gateway"]["api_endpoint"] = endpoint
        break
    
    # 3. Authentication settings (without tokens!)
    console.print("\n[bold]Step 3 of 4: Authentication[/bold]")
    console.print("[yellow]⚠️  WARNING: Never store API tokens in config files![/yellow]")
    console.print("[green]Use environment variables (.env file) for sensitive data.[/green]\n")
    
    while True:
        use_pat = Confirm.ask(
            "Use Personal Access Token (store in .env file)?",
            default=False,
            show_default=True,
            prompt_suffix="[dim](recommended)[/dim]"
        )
        
        if not use_pat:
            console.print("\n[green]✅ TIP: Create your PAT at:[/green]")
            console.print("[yellow]   https://github.com/settings/tokens[/yellow]")
            break
        else:
            # Reference to env var, not actual token
            config["auth"]["token_variable"] = "GITHUB_PAT"
            config["auth"]["use_pat"] = True
            break
    
    # 4. Security policies
    console.print("\n[bold]Step 3 of 4 (continued): Security Policies[/bold]")
    
    while True:
        allow_elevated = Confirm.ask(
            "Allow elevated file operations (sudo)?",
            default=False,
            show_default=True,
            prompt_suffix="[yellow](⚠️ requires admin rights)[/yellow]"
        )
        
        dangerous_commands = Input.ask(
            "[dim]Dangerous command patterns to block[/dim]",
            default="rm -rf;mount;dd /dev/*",
            default_whisper=True
        ) or "rm -rf;mount;dd /dev/*"
        
        config["security"]["allow_elevated_ops"] = allow_elevated
        config["security"]["dangerous_commands"] = dangerous_commands
        
        while True:
            try:
                max_timeout_input = Input.ask(
                    "[dim]Maximum exec timeout (seconds)[/dim]",
                    default="3600",  # 1 hour
                    default_whisper=True
                ) or "3600"
                config["security"]["max_exec_timeout_s"] = str(int(max_timeout_input))
                break
            except ValueError:
                pass
        break
    
    # 5. Logging configuration
    console.print("\n[bold]Step 4 of 4: Logging[/bold]")
    
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    while True:
        log_level = Confirm.ask(
            f"Log level [cyan]{', '.join(log_levels)}[/cyan]",
            choices=log_levels,
            default="INFO"
        ) or "INFO"
        config["logging"]["log_level"] = log_level.upper()
        break
    
    # Log directory
    log_dir = Input.ask(
        "[dim]Log directory path[/dim] [cyan](use ~ prefix for home dir)[/cyan]",
        default=str(Path.home() / ".openclaw" / "logs"),
        default_whisper=True
    ) or str(Path.home() / ".openclaw" / "logs")
    
    config["logging"]["log_dir"] = log_dir
    
    # Save configuration
    import tempfile
    temp_path = Path(tempfile.mktemp(str(config_file) + '.tmp'))
    with open(temp_path, 'w') as f:
        json.dump(config, f, indent=2)
    temp_path.rename(config_file)
    
    console.print("\n[bold green]✅ Configuration saved![/green]")
    console.print(f"\n📁 Config file: {config_file}")
    console.print("\n📋 Your configuration:")
    console.print(f"   • Gateway Host: {host}")
    console.print(f"   • API Endpoint: {endpoint}")
    console.print(f"   • Dangerous commands blocked: {dangerous_commands}")
    console.print(f"   • Max exec timeout: {config['security']['max_exec_timeout_s']} seconds")
    console.print(f"   • Log level: {log_level.upper()}")
    console.print(f"   • Log directory: {log_dir}\n")
    
    return config


def validate_config() -> dict:
    """Validate and display current configuration."""
    
    from rich.console import Console
    
    console = Console()
    config_file = PROJECT_ROOT.parent.parent / ".openclaw" / "config.json"
    
    if not config_file.exists():
        console.print("[red]❌ Configuration file not found![/red]")
        console.print("\nRun: python scripts/cli_provision_config.py init")
        return None
    
    try:
        with open(config_file) as f:
            config = json.load(f)
            
        console.print("[bold green]📋 Current Configuration[/green]")
        console.print("=" * 60)
        
        console.print("\n[bold dim]Gateway[/bold dim]")
        print(json.dumps(config.get("gateway", {}), indent="   ", sort_keys=True))
        
        console.print("\n[bold dim]Authentication[/bold dim]")
        print(json.dumps(config.get("auth", {}), indent="   ", sort_keys=True))
        
        console.print("\n[bold dim]Security[/bold dim]")
        print(json.dumps(config.get("security", {}), indent="   ", sort_keys=True))
        
        console.print("\n[bold dim]Logging[/bold dim]")
        print(json.dumps(config.get("logging", {}), indent="   ", sort_keys=True))
        
        return config
        
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ Invalid JSON: {e}[/red]")
        return None


def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        description="OpenClaw Gateway Configuration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize configuration interactively
  python scripts/cli_provision_config.py init
  
  # View current configuration
  python scripts/cli_provision_config.py validate

Notes:
  - Do NOT store API tokens in config files!
  - Use .env file for sensitive data (GITHUB_PAT, etc.)
  - For dangerous operations, set allow_elevated_ops=false by default
"""
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        choices=["init", "validate"],
        help="Command to run"
    )
    
    parser.add_argument(
        "--non-interactive", "-n",
        action="store_true",
        help="Disable interactive prompts (not recommended for production)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        # Show help banner
        console = None  # Disable rich output for simple usage
        
        print("\n╔═══════════════════════════════════════════════════════╗")
        print("   OpenClaw Gateway Configuration CLI")
        print("╚═══════════════════════════════════════════════════════╝\n")
        
        print("Commands:")
        print("  init       - Initialize configuration interactively")
        print("  validate   - Display current configuration\n")
        
        print("Usage:")
        print("  python scripts/cli_provision_config.py <command>\n")
        
        print("Examples:")
        print("  # Interactive setup")
        print("  python scripts/cli_provision_config.py init\n")
        
        print("  # View current config")
        print("  python scripts/cli_provision_config.py validate\n")
        
        return
    
    elif args.command == "init":
        if args.non_interactive:
            print("\n[red]❌ Cannot run non-interactively![/red]")
            print("[red]Use terminal for interactive prompts.[/red]\n")
        else:
            init_config()
            
    elif args.command == "validate":
        validate_config()


if __name__ == "__main__":
    main()
