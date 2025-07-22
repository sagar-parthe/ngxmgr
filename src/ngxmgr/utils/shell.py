"""
Shell utilities for cross-platform command execution.
"""
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


class ShellCommandBuilder:
    """Build shell commands that work across different shell environments."""

    @staticmethod
    def get_shell_info_command() -> str:
        """Get command to detect shell type and version."""
        return "ps -p $$ -o comm= 2>/dev/null || echo 'unknown'"

    @staticmethod
    def build_conda_command(base_conda_path: str, conda_args: str) -> str:
        """
        Build a conda command using absolute path to avoid activation issues.
        
        Args:
            base_conda_path: Path to the base conda installation
            conda_args: Arguments to pass to conda
            
        Returns:
            Complete conda command with absolute path
        """
        conda_binary = f"{base_conda_path.rstrip('/')}/bin/conda"
        return f"{conda_binary} {conda_args}"

    @staticmethod
    def build_nginx_command(base_conda_path: str, nginx_args: str) -> str:
        """
        Build an nginx command using absolute path from conda environment.
        
        Args:
            base_conda_path: Path to the base conda installation
            nginx_args: Arguments to pass to nginx
            
        Returns:
            Complete nginx command with absolute path
        """
        nginx_binary = f"{base_conda_path.rstrip('/')}/envs/nginx_env/bin/nginx"
        return f"{nginx_binary} {nginx_args}"

    @staticmethod
    def build_portable_variable_assignment(var_name: str, command: str) -> str:
        """
        Build a variable assignment that works across shells.
        
        Args:
            var_name: Variable name
            command: Command to execute for variable value
            
        Returns:
            Portable variable assignment
        """
        # Use backticks for command substitution (more portable than $())
        return f"{var_name}=`{command}`"

    @staticmethod
    def build_conditional_command(condition: str, true_cmd: str, false_cmd: str = "true") -> str:
        """
        Build a conditional command that works across shells.
        
        Args:
            condition: Condition to test
            true_cmd: Command to run if condition is true
            false_cmd: Command to run if condition is false (default: true)
            
        Returns:
            Conditional command
        """
        return f"if {condition}; then {true_cmd}; else {false_cmd}; fi"

    @staticmethod
    def build_safe_file_operation(operation: str, target: str) -> str:
        """
        Build file operations that handle missing files gracefully.
        
        Args:
            operation: File operation (rm, truncate, etc.)
            target: Target file or directory
            
        Returns:
            Safe file operation command
        """
        if operation == "rm":
            return f"rm -rf {target} 2>/dev/null || true"
        elif operation == "truncate":
            return f"truncate -s 0 {target} 2>/dev/null || rm -f {target}"
        else:
            return f"{operation} {target}"

    @staticmethod
    def build_environment_check() -> List[str]:
        """
        Build commands to check the remote environment.
        
        Returns:
            List of diagnostic commands
        """
        return [
            "echo 'Shell:' $(ps -p $$ -o comm= 2>/dev/null || echo 'unknown')",
            "echo 'User:' $(whoami)",
            "echo 'Home:' $HOME",
            "echo 'Path:' $PATH",
            "echo 'Working Directory:' $(pwd)",
        ]

    @staticmethod
    def validate_conda_installation(base_conda_path: str) -> str:
        """
        Build command to validate conda installation.
        
        Args:
            base_conda_path: Path to the base conda installation
            
        Returns:
            Validation command
        """
        conda_binary = f"{base_conda_path.rstrip('/')}/bin/conda"
        return f"test -x {conda_binary} && {conda_binary} --version" 