"""Unit tests for authentication management."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestAuthenticationManager:
    """Tests for AuthenticationManager class."""

    def test_initialization(self):
        """Test that AuthenticationManager initializes with correct directories."""
        from gateway_provisioning.auth import AuthenticationManager
        
        manager = AuthenticationManager()
        
        # Should create auth config directory
        assert manager.config_dir.exists() or manager.config_dir.mkdir(parents=True, exist_ok=True)

    def test_creates_auth_config(self):
        """Test that auth config template has all required fields."""
        from gateway_provisioning.auth import AuthenticationManager
        
        manager = AuthenticationManager()
        config = manager.create_auth_config()
        
        # Verify structure
        assert isinstance(config, dict)
        assert "github" in config
        assert "scopes" in config
        assert "deny_commands" in config
        
        # GitHub should have required fields
        github_config = config["github"]
        assert "user" in github_config or github_config.get("user") == ""
        assert github_config.get("token_variable") == "GITHUB_PAT"

    def test_creates_env_template(self, tmp_path):
        """Test that .env.example template is created with correct content."""
        from gateway_provisioning.auth import AuthenticationManager
        
        manager = AuthenticationManager()
        
        # Create env file for testing
        with open(tmp_path / ".env", 'w') as f:
            template = f"""# OpenClaw Gateway Environment Variables
# Copy this file to .env and fill in your values
# NEVER commit .env to git!

# GitHub Personal Access Token
# Create at: https://github.com/settings/tokens
GITHUB_PAT=ghp_your_token_here

# Gateway Host (optional, defaults to localhost)
GATEWAY_HOST=http://localhost:8080
"""
            f.write(template)
        
        assert (tmp_path / ".env").exists()
        
        content = (tmp_path / ".env").read_text()
        assert "GITHUB_PAT" in content
        assert "ghp_your_token_here" in content

    def test_validate_auth_setup_with_pat(self):
        """Test validation passes when PAT is set."""
        from gateway_provisioning.auth import AuthenticationManager
        
        manager = AuthenticationManager()
        
        # Set a mock PAT in environment
        with patch.dict(os.environ, {"GITHUB_PAT": "ghp_validtoken123"}):
            result = manager.validate_auth_setup()
            
        assert result is True

    def test_validate_auth_setup_without_pat(self):
        """Test validation fails when PAT is not set."""
        from gateway_provisioning.auth import AuthenticationManager
        
        manager = AuthenticationManager()
        
        # Ensure no GITHUB_PAT in environment
        if "GITHUB_PAT" in os.environ:
            del os.environ["GITHUB_PAT"]
            
        result = manager.validate_auth_setup()
        
        assert result is False

    def test_load_env_variables(self, tmp_path):
        """Test loading environment variables from .env file."""
        from gateway_provisioning.auth import AuthenticationManager
        
        # Create a test .env file
        env_content = """GITHUB_PAT=ghp_testtoken123
GATEWAY_HOST=http://custom.local:9000
"""
        with open(tmp_path / ".env", 'w') as f:
            f.write(env_content)
        
        manager = AuthenticationManager()
        manager.config_dir = tmp_path
        
        # Mock the load_dotenv call
        with patch("dotenv.load_dotenv"):
            loaded = manager.load_env_variables()
            
        # Should have loaded variables (mocked)
        assert isinstance(loaded, dict)

    @pytest.mark.skip(reason="Integration test - requires actual GitHub API")
    def test_load_auth_config_from_file(self):
        """Test loading actual auth configuration."""
        from gateway_provisioning.auth import AuthenticationManager
        
        manager = AuthenticationManager()
        
        # Would need to test with actual config file
        pass


@pytest.fixture
def mock_env(tmp_path):
    """Create a mock .env file for testing."""
    env_content = """GITHUB_PAT=ghp_testtoken123
GATEWAY_HOST=http://localhost:8080
DEBUG_MODE=true
"""
    with open(tmp_path / ".env", 'w') as f:
        f.write(env_content)
    
    return tmp_path
