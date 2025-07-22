"""
Unit tests for copy command functionality.
"""
import pytest
from pathlib import Path
from pydantic import ValidationError

from ngxmgr.config.models import CopyConfig
from ngxmgr.config.loader import ConfigLoader


class TestCopyConfig:
    """Test copy configuration model."""
    
    def test_copy_config_valid(self, tmp_path):
        """Test valid copy configuration."""
        # Create a temporary source file
        source_file = tmp_path / "test.txt"
        source_file.write_text("test content")
        
        config = CopyConfig(
            hosts=["server1", "server2"],
            username="testuser",
            source_path=str(source_file),
            destination_path="/remote/path/test.txt",
            recursive=False,
        )
        
        assert config.hosts == ["server1", "server2"]
        assert config.username == "testuser"
        assert config.source_path == str(source_file)
        assert config.destination_path == "/remote/path/test.txt"
        assert config.recursive == False
    
    def test_copy_config_recursive_directory(self, tmp_path):
        """Test copy config for recursive directory copy."""
        # Create a temporary directory
        source_dir = tmp_path / "test_dir"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        
        config = CopyConfig(
            hosts=["server1"],
            username="testuser",
            source_path=str(source_dir),
            destination_path="/remote/path/dir",
            recursive=True,
        )
        
        assert config.recursive == True
        assert config.source_path == str(source_dir)
    
    def test_copy_config_nonexistent_source(self):
        """Test copy config validation fails with nonexistent source."""
        with pytest.raises(ValidationError):
            CopyConfig(
                hosts=["server1"],
                username="testuser",
                source_path="/nonexistent/file.txt",
                destination_path="/remote/path/file.txt",
            )
    
    def test_copy_config_missing_hosts_and_asg(self, tmp_path):
        """Test copy config validation fails without hosts or asg."""
        source_file = tmp_path / "test.txt"
        source_file.write_text("test content")
        
        config = CopyConfig(
            username="testuser",
            source_path=str(source_file),
            destination_path="/remote/path/test.txt",
        )
        
        with pytest.raises(ValueError, match="Either hosts or asg must be provided"):
            config.validate_host_config()


class TestCopyConfigLoader:
    """Test copy configuration loader."""
    
    def test_load_copy_config(self, tmp_path):
        """Test loading copy configuration from CLI args."""
        source_file = tmp_path / "test.txt"
        source_file.write_text("test content")
        
        config = ConfigLoader.load_copy_config(
            source_path=str(source_file),
            destination_path="/remote/test.txt",
            hosts=["server1", "server2"],
            username="testuser",
            region_name="us-west-2",
            recursive=True,
        )
        
        assert config.source_path == str(source_file)
        assert config.destination_path == "/remote/test.txt"
        assert config.hosts == ["server1", "server2"]
        assert config.username == "testuser"
        assert config.region_name == "us-west-2"
        assert config.recursive == True
    
    def test_copy_config_json_override(self, tmp_path):
        """Test that CLI arguments override JSON config for copy."""
        source_file = tmp_path / "test.txt"
        source_file.write_text("test content")
        
        json_config = {
            "hosts": ["json-server1"],
            "username": "json-user",
            "source_path": str(source_file),
            "destination_path": "/json/path",
            "recursive": False,
        }
        
        cli_args = {
            "username": "cli-user",  # Should override JSON
            "destination_path": "/cli/path",  # Should override JSON
            "recursive": True,  # Should override JSON
        }
        
        config = ConfigLoader.merge_config(
            CopyConfig, json_config, cli_args
        )
        
        assert config.hosts == ["json-server1"]  # From JSON
        assert config.username == "cli-user"  # CLI override
        assert config.destination_path == "/cli/path"  # CLI override
        assert config.recursive == True  # CLI override
        assert config.source_path == str(source_file)  # From JSON 