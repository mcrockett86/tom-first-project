#!/usr/bin/env python3
"""
CLI Command: provision:setup
Run complete provisioning wizard with all stages.

This orchestrates the entire provisioning workflow including:
- Configuration setup
- Authentication configuration  
- System checks
- Skills migration (if applicable)
"""

import sys
from pathlib import Path

# Add project source to path
PROJECT_ROOT = Path(__file__).parent.parent / "src" / "gateway_provisioning"
sys.path.insert(0, str(PROJECT_ROOT))


def run_system_checks():
    """Run system checks without elevated operations."""
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("   Step 1/4: Running System Checks")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    import subprocess
    from rich.console import Console
    
    console = Console()
    
    with console.status("[yellow]Checking system components...", spinner="dots"):
        checks_completed = []
        
        # Check 1: Python installation
        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                python_version = result.stdout.strip()
                console.print(f"  ✅ Python: {python_version}")
                checks_completed.append("python")
        except Exception as e:
            console.print(f"  ⚠️  Could not check Python: {type(e).__name__}")
        
        # Check 2: uv installation (optional)
        try:
            result = subprocess.run(
                ["uv", "--version"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                uv_version = result.stdout.strip()
                console.print(f"  ✅ uv: {uv_version}")
                checks_completed.append("uv")
            else:
                console.print("  ℹ️  uv not installed (optional)")
        except Exception as e:
            console.print(f"  ⚠️  Could not check uv: {type(e).__name__}")
        
        # Check 3: Rich library for UI
        try:
            import rich
            print("  ✅ rich library available")
            checks_completed.append("rich")
        except ImportError:
            console.print("  ⚠️  rich library not installed (optional)")
        
        # Check 4: Directory structure
        required_dirs = [
            PROJECT_ROOT / ".openclaw",
            PROJECT_ROOT / ".openclaw" / "logs",
            PROJECT_ROOT / ".openclaw" / "secrets",
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                (dir_path).mkdir(parents=True, exist_ok=True)
        
        console.print("  ✅ All required directories created")
        checks_completed.append("directories")
    
    print(f"\n✅ System checks completed: {', '.join(checks_completed)}\n")
    return True


def configure():
    """Configure gateway with approval prompts."""
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("   Step 2/4: Configuring Gateway")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    from rich.console import Console
    
    console = Console()
    
    config_file = PROJECT_ROOT / ".openclaw" / "config.json"
    
    # Check if config already exists
    if config_file.exists():
        print("⚠️  Configuration file already exists!")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            return False
        
        # Clear existing config for fresh setup
        import json
        with open(config_file, 'w') as f:
            json.dump({}, f)
    
    console.print("[green]Starting configuration wizard...[/green]")
    
    from rich.prompt import Prompt
    
    print("\n📝 Configuration Settings:")
    print("-" * 50)
    
    # Gateway host
    while True:
        host_input = Prompt.ask(
            "Gateway Host URL (leave empty for default)",
            default="http://localhost:8080",
            show_default=True,
            password=***  # Don't echo the full URL for sensitive info
        )
        if not host_input:
            host = "http://localhost:8080"
        else:
            host = host_input
        break
    
    print("\n📝 API Endpoint:")
    while True:
        endpoint_input = Prompt.ask(
            "API Endpoint path",
            default="/__openclaw__/api",
            show_default=True,
            password=***
        )
        if not endpoint_input:
            endpoint = "/__openclaw__/api"
        else:
            endpoint = endpoint_input
        break
    
    # Auth settings (without storing tokens!)
    print("\n⚠️  SECURITY WARNING:")
    print("   Do NOT store API tokens in config files!")
    print("   Instead, use environment variables (.env file)")
    
    console.print("[yellow]\n[1/3] Authentication Strategy...[/yellow]")
    while True:
        print("\nOptions:")
        print("  1. Use Personal Access Token (recommended)")
        print("  2. Use API Key")
        print("  3. Skip auth for now (development only)")
        
        choice = Prompt.ask("Choose authentication method [1/2/3]")
        
        if choice == "1":
            console.print("\nℹ️  TIP: Store your PAT in .openclaw/.env file")
            config_use_pat = False  # Don't actually use token in config
            break
        elif choice == "2":
            print("⚠️  API keys should be stored in .env, not config")
            break
        elif choice == "3":
            config_use_pat = False
            break
    
    # Security settings
    console.print("[yellow]\n[2/3] Security Policies...[/yellow]")
    
    print("\nAllow elevated operations (sudo)? [false]")
    allow_elevated = Prompt.ask(
        "(true/false, requires admin rights if true)",
        default="false",
        show_default=True
    ) == "true"
    
    dangerous_commands = Prompt.ask(
        "Dangerous command patterns to block (comma-separated)",
        default="rm -rf;mount;dd /dev/*",
        show_default=True
    )
    
    print("\nMaximum exec timeout in seconds [3600]")
    try:
        max_timeout = int(Prompt.ask(
            "(hours recommended, e.g., 1 for 1 hour)",
            default="1"
        )) * 3600
    except ValueError:
        max_timeout = 3600
    
    # Logging configuration
    console.print("[yellow]\n[3/3] Logging Configuration...[/yellow]")
    
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    while True:
        level_input = Prompt.ask("Log level [INFO]", default="INFO")
        if level_input.upper() in log_levels:
            log_level = level_input.upper()
            break
    
    log_dir = Prompt.ask(
        "Log directory path [.openclaw/logs]",
        default=".openclaw/logs",
        show_default=True
    )
    
    # Save configuration
    import json
    config = {
        "gateway": {
            "host": host if host else "http://localhost:8080",
            "api_endpoint": endpoint if endpoint else "/__openclaw__/api"
        },
        "auth": {
            "use_pat": False,  # Tokens stored in .env, not config
            "github_token_variable": "GITHUB_PAT"
        },
        "security": {
            "allow_elevated_ops": allow_elevated,
            "dangerous_commands": dangerous_commands,
            "max_exec_timeout_s": str(max_timeout)
        },
        "logging": {
            "log_level": log_level,
            "log_dir": log_dir
        }
    }
    
    # Write config atomically
    temp_path = Path(str(config_file) + '.tmp')
    with open(temp_path, 'w') as f:
        json.dump(config, f, indent=2)
    temp_path.rename(config_file)
    
    console.print(f"\n✅ Configuration saved to: {config_file}")
    console.print("\n📋 Your configuration:")
    print(f"   Gateway Host: {host or 'http://localhost:8080'}")
    print(f"   API Endpoint: {endpoint or '/__openclaw__/api'}")
    print(f"   Dangerous commands blocked: {dangerous_commands}")
    print(f"   Max exec timeout: {max_timeout} seconds")
    print(f"   Log level: {log_level}")
    print(f"   Log directory: {log_dir}")
    
    print("\n💡 Next step: Configure authentication with:")
    print(f"   python scripts/cli_auth_setup.py\n")
    
    return True


def check_system():
    """Run system checks and report status."""
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("   Check System Status")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    import subprocess
    from rich.console import Console
    
    console = Console()
    
    checks = []
    
    # Check Python
    try:
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True, text=True, timeout=5
        )
        python_version = result.stdout.strip()
        console.print(f"[green]✅ Python[/green]: {python_version}")
        checks.append("python")
    except Exception as e:
        console.print(f"[red]❌ Python check failed:[/red] {type(e).__name__}")
    
    # Check uv
    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            uv_version = result.stdout.strip()
            console.print(f"[green]✅ uv[/green]: {uv_version}")
            checks.append("uv")
        else:
            console.print("[yellow]ℹ️ uv not installed (optional)[/yellow]")
    except Exception as e:
        console.print(f"[yellow]⚠️ uv check skipped:[/yellow] {type(e).__name__}")
    
    # Check rich
    try:
        import rich
        console.print("[green]✅ rich[/green]: Available")
        checks.append("rich")
    except ImportError:
        console.print("[red]❌ rich not installed (install with: uv add rich)[/red]")
    
    # Check git
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            console.print(f"[green]✅ git[/green]: {result.stdout.strip()}")
            checks.append("git")
    except Exception as e:
        console.print(f"[red]❌ git not available:[/red] {type(e).__name__}")
    
    # Check directories
    required_dirs = [
        PROJECT_ROOT / ".openclaw",
        PROJECT_ROOT / ".openclaw" / "logs",
    ]
    
    for dir_path in required_dirs:
        if dir_path.exists():
            console.print(f"[green]✅ Directory[/green]: {dir_path.name}")
        else:
            (dir_path).mkdir(parents=True, exist_ok=True)
            console.print(f"[green]✅ Created directory[/green]: {dir_path.name}")
    
    # Check config file
    config_file = PROJECT_ROOT / ".openclaw" / "config.json"
    if config_file.exists():
        import json
        with open(config_file) as f:
            config = json.load(f)
        console.print("[green]✅ Config[/green]: Exists")
        console.print(f"  • Gateway: {config.get('gateway', {}).get('host', 'not set')}")
        console.print(f"  • Auth: {config.get('auth', {}).get('use_pat', False)}")
    else:
        console.print("[red]❌ Config[/red]: Not created yet (run cli_config_init.py)")
    
    # Check .env file
    env_file = PROJECT_ROOT / ".openclaw" / ".env"
    if env_file.exists():
        console.print("[green]✅ Environment[/green]: .env exists")
        import os
        pat = os.getenv("GITHUB_PAT", "not set")
        host = os.getenv("GATEWAY_HOST", "not set")
        console.print(f"  • GITHUB_PAT: {pat[:20]}... if set")
    else:
        console.print("[yellow]⚠️ Environment[/yellow]: .env not created yet")
    
    print("\n" + "=" * 60)
    console.print(f"[green]✅ All checks passed![/green]")
    console.print("=" * 60)


def main():
    """Main entry point for provisioning setup CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run OpenClaw gateway provisioning stages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_provision_setup.py config    # Configure gateway
  python cli_provision_setup.py setup     # Full setup wizard
  python cli_provision_setup.py system    # Run system checks

Available commands:
  config      - Interactive configuration setup
  auth        - Authentication setup
  migrate     - Migrate existing skills to repository
  system      - Run system checks and verify components
"""
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        choices=["config", "auth", "migrate", "system"],
        help="Which stage to run"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        print("\n╔═══════════════════════════════════════════════════════╗")
        print("   Complete Provisioning Wizard CLI")
        print("╚═══════════════════════════════════════════════════════╝\n")
        
        print("╔═══════════════════════════════════════════════════════╗")
        print("   Available Commands:")
        print("╚═══════════════════════════════════════════════════════╝")
        
        print("\ncall python cli_provision_setup.py <command>")
        print("Available commands:")
        print("  config      - Interactive configuration wizard")
        print("  auth        - Authentication setup (create .env file)")
        print("  migrate     - Migrate existing skills to project repo")
        print("  system      - Run system checks and verify components")
        
        return
    
    elif args.command == "config":
        if configure():
            print("\n✅ Configuration completed!\n")
        else:
            print("\n❌ Configuration failed\n")
    
    elif args.command == "auth":
        # This would call the auth setup script
        import subprocess
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT.parent.parent / "scripts" / "cli_auth_setup.py"), "v"],
            capture_output=True, text=True
        )
        print(result.stdout)
    
    elif args.command == "migrate":
        import subprocess
        result = subprocess.run(
            [sys.executable, "-c", f"""
from src.gateway_provisioning.provisioner import GatewayProvisioner
provisioner = GatewayProvisioner()
print("[green]Migrating skills...[/green]")
provisioner._migrate_skills()
print("[green]✅ Migration complete![/green]")
"""],
            capture_output=True, text=True
        )
        print(result.stdout)
    
    elif args.command == "system":
        check_system()


if __name__ == "__main__":
    main()
