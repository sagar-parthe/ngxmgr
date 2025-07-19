"""
Remove command handler for ngxmgr.
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


def remove_command(
    hosts: Optional[str] = None,
    asg: Optional[str] = None,
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
    """Remove NGINX from target servers."""
    setup_logging(log_file, verbose=dry_run)
    
    try:
        config_data = ConfigLoader.load_remove_config(
            config_file=config,
            hosts=hosts,
            asg=asg,
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
        
        result = nginx_ops.remove(config_data)
        handle_execution_result(result, "NGINX removal")
        sys.exit(get_exit_code(result))
        
    except Exception as e:
        handle_error(e, "remove") 