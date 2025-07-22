"""
Configuration loader for ngxmgr.
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

from ngxmgr.config.models import (
    BaseConfig,
    InstallConfig,
    RemoveConfig,
    ServiceConfig,
    MaintenanceConfig,
    LogUploadConfig,
    CopyConfig,
)

T = TypeVar("T", bound=BaseConfig)


class ConfigLoader:
    """Configuration loader with JSON and CLI override support."""

    @staticmethod
    def load_json_config(config_path: Path) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
            return config_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file {config_path}: {e}")

    @staticmethod
    def merge_config(
        config_class: Type[T],
        json_config: Optional[Dict[str, Any]] = None,
        cli_args: Optional[Dict[str, Any]] = None,
    ) -> T:
        """
        Merge JSON config with CLI arguments.
        CLI arguments override JSON config values.
        """
        # Start with empty config
        merged_config = {}
        
        # Add JSON config if provided
        if json_config:
            merged_config.update(json_config)
        
        # Override with CLI args (exclude None values)
        if cli_args:
            cli_filtered = {k: v for k, v in cli_args.items() if v is not None}
            merged_config.update(cli_filtered)
        
        try:
            config = config_class(**merged_config)
            config.validate_host_config()
            return config
        except ValidationError as e:
            raise ValueError(f"Configuration validation failed: {e}")

    @classmethod
    def load_install_config(
        cls,
        config_file: Optional[Path] = None,
        **cli_args: Any,
    ) -> InstallConfig:
        """Load configuration for install command."""
        json_config = cls.load_json_config(config_file) if config_file else None
        return cls.merge_config(InstallConfig, json_config, cli_args)

    @classmethod
    def load_remove_config(
        cls,
        config_file: Optional[Path] = None,
        **cli_args: Any,
    ) -> RemoveConfig:
        """Load configuration for remove command."""
        json_config = cls.load_json_config(config_file) if config_file else None
        return cls.merge_config(RemoveConfig, json_config, cli_args)

    @classmethod
    def load_service_config(
        cls,
        config_file: Optional[Path] = None,
        **cli_args: Any,
    ) -> ServiceConfig:
        """Load configuration for service commands."""
        json_config = cls.load_json_config(config_file) if config_file else None
        return cls.merge_config(ServiceConfig, json_config, cli_args)

    @classmethod
    def load_maintenance_config(
        cls,
        config_file: Optional[Path] = None,
        **cli_args: Any,
    ) -> MaintenanceConfig:
        """Load configuration for maintenance commands."""
        json_config = cls.load_json_config(config_file) if config_file else None
        return cls.merge_config(MaintenanceConfig, json_config, cli_args)

    @classmethod
    def load_log_upload_config(
        cls,
        config_file: Optional[Path] = None,
        **cli_args: Any,
    ) -> LogUploadConfig:
        """Load configuration for log upload command."""
        json_config = cls.load_json_config(config_file) if config_file else None
        return cls.merge_config(LogUploadConfig, json_config, cli_args)

    @classmethod
    def load_copy_config(
        cls,
        config_file: Optional[Path] = None,
        **cli_args: Any,
    ) -> CopyConfig:
        """Load configuration for copy command."""
        json_config = cls.load_json_config(config_file) if config_file else None
        return cls.merge_config(CopyConfig, json_config, cli_args) 