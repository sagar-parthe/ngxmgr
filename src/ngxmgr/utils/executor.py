"""
Remote command execution engine with parallel and serial modes.
"""
import getpass
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, NamedTuple, Optional
from pathlib import Path
import os

from ngxmgr.aws.asg import ASGClient
from ngxmgr.config.models import BaseConfig, ExecutionMode
from ngxmgr.ssh.client import SSHClient, CommandResult


logger = logging.getLogger(__name__)


class HostResult(NamedTuple):
    """Result of command execution on a single host."""
    hostname: str
    success: bool
    command_result: Optional[CommandResult] = None
    error: Optional[str] = None


class ExecutionSummary(NamedTuple):
    """Summary of execution across all hosts."""
    total_hosts: int
    successful_hosts: int
    failed_hosts: int
    results: List[HostResult]
    overall_success: bool


class RemoteExecutor:
    """Execute commands on multiple remote hosts with parallel/serial support."""

    def __init__(self, config: BaseConfig):
        """
        Initialize remote executor.
        
        Args:
            config: Configuration object with execution settings
        """
        self.config = config
        self._password: Optional[str] = None
        self._password_lock = threading.Lock()
        self._password_prompted = False

    def get_target_hosts(self) -> List[str]:
        """
        Get list of target hosts from configuration.
        
        Returns:
            List of hostnames/IPs to target
        """
        if self.config.hosts:
            return self.config.hosts
        elif self.config.asg:
            asg_client = ASGClient(region_name=self.config.region_name)
            return asg_client.get_running_hostnames(self.config.asg)
        else:
            raise ValueError("No hosts or ASG specified in configuration")

    def _ensure_password(self) -> str:
        """
        Ensure password is available, prompting only once if needed.
        Thread-safe implementation.
        
        Returns:
            The SSH password
        """
        with self._password_lock:
            if not self._password and not self._password_prompted:
                self._password = getpass.getpass(f"Password for {self.config.username}: ")
                self._password_prompted = True
            elif not self._password and self._password_prompted:
                # This shouldn't happen, but just in case
                raise RuntimeError("Password was prompted but not captured")
            
        return self._password

    def execute_on_host(self, hostname: str, command: str) -> HostResult:
        """
        Execute a command on a single host.
        
        Args:
            hostname: Target hostname
            command: Command to execute
            
        Returns:
            HostResult with execution details
        """
        try:
            if self.config.dry_run:
                logger.info(f"[DRY RUN] Would execute on {hostname}: {command}")
                return HostResult(
                    hostname=hostname,
                    success=True,
                    command_result=CommandResult(0, "DRY RUN", "", True)
                )

            # Get password (thread-safe, prompts only once)
            password = self._ensure_password()

            with SSHClient(hostname, self.config.username, self.config.timeout) as ssh:
                ssh.connect(password)
                result = ssh.execute_command(command, timeout=self.config.timeout)
                
                return HostResult(
                    hostname=hostname,
                    success=result.success,
                    command_result=result
                )

        except Exception as e:
            error_msg = f"Connection/execution error: {e}"
            logger.error(f"Failed to execute command on {hostname}: {error_msg}")
            return HostResult(
                hostname=hostname,
                success=False,
                error=error_msg
            )

    def upload_file_to_host(self, hostname: str, local_path: str, remote_path: str) -> HostResult:
        """
        Upload a file to a single host.
        
        Args:
            hostname: Target hostname
            local_path: Local file path
            remote_path: Remote file path
            
        Returns:
            HostResult with upload details
        """
        try:
            if self.config.dry_run:
                logger.info(f"[DRY RUN] Would upload {local_path} to {hostname}:{remote_path}")
                return HostResult(
                    hostname=hostname,
                    success=True,
                    command_result=CommandResult(0, "DRY RUN upload", "", True)
                )

            # Get password (thread-safe, prompts only once)
            password = self._ensure_password()

            with SSHClient(hostname, self.config.username, self.config.timeout) as ssh:
                ssh.connect(password)
                success = ssh.upload_file(local_path, remote_path)
                
                return HostResult(
                    hostname=hostname,
                    success=success,
                    command_result=CommandResult(
                        0 if success else 1,
                        "File upload successful" if success else "File upload failed",
                        "" if success else "Upload error",
                        success
                    )
                )

        except Exception as e:
            error_msg = f"File upload error: {e}"
            logger.error(f"Failed to upload file to {hostname}: {error_msg}")
            return HostResult(
                hostname=hostname,
                success=False,
                error=error_msg
            )

    def copy_to_host(self, hostname: str, local_path: str, remote_path: str, recursive: bool = False) -> HostResult:
        """
        Copy a file or directory to a single host.
        
        Args:
            hostname: Target hostname
            local_path: Local file or directory path
            remote_path: Remote destination path
            recursive: Whether to copy directories recursively
            
        Returns:
            HostResult with copy details
        """
        try:
            if self.config.dry_run:
                copy_type = "directory" if recursive else "file"
                logger.info(f"[DRY RUN] Would copy {copy_type} {local_path} to {hostname}:{remote_path}")
                return HostResult(
                    hostname=hostname,
                    success=True,
                    command_result=CommandResult(0, "DRY RUN copy", "", True)
                )

            # Get password (thread-safe, prompts only once)
            password = self._ensure_password()

            with SSHClient(hostname, self.config.username, self.config.timeout) as ssh:
                ssh.connect(password)
                
                # Use scp-like functionality
                if recursive:
                    # For directories, use tar and ssh for efficient transfer
                    import tempfile
                    import subprocess
                    
                    # Create tar archive locally
                    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp_file:
                        tar_path = tmp_file.name
                    
                    try:
                        # Create tar archive
                        subprocess.run([
                            'tar', '-czf', tar_path, '-C', str(Path(local_path).parent), 
                            str(Path(local_path).name)
                        ], check=True)
                        
                        # Upload tar file
                        remote_tar = f"/tmp/{Path(tar_path).name}"
                        upload_success = ssh.upload_file(tar_path, remote_tar)
                        
                        if upload_success:
                            # Extract tar file on remote
                            extract_cmd = f"mkdir -p {remote_path} && tar -xzf {remote_tar} -C {remote_path} && rm {remote_tar}"
                            result = ssh.execute_command(extract_cmd)
                            success = result.success
                        else:
                            success = False
                            
                    finally:
                        # Clean up local tar file
                        Path(tar_path).unlink(missing_ok=True)
                        
                else:
                    # For files, use direct upload
                    success = ssh.upload_file(local_path, remote_path)
                
                return HostResult(
                    hostname=hostname,
                    success=success,
                    command_result=CommandResult(
                        0 if success else 1,
                        "Copy successful" if success else "Copy failed",
                        "" if success else "Copy error",
                        success
                    )
                )

        except Exception as e:
            error_msg = f"Copy error: {e}"
            logger.error(f"Failed to copy to {hostname}: {error_msg}")
            return HostResult(
                hostname=hostname,
                success=False,
                error=error_msg
            )

    def execute_script_on_host(
        self, 
        hostname: str, 
        local_script_path: str, 
        script_args: Optional[str] = None,
        interpreter: str = "/bin/bash",
        remote_temp_dir: str = "/tmp",
        cleanup_after_execution: bool = True,
        make_executable: bool = True
    ) -> HostResult:
        """
        Execute a script on a single host.
        
        Args:
            hostname: Target hostname
            local_script_path: Local script file path
            script_args: Arguments to pass to the script
            interpreter: Interpreter to use for execution
            remote_temp_dir: Remote temporary directory
            cleanup_after_execution: Whether to delete script after execution
            make_executable: Whether to make script executable
            
        Returns:
            HostResult with execution details
        """
        try:
            if self.config.dry_run:
                args_info = f" with args: {script_args}" if script_args else ""
                logger.info(f"[DRY RUN] Would execute script {local_script_path} on {hostname}{args_info}")
                return HostResult(
                    hostname=hostname,
                    success=True,
                    command_result=CommandResult(0, "DRY RUN script execution", "", True)
                )

            # Get password (thread-safe, prompts only once)
            password = self._ensure_password()

            # Generate remote script path
            script_name = Path(local_script_path).name
            remote_script_path = f"{remote_temp_dir.rstrip('/')}/{script_name}"

            with SSHClient(hostname, self.config.username, self.config.timeout) as ssh:
                ssh.connect(password)
                
                # Upload script
                upload_success = ssh.upload_file(local_script_path, remote_script_path)
                if not upload_success:
                    return HostResult(
                        hostname=hostname,
                        success=False,
                        error="Failed to upload script to remote host"
                    )
                
                # Make script executable if requested
                if make_executable:
                    chmod_result = ssh.execute_command(f"chmod +x {remote_script_path}")
                    if not chmod_result.success:
                        logger.warning(f"Failed to make script executable on {hostname}")
                
                # Build execution command
                script_command_parts = [interpreter, remote_script_path]
                if script_args:
                    script_command_parts.append(script_args)
                
                script_command = " ".join(script_command_parts)
                
                # Execute script
                logger.debug(f"Executing script on {hostname}: {script_command}")
                result = ssh.execute_command(script_command, timeout=self.config.timeout)
                
                # Clean up script if requested
                if cleanup_after_execution:
                    cleanup_result = ssh.execute_command(f"rm -f {remote_script_path}")
                    if not cleanup_result.success:
                        logger.warning(f"Failed to clean up script on {hostname}")
                
                return HostResult(
                    hostname=hostname,
                    success=result.success,
                    command_result=result
                )

        except Exception as e:
            error_msg = f"Script execution error: {e}"
            logger.error(f"Failed to execute script on {hostname}: {error_msg}")
            return HostResult(
                hostname=hostname,
                success=False,
                error=error_msg
            )

    def execute_command(self, command: str) -> ExecutionSummary:
        """
        Execute a command on all target hosts.
        
        Args:
            command: Command to execute
            
        Returns:
            ExecutionSummary with results from all hosts
        """
        hosts = self.get_target_hosts()
        logger.info(f"Executing command on {len(hosts)} hosts in {self.config.execution_mode.value} mode")

        # Ensure password is prompted upfront, before any parallel execution
        if not self.config.dry_run:
            self._ensure_password()
            logger.debug("Password cached for SSH connections")

        if self.config.execution_mode == ExecutionMode.SERIAL:
            return self._execute_serial(hosts, command)
        else:
            return self._execute_parallel(hosts, command)

    def upload_file(self, local_path: str, remote_path: str) -> ExecutionSummary:
        """
        Upload a file to all target hosts.
        
        Args:
            local_path: Local file path
            remote_path: Remote file path
            
        Returns:
            ExecutionSummary with results from all hosts
        """
        hosts = self.get_target_hosts()
        logger.info(f"Uploading file to {len(hosts)} hosts in {self.config.execution_mode.value} mode")

        # Ensure password is prompted upfront, before any parallel execution
        if not self.config.dry_run:
            self._ensure_password()
            logger.debug("Password cached for file uploads")

        if self.config.execution_mode == ExecutionMode.SERIAL:
            return self._upload_serial(hosts, local_path, remote_path)
        else:
            return self._upload_parallel(hosts, local_path, remote_path)

    def copy_files(self, local_path: str, remote_path: str, recursive: bool = False) -> ExecutionSummary:
        """
        Copy files or directories to all target hosts.
        
        Args:
            local_path: Local file or directory path
            remote_path: Remote destination path
            recursive: Whether to copy directories recursively
            
        Returns:
            ExecutionSummary with results from all hosts
        """
        hosts = self.get_target_hosts()
        copy_type = "directory" if recursive else "file"
        logger.info(f"Copying {copy_type} to {len(hosts)} hosts in {self.config.execution_mode.value} mode")

        # Ensure password is prompted upfront, before any parallel execution
        if not self.config.dry_run:
            self._ensure_password()
            logger.debug("Password cached for file copies")

        if self.config.execution_mode == ExecutionMode.SERIAL:
            return self._copy_serial(hosts, local_path, remote_path, recursive)
        else:
            return self._copy_parallel(hosts, local_path, remote_path, recursive)

    def execute_script(
        self,
        local_script_path: str,
        script_args: Optional[str] = None,
        interpreter: str = "/bin/bash",
        remote_temp_dir: str = "/tmp",
        cleanup_after_execution: bool = True,
        make_executable: bool = True
    ) -> ExecutionSummary:
        """
        Execute a script on all target hosts.
        
        Args:
            local_script_path: Local script file path
            script_args: Arguments to pass to the script
            interpreter: Interpreter to use for execution
            remote_temp_dir: Remote temporary directory
            cleanup_after_execution: Whether to delete script after execution
            make_executable: Whether to make script executable
            
        Returns:
            ExecutionSummary with results from all hosts
        """
        hosts = self.get_target_hosts()
        logger.info(f"Executing script on {len(hosts)} hosts in {self.config.execution_mode.value} mode")

        # Ensure password is prompted upfront, before any parallel execution
        if not self.config.dry_run:
            self._ensure_password()
            logger.debug("Password cached for script execution")

        if self.config.execution_mode == ExecutionMode.SERIAL:
            return self._execute_script_serial(
                hosts, local_script_path, script_args, interpreter, 
                remote_temp_dir, cleanup_after_execution, make_executable
            )
        else:
            return self._execute_script_parallel(
                hosts, local_script_path, script_args, interpreter,
                remote_temp_dir, cleanup_after_execution, make_executable
            )

    def _execute_serial(self, hosts: List[str], command: str) -> ExecutionSummary:
        """Execute command serially across hosts."""
        results = []
        
        for hostname in hosts:
            logger.info(f"Executing on {hostname}")
            result = self.execute_on_host(hostname, command)
            results.append(result)
            
            if not result.success:
                logger.warning(f"Command failed on {hostname}")

        return self._create_summary(results)

    def _execute_parallel(self, hosts: List[str], command: str) -> ExecutionSummary:
        """Execute command in parallel across hosts."""
        results = []
        
        with ThreadPoolExecutor(max_workers=min(len(hosts), 10)) as executor:
            # Submit all tasks
            future_to_host = {
                executor.submit(self.execute_on_host, hostname, command): hostname
                for hostname in hosts
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_host):
                hostname = future_to_host[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.success:
                        logger.info(f"Command succeeded on {hostname}")
                    else:
                        logger.warning(f"Command failed on {hostname}")
                        
                except Exception as e:
                    logger.error(f"Unexpected error for {hostname}: {e}")
                    results.append(HostResult(
                        hostname=hostname,
                        success=False,
                        error=f"Executor error: {e}"
                    ))

        return self._create_summary(results)

    def _upload_serial(self, hosts: List[str], local_path: str, remote_path: str) -> ExecutionSummary:
        """Upload file serially to hosts."""
        results = []
        
        for hostname in hosts:
            logger.info(f"Uploading to {hostname}")
            result = self.upload_file_to_host(hostname, local_path, remote_path)
            results.append(result)

        return self._create_summary(results)

    def _upload_parallel(self, hosts: List[str], local_path: str, remote_path: str) -> ExecutionSummary:
        """Upload file in parallel to hosts."""
        results = []
        
        with ThreadPoolExecutor(max_workers=min(len(hosts), 10)) as executor:
            future_to_host = {
                executor.submit(self.upload_file_to_host, hostname, local_path, remote_path): hostname
                for hostname in hosts
            }
            
            for future in as_completed(future_to_host):
                hostname = future_to_host[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Upload error for {hostname}: {e}")
                    results.append(HostResult(
                        hostname=hostname,
                        success=False,
                        error=f"Upload executor error: {e}"
                    ))

        return self._create_summary(results)

    def _copy_serial(self, hosts: List[str], local_path: str, remote_path: str, recursive: bool) -> ExecutionSummary:
        """Copy files serially to hosts."""
        results = []
        
        for hostname in hosts:
            logger.info(f"Copying to {hostname}")
            result = self.copy_to_host(hostname, local_path, remote_path, recursive)
            results.append(result)

        return self._create_summary(results)

    def _copy_parallel(self, hosts: List[str], local_path: str, remote_path: str, recursive: bool) -> ExecutionSummary:
        """Copy files in parallel to hosts."""
        results = []
        
        with ThreadPoolExecutor(max_workers=min(len(hosts), 10)) as executor:
            future_to_host = {
                executor.submit(self.copy_to_host, hostname, local_path, remote_path, recursive): hostname
                for hostname in hosts
            }
            
            for future in as_completed(future_to_host):
                hostname = future_to_host[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Copy error for {hostname}: {e}")
                    results.append(HostResult(
                        hostname=hostname,
                        success=False,
                        error=f"Copy executor error: {e}"
                    ))

        return self._create_summary(results)

    def _execute_script_serial(
        self, 
        hosts: List[str], 
        local_script_path: str, 
        script_args: Optional[str],
        interpreter: str, 
        remote_temp_dir: str, 
        cleanup_after_execution: bool, 
        make_executable: bool
    ) -> ExecutionSummary:
        """Execute script serially on hosts."""
        results = []
        
        for hostname in hosts:
            logger.info(f"Executing script on {hostname}")
            result = self.execute_script_on_host(
                hostname, local_script_path, script_args, interpreter,
                remote_temp_dir, cleanup_after_execution, make_executable
            )
            results.append(result)

        return self._create_summary(results)

    def _execute_script_parallel(
        self, 
        hosts: List[str], 
        local_script_path: str, 
        script_args: Optional[str],
        interpreter: str, 
        remote_temp_dir: str, 
        cleanup_after_execution: bool, 
        make_executable: bool
    ) -> ExecutionSummary:
        """Execute script in parallel on hosts."""
        results = []
        
        with ThreadPoolExecutor(max_workers=min(len(hosts), 10)) as executor:
            future_to_host = {
                executor.submit(
                    self.execute_script_on_host, hostname, local_script_path, 
                    script_args, interpreter, remote_temp_dir, 
                    cleanup_after_execution, make_executable
                ): hostname
                for hostname in hosts
            }
            
            for future in as_completed(future_to_host):
                hostname = future_to_host[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Script execution error for {hostname}: {e}")
                    results.append(HostResult(
                        hostname=hostname,
                        success=False,
                        error=f"Script executor error: {e}"
                    ))

        return self._create_summary(results)

    def _create_summary(self, results: List[HostResult]) -> ExecutionSummary:
        """Create execution summary from results."""
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        overall_success = failed == 0

        return ExecutionSummary(
            total_hosts=len(results),
            successful_hosts=successful,
            failed_hosts=failed,
            results=results,
            overall_success=overall_success
        ) 