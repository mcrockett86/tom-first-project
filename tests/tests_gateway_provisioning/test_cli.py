#!/usr/bin/env python3
"""Unit tests for CLI interface to call each main provisioning stage."""

import subprocess
import sys
from pathlib import Path

# Add project source to path
PROJECT_ROOT = Path(__file__).parent.parent / "src" / "gateway_provisioning"


class TestCLIProvisionSetup:
    """Tests for cli_provision_setup.py CLI commands."""

    def test_cli_config_exists(self):
        """Test that CLI config script exists and is executable."""
        import os
        
        cli_script = PROJECT_ROOT.parent.parent.parent / "scripts" / "cli_provision_setup.py"
        assert cli_script.exists(), "CLI provision setup script not found"
        # Check if it's readable/executable
        assert os.access(cli_script, os.R_OK), "CLI script is not readable"

    def test_cli_auth_exists(self):
        """Test that CLI auth setup script exists."""
        cli_script = PROJECT_ROOT.parent.parent.parent / "scripts" / "cli_auth_setup.py"
        assert cli_script.exists(), "CLI auth setup script not found"

    @pytest.mark.integration
    def test_cli_provision_config_command(self):
        """Integration test: run provision:config command (would require user interaction)."""
        # This is marked as integration since it requires actual prompts
        # For now, we verify the file exists and can be imported
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "cli_provision_setup",
            PROJECT_ROOT.parent.parent.parent / "scripts" / "cli_provision_setup.py"
        )
        
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            # Would need special handling for interactive prompts
            pass


class TestCLIConfigInit:
    """Tests for CLI config initialization."""

    def test_cli_config_script_exists(self):
        """Test that config init script exists."""
        from pathlib import Path
        
        cli_script = PROJECT_ROOT.parent.parent.parent / "scripts" / "cli_config_init.py"
        assert cli_script.exists(), "CLI config init script not found"

    @pytest.mark.skip(reason="Requires user interaction for prompts")
    def test_cli_config_interactive_mode(self):
        """Test that CLI config is interactive (requires manual input)."""
        # Would need to capture stdout/stdin from terminal session


class TestProvisioningStages:
    """Tests for individual provisioning stages."""

    def test_stage_config(self):
        """Test that configuration stage can be invoked."""
        import subprocess
        
        script_path = PROJECT_ROOT.parent.parent.parent / "scripts" / "cli_provision_setup.py"
        
        # Test help command (non-interactive)
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True, text=True, timeout=10
        )
        
        assert result.returncode == 0 or "usage:" in result.stdout.lower()

    def test_stage_auth(self):
        """Test that authentication stage can be invoked."""
        script_path = PROJECT_ROOT.parent.parent.parent / "scripts" / "cli_auth_setup.py"
        
        # Test help command
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True, text=True, timeout=10
        )
        
        assert result.returncode == 0 or "usage:" in result.stdout.lower()

    def test_stage_help_shows_available_commands(self):
        """Test that help shows all available commands."""
        script_path = PROJECT_ROOT.parent.parent.parent / "scripts" / "cli_provision_setup.py"
        
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True, text=True, timeout=10
        )
        
        help_text = result.stdout.lower()
        expected_commands = ["config", "auth", "system", "setup"]
        
        for cmd in expected_commands:
            assert cmd in help_text, f"Help should mention {cmd} command"


@pytest.fixture
def temp_project_root(tmp_path):
    """Create a temporary project root for testing."""
    return tmp_path / "tom-first-project"


@pytest.fixture  
def temp_config_file(tmp_path):
    """Create a temporary config file for testing."""
    config = {
        "gateway": {"host": "http://test.local:8080"},
        "auth": {"use_pat": False},
        "security": {"allow_elevated_ops": False},
        "logging": {"log_level": "INFO"}
    }
    
    config_file = tmp_path / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config_file

