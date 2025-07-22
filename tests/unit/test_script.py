"""
Unit tests for script command functionality.
"""
import pytest
from pathlib import Path
from pydantic import ValidationError

from ngxmgr.config.models import ScriptConfig
from ngxmgr.config.loader import ConfigLoader


class TestScriptConfig:
    """Test script configuration model."""
    
    def test_script_config_valid(self, tmp_path):
        """Test valid script configuration."""
        # Create a temporary script file
        script_file = tmp_path / "test_script.sh"
        script_file.write_text("#!/bin/bash\necho 'Hello World'")
        
        config = ScriptConfig(
            hosts=["server1", "server2"],
            username="testuser",
            script_path=str(script_file),
            script_args="arg1 arg2",
            interpreter="/bin/bash",
            remote_temp_dir="/tmp",
            cleanup_after_execution=True,
            make_executable=True,
        )
        
        assert config.hosts == ["server1", "server2"]
        assert config.username == "testuser"
        assert config.script_path == str(script_file)
        assert config.script_args == "arg1 arg2"
        assert config.interpreter == "/bin/bash"
        assert config.remote_temp_dir == "/tmp"
        assert config.cleanup_after_execution == True
        assert config.make_executable == True
    
    def test_script_config_defaults(self, tmp_path):
        """Test script config with default values."""
        script_file = tmp_path / "test.py"
        script_file.write_text("print('Hello')")
        
        config = ScriptConfig(
            hosts=["server1"],
            username="testuser",
            script_path=str(script_file),
        )
        
        assert config.script_args is None
        assert config.interpreter == "/bin/bash"
        assert config.remote_temp_dir == "/tmp"
        assert config.cleanup_after_execution == True
        assert config.make_executable == True
    
    def test_script_config_nonexistent_script(self):
        """Test script config validation fails with nonexistent script."""
        with pytest.raises(ValidationError):
            ScriptConfig(
                hosts=["server1"],
                username="testuser",
                script_path="/nonexistent/script.sh",
            )
    
    def test_script_config_directory_as_script(self, tmp_path):
        """Test script config validation fails when script path is a directory."""
        script_dir = tmp_path / "scripts"
        script_dir.mkdir()
        
        with pytest.raises(ValidationError):
            ScriptConfig(
                hosts=["server1"],
                username="testuser",
                script_path=str(script_dir),
            )
    
    def test_script_config_invalid_interpreter(self, tmp_path):
        """Test script config validation fails with relative interpreter path."""
        script_file = tmp_path / "test.sh"
        script_file.write_text("echo test")
        
        with pytest.raises(ValidationError):
            ScriptConfig(
                hosts=["server1"],
                username="testuser",
                script_path=str(script_file),
                interpreter="bash",  # Should be absolute path
            )
    
    def test_script_config_missing_hosts_and_asg(self, tmp_path):
        """Test script config validation fails without hosts or asg."""
        script_file = tmp_path / "test.sh"
        script_file.write_text("echo test")
        
        config = ScriptConfig(
            username="testuser",
            script_path=str(script_file),
        )
        
        with pytest.raises(ValueError, match="Either hosts or asg must be provided"):
            config.validate_host_config()


class TestScriptConfigLoader:
    """Test script configuration loader."""
    
    def test_load_script_config(self, tmp_path):
        """Test loading script configuration from CLI args."""
        script_file = tmp_path / "deploy.sh"
        script_file.write_text("#!/bin/bash\necho 'Deploying...'")
        
        config = ConfigLoader.load_script_config(
            script_path=str(script_file),
            script_args="--env=prod --version=1.2.3",
            hosts=["server1", "server2"],
            username="deploy",
            region_name="us-west-2",
            interpreter="/bin/sh",
            remote_temp_dir="/var/tmp",
            cleanup_after_execution=False,
            make_executable=True,
        )
        
        assert config.script_path == str(script_file)
        assert config.script_args == "--env=prod --version=1.2.3"
        assert config.hosts == ["server1", "server2"]
        assert config.username == "deploy"
        assert config.region_name == "us-west-2"
        assert config.interpreter == "/bin/sh"
        assert config.remote_temp_dir == "/var/tmp"
        assert config.cleanup_after_execution == False
        assert config.make_executable == True
    
    def test_script_config_json_override(self, tmp_path):
        """Test that CLI arguments override JSON config for script."""
        script_file = tmp_path / "script.py"
        script_file.write_text("#!/usr/bin/env python3\nprint('Hello')")
        
        json_config = {
            "hosts": ["json-server1"],
            "username": "json-user",
            "script_path": str(script_file),
            "script_args": "json-args",
            "interpreter": "/usr/bin/python3",
            "remote_temp_dir": "/tmp",
            "cleanup_after_execution": True,
            "make_executable": False,
        }
        
        cli_args = {
            "username": "cli-user",  # Should override JSON
            "script_args": "cli-args",  # Should override JSON
            "interpreter": "/bin/python3",  # Should override JSON
            "cleanup_after_execution": False,  # Should override JSON
        }
        
        config = ConfigLoader.merge_config(
            ScriptConfig, json_config, cli_args
        )
        
        assert config.hosts == ["json-server1"]  # From JSON
        assert config.username == "cli-user"  # CLI override
        assert config.script_args == "cli-args"  # CLI override
        assert config.interpreter == "/bin/python3"  # CLI override
        assert config.cleanup_after_execution == False  # CLI override
        assert config.make_executable == False  # From JSON
        assert config.script_path == str(script_file)  # From JSON
    
    def test_script_config_different_interpreters(self, tmp_path):
        """Test script config with different interpreters."""
        interpreters = [
            "/bin/bash",
            "/bin/sh", 
            "/usr/bin/python3",
            "/usr/bin/node",
            "/usr/bin/ruby"
        ]
        
        script_file = tmp_path / "test_script"
        script_file.write_text("echo test")
        
        for interpreter in interpreters:
            config = ScriptConfig(
                hosts=["server1"],
                username="testuser",
                script_path=str(script_file),
                interpreter=interpreter,
            )
            assert config.interpreter == interpreter 