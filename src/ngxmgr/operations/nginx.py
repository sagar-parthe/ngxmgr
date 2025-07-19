"""
NGINX operations manager for installation, service management, and maintenance.
"""
import logging
from pathlib import Path
from typing import List

from ngxmgr.config.models import (
    InstallConfig,
    RemoveConfig,
    ServiceConfig,
    MaintenanceConfig,
    LogUploadConfig,
)
from ngxmgr.utils.executor import RemoteExecutor, ExecutionSummary


logger = logging.getLogger(__name__)


class NGINXOperations:
    """NGINX operations manager."""

    def __init__(self, executor: RemoteExecutor):
        """
        Initialize NGINX operations.
        
        Args:
            executor: RemoteExecutor instance for command execution
        """
        self.executor = executor

    def install(self, config: InstallConfig) -> ExecutionSummary:
        """
        Install NGINX on target servers.
        
        Args:
            config: Installation configuration
            
        Returns:
            ExecutionSummary with installation results
        """
        logger.info("Starting NGINX installation")

        # Step 1: Create directory structure
        nginx_path = f"{config.deployment_path.rstrip('/')}/{config.nginx_dir_name}"
        dirs_to_create = [
            f"{nginx_path}/conf",
            f"{nginx_path}/cache",
            f"{nginx_path}/logs",
            f"{nginx_path}/var/tmp/nginx/client",
        ]

        create_dirs_cmd = f"mkdir -p {' '.join(dirs_to_create)}"
        logger.info("Creating directory structure")
        
        dir_result = self.executor.execute_command(create_dirs_cmd)
        if not dir_result.overall_success:
            logger.error("Failed to create directory structure on some hosts")
            return dir_result

        # Step 2: Activate base conda environment and create nginx environment
        activate_cmd = f"source {config.base_conda_path.rstrip('/')}/bin/activate"
        
        # Check if nginx_env already exists and remove it
        check_env_cmd = f"{activate_cmd} && conda env list | grep -q '^nginx_env ' && conda remove -n nginx_env --all -y || true"
        
        # Create new nginx environment
        create_env_cmd = (
            f"{activate_cmd} && "
            f"conda create --name nginx_env -y -k nginx -c {config.custom_conda_channel}"
        )

        logger.info("Setting up conda environment")
        env_setup_cmd = f"{check_env_cmd} && {create_env_cmd}"
        
        env_result = self.executor.execute_command(env_setup_cmd)
        if not env_result.overall_success:
            logger.error("Failed to set up conda environment on some hosts")
            return env_result

        # Step 3: Upload nginx.conf file
        remote_conf_path = f"{nginx_path}/conf/nginx.conf"
        logger.info("Uploading nginx.conf file")
        
        upload_result = self.executor.upload_file(
            str(config.nginx_conf_path), 
            remote_conf_path
        )
        if not upload_result.overall_success:
            logger.error("Failed to upload nginx.conf to some hosts")
            return upload_result

        logger.info("NGINX installation completed successfully")
        return upload_result

    def remove(self, config: RemoveConfig) -> ExecutionSummary:
        """
        Remove NGINX from target servers.
        
        Args:
            config: Removal configuration
            
        Returns:
            ExecutionSummary with removal results
        """
        logger.info("Starting NGINX removal")

        # Step 1: Stop NGINX if running
        nginx_path = f"{config.deployment_path.rstrip('/')}/{config.nginx_dir_name}"
        stop_cmd = f"pkill -f nginx || true"
        
        logger.info("Stopping NGINX processes")
        self.executor.execute_command(stop_cmd)

        # Step 2: Remove deployment directory
        remove_dir_cmd = f"rm -rf {nginx_path}"
        
        logger.info("Removing NGINX deployment directory")
        dir_result = self.executor.execute_command(remove_dir_cmd)

        # Step 3: Remove conda environment
        activate_cmd = f"source {config.base_conda_path.rstrip('/')}/bin/activate"
        remove_env_cmd = f"{activate_cmd} && conda remove -n nginx_env --all -y"
        
        logger.info("Removing conda environment")
        env_result = self.executor.execute_command(remove_env_cmd)

        # Return the result of the last critical operation
        if not env_result.overall_success:
            logger.warning("Failed to remove conda environment on some hosts")
            return env_result
        
        logger.info("NGINX removal completed successfully")
        return dir_result

    def start(self, config: ServiceConfig) -> ExecutionSummary:
        """
        Start NGINX on target servers.
        
        Args:
            config: Service configuration
            
        Returns:
            ExecutionSummary with start results
        """
        logger.info("Starting NGINX service")

        nginx_path = f"{config.deployment_path.rstrip('/')}/{config.nginx_dir_name}"
        activate_conda = f"source {config.base_conda_path.rstrip('/')}/bin/activate"
        activate_nginx = f"conda activate nginx_env"
        
        start_cmd = (
            f"{activate_conda} && {activate_nginx} && "
            f"nginx -c {nginx_path}/conf/nginx.conf -p {nginx_path}/"
        )

        result = self.executor.execute_command(start_cmd)
        
        if result.overall_success:
            logger.info("NGINX started successfully on all hosts")
        else:
            logger.warning("NGINX failed to start on some hosts")
            
        return result

    def stop(self, config: ServiceConfig) -> ExecutionSummary:
        """
        Stop NGINX on target servers.
        
        Args:
            config: Service configuration
            
        Returns:
            ExecutionSummary with stop results
        """
        logger.info("Stopping NGINX service")

        nginx_path = f"{config.deployment_path.rstrip('/')}/{config.nginx_dir_name}"
        
        # Try graceful stop first, then force kill
        stop_cmd = (
            f"if [ -f {nginx_path}/logs/nginx.pid ]; then "
            f"nginx -s quit -c {nginx_path}/conf/nginx.conf -p {nginx_path}/; "
            f"else pkill -f nginx; fi"
        )

        result = self.executor.execute_command(stop_cmd)
        
        if result.overall_success:
            logger.info("NGINX stopped successfully on all hosts")
        else:
            logger.warning("NGINX failed to stop cleanly on some hosts")
            
        return result

    def restart(self, config: ServiceConfig) -> ExecutionSummary:
        """
        Restart NGINX on target servers.
        
        Args:
            config: Service configuration
            
        Returns:
            ExecutionSummary with restart results
        """
        logger.info("Restarting NGINX service")

        # Stop first
        stop_result = self.stop(config)
        
        # Wait a moment then start
        if stop_result.overall_success:
            start_result = self.start(config)
            return start_result
        else:
            logger.error("Failed to stop NGINX on some hosts, skipping start")
            return stop_result

    def clear_cache(self, config: MaintenanceConfig) -> ExecutionSummary:
        """
        Clear NGINX cache on target servers.
        
        Args:
            config: Maintenance configuration
            
        Returns:
            ExecutionSummary with cache clear results
        """
        logger.info("Clearing NGINX cache")

        nginx_path = f"{config.deployment_path.rstrip('/')}/{config.nginx_dir_name}"
        clear_cmd = f"rm -rf {nginx_path}/cache/*"

        result = self.executor.execute_command(clear_cmd)
        
        if result.overall_success:
            logger.info("Cache cleared successfully on all hosts")
        else:
            logger.warning("Failed to clear cache on some hosts")
            
        return result

    def clear_logs(self, config: MaintenanceConfig) -> ExecutionSummary:
        """
        Clear NGINX logs on target servers.
        
        Args:
            config: Maintenance configuration
            
        Returns:
            ExecutionSummary with log clear results
        """
        logger.info("Clearing NGINX logs")

        nginx_path = f"{config.deployment_path.rstrip('/')}/{config.nginx_dir_name}"
        clear_cmd = f"truncate -s 0 {nginx_path}/logs/*.log 2>/dev/null || rm -f {nginx_path}/logs/*.log"

        result = self.executor.execute_command(clear_cmd)
        
        if result.overall_success:
            logger.info("Logs cleared successfully on all hosts")
        else:
            logger.warning("Failed to clear logs on some hosts")
            
        return result

    def upload_logs(self, config: LogUploadConfig) -> ExecutionSummary:
        """
        Upload NGINX logs to S3.
        
        Args:
            config: Log upload configuration
            
        Returns:
            ExecutionSummary with upload results
        """
        logger.info("Uploading NGINX logs to S3")

        nginx_path = f"{config.deployment_path.rstrip('/')}/{config.nginx_dir_name}"
        
        # Create timestamp for log archive
        timestamp_cmd = "date +%Y%m%d_%H%M%S"
        hostname_cmd = "hostname -s"
        
        # Build the upload command
        upload_commands = [
            f"cd {nginx_path}/logs",
            f"TIMESTAMP=$({timestamp_cmd})",
            f"HOSTNAME=$({hostname_cmd})",
            f"ARCHIVE_NAME=\"nginx_logs_${{HOSTNAME}}_${{TIMESTAMP}}.tar.gz\"",
            f"tar -czf /tmp/${{ARCHIVE_NAME}} *.log 2>/dev/null || echo 'No logs to archive'",
            f"aws s3 cp /tmp/${{ARCHIVE_NAME}} {config.s3_bucket}",
        ]

        # Add post-upload actions
        if config.archive_after_upload:
            upload_commands.append(f"mkdir -p {config.archive_after_upload}")
            upload_commands.append(f"mv /tmp/${{ARCHIVE_NAME}} {config.archive_after_upload}/")
        elif config.delete_after_upload:
            upload_commands.append(f"rm -f /tmp/${{ARCHIVE_NAME}}")
        
        if config.delete_after_upload:
            upload_commands.append(f"rm -f {nginx_path}/logs/*.log")

        # Clean up temp file if not archived
        if not config.archive_after_upload:
            upload_commands.append(f"rm -f /tmp/${{ARCHIVE_NAME}}")

        upload_cmd = " && ".join(upload_commands)
        
        result = self.executor.execute_command(upload_cmd)
        
        if result.overall_success:
            logger.info("Logs uploaded successfully from all hosts")
        else:
            logger.warning("Failed to upload logs from some hosts")
            
        return result 