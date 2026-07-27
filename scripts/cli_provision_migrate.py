#!/usr/bin/env python3
"""CLI Command: provision:migrate
Migrate existing skills to the project repository with sanitization.

This script copies skills from previous locations and removes any sensitive data.

Usage:
    python scripts/cli_provision_migrate.py --help
    python scripts/cli_provision_migrate.py run          # Run migration
"""

import sys
from pathlib import Path
import re

# Add project source to path
PROJECT_ROOT = Path(__file__).parent.parent / "src" / "gateway_provisioning"
sys.path.insert(0, str(PROJECT_ROOT))


def sanitize_content(content: str) -> str:
    """Remove sensitive data from skill files."""
    
    patterns_to_redact = [
        (r'ghp_[^\s]+', '[REDACTED_GITHUB_PAT]'),  # GitHub PAT
        (r'token_[^\s]+', '[REDACTED_TOKEN]'),     # Generic token
        (r'api[_-]?key\s*[:=]\s*[^\s,)]+', '[REDACTED_API_KEY]'),
        (r'secret[_-]?key\s*[:=]\s*[^\s,)]+', '[REDACTED_SECRET]'),
        (r'password\s*[:=]\s*[^\s,)]+', '[REDACTED_PASSWORD]'),
        (r'https://github\.com/[\w-]+/tokens/', 'https://github.com/user/tokens/'),
        # API keys
        (r'(?i)"key"\s*:\s*"[^"]+",', '"key": "[REDACTED_API_KEY]",'),
        (r'(?i)"secret"\s*:\s*"[^"]+",', '"secret": "[REDACTED_SECRET]",'),
        # JWT tokens and similar
        (r'[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', '[REDACTED_JWT]'),
    ]
    
    for pattern, replacement in patterns_to_redact:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    return content


def migrate_git_operations_skill() -> bool:
    """Migrate git-operations skill."""
    
    console = None  # Import here if needed
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("   Migrate Git Operations Skill")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    # Source locations to check
    source_locations = [
        "/home/manager/skills/git-operations/SKILL.md",
        Path.home() / "skills" / "git-operations" / "SKILL.md",
        PROJECT_ROOT.parent.parent / "skills" / "git-operations" / "SKILL.md",
    ]
    
    # Destination
    dest_dir = PROJECT_ROOT.parent.parent / "skills" / "git-operations"
    dest_path = dest_dir / "SKILL.md"
    
    if not dest_dir.exists():
        print(f"  Creating destination directory: {dest_dir}")
        dest_dir.mkdir(parents=True, exist_ok=True)
    
    migrated = False
    
    for src_path in source_locations:
        if Path(src_path).exists():
            print(f"  Found git-operations skill at: {src_path}")
            
            try:
                # Read and sanitize content
                with open(src_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                sanitized = sanitize_content(content)
                
                # Write to destination
                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(sanitized)
                
                print(f"  ✅ Migrated git-operations skill")
                migrated = True
                break
                
            except Exception as e:
                print(f"  ⚠️  Could not migrate: {str(e)}")
    
    if not migrated:
        print("  ℹ️  No git-operations skill found at common locations\n")
    
    return migrated


def migrate_advanced_browser_automation_skill() -> bool:
    """Migrate advanced-browser-automation skill."""
    
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("   Migrate Advanced Browser Automation Skill")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    source_locations = [
        "/home/manager/skills/advanced-browser-automation/SKILL.md",
        Path.home() / "skills" / "advanced-browser-automation" / "SKILL.md",
        PROJECT_ROOT.parent.parent / "skills" / "advanced-browser-automation" / "SKILL.md",
    ]
    
    dest_dir = PROJECT_ROOT.parent.parent / "skills" / "advanced-browser-automation"
    dest_path = dest_dir / "SKILL.md"
    
    if not dest_dir.exists():
        print(f"  Creating destination directory: {dest_dir}")
        dest_dir.mkdir(parents=True, exist_ok=True)
    
    migrated = False
    
    for src_path in source_locations:
        if Path(src_path).exists():
            print(f"  Found skill at: {src_path}")
            
            try:
                with open(src_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                sanitized = sanitize_content(content)
                
                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(sanitized)
                
                print(f"  ✅ Migrated advanced-browser-automation skill")
                migrated = True
                break
                
            except Exception as e:
                print(f"  ⚠️  Could not migrate: {str(e)}")
    
    if not migrated:
        print("  ℹ️  No advanced-browser-automation skill found at common locations\n")
    
    return migrated


def migrate_software_developer_skill() -> bool:
    """Migrate software-developer skill."""
    
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("   Migrate Software Developer Skill")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    source_locations = [
        Path.home() / ".npm-global" / "lib" / "node_modules" / "openclaw" / "skills" / "software-developer" / "SKILL.md",
        PROJECT_ROOT.parent.parent / "skills" / "software-developer" / "SKILL.md",
    ]
    
    dest_dir = PROJECT_ROOT.parent.parent / "skills" / "software-developer"
    dest_path = dest_dir / "SKILL.md"
    
    if not dest_dir.exists():
        print(f"  Creating destination directory: {dest_dir}")
        dest_dir.mkdir(parents=True, exist_ok=True)
    
    migrated = False
    
    for src_path in source_locations:
        if Path(src_path).exists():
            print(f"  Found skill at: {src_path}")
            
            try:
                with open(src_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                sanitized = sanitize_content(content)
                
                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(sanitized)
                
                print(f"  ✅ Migrated software-developer skill")
                migrated = True
                break
                
            except Exception as e:
                print(f"  ⚠️  Could not migrate: {str(e)}")
    
    if not migrated:
        print("  ℹ️  No software-developer skill found at common locations\n")
    
    return migrated


def check_skills_in_project() -> dict:
    """Check which skills exist in the project."""
    
    skills_dir = PROJECT_ROOT.parent.parent / "skills"
    migration_status = {
        "git-operations": False,
        "advanced-browser-automation": False,
        "software-developer": False,
    }
    
    if skills_dir.exists():
        for skill_name in migration_status.keys():
            skill_path = skills_dir / skill_name / "SKILL.md"
            migration_status[skill_name] = skill_path.exists()
    
    return migration_status


def main():
    """Main CLI entry point."""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migrate existing skills to project repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/cli_provision_migrate.py run       # Run migration
  python scripts/cli_provision_migrate.py check     # Check which skills exist

This script migrates skills from previous installations and removes
any sensitive data (API tokens, passwords, etc.) using pattern-based redaction.
"""
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        choices=["run", "check"],
        help="Command to run"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        # Show usage info
        print("\n╔═══════════════════════════════════════════════════════╗")
        print("   Skills Migration CLI")
        print("╚═══════════════════════════════════════════════════════╝\n")
        
        print("Commands:")
        print("  run       - Run migration (copy skills with sanitization)")
        print("  check     - Check which skills exist in project\n")
        
        print("Usage:")
        print("  python scripts/cli_provision_migrate.py <command>\n")
    
    elif args.command == "run":
        migrated_count = 0
        
        if migrate_git_operations_skill():
            migrated_count += 1
        
        if migrate_advanced_browser_automation_skill():
            migrated_count += 1
        
        if migrate_software_developer_skill():
            migrated_count += 1
        
        print("\n" + "=" * 60)
        
        if migrated_count > 0:
            print(f"[green]✅ Migration complete! Migrated {migrated_count} skill(s).[/green]\n")
        else:
            print("[yellow]ℹ️  No skills found at common locations.[/yellow]\n")
    
    elif args.command == "check":
        status = check_skills_in_project()
        
        print("\n╔═══════════════════════════════════════════════════════╗")
        print("   Skills Inventory Check")
        print("╚═══════════════════════════════════════════════════════╝\n")
        
        for skill_name, exists in status.items():
            if exists:
                print(f"[green]✅ {skill_name}[/green]")
                print(f"   Location: skills/{skill_name}/SKILL.md\n")
            else:
                print(f"[red]❌ {skill_name}[/red]\n")


if __name__ == "__main__":
    main()
