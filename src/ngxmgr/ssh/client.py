"""
SSH client for secure remote command execution.
"""
import getpass
import logging
from typing import NamedTuple, Optional

import paramiko
from paramiko import AuthenticationException, SSHException


logger = logging.getLogger(__name__)


class CommandResult(NamedTuple):
    """Result of a remote command execution."""
    exit_code: int
    stdout: str
    stderr: str
    success: bool


class SSHClient:
    """Secure SSH client for remote command execution."""

    def __init__(self, hostname: str, username: str, timeout: int = 300):
        """
        Initialize SSH client.
        
        Args:
            hostname: Target hostname or IP address
            username: SSH username
            timeout: Connection timeout in seconds
        """
        self.hostname = hostname
        self.username = username
        self.timeout = timeout
        self._client: Optional[paramiko.SSHClient] = None
        self._password: Optional[str] = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def connect(self, password: Optional[str] = None) -> None:
        """
        Connect to the remote server.
        
        Args:
            password: SSH password (prompted if not provided)
        """
        if self._client and self._client.get_transport() and self._client.get_transport().is_active():
            return

        if password:
            self._password = password
        elif not self._password:
            self._password = getpass.getpass(f"Password for {self.username}@{self.hostname}: ")

        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddHostKeyPolicy())

        try:
            logger.info(f"Connecting to {self.hostname} as {self.username}")
            self._client.connect(
                hostname=self.hostname,
                username=self.username,
                password=self._password,
                timeout=self.timeout,
                look_for_keys=False,
                allow_agent=False,
            )
            logger.info(f"Successfully connected to {self.hostname}")
        except AuthenticationException:
            logger.error(f"Authentication failed for {self.username}@{self.hostname}")
            raise
        except SSHException as e:
            logger.error(f"SSH connection failed to {self.hostname}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to {self.hostname}: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from the remote server."""
        if self._client:
            self._client.close()
            self._client = None
            logger.info(f"Disconnected from {self.hostname}")

    def execute_command(self, command: str, timeout: Optional[int] = None) -> CommandResult:
        """
        Execute a command on the remote server.
        
        Args:
            command: Command to execute
            timeout: Command timeout (uses client timeout if not specified)
            
        Returns:
            CommandResult with execution details
        """
        if not self._client:
            raise RuntimeError("Not connected to server")

        cmd_timeout = timeout or self.timeout
        
        try:
            logger.debug(f"Executing command on {self.hostname}: {command}")
            stdin, stdout, stderr = self._client.exec_command(
                command, timeout=cmd_timeout
            )
            
            # Close stdin to prevent hanging
            stdin.close()
            
            # Wait for command completion and get exit status
            exit_code = stdout.channel.recv_exit_status()
            
            # Read output
            stdout_data = stdout.read().decode('utf-8')
            stderr_data = stderr.read().decode('utf-8')
            
            success = exit_code == 0
            
            if success:
                logger.debug(f"Command succeeded on {self.hostname} (exit code: {exit_code})")
            else:
                logger.warning(f"Command failed on {self.hostname} (exit code: {exit_code})")
                
            return CommandResult(
                exit_code=exit_code,
                stdout=stdout_data,
                stderr=stderr_data,
                success=success
            )
            
        except paramiko.ssh_exception.SSHException as e:
            logger.error(f"SSH execution error on {self.hostname}: {e}")
            return CommandResult(
                exit_code=-1,
                stdout="",
                stderr=f"SSH execution error: {e}",
                success=False
            )
        except Exception as e:
            logger.error(f"Unexpected error executing command on {self.hostname}: {e}")
            return CommandResult(
                exit_code=-1,
                stdout="",
                stderr=f"Unexpected error: {e}",
                success=False
            )

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        Upload a file to the remote server.
        
        Args:
            local_path: Local file path
            remote_path: Remote file path
            
        Returns:
            True if successful, False otherwise
        """
        if not self._client:
            raise RuntimeError("Not connected to server")

        try:
            logger.info(f"Uploading {local_path} to {self.hostname}:{remote_path}")
            sftp = self._client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            logger.info(f"Successfully uploaded file to {self.hostname}")
            return True
        except Exception as e:
            logger.error(f"File upload failed to {self.hostname}: {e}")
            return False

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return (
            self._client is not None 
            and self._client.get_transport() is not None 
            and self._client.get_transport().is_active()
        ) 