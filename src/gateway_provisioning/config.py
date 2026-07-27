"""Configuration management with secure approval prompts."""

import os
import json
from pathlib import Path
from rich.prompt import Prompt, Confirm, Password
from typing import Optional
from dotenv import load_dotenv


class ConfigManager:
    """Manages OpenClaw configuration with safe approval flows."""

    def __init__(self, config_path: Path = None):
        """Initialize config manager.
        
        Args:
            config_path: Optional path to config file (defaults to ~/.openclaw/config.json)
        """
        self.config_path = config_path or Path.home() / ".openclaw" / "config.json"
        self._ensure_config_dir()
        
    def _ensure_config_dir(self):
        """Ensure config directory exists."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_from_file(self, config_path: Optional[Path] = None) -> dict:
        """Load configuration from JSON file.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Dictionary of configuration settings
        """
        if config_path:
            self.config_path = config_path
        
        if not self.config_path.exists():
            return {}
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except (json.JSONDecodeError, IOError):
            print("⚠️ Warning: Could not load config file")
            return {}
    
    def save_to_file(self, config: dict) -> None:
        """Save configuration to JSON file.
        
        Args:
            config: Configuration dictionary to save
        """
        # Write to temporary file first for atomic write
        temp_path = Path(str(self.config_path) + '.tmp')
        with open(temp_path, 'w') as f:
            json.dump(config, f, indent=2)
        temp_path.rename(self.config_path)
    
    def create_initial_config(self) -> None:
        """Create initial config with user approval prompts."""
        print("\n🔐 OpenClaw Configuration Setup")
        print("=" * 50)
        
        config = {
            "gateway": {},
            "auth": {},
            "security": {},
            "logging": {}
        }
        
        # Gateway host configuration
        print("\n[1/4] Setting up gateway connection...")
        print("Note: Do NOT include API keys in this config.")
        
        config["gateway"]["host"] = Prompt.ask(
            "Gateway Host URL (leave empty for default)",
            default="http://localhost:8080",
            secret=False
        )
        
        config["gateway"]["api_endpoint"] = Prompt.ask(
            "API Endpoint path",
            default="/__openclaw__/api",
            secret=False
        )
        
        # Authentication settings (without tokens!)
        print("\n[2/4] Setting up authentication...")
        print("⚠️  WARNING: Never store API tokens in config files!")
        print("   Instead, use environment variables (see .env.example)")
        
        config["auth"]["use_pat"] = Confirm.ask(
            "Use Personal Access Token for auth?",
            default=False,
            show_default=True
        )
        
        # Security settings with approvals
        print("\n[3/4] Setting up security policies...")
        
        config["security"]["allow_elevated_ops"] = Confirm.ask(
            "Allow elevated file operations (sudo)?",
            default=False,
            show_default=True,
            prompt_suffix="⚠️  Requires system admin rights"
        )
        
        config["security"]["dangerous_commands"] = Prompt.ask(
            "Dangerous command patterns to block (comma-separated)",
            default="rm -rf;mount;dd /dev/*",
            secret=False
        )
        
        config["security"]["max_exec_timeout_s"] = Prompt.ask(
            "Maximum exec timeout in seconds",
            default="3600",  # 1 hour
            default_whisper=True,
            show_default=True
        )
        
        # Logging configuration
        print("\n[4/4] Setting up logging...")
        
        config["logging"]["log_level"] = Prompt.select(
            "Log level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO"
        )
        
        config["logging"]["log_dir"] = Prompt.ask(
            "Log directory path",
            default=str(Path.home() / ".openclaw" / "logs"),
            show_default=True,
            default_whisper=True
        )
        
        print("\n✅ Configuration created successfully!")
        print(f"\n📁 Config saved to: {self.config_path}")
        print("💡 View the config with: cat ~/.openclaw/config.json")
        
        # Save the configuration
        self.save_to_file(config)
        
    def update_sensitive_field(self, field_name: str, value: str) -> bool:
        """Update a sensitive field with approval confirmation.
        
        Args:
            field_name: Name of the config field to update
            value: New value for the field
            
        Returns:
            True if update succeeded, False otherwise
        """
        config = self.load_from_file()
        
        if not config:
            print("❌ No configuration file found. Run create_initial_config() first.")
            return False
        
        # Show the field being updated
        field_path = ".".join(field_name.split(".")[:-1]) if len(field_name.split(".")) > 1 else None
        
        print(f"\n🔒 Updating sensitive field: {field_name}")
        
        # For critical fields, require explicit confirmation
        dangerous_fields = ["github_pat", "api_key", "password", "secret"]
        is_dangerous = any(d in field_name.lower() for d in dangerous_fields)
        
        if is_dangerous or len(value) > 20:
            print("⚠️  This is a sensitive operation. Proceeding requires explicit approval.")
            
            if not Confirm.ask(
                f"Are you sure you want to update {field_name}? (type 'yes' to confirm)",
                default=False,
                show_default=True
            ):
                print("❌ Update cancelled")
                return False
        
        # Update the config
        current_section = ".".join(field_name.split(".")[:-1])
        current_field = field_name.split(".")[-1]
        
        if current_section in config:
            config[current_section][current_field] = value
            self.save_to_file(config)
            print(f"✅ Field updated successfully")
            return True
        
        return False
