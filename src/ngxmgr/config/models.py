"""
Configuration models for ngxmgr.
"""
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class ExecutionMode(str, Enum):
    """Execution mode for operations."""
    PARALLEL = "parallel"
    SERIAL = "serial"


class BaseConfig(BaseModel):
    """Base configuration with common fields."""
    hosts: Optional[List[str]] = None
    asg: Optional[str] = None
    region_name: Optional[str] = None
    username: str
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL
    timeout: int = Field(default=300, ge=0)
    log_file: Optional[Path] = None
    dry_run: bool = False

    @validator("hosts", pre=True)
    def parse_hosts_string(cls, v):
        """Parse comma-separated hosts string into list."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v

    @validator("timeout")
    def validate_timeout(cls, v):
        """Validate timeout value."""
        if v < 0:
            raise ValueError("Timeout must be non-negative")
        return v

    def validate_host_config(self):
        """Validate that either hosts or asg is provided."""
        if not self.hosts and not self.asg:
            raise ValueError("Either hosts or asg must be provided")
        if self.hosts and self.asg:
            raise ValueError("Cannot specify both hosts and asg")


class InstallConfig(BaseConfig):
    """Configuration for NGINX installation."""
    base_conda_path: str
    deployment_path: str
    nginx_dir_name: str = "nginx_run"
    nginx_conf_path: Path
    custom_conda_channel: str

    @validator("nginx_conf_path")
    def validate_nginx_conf_exists(cls, v):
        """Validate that nginx.conf file exists."""
        if not v.exists():
            raise ValueError(f"nginx.conf file not found: {v}")
        return v


class RemoveConfig(BaseConfig):
    """Configuration for NGINX removal."""
    base_conda_path: str
    deployment_path: str
    nginx_dir_name: str = "nginx_run"


class ServiceConfig(BaseConfig):
    """Configuration for NGINX service operations."""
    base_conda_path: str
    deployment_path: str
    nginx_dir_name: str = "nginx_run"


class MaintenanceConfig(BaseConfig):
    """Configuration for maintenance operations."""
    deployment_path: str
    nginx_dir_name: str = "nginx_run"


class LogUploadConfig(BaseConfig):
    """Configuration for log upload operations."""
    deployment_path: str
    nginx_dir_name: str = "nginx_run"
    s3_bucket: str
    archive_after_upload: Optional[str] = None
    delete_after_upload: bool = False

    @validator("s3_bucket")
    def validate_s3_bucket(cls, v):
        """Validate S3 bucket URI format."""
        if not v.startswith("s3://"):
            raise ValueError("S3 bucket must start with 's3://'")
        return v


class CopyConfig(BaseConfig):
    """Configuration for copy operations."""
    source_path: str
    destination_path: str
    recursive: bool = False

    @validator("source_path")
    def validate_source_exists(cls, v):
        """Validate that source path exists."""
        source = Path(v)
        if not source.exists():
            raise ValueError(f"Source path not found: {v}")
        return v 