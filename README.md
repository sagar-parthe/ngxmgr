# ngxmgr

A command-line interface (CLI) tool for managing NGINX deployments across multiple Linux servers. The tool centralizes control of NGINX infrastructure, streamlines routine operations, and allows consistent configuration and log management across environments.

## Features

- **Multi-server operations**: Execute commands across multiple servers in parallel or serial mode
- **AWS Auto Scaling Group integration**: Automatically discover target servers from ASG
- **Conda environment management**: Install NGINX in isolated conda environments
- **Secure SSH authentication**: Password-based authentication with secure prompts
- **Log management**: Upload logs to S3 with compression and archiving options
- **Configuration flexibility**: Support for both CLI arguments and JSON configuration files
- **Comprehensive error handling**: Detailed logging and structured output
- **Dry-run support**: Test operations without making changes

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

# Install NGINX on ASG instances
ngxmgr install \
    --asg my-nginx-asg \
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
```

### Using Configuration Files

Create a JSON configuration file:

```json
{
  "hosts": ["server1.example.com", "server2.example.com"],
  "username": "nginx-admin",
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
ngxmgr install --config config.json --timeout 900
```

## Command Line Arguments

### Global Arguments

| Argument              | Short | Description                                     | Required |
| --------------------- | ----- | ----------------------------------------------- | -------- |
| `--hosts`             | `-h`  | Comma-separated list of hostnames/IPs          | *        |
| `--asg`               | `-a`  | AWS Auto Scaling Group name                     | *        |
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

## Configuration Priority

When both configuration files and CLI arguments are provided:

1. **CLI arguments** override configuration file values
2. **Configuration file** provides defaults for unspecified CLI arguments
3. **Built-in defaults** are used when neither CLI nor config file specify a value

## AWS Integration

The tool automatically uses the IAM role of the EC2 instance it's running on for AWS authentication. Ensure the instance has the following permissions:

- `autoscaling:DescribeAutoScalingGroups`
- `ec2:DescribeInstances`

## Security

- SSH passwords are prompted securely and never logged or echoed
- AWS authentication uses IAM roles (no hardcoded credentials)
- All operations support dry-run mode for testing

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

