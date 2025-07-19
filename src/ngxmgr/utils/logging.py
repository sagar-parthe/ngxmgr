"""
Logging and error handling utilities for ngxmgr.
"""
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

from ngxmgr.utils.executor import ExecutionSummary, HostResult


def setup_logging(log_file: Optional[Path] = None, verbose: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        log_file: Optional log file path
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler with Rich
    console_handler = RichHandler(rich_tracebacks=True)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def format_execution_summary(summary: ExecutionSummary, show_details: bool = True) -> str:
    """
    Format execution summary for display.
    
    Args:
        summary: ExecutionSummary to format
        show_details: Whether to show detailed results per host
        
    Returns:
        Formatted summary string
    """
    console = Console(file=sys.stderr, force_terminal=False)
    
    # Create summary table
    table = Table(title="Execution Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Hosts", str(summary.total_hosts))
    table.add_row("Successful", str(summary.successful_hosts))
    table.add_row("Failed", str(summary.failed_hosts))
    table.add_row("Overall Success", "✓" if summary.overall_success else "✗")
    
    # Capture table output
    with console.capture() as capture:
        console.print(table)
    
    output = capture.get()
    
    if show_details and summary.results:
        output += "\n\nDetailed Results:\n"
        for result in summary.results:
            status = "✓" if result.success else "✗"
            output += f"  {status} {result.hostname}"
            
            if not result.success and result.error:
                output += f" - Error: {result.error}"
            elif result.command_result and result.command_result.stderr:
                output += f" - {result.command_result.stderr.strip()}"
            
            output += "\n"
    
    return output


def format_json_summary(summary: ExecutionSummary) -> str:
    """
    Format execution summary as JSON.
    
    Args:
        summary: ExecutionSummary to format
        
    Returns:
        JSON formatted summary
    """
    summary_dict = {
        "total_hosts": summary.total_hosts,
        "successful_hosts": summary.successful_hosts,
        "failed_hosts": summary.failed_hosts,
        "overall_success": summary.overall_success,
        "results": []
    }
    
    for result in summary.results:
        result_dict = {
            "hostname": result.hostname,
            "success": result.success,
            "error": result.error
        }
        
        if result.command_result:
            result_dict.update({
                "exit_code": result.command_result.exit_code,
                "stdout": result.command_result.stdout,
                "stderr": result.command_result.stderr
            })
        
        summary_dict["results"].append(result_dict)
    
    return json.dumps(summary_dict, indent=2)


def handle_execution_result(
    summary: ExecutionSummary,
    operation_name: str,
    json_output: bool = False,
    show_details: bool = True
) -> None:
    """
    Handle and display execution results.
    
    Args:
        summary: ExecutionSummary from operation
        operation_name: Name of the operation for logging
        json_output: Whether to output JSON format
        show_details: Whether to show detailed results
    """
    logger = logging.getLogger(__name__)
    
    if json_output:
        print(format_json_summary(summary))
    else:
        print(format_execution_summary(summary, show_details))
    
    if summary.overall_success:
        logger.info(f"{operation_name} completed successfully on all hosts")
    else:
        logger.warning(f"{operation_name} failed on {summary.failed_hosts} out of {summary.total_hosts} hosts")
        
        # Log individual failures
        for result in summary.results:
            if not result.success:
                logger.error(f"{operation_name} failed on {result.hostname}: {result.error or 'Unknown error'}")


def get_exit_code(summary: ExecutionSummary) -> int:
    """
    Get appropriate exit code based on execution summary.
    
    Args:
        summary: ExecutionSummary to evaluate
        
    Returns:
        Exit code (0 for success, 1 for partial failure, 2 for complete failure)
    """
    if summary.overall_success:
        return 0
    elif summary.successful_hosts > 0:
        return 1  # Partial failure
    else:
        return 2  # Complete failure


class NGXMgrError(Exception):
    """Base exception for ngxmgr operations."""
    pass


class ConfigurationError(NGXMgrError):
    """Configuration validation error."""
    pass


class ConnectionError(NGXMgrError):
    """SSH connection error."""
    pass


class OperationError(NGXMgrError):
    """Operation execution error."""
    pass


def handle_error(error: Exception, operation: str) -> None:
    """
    Handle and log errors appropriately.
    
    Args:
        error: Exception that occurred
        operation: Operation being performed when error occurred
    """
    logger = logging.getLogger(__name__)
    
    if isinstance(error, ConfigurationError):
        logger.error(f"Configuration error in {operation}: {error}")
        typer.echo(f"Configuration error: {error}", err=True)
        sys.exit(2)
    elif isinstance(error, ConnectionError):
        logger.error(f"Connection error in {operation}: {error}")
        typer.echo(f"Connection error: {error}", err=True)
        sys.exit(3)
    elif isinstance(error, OperationError):
        logger.error(f"Operation error in {operation}: {error}")
        typer.echo(f"Operation error: {error}", err=True)
        sys.exit(4)
    else:
        logger.error(f"Unexpected error in {operation}: {error}")
        typer.echo(f"Unexpected error: {error}", err=True)
        sys.exit(5) 