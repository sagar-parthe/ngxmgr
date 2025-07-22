"""
Script command handler for ngxmgr.
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


def script_command(
    script_path: str = "",
    script_args: Optional[str] = None,
    hosts: Optional[str] = None,
    asg: Optional[str] = None,
    region_name: Optional[str] = None,
    username: str = "",
    interpreter: str = "/bin/bash",
    remote_temp_dir: str = "/tmp",
    cleanup_after_execution: bool = True,
    make_executable: bool = True,
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL,
    config: Optional[Path] = None,
    timeout: int = 300,
    log_file: Optional[Path] = None,
    dry_run: bool = False,
) -> None:
    """
    Execute a shell script on target servers.
    
    Args:
        script_path: Local script file path
        script_args: Arguments to pass to the script
        hosts: Comma-separated list of hostnames/IPs
        asg: AWS Auto Scaling Group name
        region_name: AWS region name
        username: SSH username
        interpreter: Interpreter to use for script execution
        remote_temp_dir: Remote temporary directory for script
        cleanup_after_execution: Whether to delete script after execution
        make_executable: Whether to make script executable
        execution_mode: Execution mode (parallel/serial)
        config: Path to JSON config file
        timeout: Timeout per operation
        log_file: Log file path
        dry_run: Dry run mode
    """
    setup_logging(log_file, verbose=dry_run)
    
    try:
        config_data = ConfigLoader.load_script_config(
            config_file=config,
            script_path=script_path,
            script_args=script_args,
            hosts=hosts,
            asg=asg,
            region_name=region_name,
            username=username,
            interpreter=interpreter,
            remote_temp_dir=remote_temp_dir,
            cleanup_after_execution=cleanup_after_execution,
            make_executable=make_executable,
            execution_mode=execution_mode,
            timeout=timeout,
            log_file=log_file,
            dry_run=dry_run,
        )
        
        executor = RemoteExecutor(config_data)
        
        result = executor.execute_script(
            config_data.script_path,
            config_data.script_args,
            config_data.interpreter,
            config_data.remote_temp_dir,
            config_data.cleanup_after_execution,
            config_data.make_executable
        )
        
        handle_execution_result(result, "Script execution")
        sys.exit(get_exit_code(result))
        
    except Exception as e:
        handle_error(e, "script") 