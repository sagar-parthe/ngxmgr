"""
Service command handlers for ngxmgr.
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
)


def start_command(
    hosts: Optional[str] = None,
    asg: Optional[str] = None,
    region_name: Optional[str] = None,
    username: str = "",
    base_conda_path: str = "",
    deployment_path: str = "",
    nginx_dir_name: str = "nginx_run",
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL,
    config: Optional[Path] = None,
    timeout: int = 300,
    log_file: Optional[Path] = None,
    dry_run: bool = False,
) -> None:
    """Start NGINX on target servers."""
    setup_logging(log_file, verbose=dry_run)
    
    try:
        config_data = ConfigLoader.load_service_config(
            config_file=config,
            hosts=hosts,
            asg=asg,
            region_name=region_name,
            username=username,
            base_conda_path=base_conda_path,
            deployment_path=deployment_path,
            nginx_dir_name=nginx_dir_name,
            execution_mode=execution_mode,
            timeout=timeout,
            log_file=log_file,
            dry_run=dry_run,
        )
        
        executor = RemoteExecutor(config_data)
        nginx_ops = NGINXOperations(executor)
        
        result = nginx_ops.start(config_data)
        handle_execution_result(result, "NGINX start")
        sys.exit(get_exit_code(result))
        
    except Exception as e:
        handle_error(e, "start")


def stop_command(
    hosts: Optional[str] = None,
    asg: Optional[str] = None,
    region_name: Optional[str] = None,
    username: str = "",
    base_conda_path: str = "",
    deployment_path: str = "",
    nginx_dir_name: str = "nginx_run",
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL,
    config: Optional[Path] = None,
    timeout: int = 300,
    log_file: Optional[Path] = None,
    dry_run: bool = False,
) -> None:
    """Stop NGINX on target servers."""
    setup_logging(log_file, verbose=dry_run)
    
    try:
        config_data = ConfigLoader.load_service_config(
            config_file=config,
            hosts=hosts,
            asg=asg,
            region_name=region_name,
            username=username,
            base_conda_path=base_conda_path,
            deployment_path=deployment_path,
            nginx_dir_name=nginx_dir_name,
            execution_mode=execution_mode,
            timeout=timeout,
            log_file=log_file,
            dry_run=dry_run,
        )
        
        executor = RemoteExecutor(config_data)
        nginx_ops = NGINXOperations(executor)
        
        result = nginx_ops.stop(config_data)
        handle_execution_result(result, "NGINX stop")
        sys.exit(get_exit_code(result))
        
    except Exception as e:
        handle_error(e, "stop")


def restart_command(
    hosts: Optional[str] = None,
    asg: Optional[str] = None,
    region_name: Optional[str] = None,
    username: str = "",
    base_conda_path: str = "",
    deployment_path: str = "",
    nginx_dir_name: str = "nginx_run",
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL,
    config: Optional[Path] = None,
    timeout: int = 300,
    log_file: Optional[Path] = None,
    dry_run: bool = False,
) -> None:
    """Restart NGINX on target servers."""
    setup_logging(log_file, verbose=dry_run)
    
    try:
        config_data = ConfigLoader.load_service_config(
            config_file=config,
            hosts=hosts,
            asg=asg,
            region_name=region_name,
            username=username,
            base_conda_path=base_conda_path,
            deployment_path=deployment_path,
            nginx_dir_name=nginx_dir_name,
            execution_mode=execution_mode,
            timeout=timeout,
            log_file=log_file,
            dry_run=dry_run,
        )
        
        executor = RemoteExecutor(config_data)
        nginx_ops = NGINXOperations(executor)
        
        result = nginx_ops.restart(config_data)
        handle_execution_result(result, "NGINX restart")
        sys.exit(get_exit_code(result))
        
    except Exception as e:
        handle_error(e, "restart") 