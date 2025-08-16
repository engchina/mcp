# OCI Compute MCP Server

A Model Context Protocol (MCP) server that provides comprehensive Oracle Cloud Infrastructure (OCI) compute instance management capabilities. This server enables AI assistants and applications to interact with OCI compute resources through a standardized interface.

## Features

### Compartment Management
- **List Compartments**: Retrieve all compartments in your OCI tenancy with pagination support
- **Get Compartment by Name**: Find specific compartments by name across your tenancy
- **Hierarchical Navigation**: Support for nested compartment structures

### Compute Instance Operations
- **List Instances**: Get compute instances within specific compartments or across all compartments
- **Instance Details**: Retrieve comprehensive information about specific instances
- **Instance Search**: Find instances by name within compartments
- **Instance Actions**: Perform lifecycle operations (START, STOP, RESTART, RESET) on compute instances
- **Multi-Region Support**: Operate across different OCI regions

### Additional Features
- **Cross-Region Operations**: Support for operations across multiple OCI regions
- **Flexible Authentication**: Support for OCI configuration files and environment variable overrides
- **Comprehensive Error Handling**: Detailed error messages and status reporting
- **JSON Response Format**: Structured responses for easy integration

## Prerequisites

- Python 3.8 or higher
- Oracle Cloud Infrastructure (OCI) account with appropriate permissions
- OCI CLI configured or OCI configuration file set up
- Required Python packages (see below)

## Installation

1. **Clone or download the server file**:
   ```bash
   # Download the oci-compute-mcp-server.py file to your desired location
   ```

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## OCI Configuration

The server uses the standard OCI configuration file (`~/.oci/config`) by default. Ensure your configuration includes:

```ini
[DEFAULT]
user=ocid1.user.oc1..your_user_ocid
fingerprint=your_key_fingerprint
tenancy=ocid1.tenancy.oc1..your_tenancy_ocid
region=us-ashburn-1
key_file=~/.oci/your_private_key.pem
```

### Required OCI Permissions

Your OCI user or group should have the following permissions:

```
Allow group <your-group> to read compartments in tenancy
Allow group <your-group> to read instances in tenancy
Allow group <your-group> to manage instances in tenancy
Allow group <your-group> to use compute-management in tenancy
```

## Required Python Packages

- `oci` - Oracle Cloud Infrastructure Python SDK
- `mcp` - Model Context Protocol framework
- `requests` - HTTP library for Python

## MCP Server Configuration

To use this server with an MCP client, add the following configuration:

```json
{
  "mcpServers": {
    "oci-compute": {
      "command": "python",
      "args": ["/path/to/oci-compute-mcp-server.py"],
      "env": {
        "TENANCY_ID_OVERRIDE": "your_tenancy_id",
        "REGION_ID_OVERRIDE": "your_region"
      }
    }
  }
}
```

## Environment Variables

The following environment variables can be used to override default configurations:

### Configuration Overrides (stdio transport only)
- **`TENANCY_ID_OVERRIDE`**: Override the tenancy ID from OCI config
- **`REGION_ID_OVERRIDE`**: Override the default region from OCI config

**Note**: Environment variable overrides are only effective when using `stdio` transport mode.

### Testing Environment Variables
- **`TEST_COMPARTMENT_NAME`**: Compartment name for testing (default: 'test-compartment')
- **`TEST_INSTANCE_NAME`**: Instance name for testing (default: 'test-instance')
- **`TEST_INSTANCE_ID`**: Instance OCID for testing
- **`TEST_REGION`**: Region for testing (default: 'us-ashburn-1')

## Usage

### As MCP Server

1. **Start the server**:
   ```bash
   python oci-compute-mcp-server.py
   ```

2. **Connect your MCP client** to the server using the appropriate transport method.

## API Tools

The server provides the following MCP tools:

1. **`list_compartments`** - List all compartments in the tenancy
2. **`get_compartment_by_name`** - Find a compartment by name
   - Parameters: `compartment_name` (string)
3. **`list_compute_instances`** - List instances in a specific compartment
   - Parameters: `compartment_name` (string), `region` (optional string)
4. **`get_compute_instance`** - Get details of a specific instance
   - Parameters: `instance_id` (string), `region` (optional string)
5. **`get_compute_instance_by_name`** - Find an instance by name in a compartment
   - Parameters: `instance_name` (string), `compartment_name` (string), `region` (optional string)
6. **`compute_instance_action`** - Perform actions on an instance
   - Parameters: `instance_id` (string), `action` (string: START|STOP|RESTART|RESET), `region` (optional string)

## Security

- **Credentials**: Never hardcode OCI credentials in your code
- **Permissions**: Follow the principle of least privilege when setting up OCI permissions
- **Network**: Consider network security when deploying the MCP server
- **Logging**: Be cautious about logging sensitive information
- **Transport Security**: Use secure transport methods in production environments

## Example Prompts

Here are some example prompts you can use with AI assistants connected to this MCP server:

### Compartment Management
```
"List all compartments in my OCI tenancy"
"Find the compartment named 'production'"
"Show me all compartments and their current status"
```

### Instance Discovery
```
"List all compute instances in the 'development' compartment"
"Show me all running instances across all compartments"
"Find the instance named 'web-server-01' in the 'production' compartment"
"List all instances in the us-phoenix-1 region"
```

### Instance Management
```
"Start the instance with ID ocid1.instance.oc1.iad.abcd1234"
"Stop all instances in the 'development' compartment that are currently running"
"Restart the instance named 'database-server' in the 'production' compartment"
"Show me the current status of instance 'web-server-01'"
```

### Cross-Region Operations
```
"List all instances in the us-west-1 region"
"Start the instance 'backup-server' in the eu-frankfurt-1 region"
"Show me all stopped instances across all regions"
```

### Monitoring and Reporting
```
"Generate a report of all instances grouped by compartment and lifecycle state"
"Show me all instances that have been running for more than 30 days"
"List all instances with their shapes and availability domains"
"Find all instances that are currently stopped and need to be started"
```

### Troubleshooting
```
"Check the status of all instances in the 'production' compartment"
"Show me any instances that are in a failed state"
"List all instances and their last state change times"
```

## Testing

Run the test suite to verify the server functionality:

```bash
# Run all tests
python test_oci_compute_mcp_server.py

# Run specific test
python test_oci_compute_mcp_server.py test_list_compartments

# Run tests with custom environment variables
TEST_COMPARTMENT_NAME="my-test-compartment" python test_oci_compute_mcp_server.py
```

The test suite includes:
- Compartment listing and lookup tests
- Compute instance operations tests
- Error handling validation
- JSON response format verification
- Invalid input handling tests

## Error Handling

The server provides comprehensive error handling with detailed error messages:

- **Authentication Errors**: Issues with OCI credentials or configuration
- **Permission Errors**: Insufficient OCI permissions for requested operations
- **Resource Not Found**: When specified compartments or instances don't exist
- **Invalid Parameters**: When provided parameters are malformed or invalid
- **Service Errors**: When OCI services are unavailable or return errors

## Contributing

Contributions are welcome! Please ensure that:

1. All tests pass
2. Code follows the existing style
3. New features include appropriate tests
4. Documentation is updated accordingly

## License

This project is licensed under the Universal Permissive License v1.0.