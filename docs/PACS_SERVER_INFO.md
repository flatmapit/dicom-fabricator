# Orthanc PACS Server Connection Details

## Server Status
✅ **PACS Server is running and ready for testing**

## Connection Details

### DICOM Configuration
- **AE Title (AET):** TESTPACS
- **DICOM Port:** 4242
- **Host:** localhost (or host.docker.internal from within Docker)

### Web Interface
- **URL:** http://localhost:8042
- **Username:** test
- **Password:** test123

## Configured DICOM Modalities
The PACS server is configured to accept connections from:
- **DICOMFAB** - Your DICOM Fabricator application (expected at localhost:11112)

## Testing the Connection

### Using DCMTK (installed via Homebrew)
```bash
# Test DICOM echo (ping)
echoscu -aet DICOMFAB -aec TESTPACS localhost 4242

# Send a DICOM file
storescu -aet DICOMFAB -aec TESTPACS localhost 4242 your_dicom_file.dcm

# Query the PACS
findscu -P -aet DICOMFAB -aec TESTPACS -k 0008,0052=PATIENT localhost 4242
```

### Using curl for REST API
```bash
# Get system info
curl -u test:test123 http://localhost:8042/system

# List all studies
curl -u test:test123 http://localhost:8042/studies

# List all patients
curl -u test:test123 http://localhost:8042/patients
```

## Docker Management

### Start the PACS server
```bash
docker-compose up -d
```

### Stop the PACS server
```bash
docker-compose down
```

### View logs
```bash
docker logs orthanc-test-pacs -f
```

### Restart the server
```bash
docker-compose restart
```

## Storage
- DICOM files are stored in: `./orthanc-data/`
- Configuration file: `./orthanc-config.json`

## Notes
- The server accepts all DICOM stores without authentication for testing purposes
- C-ECHO is always allowed from any AE Title
- The web interface provides a full DICOM viewer and management tools
- Platform warning about linux/amd64 vs arm64 can be ignored - the server runs fine on Apple Silicon

## For DICOM Fabricator Integration
When configuring your DICOM Fabricator application:
- Set the destination AE Title to: **TESTPACS**
- Set the destination host to: **localhost**
- Set the destination port to: **4242**
- Your application's AE Title should be: **DICOMFAB** (or configure a new one in orthanc-config.json)