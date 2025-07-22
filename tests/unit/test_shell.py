"""
Unit tests for shell utilities.
"""
import pytest

from ngxmgr.utils.shell import ShellCommandBuilder


class TestShellCommandBuilder:
    """Test shell command builder utilities."""
    
    def test_build_conda_command(self):
        """Test conda command building with absolute paths."""
        builder = ShellCommandBuilder()
        
        result = builder.build_conda_command("/opt/conda", "env list")
        expected = "/opt/conda/bin/conda env list"
        
        assert result == expected
    
    def test_build_nginx_command(self):
        """Test nginx command building with conda environment path."""
        builder = ShellCommandBuilder()
        
        result = builder.build_nginx_command("/opt/conda", "-c /path/to/nginx.conf")
        expected = "/opt/conda/envs/nginx_env/bin/nginx -c /path/to/nginx.conf"
        
        assert result == expected
    
    def test_build_portable_variable_assignment(self):
        """Test portable variable assignment using backticks."""
        builder = ShellCommandBuilder()
        
        result = builder.build_portable_variable_assignment("TIMESTAMP", "date +%Y%m%d")
        expected = "TIMESTAMP=`date +%Y%m%d`"
        
        assert result == expected
    
    def test_build_conditional_command(self):
        """Test conditional command building."""
        builder = ShellCommandBuilder()
        
        result = builder.build_conditional_command(
            "[ -f /path/to/file ]",
            "echo 'file exists'",
            "echo 'file missing'"
        )
        expected = "if [ -f /path/to/file ]; then echo 'file exists'; else echo 'file missing'; fi"
        
        assert result == expected
    
    def test_build_conditional_command_default_false(self):
        """Test conditional command with default false action."""
        builder = ShellCommandBuilder()
        
        result = builder.build_conditional_command(
            "[ -f /path/to/file ]",
            "echo 'file exists'"
        )
        expected = "if [ -f /path/to/file ]; then echo 'file exists'; else true; fi"
        
        assert result == expected
    
    def test_build_safe_file_operation_rm(self):
        """Test safe file removal operation."""
        builder = ShellCommandBuilder()
        
        result = builder.build_safe_file_operation("rm", "/path/to/file")
        expected = "rm -rf /path/to/file 2>/dev/null || true"
        
        assert result == expected
    
    def test_build_safe_file_operation_truncate(self):
        """Test safe file truncate operation."""
        builder = ShellCommandBuilder()
        
        result = builder.build_safe_file_operation("truncate", "/path/to/file")
        expected = "truncate -s 0 /path/to/file 2>/dev/null || rm -f /path/to/file"
        
        assert result == expected
    
    def test_validate_conda_installation(self):
        """Test conda installation validation command."""
        builder = ShellCommandBuilder()
        
        result = builder.validate_conda_installation("/opt/conda")
        expected = "test -x /opt/conda/bin/conda && /opt/conda/bin/conda --version"
        
        assert result == expected
    
    def test_get_shell_info_command(self):
        """Test shell detection command."""
        builder = ShellCommandBuilder()
        
        result = builder.get_shell_info_command()
        expected = "ps -p $$ -o comm= 2>/dev/null || echo 'unknown'"
        
        assert result == expected
    
    def test_build_environment_check(self):
        """Test environment diagnostic commands."""
        builder = ShellCommandBuilder()
        
        result = builder.build_environment_check()
        
        assert isinstance(result, list)
        assert len(result) == 5
        assert "Shell:" in result[0]
        assert "User:" in result[1]
        assert "Home:" in result[2]
        assert "Path:" in result[3]
        assert "Working Directory:" in result[4]
    
    def test_conda_path_handling_with_trailing_slash(self):
        """Test that trailing slashes in conda paths are handled correctly."""
        builder = ShellCommandBuilder()
        
        # Test with trailing slash
        result1 = builder.build_conda_command("/opt/conda/", "env list")
        # Test without trailing slash
        result2 = builder.build_conda_command("/opt/conda", "env list")
        
        # Both should produce the same result
        expected = "/opt/conda/bin/conda env list"
        assert result1 == expected
        assert result2 == expected 