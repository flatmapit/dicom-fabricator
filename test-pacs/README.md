# Test PACS Environment

This directory contains the test PACS environment for DICOM Fabricator, including Docker containers, configuration files, and testing scripts.

## Directory Structure

```
test-pacs/
├── docker/                 # Docker configuration files
│   ├── docker-compose.yml           # Basic test PACS setup
│   ├── docker-compose.troubleshoot.yml  # PACS with troubleshooting tools
│   ├── docker-compose.enhanced.yml      # Enhanced PACS with DICOM tools
│   ├── Dockerfile.enhanced              # Enhanced container definition
│   ├── orthanc-config.json             # Test PACS 1 configuration
│   ├── orthanc-config-2.json           # Test PACS 2 configuration
│   ├── orthanc-data/                   # Test PACS 1 data volume
│   └── orthanc-data-2/                 # Test PACS 2 data volume
├── scripts/                # Setup and testing scripts
│   ├── setup_pacs_config.py           # PACS configuration setup
│   ├── setup_enhanced_pacs.sh         # Enhanced PACS setup
│   ├── setup_troubleshoot_pacs.sh     # Troubleshooting PACS setup
│   ├── troubleshoot_pacs.sh           # PACS troubleshooting tool
│   └── test_cmove_*.py                # C-MOVE testing scripts
├── docs/                   # Test PACS documentation
├── data/                   # Test data and configurations
└── setup.sh               # Main setup script
```

## Quick Start

### Basic Test PACS
```bash
cd test-pacs
./setup.sh basic
```

### Troubleshooting Environment
```bash
cd test-pacs
./setup.sh troubleshoot
```

### Enhanced Environment (with DICOM tools)
```bash
cd test-pacs
./setup.sh enhanced
```

## Available Commands

- `./setup.sh basic` - Start basic test PACS (default)
- `./setup.sh troubleshoot` - Start PACS with troubleshooting container
- `./setup.sh enhanced` - Start enhanced PACS with DICOM tools
- `./setup.sh stop` - Stop all test PACS containers
- `./setup.sh clean` - Stop and remove all containers and data
- `./setup.sh help` - Show help message

## Test PACS Configuration

### Test PACS 1
- **Container**: `orthanc-test-pacs`
- **DICOM Port**: `4242`
- **HTTP Port**: `8042`
- **AE Title**: `TESTPACS`
- **Network**: `dicom-fabricator-network`

### Test PACS 2
- **Container**: `orthanc-test-pacs-2`
- **DICOM Port**: `4243`
- **HTTP Port**: `8043`
- **AE Title**: `TESTPACS2`
- **Network**: `dicom-fabricator-network`

## C-MOVE Configuration

The test PACS are configured with C-MOVE routing between all PACS:

- **Test PACS 1** → **Test PACS 2**: `CMOVE_TO_TESTPACS2`
- **Test PACS 2** → **Test PACS 1**: `CMOVE_TO_TESTPACS1`
- **Test PACS 1** → **Prod PACS 1**: `CMOVE_TO_PRODPACS1`
- **Test PACS 1** → **Prod PACS 2**: `CMOVE_TO_PRODPACS2`
- **Test PACS 2** → **Prod PACS 1**: `CMOVE_TO_PRODPACS1`
- **Test PACS 2** → **Prod PACS 2**: `CMOVE_TO_PRODPACS2`

## Troubleshooting

### Using the Troubleshooting Container
```bash
# Start troubleshooting environment
./setup.sh troubleshoot

# Run DICOM tools from within the container
docker exec dicom-troubleshoot findscu -v -aet DICOMFAB -aec TESTPACS orthanc-test-pacs 4242 -k QueryRetrieveLevel=STUDY
docker exec dicom-troubleshoot movescu -v -aet DICOMFAB -aec TESTPACS -aem CMOVE_TO_TESTPACS2 orthanc-test-pacs 4242 -k StudyInstanceUID=<UID> -k QueryRetrieveLevel=STUDY
```

### Available Tools in Troubleshooting Container
- `findscu`, `movescu`, `echoscu`, `storescu` - DICOM tools
- `ping`, `netcat`, `curl` - Network tools
- Access to internal container network

### Common Issues

1. **"No Acceptable Presentation Contexts"**
   - Check that Orthanc configuration has correct transfer syntaxes
   - Verify AE titles match between source and destination

2. **"Failed: UnableToProcess"**
   - Verify study exists in source PACS
   - Check C-MOVE AE title configuration
   - Ensure destination PACS is accessible

3. **Container connectivity issues**
   - Use troubleshooting container to test internal connectivity
   - Check Docker network configuration

## Integration with Main Application

The test PACS are configured to work with the main DICOM Fabricator application:

1. **PACS Configuration**: The app's `data/pacs_config.json` references these test PACS
2. **C-MOVE Routing**: C-MOVE operations use the configured AE titles
3. **Study Generation**: Generated studies can be sent to test PACS
4. **Testing**: C-MOVE operations can be tested between test PACS

## Development

### Adding New Test PACS
1. Add new container to `docker/docker-compose.yml`
2. Create configuration file in `docker/`
3. Update `scripts/setup_pacs_config.py`
4. Add C-MOVE routing configuration

### Modifying Configuration
1. Edit configuration files in `docker/`
2. Restart containers: `./setup.sh stop && ./setup.sh basic`
3. Test changes using troubleshooting tools

## Security Notes

- Test PACS are configured for development/testing only
- Default credentials are used (test/test123, test2/test456)
- Network access is restricted to local development
- Do not use in production environments
