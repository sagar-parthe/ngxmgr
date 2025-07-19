"""
Install command handler for ngxmgr.
"""
import sys
from pathlib import Path
from typing import Optional

from ngxmgr.config.loader import ConfigLoader
from ngxmgr.config.models import ExecutionMode
from ngxmgr.operations.nginx import NGINXOperations
from ngxmgr.utils.executor import RemoteExecutor
from ngxmgr.utils.logging import (
    setup_logging,
    handle_execution_result,
    handle_error,
    get_exit_code,
    ConfigurationError,
)


def install_command(
    hosts: Optional[str] = None,
    asg: Optional[str] = None,
    username: str = "",
    base_conda_path: str = "",
    deployment_path: str = "",
    nginx_dir_name: str = "nginx_run",
    nginx_conf_path: Optional[Path] = None,
    custom_conda_channel: str = "",
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL,
    config: Optional[Path] = None,
    timeout: int = 300,
    log_file: Optional[Path] = None,
    dry_run: bool = False,
) -> None:
    """
    Install NGINX on target servers.
    
    Args:
        hosts: Comma-separated list of hostnames/IPs
        asg: AWS Auto Scaling Group name
        username: SSH username
        base_conda_path: Path to base conda environment
        deployment_path: Root path for deployment
        nginx_dir_name: Directory name for NGINX
        nginx_conf_path: Path to local nginx.conf file
        custom_conda_channel: Custom conda channel for NGINX
        execution_mode: Execution mode (parallel/serial)
        config: Path to JSON config file
        timeout: Timeout per operation
        log_file: Log file path
        dry_run: Dry run mode
    """
    # Setup logging
    setup_logging(log_file, verbose=dry_run)
    
    try:
        # Load configuration
        config_data = ConfigLoader.load_install_config(
            config_file=config,
            hosts=hosts,
            asg=asg,
            username=username,
            base_conda_path=base_conda_path,
            deployment_path=deployment_path,
            nginx_dir_name=nginx_dir_name,
            nginx_conf_path=nginx_conf_path,
            custom_conda_channel=custom_conda_channel,
            execution_mode=execution_mode,
            timeout=timeout,
            log_file=log_file,
            dry_run=dry_run,
        )
        
        # Create executor and operations
        executor = RemoteExecutor(config_data)
        nginx_ops = NGINXOperations(executor)
        
        # Execute installation
        result = nginx_ops.install(config_data)
        
        # Handle results
        handle_execution_result(result, "NGINX installation")
        
        # Exit with appropriate code
        sys.exit(get_exit_code(result))
        
    except Exception as e:
        handle_error(e, "install") 