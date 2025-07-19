# **ngxmgr CLI Tool — Requirements Document**

## **1. Overview**

This document defines the requirements for a command-line interface (CLI) tool called ngxmgr to simplify and automate the management of NGINX deployments across multiple Linux-based servers. The tool will centralize control of NGINX infrastructure, streamline routine operations, and allow consistent configuration and log management across environments. It is intended for use in environments where NGINX is installed in user space via conda.

The tool supports both **interactive use** and **automated workflows** by accepting parameters via command-line flags or a **JSON-based configuration file**.

---

## **2. Key Features**

### **2.1 Server Operations**

The CLI must support the following actions on remote Linux servers:

| Command       | Description                                                             |
| ------------- | ----------------------------------------------------------------------- |
| `install`     | Install NGINX using a conda environment, prepare necessary directories. |
| `remove`      | Remove NGINX installation and cleanup environment and directories.      |
| `start`       | Start the NGINX server.                                                 |
| `stop`        | Stop the NGINX server.                                                  |
| `restart`     | Restart the NGINX server.                                               |
| `clear-cache` | Delete the contents of the NGINX cache directory.                       |
| `clear-logs`  | Delete or truncate access and error logs.                               |
| `upload-logs` | Upload logs to AWS S3, with optional deletion or local archiving.       |

* All operations should support **parallel execution** across servers by default, with a `--execution-mode serial` to run sequentially.
* The CLI must provide meaningful output and status per server.

---

## **3. Authentication & Connectivity**

* Server access will be via **SSH using username/password authentication**.
* The CLI should:

  * Accept the `--username` as a required argument.
  * Prompt the user for the password securely (without echoing input).
* Connections should support both IP addresses and domain names.
* For each operation, SSH must be used to remotely execute commands on target servers.

---

## **4. NGINX Installation Details**

### **4.1 Installation Workflow**

When the `install` command is executed:

1. **Activate a base conda environment**:

   ```bash
   source /apps/environments/myenv/bin/activate
   ```

   * The path to the base environment is provided by the user.

2. **Create a conda environment with NGINX**:

   ```bash
   conda create --name nginx_env -y -k nginx -c [custom_channel]
   ```

   * The CLI must use a user-defined **custom conda channel**.
   * The default environment name is nginx_env. Allow nginx_env name to be customized via CLI and JSON.

3. **Create the following directory structure** under the deployment path:

   ```
   [deployment_path]/[nginx_dir_name]/conf
   [deployment_path]/[nginx_dir_name]/cache
   [deployment_path]/[nginx_dir_name]/logs
   [deployment_path]/[nginx_dir_name]/var/tmp/nginx/client
   ```

   * Default `nginx_dir_name` is `nginx_run` (configurable).

4. **Upload the `nginx.conf` file** (provided via CLI) to the `conf/` directory on each server.

---

### **4.2 Removal Workflow**

The `remove` command will:

1. **Delete the entire NGINX deployment directory** (e.g., `/apps/tools/nginx_run`).
2. **Activate the base conda environment** as provided.
3. **Remove the NGINX conda environment**:

   ```bash
   conda remove -n nginx_env --all
   ```

---

## **5. Log Management**

### **5.1 Upload Logs**

The `upload-logs` command will:

* Compress the logs from the `logs/` directory.
* Prefix logs with hostname and timestamp.
* Upload them to the specified **AWS S3 bucket**.
* Optionally:

  * **Delete logs after upload**, or
  * **Archive them locally** under a specified path.
* These behaviors are controlled via command-line arguments.

---

## **6. Configuration & Input Options**

### **6.1 CLI Arguments**

The tool must support the following command-line arguments:

| Argument                               | Description                                     | Required                       |
| -------------------------------------- | ----------------------------------------------- | ------------------------------ |
| `--hosts`                              | Comma-separated list of hostnames/IPs           | Yes (unless `--asg` is used)   |
| `--asg`                                | AWS Auto Scaling Group name                     | Yes (unless `--hosts` is used) |
| `--username`                           | SSH username for server login                   | Yes                            |
| *(Password is prompted interactively)* |                                                 |                                |
| `--base-conda-path`                    | Path to the base conda environment              | Yes (for install/remove)       |
| `--deployment-path`                    | Root path for deployment                        | Yes (for install/remove)       |
| `--nginx-dir-name`                     | Directory name for NGINX (default: `nginx_run`) | No                             |
| `--nginx-conf-path`                    | Path to local `nginx.conf` file                 | Yes (for install)              |
| `--custom-conda-channel`               | Custom channel for installing nginx             | Yes (for install)              |
| `--s3-bucket`                          | S3 URI for log uploads                          | Required (for upload-logs)     |
| `--archive-after-upload`               | Path to archive logs after upload               | Optional                       |
| `--delete-after-upload`                | Flag to delete logs after upload                | Optional                       |
| `--execution-mode`                             | Either 'serial' or 'parallel'. Execute commands serially (default is parallel) | No                             |
| `--config`                             | Path to a JSON config file with parameters      | Optional                       |

> If the same argument is specified in both the **JSON config file** and **command line**, the **command-line value overrides** the config file. If an attribute is not passed in the JSON config file for an optional argument, use the default value.

- Add short-form flags, wherever relevant.
---

### **6.2 JSON Config File Format**

The tool should support passing a JSON config file using the `--config` argument. Example structure:

```json
{
  "hosts": ["192.168.0.1", "192.168.0.2"],
  "username": "nginxadmin",
  "base_conda_path": "/apps/environments/myenv/",
  "deployment_path": "/apps/tools/",
  "nginx_dir_name": "nginx_prod",
  "nginx_conf_path": "./configs/nginx.conf",
  "custom_conda_channel": "http://mychannel.example.com/conda",
  "s3_bucket": "s3://my-nginx-logs/",
  "archive_after_upload": "/var/archive/logs",
  "delete_after_upload": true
}
```

---

## **7. Execution & Error Handling**

* All operations must be executed via **SSH on each server**.
* To handle failure in one server during a parallel op. Specify flag for fail-fast or continue-on-error, with continue-on-error being default.
* Provide --timeout or similar for operations on each server to prevent hangs. Set an appropriate high value as default, with setting it to 0 has the effect of infinite timeouts by disabling timeouts
* Add option for log file output (--log-file)
* Support structured logs, especially for machine-readable logs or integration (e.g., JSON output option) and structured summaries per host
* Errors should be logged with:

  * Server name
  * Operation attempted
  * Error message or stack trace
* CLI should exit with appropriate codes:

  * `0` for success
  * Non-zero codes for partial/full failure
* Support dry run & validation by implementing `--dry-run` flag for testing configurations without execution.

---

## **8. Security Considerations**

* Do **not** log or echo passwords.
* Use secure password prompts (e.g., Python’s `getpass`) for authentication.

---

## **9. Technologies**
* Typer for CLI framework
* Poetry for dependency management
* Pytest as the testing framework
* Use AWS CLI on the remote servers (pre-installed) for uploading logs to S3
* For linting/formatting, use ruff