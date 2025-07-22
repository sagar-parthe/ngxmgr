# ngxmgr

A command-line interface (CLI) tool for managing NGINX deployments across multiple Linux servers. The tool centralizes control of NGINX infrastructure, streamlines routine operations, and allows consistent configuration and log management across environments.

## Features

- **Multi-server operations**: Execute commands across multiple servers in parallel or serial mode
- **AWS Auto Scaling Group integration**: Automatically discover target servers from ASG with region support
- **Conda environment management**: Install NGINX in isolated conda environments
- **Shell compatibility**: Works across different shells (bash, ksh, zsh, etc.)
- **Secure SSH authentication**: Password-based authentication with secure prompts
- **Single password prompt**: Password is requested only once per CLI command execution
- **File and directory copying**: Copy files or directories to remote servers with recursive support
- **Log management**: Upload logs to S3 with compression and archiving options
- **Configuration flexibility**: Support for both CLI arguments and JSON configuration files
- **Comprehensive error handling**: Detailed logging and structured output
- **Dry-run support**: Test operations without making changes

## Shell Compatibility

**ngxmgr is designed to work across different shell environments without requiring special configuration:**

### Supported Shells
- **bash** (Bourne Again Shell)
- **ksh** (Korn Shell) 
- **zsh** (Z Shell)
- **dash** (Debian Almquist Shell)
- **sh** (POSIX Shell)

### Key Compatibility Features

1. **No conda activation required**: Uses direct paths to conda binaries instead of `conda activate`
2. **Portable command syntax**: Avoids shell-specific features like `$()` substitution
3. **Cross-shell variable assignment**: Uses backticks for command substitution
4. **Robust error handling**: Commands work even when features like `local` are unavailable

### How it works:

```bash
# Instead of this (bash-specific, requires conda init):
source /opt/conda/bin/activate && conda activate nginx_env && nginx -c config

# ngxmgr does this (works in any shell):
/opt/conda/envs/nginx_env/bin/nginx -c config
```

## Supported Operations

| Command       | Description                                                             |
| ------------- | ----------------------------------------------------------------------- |
| `install`     | Install NGINX using conda environment and set up directory structure   |
| `remove`      | Remove NGINX installation and cleanup environment                       |
| `start`       | Start the NGINX server                                                  |
| `stop`        | Stop the NGINX server                                                   |
| `restart`     | Restart the NGINX server                                                |
| `clear-cache` | Delete the contents of the NGINX cache directory                        |
| `clear-logs`  | Delete or truncate access and error logs                               |
| `upload-logs` | Upload logs to AWS S3 with optional deletion or local archiving        |
| `copy`        | Copy files or directories to remote servers                            |

## Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ngxmgr

# Install dependencies
poetry install

# Activate the environment
poetry shell
```

### Using pip

```bash
# Install from source
pip install -e .
```

## Usage

### Basic Examples

```bash
# Install NGINX on specific hosts
ngxmgr install \
    --hosts "server1.example.com,server2.example.com" \
    --username nginx-admin \
    --base-conda-path /opt/miniconda3 \
    --deployment-path /opt/nginx \
    --nginx-conf-path ./nginx.conf \
    --custom-conda-channel https://conda.example.com/

# Install NGINX on ASG instances in specific region
ngxmgr install \
    --asg my-nginx-asg \
    --region-name us-west-2 \
    --username nginx-admin \
    --base-conda-path /opt/miniconda3 \
    --deployment-path /opt/nginx \
    --nginx-conf-path ./nginx.conf \
    --custom-conda-channel https://conda.example.com/

# Start NGINX services
ngxmgr start \
    --hosts "server1.example.com,server2.example.com" \
    --username nginx-admin \
    --base-conda-path /opt/miniconda3 \
    --deployment-path /opt/nginx

# Upload logs to S3
ngxmgr upload-logs \
    --hosts "server1.example.com,server2.example.com" \
    --username nginx-admin \
    --deployment-path /opt/nginx \
    --s3-bucket s3://my-nginx-logs/ \
    --delete-after-upload

# Copy a file to all servers
ngxmgr copy config.json /opt/app/config.json \
    --hosts "server1.example.com,server2.example.com" \
    --username admin

# Copy a directory recursively to ASG instances
ngxmgr copy ./assets /var/www/html/assets \
    --asg my-web-asg \
    --region-name us-east-1 \
    --username admin \
    --recursive
```

### Copy Command

The `copy` command provides Unix `cp`-like functionality for remote servers:

```bash
# Basic file copy
ngxmgr copy local-file.txt /remote/path/file.txt --hosts "server1,server2" --username admin

# Copy directory recursively
ngxmgr copy ./local-dir /remote/path/dir --hosts "server1,server2" --username admin --recursive

# Copy to ASG instances
ngxmgr copy app.jar /opt/app/app.jar --asg my-app-asg --region-name us-west-2 --username deploy

# Copy with execution mode
ngxmgr copy large-file.bin /tmp/large-file.bin --hosts "server1,server2" --username admin --execution-mode serial
```

### Using Configuration Files

Create a JSON configuration file:

```json
{
  "hosts": ["server1.example.com", "server2.example.com"],
  "username": "nginx-admin",
  "region_name": "us-west-2",
  "base_conda_path": "/opt/miniconda3",
  "deployment_path": "/opt/nginx",
  "nginx_dir_name": "nginx_prod",
  "nginx_conf_path": "./nginx.conf",
  "custom_conda_channel": "https://conda.example.com/",
  "s3_bucket": "s3://my-nginx-logs/",
  "execution_mode": "parallel",
  "timeout": 600
}
```

Use the configuration file:

```bash
# Install using config file
ngxmgr install --config config.json

# Override specific values
ngxmgr install --config config.json --timeout 900 --region-name us-east-1
```

## Password Management

**ngxmgr uses smart password caching to ensure you only need to enter your SSH password once per command execution, regardless of:**

- Number of target hosts (1 or 100+)
- Execution mode (parallel or serial)
- Number of operations in a command (install has 3+ steps)
- Multiple SSH connections required

### How it works:

1. **Single prompt**: Password is requested once before any SSH operations begin
2. **Thread-safe caching**: Password is securely cached in memory with thread locks
3. **Reuse across operations**: All SSH connections in the command use the cached password
4. **Automatic cleanup**: Password is cleared when the command completes

### Example scenarios:

```bash
# Install on 10 servers - password prompted ONCE
ngxmgr install --hosts "server1,server2,server3,server4,server5,server6,server7,server8,server9,server10" --username admin ...

# Multi-step install operation - password prompted ONCE
# (Even though install involves: directory creation + conda setup + file upload)
ngxmgr install --asg my-asg --username admin ...

# Parallel execution - password prompted ONCE
# (No race conditions or multiple prompts)
ngxmgr start --hosts "server1,server2,server3" --execution-mode parallel --username admin ...
```

## Troubleshooting

### Common Issues

**"CondaError: Run 'conda init' before 'conda activate'"**
- ✅ **Fixed**: ngxmgr no longer requires conda activation or initialization
- Uses direct paths to conda binaries: `/path/to/conda/bin/conda` and `/path/to/conda/envs/nginx_env/bin/nginx`

**"ksh: local: not found"**
- ✅ **Fixed**: ngxmgr avoids shell-specific features and uses portable POSIX syntax
- Works across bash, ksh, zsh, and other shells without modification

**Multiple password prompts**
- ✅ **Fixed**: Password is cached and reused across all SSH connections in a command

### Environment Validation

ngxmgr includes built-in environment validation to help diagnose issues:

```bash
# The install command automatically validates:
# - Conda installation exists and is executable
# - Required paths are accessible
# - Shell environment compatibility

# For manual diagnostics, check logs or use dry-run mode:
ngxmgr install --dry-run --hosts "server1" --username admin ...
```

## Command Line Arguments

### Global Arguments

| Argument              | Short | Description                                     | Required |
| --------------------- | ----- | ----------------------------------------------- | -------- |
| `--hosts`             | `-h`  | Comma-separated list of hostnames/IPs          | *        |
| `--asg`               | `-a`  | AWS Auto Scaling Group name                     | *        |
| `--region-name`       | `-r`  | AWS region name                                 | No       |
| `--username`          | `-u`  | SSH username for server login                   | Yes      |
| `--execution-mode`    | `-e`  | Execution mode: parallel or serial             | No       |
| `--timeout`           | `-t`  | Timeout per operation (seconds)                 | No       |
| `--config`            | `-f`  | Path to JSON config file                        | No       |
| `--log-file`          | `-l`  | Log file path                                   | No       |
| `--dry-run`           |       | Test mode without making changes               | No       |

*Either `--hosts` or `--asg` must be provided.

### Install/Remove Specific

| Argument                  | Description                           | Required |
| ------------------------- | ------------------------------------- | -------- |
| `--base-conda-path`       | Path to base conda environment        | Yes      |
| `--deployment-path`       | Root path for deployment              | Yes      |
| `--nginx-dir-name`        | Directory name for NGINX              | No       |
| `--nginx-conf-path`       | Path to local nginx.conf file         | Yes*     |
| `--custom-conda-channel`  | Custom conda channel for NGINX        | Yes*     |

*Required for install command only.

### Log Upload Specific

| Argument                  | Description                           | Required |
| ------------------------- | ------------------------------------- | -------- |
| `--s3-bucket`             | S3 bucket URI for log uploads         | Yes      |
| `--archive-after-upload`  | Path to archive logs after upload     | No       |
| `--delete-after-upload`   | Delete logs after upload              | No       |

### Copy Command Specific

| Argument         | Short | Description                           | Required |
| ---------------- | ----- | ------------------------------------- | -------- |
| `source_path`    |       | Local source file or directory path   | Yes      |
| `destination_path` |     | Remote destination path               | Yes      |
| `--recursive`    | `-R`  | Copy directories recursively          | No       |

## Configuration Priority

When both configuration files and CLI arguments are provided:

1. **CLI arguments** override configuration file values
2. **Configuration file** provides defaults for unspecified CLI arguments
3. **Built-in defaults** are used when neither CLI nor config file specify a value

## AWS Integration

The tool automatically uses the IAM role of the EC2 instance it's running on for AWS authentication. 

### Required Permissions

Ensure the instance has the following permissions:

- `autoscaling:DescribeAutoScalingGroups`
- `ec2:DescribeInstances`

### Region Configuration

- Use `--region-name` to specify the AWS region for ASG operations
- If not specified, uses the default region from AWS configuration
- Can be set in JSON config files for consistency across commands

```bash
# Examples with region specification
ngxmgr install --asg my-asg --region-name us-west-2 --username admin ...
ngxmgr copy app.jar /opt/app.jar --asg prod-asg --region-name eu-west-1 --username deploy
```

## Security

- **SSH passwords** are prompted securely and never logged or echoed
- **Password caching** is memory-only and cleared after command completion
- **AWS authentication** uses IAM roles (no hardcoded credentials)
- **All operations** support dry-run mode for testing

## Error Handling

The tool provides comprehensive error handling with appropriate exit codes:

- `0`: Success
- `1`: Partial failure (some hosts failed)
- `2`: Complete failure or configuration error
- `3`: Connection error
- `4`: Operation error
- `5`: Unexpected error

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/ngxmgr

# Run specific test file
poetry run pytest tests/unit/test_config.py

# Test password caching functionality
python test_password_caching.py
```

### Code Quality

```bash
# Format code
poetry run ruff format

# Lint code
poetry run ruff check

# Type checking
poetry run mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure code quality checks pass
5. Submit a pull request

## License

[Specify your license here]

