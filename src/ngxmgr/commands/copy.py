"""
Copy command handler for ngxmgr.
"""
import sys
from pathlib import Path
from typing import Optional

from ngxmgr.config.loader import ConfigLoader
from ngxmgr.config.models import ExecutionMode
from ngxmgr.utils.executor import RemoteExecutor
from ngxmgr.utils.logging import (
    setup_logging,
    handle_execution_result,
    handle_error,
    get_exit_code,
)


def copy_command(
    source_path: str = "",
    destination_path: str = "",
    hosts: Optional[str] = None,
    asg: Optional[str] = None,
    region_name: Optional[str] = None,
    username: str = "",
    recursive: bool = False,
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL,
    config: Optional[Path] = None,
    timeout: int = 300,
    log_file: Optional[Path] = None,
    dry_run: bool = False,
) -> None:
    """
    Copy files or directories to target servers.
    
    Args:
        source_path: Local source file or directory path
        destination_path: Remote destination path
        hosts: Comma-separated list of hostnames/IPs
        asg: AWS Auto Scaling Group name
        region_name: AWS region name
        username: SSH username
        recursive: Copy directories recursively
        execution_mode: Execution mode (parallel/serial)
        config: Path to JSON config file
        timeout: Timeout per operation
        log_file: Log file path
        dry_run: Dry run mode
    """
    setup_logging(log_file, verbose=dry_run)
    
    try:
        config_data = ConfigLoader.load_copy_config(
            config_file=config,
            source_path=source_path,
            destination_path=destination_path,
            hosts=hosts,
            asg=asg,
            region_name=region_name,
            username=username,
            recursive=recursive,
            execution_mode=execution_mode,
            timeout=timeout,
            log_file=log_file,
            dry_run=dry_run,
        )
        
        executor = RemoteExecutor(config_data)
        
        result = executor.copy_files(
            config_data.source_path,
            config_data.destination_path,
            config_data.recursive
        )
        
        copy_type = "directory" if config_data.recursive else "file"
        handle_execution_result(result, f"{copy_type.title()} copy")
        sys.exit(get_exit_code(result))
        
    except Exception as e:
        handle_error(e, "copy") 