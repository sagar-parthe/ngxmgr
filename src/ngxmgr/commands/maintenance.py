"""
Maintenance command handlers for ngxmgr.
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


def clear_cache_command(
    hosts: Optional[str] = None,
    asg: Optional[str] = None,
    region_name: Optional[str] = None,
    username: str = "",
    deployment_path: str = "",
    nginx_dir_name: str = "nginx_run",
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL,
    config: Optional[Path] = None,
    timeout: int = 300,
    log_file: Optional[Path] = None,
    dry_run: bool = False,
) -> None:
    """Clear NGINX cache on target servers."""
    setup_logging(log_file, verbose=dry_run)
    
    try:
        config_data = ConfigLoader.load_maintenance_config(
            config_file=config,
            hosts=hosts,
            asg=asg,
            region_name=region_name,
            username=username,
            deployment_path=deployment_path,
            nginx_dir_name=nginx_dir_name,
            execution_mode=execution_mode,
            timeout=timeout,
            log_file=log_file,
            dry_run=dry_run,
        )
        
        executor = RemoteExecutor(config_data)
        nginx_ops = NGINXOperations(executor)
        
        result = nginx_ops.clear_cache(config_data)
        handle_execution_result(result, "Cache clear")
        sys.exit(get_exit_code(result))
        
    except Exception as e:
        handle_error(e, "clear-cache")


def clear_logs_command(
    hosts: Optional[str] = None,
    asg: Optional[str] = None,
    region_name: Optional[str] = None,
    username: str = "",
    deployment_path: str = "",
    nginx_dir_name: str = "nginx_run",
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL,
    config: Optional[Path] = None,
    timeout: int = 300,
    log_file: Optional[Path] = None,
    dry_run: bool = False,
) -> None:
    """Clear NGINX logs on target servers."""
    setup_logging(log_file, verbose=dry_run)
    
    try:
        config_data = ConfigLoader.load_maintenance_config(
            config_file=config,
            hosts=hosts,
            asg=asg,
            region_name=region_name,
            username=username,
            deployment_path=deployment_path,
            nginx_dir_name=nginx_dir_name,
            execution_mode=execution_mode,
            timeout=timeout,
            log_file=log_file,
            dry_run=dry_run,
        )
        
        executor = RemoteExecutor(config_data)
        nginx_ops = NGINXOperations(executor)
        
        result = nginx_ops.clear_logs(config_data)
        handle_execution_result(result, "Log clear")
        sys.exit(get_exit_code(result))
        
    except Exception as e:
        handle_error(e, "clear-logs") 