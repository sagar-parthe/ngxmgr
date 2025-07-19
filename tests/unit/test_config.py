"""
Unit tests for configuration management.
"""
import pytest
from pathlib import Path
from pydantic import ValidationError

from ngxmgr.config.models import (
    ExecutionMode,
    InstallConfig,
    RemoveConfig,
    ServiceConfig,
)
from ngxmgr.config.loader import ConfigLoader


class TestConfigModels:
    """Test configuration models."""
    
    def test_install_config_valid(self, tmp_path):
        """Test valid install configuration."""
        # Create a temporary nginx.conf file
        nginx_conf = tmp_path / "nginx.conf"
        nginx_conf.write_text("# Test nginx config")
        
        config = InstallConfig(
            hosts=["server1", "server2"],
            username="testuser",
            base_conda_path="/opt/conda",
            deployment_path="/opt/nginx",
            nginx_conf_path=nginx_conf,
            custom_conda_channel="http://example.com/conda",
        )
        
        assert config.hosts == ["server1", "server2"]
        assert config.username == "testuser"
        assert config.nginx_dir_name == "nginx_run"  # default
        assert config.execution_mode == ExecutionMode.PARALLEL  # default
    
    def test_install_config_missing_hosts_and_asg(self, tmp_path):
        """Test install config validation fails without hosts or asg."""
        nginx_conf = tmp_path / "nginx.conf"
        nginx_conf.write_text("# Test nginx config")
        
        config = InstallConfig(
            username="testuser",
            base_conda_path="/opt/conda",
            deployment_path="/opt/nginx",
            nginx_conf_path=nginx_conf,
            custom_conda_channel="http://example.com/conda",
        )
        
        with pytest.raises(ValueError, match="Either hosts or asg must be provided"):
            config.validate_host_config()
    
    def test_install_config_nonexistent_nginx_conf(self):
        """Test install config validation fails with nonexistent nginx.conf."""
        with pytest.raises(ValidationError):
            InstallConfig(
                hosts=["server1"],
                username="testuser",
                base_conda_path="/opt/conda",
                deployment_path="/opt/nginx",
                nginx_conf_path=Path("/nonexistent/nginx.conf"),
                custom_conda_channel="http://example.com/conda",
            )
    
    def test_hosts_string_parsing(self):
        """Test parsing of comma-separated hosts string."""
        config = ServiceConfig(
            hosts="server1, server2,server3 ",
            username="testuser",
            base_conda_path="/opt/conda",
            deployment_path="/opt/nginx",
        )
        
        assert config.hosts == ["server1", "server2", "server3"]


class TestConfigLoader:
    """Test configuration loader."""
    
    def test_merge_config_cli_overrides_json(self, tmp_path):
        """Test that CLI arguments override JSON config."""
        # Create nginx.conf
        nginx_conf = tmp_path / "nginx.conf"
        nginx_conf.write_text("# Test nginx config")
        
        json_config = {
            "hosts": ["json-server1", "json-server2"],
            "username": "json-user",
            "deployment_path": "/json/path",
        }
        
        cli_args = {
            "username": "cli-user",  # Should override JSON
            "nginx_conf_path": nginx_conf,
            "base_conda_path": "/opt/conda",
            "custom_conda_channel": "http://example.com/conda",
        }
        
        config = ConfigLoader.merge_config(
            InstallConfig, json_config, cli_args
        )
        
        assert config.hosts == ["json-server1", "json-server2"]  # From JSON
        assert config.username == "cli-user"  # CLI override
        assert config.deployment_path == "/json/path"  # From JSON
    
    def test_merge_config_excludes_none_values(self, tmp_path):
        """Test that None values in CLI args are excluded."""
        nginx_conf = tmp_path / "nginx.conf"
        nginx_conf.write_text("# Test nginx config")
        
        cli_args = {
            "hosts": ["server1"],
            "username": "testuser",
            "base_conda_path": "/opt/conda",
            "deployment_path": "/opt/nginx",
            "nginx_conf_path": nginx_conf,
            "custom_conda_channel": "http://example.com/conda",
            "log_file": None,  # Should be excluded
            "asg": None,  # Should be excluded
        }
        
        config = ConfigLoader.merge_config(InstallConfig, None, cli_args)
        
        assert config.hosts == ["server1"]
        assert config.username == "testuser"
        # None values should not be in the final config
        assert not hasattr(config, 'log_file') or config.log_file is None 