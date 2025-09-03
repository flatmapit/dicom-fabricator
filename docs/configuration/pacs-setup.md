# PACS Setup Guide

This guide explains how to configure image servers (PACS) for DICOM Fabricator.

## Related Documents
- [Installation Guide](../getting-started/installation.md) - Basic setup instructions
- [Authentication Setup](authentication.md) - User access control
- [Glossary](../glossary.md) - Technical terms explained
- [C-MOVE Troubleshooting](../troubleshooting/cmove-troubleshooting.md) - Transfer issues

## What is a PACS?

A PACS (Picture Archiving and Communication System) is a server that stores and manages medical images. DICOM Fabricator can connect to multiple PACS servers to:
- Send generated studies to servers
- Query existing studies
- Move studies between servers

## Quick Setup with Test Servers

The easiest way to get started is with the included test servers:

### 1. Start Test Servers
```bash
# Start all 4 test servers (2 test + 2 production)
cd test-pacs
./setup_all_pacs.sh start
```

This creates:
- **Test PACS 1**: localhost:4242 (DICOM), localhost:8042 (Web)
- **Test PACS 2**: localhost:4243 (DICOM), localhost:8043 (Web)
- **Prod PACS 1**: localhost:4245 (DICOM), localhost:8045 (Web)
- **Prod PACS 2**: localhost:4246 (DICOM), localhost:8046 (Web)

### 2. Configure DICOM Fabricator
```bash
# Set up PACS configuration with proper routing
python3 test-pacs/scripts/setup_pacs_config.py
```

### 3. Access Web Interfaces
- **Test PACS 1**: http://localhost:8042 (username: test, password: test123)
- **Test PACS 2**: http://localhost:8043 (username: test, password: test123)
- **Prod PACS 1**: http://localhost:8045 (username: test, password: test123)
- **Prod PACS 2**: http://localhost:8046 (username: test, password: test123)

## Understanding PACS Configuration

### Connection Settings
Each PACS server needs these basic settings:

```json
{
  "name": "My PACS Server",
  "host": "pacs.example.com",
  "port": 104,
  "aec": "PACS",
  "environment": "test"
}
```

**Settings explained:**
- **name**: Friendly name for the server
- **host**: Server address (IP or hostname)
- **port**: DICOM port (usually 104)
- **aec**: Server's connection name (AE Title)
- **environment**: "test" or "prod" for access control

### Application Connection Names
DICOM Fabricator needs its own connection names for different operations:

```json
{
  "aet_find": "DICOMFAB",
  "aet_store": "DICOMFAB", 
  "aet_echo": "DICOMFAB"
}
```

**Connection names explained:**
- **aet_find**: Used when searching for studies
- **aet_store**: Used when sending studies to the server
- **aet_echo**: Used when testing connectivity

## Adding Your Own PACS Server

### 1. Get Server Information
Contact your PACS administrator to get:
- Server address (IP or hostname)
- DICOM port number
- Server's connection name (AE Title)
- Connection names your application should use

### 2. Add Server Configuration
1. Go to **PACS Management** in the web interface
2. Click **"Add New PACS"**
3. Fill in the server information:
   - **Name**: Friendly name (e.g., "Hospital PACS")
   - **Host**: Server address
   - **Port**: DICOM port (usually 104)
   - **AEC**: Server's connection name
   - **Environment**: Choose "test" or "prod"
   - **Find AE**: Your application's search connection name
   - **Store AE**: Your application's send connection name
   - **Echo AE**: Your application's test connection name

### 3. Test Connection
Click **"Test Connection"** to verify the server is reachable.

## C-MOVE Routing (Advanced)

C-MOVE allows transferring studies between PACS servers. This requires special configuration:

### Understanding C-MOVE
- **Source PACS**: Where the study currently exists
- **Destination PACS**: Where you want to move the study
- **Move AE**: Special connection name for transfers

### Setting Up C-MOVE Routing
1. Go to **PACS Management**
2. Click **"Edit C-MOVE Routing"** for a PACS
3. For each destination PACS, enter the Move AE title
4. Leave blank if C-MOVE is not supported to that destination

### Example Configuration
```json
{
  "move_routing": {
    "pacs-2-id": "MOVE_TO_PACS2",
    "pacs-3-id": "MOVE_TO_PACS3"
  }
}
```

## Environment Separation

DICOM Fabricator separates test and production environments:

### Test Environment
- Safe for testing and development
- Users with test roles can access
- Usually contains test data

### Production Environment
- Real clinical data
- Restricted access
- Users need production roles

### Access Control
- **test_read**: Can view test PACS only
- **test_write**: Can work with test PACS
- **prod_read**: Can view production PACS only
- **prod_write**: Can work with production PACS
- **admin**: Can access all PACS

## Troubleshooting

### Common Issues

**"Connection failed" errors:**
- Check server address and port
- Verify network connectivity
- Ensure firewall allows DICOM traffic
- Check if server is running

**"AE Title not recognized" errors:**
- Verify the server's AE Title (AEC)
- Check your application's AE Titles
- Ensure both sides use the same connection names

**"C-MOVE failed" errors:**
- Check C-MOVE routing configuration
- Verify Move AE titles are correct
- Ensure both PACS support C-MOVE
- Check network connectivity between PACS

### Testing Connectivity
Use the built-in connection test:
1. Go to **PACS Management**
2. Click **"Test Connection"** for the server
3. Check the results and error messages

### Getting Help
- Check the [C-MOVE Troubleshooting](../troubleshooting/cmove-troubleshooting.md) guide
- Review server logs for detailed error messages
- Contact your PACS administrator for server-specific issues

## Server Management

### Available Commands
```bash
# Start all test servers
./setup_all_pacs.sh start

# Check server status
./setup_all_pacs.sh status

# Stop all servers
./setup_all_pacs.sh stop

# Restart servers
./setup_all_pacs.sh restart

# Clean up (remove all data)
./setup_all_pacs.sh clean
```

### Server Status
Check if servers are running:
```bash
# Check if ports are in use
lsof -i :8042  # Test PACS 1
lsof -i :8043  # Test PACS 2
lsof -i :8045  # Prod PACS 1
lsof -i :8046  # Prod PACS 2
```

## Next Steps

- [Web Interface Guide](../user-guides/web-interface.md) - Learn the interface
- [C-MOVE Troubleshooting](../troubleshooting/cmove-troubleshooting.md) - Transfer issues
- [Common Issues](../troubleshooting/common-issues.md) - General problems
