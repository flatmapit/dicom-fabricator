# Test PACS Setup - Orthanc

## Overview
This project uses Orthanc as a local test PACS server for development and testing of the DICOM Fabricator application.

## Prerequisites
- Docker and Docker Compose installed on your system
- No admin access required

## Quick Start

### 1. Start the PACS Server
```bash
docker-compose up -d
```

### 2. Access the Web Interface
- URL: http://localhost:8042
- Username: `test`
- Password: `test123`

### 3. Stop the PACS Server
```bash
docker-compose down
```

## Connection Parameters

### DICOM Configuration
- **AE Title**: `TESTPACS`
- **DICOM Port**: `4242`
- **Host**: `localhost` (or `host.docker.internal` from within Docker)

### REST API
- **URL**: http://localhost:8042
- **Authentication**: Basic Auth (test/test123)

### DICOMweb Endpoints
- **WADO-RS**: http://localhost:8042/dicom-web/
- **QIDO-RS**: http://localhost:8042/dicom-web/
- **STOW-RS**: http://localhost:8042/dicom-web/

## DICOM Fabricator Connection Settings
When configuring the DICOM Fabricator to send to this test PACS:
- **AE Title (Calling)**: `DICOMFAB`
- **AE Title (Called)**: `TESTPACS`
- **Host**: `localhost`
- **Port**: `4242`

## Useful Commands

### View PACS Logs
```bash
docker-compose logs -f orthanc
```

### Clear All Studies
```bash
# Warning: This will delete all stored studies
docker-compose down -v
docker-compose up -d
```

### Test DICOM Echo
```bash
# Using dcm4che tools (if installed)
echoscu -c TESTPACS@localhost:4242

# Using pydicom/pynetdicom (if installed)
python -c "from pynetdicom import AE; ae = AE(); ae.add_requested_context('1.2.840.10008.1.1'); assoc = ae.associate('localhost', 4242, ae_title='TESTPACS'); print('Echo successful!' if assoc.is_established else 'Failed'); assoc.release() if assoc.is_established else None"
```

## Storage
- Studies are stored in `./orthanc-data/` directory
- This directory is created automatically on first run
- Data persists between container restarts

## Troubleshooting

### Port Already in Use
If ports 4242 or 8042 are already in use, modify the port mappings in `docker-compose.yml`:
```yaml
ports:
  - "14242:4242"  # Change to different port
  - "18042:8042"  # Change to different port
```

### Connection Refused
- Ensure Docker is running
- Check firewall settings
- Verify ports are not blocked

## Security Note
This configuration is for **development/testing only**. For production:
- Change default credentials
- Enable proper authentication
- Configure TLS/SSL
- Restrict network access