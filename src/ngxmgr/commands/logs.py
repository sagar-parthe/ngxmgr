"""
Logs command handler for ngxmgr.
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


def upload_logs_command(
    hosts: Optional[str] = None,
    asg: Optional[str] = None,
    username: str = "",
    deployment_path: str = "",
    nginx_dir_name: str = "nginx_run",
    s3_bucket: str = "",
    archive_after_upload: Optional[str] = None,
    delete_after_upload: bool = False,
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL,
    config: Optional[Path] = None,
    timeout: int = 300,
    log_file: Optional[Path] = None,
    dry_run: bool = False,
) -> None:
    """Upload NGINX logs to S3."""
    setup_logging(log_file, verbose=dry_run)
    
    try:
        config_data = ConfigLoader.load_log_upload_config(
            config_file=config,
            hosts=hosts,
            asg=asg,
            username=username,
            deployment_path=deployment_path,
            nginx_dir_name=nginx_dir_name,
            s3_bucket=s3_bucket,
            archive_after_upload=archive_after_upload,
            delete_after_upload=delete_after_upload,
            execution_mode=execution_mode,
            timeout=timeout,
            log_file=log_file,
            dry_run=dry_run,
        )
        
        executor = RemoteExecutor(config_data)
        nginx_ops = NGINXOperations(executor)
        
        result = nginx_ops.upload_logs(config_data)
        handle_execution_result(result, "Log upload")
        sys.exit(get_exit_code(result))
        
    except Exception as e:
        handle_error(e, "upload-logs") 