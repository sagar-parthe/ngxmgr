"""
Main CLI entry point for ngxmgr.
"""
import typer
from typing import Optional, List
from pathlib import Path

from ngxmgr.config.models import ExecutionMode
from ngxmgr.commands.install import install_command
from ngxmgr.commands.service import start_command, stop_command, restart_command
from ngxmgr.commands.maintenance import clear_cache_command, clear_logs_command
from ngxmgr.commands.logs import upload_logs_command
from ngxmgr.commands.remove import remove_command
from ngxmgr.commands.copy import copy_command

app = typer.Typer(
    name="ngxmgr",
    help="CLI tool for managing NGINX deployments across multiple Linux servers",
    no_args_is_help=True,
)


@app.command()
def install(
    hosts: Optional[str] = typer.Option(
        None, "--hosts", "-h", help="Comma-separated list of hostnames/IPs"
    ),
    asg: Optional[str] = typer.Option(
        None, "--asg", "-a", help="AWS Auto Scaling Group name"
    ),
    region_name: Optional[str] = typer.Option(
        None, "--region-name", "-r", help="AWS region name"
    ),
    username: str = typer.Option(..., "--username", "-u", help="SSH username"),
    base_conda_path: str = typer.Option(
        ..., "--base-conda-path", "-b", help="Path to base conda environment"
    ),
    deployment_path: str = typer.Option(
        ..., "--deployment-path", "-d", help="Root path for deployment"
    ),
    nginx_dir_name: str = typer.Option(
        "nginx_run", "--nginx-dir-name", "-n", help="Directory name for NGINX"
    ),
    nginx_conf_path: Path = typer.Option(
        ..., "--nginx-conf-path", "-c", help="Path to local nginx.conf file"
    ),
    custom_conda_channel: str = typer.Option(
        ..., "--custom-conda-channel", "-ch", help="Custom conda channel for NGINX"
    ),
    execution_mode: ExecutionMode = typer.Option(
        ExecutionMode.PARALLEL, "--execution-mode", "-e", help="Execution mode"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-f", help="Path to JSON config file"
    ),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout per operation"),
    log_file: Optional[Path] = typer.Option(
        None, "--log-file", "-l", help="Log file path"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode"),
) -> None:
    """Install NGINX on target servers."""
    install_command(
        hosts=hosts,
        asg=asg,
        region_name=region_name,
        username=username,
        base_conda_path=base_conda_path,
        deployment_path=deployment_path,
        nginx_dir_name=nginx_dir_name,
        nginx_conf_path=nginx_conf_path,
        custom_conda_channel=custom_conda_channel,
        execution_mode=execution_mode,
        config=config,
        timeout=timeout,
        log_file=log_file,
        dry_run=dry_run,
    )


@app.command()
def remove(
    hosts: Optional[str] = typer.Option(
        None, "--hosts", "-h", help="Comma-separated list of hostnames/IPs"
    ),
    asg: Optional[str] = typer.Option(
        None, "--asg", "-a", help="AWS Auto Scaling Group name"
    ),
    region_name: Optional[str] = typer.Option(
        None, "--region-name", "-r", help="AWS region name"
    ),
    username: str = typer.Option(..., "--username", "-u", help="SSH username"),
    base_conda_path: str = typer.Option(
        ..., "--base-conda-path", "-b", help="Path to base conda environment"
    ),
    deployment_path: str = typer.Option(
        ..., "--deployment-path", "-d", help="Root path for deployment"
    ),
    nginx_dir_name: str = typer.Option(
        "nginx_run", "--nginx-dir-name", "-n", help="Directory name for NGINX"
    ),
    execution_mode: ExecutionMode = typer.Option(
        ExecutionMode.PARALLEL, "--execution-mode", "-e", help="Execution mode"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-f", help="Path to JSON config file"
    ),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout per operation"),
    log_file: Optional[Path] = typer.Option(
        None, "--log-file", "-l", help="Log file path"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode"),
) -> None:
    """Remove NGINX from target servers."""
    remove_command(
        hosts=hosts,
        asg=asg,
        region_name=region_name,
        username=username,
        base_conda_path=base_conda_path,
        deployment_path=deployment_path,
        nginx_dir_name=nginx_dir_name,
        execution_mode=execution_mode,
        config=config,
        timeout=timeout,
        log_file=log_file,
        dry_run=dry_run,
    )


@app.command()
def start(
    hosts: Optional[str] = typer.Option(
        None, "--hosts", "-h", help="Comma-separated list of hostnames/IPs"
    ),
    asg: Optional[str] = typer.Option(
        None, "--asg", "-a", help="AWS Auto Scaling Group name"
    ),
    region_name: Optional[str] = typer.Option(
        None, "--region-name", "-r", help="AWS region name"
    ),
    username: str = typer.Option(..., "--username", "-u", help="SSH username"),
    base_conda_path: str = typer.Option(
        ..., "--base-conda-path", "-b", help="Path to base conda environment"
    ),
    deployment_path: str = typer.Option(
        ..., "--deployment-path", "-d", help="Root path for deployment"
    ),
    nginx_dir_name: str = typer.Option(
        "nginx_run", "--nginx-dir-name", "-n", help="Directory name for NGINX"
    ),
    execution_mode: ExecutionMode = typer.Option(
        ExecutionMode.PARALLEL, "--execution-mode", "-e", help="Execution mode"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-f", help="Path to JSON config file"
    ),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout per operation"),
    log_file: Optional[Path] = typer.Option(
        None, "--log-file", "-l", help="Log file path"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode"),
) -> None:
    """Start NGINX on target servers."""
    start_command(
        hosts=hosts,
        asg=asg,
        region_name=region_name,
        username=username,
        base_conda_path=base_conda_path,
        deployment_path=deployment_path,
        nginx_dir_name=nginx_dir_name,
        execution_mode=execution_mode,
        config=config,
        timeout=timeout,
        log_file=log_file,
        dry_run=dry_run,
    )


@app.command()
def stop(
    hosts: Optional[str] = typer.Option(
        None, "--hosts", "-h", help="Comma-separated list of hostnames/IPs"
    ),
    asg: Optional[str] = typer.Option(
        None, "--asg", "-a", help="AWS Auto Scaling Group name"
    ),
    region_name: Optional[str] = typer.Option(
        None, "--region-name", "-r", help="AWS region name"
    ),
    username: str = typer.Option(..., "--username", "-u", help="SSH username"),
    base_conda_path: str = typer.Option(
        ..., "--base-conda-path", "-b", help="Path to base conda environment"
    ),
    deployment_path: str = typer.Option(
        ..., "--deployment-path", "-d", help="Root path for deployment"
    ),
    nginx_dir_name: str = typer.Option(
        "nginx_run", "--nginx-dir-name", "-n", help="Directory name for NGINX"
    ),
    execution_mode: ExecutionMode = typer.Option(
        ExecutionMode.PARALLEL, "--execution-mode", "-e", help="Execution mode"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-f", help="Path to JSON config file"
    ),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout per operation"),
    log_file: Optional[Path] = typer.Option(
        None, "--log-file", "-l", help="Log file path"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode"),
) -> None:
    """Stop NGINX on target servers."""
    stop_command(
        hosts=hosts,
        asg=asg,
        region_name=region_name,
        username=username,
        base_conda_path=base_conda_path,
        deployment_path=deployment_path,
        nginx_dir_name=nginx_dir_name,
        execution_mode=execution_mode,
        config=config,
        timeout=timeout,
        log_file=log_file,
        dry_run=dry_run,
    )


@app.command()
def restart(
    hosts: Optional[str] = typer.Option(
        None, "--hosts", "-h", help="Comma-separated list of hostnames/IPs"
    ),
    asg: Optional[str] = typer.Option(
        None, "--asg", "-a", help="AWS Auto Scaling Group name"
    ),
    region_name: Optional[str] = typer.Option(
        None, "--region-name", "-r", help="AWS region name"
    ),
    username: str = typer.Option(..., "--username", "-u", help="SSH username"),
    base_conda_path: str = typer.Option(
        ..., "--base-conda-path", "-b", help="Path to base conda environment"
    ),
    deployment_path: str = typer.Option(
        ..., "--deployment-path", "-d", help="Root path for deployment"
    ),
    nginx_dir_name: str = typer.Option(
        "nginx_run", "--nginx-dir-name", "-n", help="Directory name for NGINX"
    ),
    execution_mode: ExecutionMode = typer.Option(
        ExecutionMode.PARALLEL, "--execution-mode", "-e", help="Execution mode"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-f", help="Path to JSON config file"
    ),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout per operation"),
    log_file: Optional[Path] = typer.Option(
        None, "--log-file", "-l", help="Log file path"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode"),
) -> None:
    """Restart NGINX on target servers."""
    restart_command(
        hosts=hosts,
        asg=asg,
        region_name=region_name,
        username=username,
        base_conda_path=base_conda_path,
        deployment_path=deployment_path,
        nginx_dir_name=nginx_dir_name,
        execution_mode=execution_mode,
        config=config,
        timeout=timeout,
        log_file=log_file,
        dry_run=dry_run,
    )


@app.command(name="clear-cache")
def clear_cache(
    hosts: Optional[str] = typer.Option(
        None, "--hosts", "-h", help="Comma-separated list of hostnames/IPs"
    ),
    asg: Optional[str] = typer.Option(
        None, "--asg", "-a", help="AWS Auto Scaling Group name"
    ),
    region_name: Optional[str] = typer.Option(
        None, "--region-name", "-r", help="AWS region name"
    ),
    username: str = typer.Option(..., "--username", "-u", help="SSH username"),
    deployment_path: str = typer.Option(
        ..., "--deployment-path", "-d", help="Root path for deployment"
    ),
    nginx_dir_name: str = typer.Option(
        "nginx_run", "--nginx-dir-name", "-n", help="Directory name for NGINX"
    ),
    execution_mode: ExecutionMode = typer.Option(
        ExecutionMode.PARALLEL, "--execution-mode", "-e", help="Execution mode"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-f", help="Path to JSON config file"
    ),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout per operation"),
    log_file: Optional[Path] = typer.Option(
        None, "--log-file", "-l", help="Log file path"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode"),
) -> None:
    """Clear NGINX cache on target servers."""
    clear_cache_command(
        hosts=hosts,
        asg=asg,
        region_name=region_name,
        username=username,
        deployment_path=deployment_path,
        nginx_dir_name=nginx_dir_name,
        execution_mode=execution_mode,
        config=config,
        timeout=timeout,
        log_file=log_file,
        dry_run=dry_run,
    )


@app.command(name="clear-logs")
def clear_logs(
    hosts: Optional[str] = typer.Option(
        None, "--hosts", "-h", help="Comma-separated list of hostnames/IPs"
    ),
    asg: Optional[str] = typer.Option(
        None, "--asg", "-a", help="AWS Auto Scaling Group name"
    ),
    region_name: Optional[str] = typer.Option(
        None, "--region-name", "-r", help="AWS region name"
    ),
    username: str = typer.Option(..., "--username", "-u", help="SSH username"),
    deployment_path: str = typer.Option(
        ..., "--deployment-path", "-d", help="Root path for deployment"
    ),
    nginx_dir_name: str = typer.Option(
        "nginx_run", "--nginx-dir-name", "-n", help="Directory name for NGINX"
    ),
    execution_mode: ExecutionMode = typer.Option(
        ExecutionMode.PARALLEL, "--execution-mode", "-e", help="Execution mode"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-f", help="Path to JSON config file"
    ),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout per operation"),
    log_file: Optional[Path] = typer.Option(
        None, "--log-file", "-l", help="Log file path"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode"),
) -> None:
    """Clear NGINX logs on target servers."""
    clear_logs_command(
        hosts=hosts,
        asg=asg,
        region_name=region_name,
        username=username,
        deployment_path=deployment_path,
        nginx_dir_name=nginx_dir_name,
        execution_mode=execution_mode,
        config=config,
        timeout=timeout,
        log_file=log_file,
        dry_run=dry_run,
    )


@app.command(name="upload-logs")
def upload_logs(
    hosts: Optional[str] = typer.Option(
        None, "--hosts", "-h", help="Comma-separated list of hostnames/IPs"
    ),
    asg: Optional[str] = typer.Option(
        None, "--asg", "-a", help="AWS Auto Scaling Group name"
    ),
    region_name: Optional[str] = typer.Option(
        None, "--region-name", "-r", help="AWS region name"
    ),
    username: str = typer.Option(..., "--username", "-u", help="SSH username"),
    deployment_path: str = typer.Option(
        ..., "--deployment-path", "-d", help="Root path for deployment"
    ),
    nginx_dir_name: str = typer.Option(
        "nginx_run", "--nginx-dir-name", "-n", help="Directory name for NGINX"
    ),
    s3_bucket: str = typer.Option(
        ..., "--s3-bucket", "-s", help="S3 bucket URI for log uploads"
    ),
    archive_after_upload: Optional[str] = typer.Option(
        None, "--archive-after-upload", help="Path to archive logs after upload"
    ),
    delete_after_upload: bool = typer.Option(
        False, "--delete-after-upload", help="Delete logs after upload"
    ),
    execution_mode: ExecutionMode = typer.Option(
        ExecutionMode.PARALLEL, "--execution-mode", "-e", help="Execution mode"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-f", help="Path to JSON config file"
    ),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout per operation"),
    log_file: Optional[Path] = typer.Option(
        None, "--log-file", "-l", help="Log file path"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode"),
) -> None:
    """Upload NGINX logs to S3."""
    upload_logs_command(
        hosts=hosts,
        asg=asg,
        region_name=region_name,
        username=username,
        deployment_path=deployment_path,
        nginx_dir_name=nginx_dir_name,
        s3_bucket=s3_bucket,
        archive_after_upload=archive_after_upload,
        delete_after_upload=delete_after_upload,
        execution_mode=execution_mode,
        config=config,
        timeout=timeout,
        log_file=log_file,
        dry_run=dry_run,
    )


@app.command()
def copy(
    source_path: str = typer.Argument(..., help="Local source file or directory path"),
    destination_path: str = typer.Argument(..., help="Remote destination path"),
    hosts: Optional[str] = typer.Option(
        None, "--hosts", "-h", help="Comma-separated list of hostnames/IPs"
    ),
    asg: Optional[str] = typer.Option(
        None, "--asg", "-a", help="AWS Auto Scaling Group name"
    ),
    region_name: Optional[str] = typer.Option(
        None, "--region-name", "-r", help="AWS region name"
    ),
    username: str = typer.Option(..., "--username", "-u", help="SSH username"),
    recursive: bool = typer.Option(
        False, "--recursive", "-R", help="Copy directories recursively"
    ),
    execution_mode: ExecutionMode = typer.Option(
        ExecutionMode.PARALLEL, "--execution-mode", "-e", help="Execution mode"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-f", help="Path to JSON config file"
    ),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout per operation"),
    log_file: Optional[Path] = typer.Option(
        None, "--log-file", "-l", help="Log file path"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode"),
) -> None:
    """Copy files or directories to target servers."""
    copy_command(
        source_path=source_path,
        destination_path=destination_path,
        hosts=hosts,
        asg=asg,
        region_name=region_name,
        username=username,
        recursive=recursive,
        execution_mode=execution_mode,
        config=config,
        timeout=timeout,
        log_file=log_file,
        dry_run=dry_run,
    )


if __name__ == "__main__":
    app() 