# C-MOVE and C-FIND Troubleshooting Guide

## Overview
This document provides solutions for common C-FIND and C-MOVE operation failures in DICOM Fabricator with Orthanc PACS servers.

## Common Issues and Solutions

### 1. C-FIND "No Acceptable Presentation Contexts" Error

**Symptom:**
```
findscu -v -aet DICOMFAB -aec TESTPACS orthanc-test-pacs 4242 -k QueryRetrieveLevel=STUDY
E: No Acceptable Presentation Contexts
Exit Code: 2
```

**Cause:**
The findscu command needs to specify the correct information model for the query.

**Solution:**
Use the `-S` flag to specify STUDY model:
```bash
findscu -S -aet DICOMFAB -aec TESTPACS orthanc-test-pacs 4242 \
  -k QueryRetrieveLevel=STUDY \
  -k StudyInstanceUID="" \
  -k PatientName=""
```

For PATIENT level queries:
```bash
findscu -P -aet DICOMFAB -aec TESTPACS orthanc-test-pacs 4242 \
  -k QueryRetrieveLevel=PATIENT \
  -k PatientID="" \
  -k PatientName=""
```

### 2. C-MOVE "UnableToProcess" Error

**Symptom:**
```
movescu -v -aet DICOMFAB -aec TESTPACS -aem CMOVE_TO_TESTPACS2 orthanc-test-pacs 4242 ...
W: Move response with error status (Failed: UnableToProcess)
Exit Code: 69
```

**Common Causes and Solutions:**

#### A. Incorrect Network References in DicomModalities

**Issue:** Using `localhost` in Docker container configurations prevents inter-container communication.

**Solution:** Update Orthanc configuration files to use container names:

For `orthanc-config.json` (TESTPACS):
```json
"DicomModalities": {
  "DICOMFAB": ["DICOMFAB", "host.docker.internal", 11112],
  "TESTPACS2": ["TESTPACS2", "orthanc-test-pacs-2", 4242],
  "CMOVE_TO_TESTPACS2": ["TESTPACS2", "orthanc-test-pacs-2", 4242]
}
```

For `orthanc-config-2.json` (TESTPACS2):
```json
"DicomModalities": {
  "DICOMFAB": ["DICOMFAB", "host.docker.internal", 11112],
  "TESTPACS": ["TESTPACS", "orthanc-test-pacs", 4242],
  "CMOVE_TO_TESTPACS": ["TESTPACS", "orthanc-test-pacs", 4242]
}
```

#### B. Missing or Incorrect C-MOVE Destination Configuration

**Issue:** The destination AE title used in C-MOVE must be defined in source PACS's DicomModalities.

**Solution:** Ensure the `-aem` parameter matches a configured modality:
```bash
# Check configured modalities via Orthanc REST API
curl -u test:test123 http://localhost:8042/modalities

# Use the correct AE title in movescu
movescu -aet DICOMFAB -aec TESTPACS -aem TESTPACS2 ...
```

#### C. Study Not Present in Source PACS

**Solution:** Verify study exists before attempting C-MOVE:
```bash
# Query for the study first
findscu -S -aet DICOMFAB -aec TESTPACS localhost 4242 \
  -k QueryRetrieveLevel=STUDY \
  -k StudyInstanceUID="1.2.826.0.1.3680043.8.498.*"

# Check via HTTP API
curl -u test:test123 http://localhost:8042/studies
```

### 3. Docker Network Configuration Issues

**Issue:** Containers cannot communicate due to network isolation.

**Solution:** Ensure all containers are on the same Docker network:
```bash
# Create network if not exists
docker network create dicom-fabricator-network

# Run containers with network
docker run -d --name orthanc-test-pacs \
  --network dicom-fabricator-network \
  -p 4242:4242 -p 8042:8042 \
  -v $(pwd)/orthanc-config.json:/etc/orthanc/orthanc.json \
  osimis/orthanc

docker run -d --name orthanc-test-pacs-2 \
  --network dicom-fabricator-network \
  -p 4243:4242 -p 8043:8042 \
  -v $(pwd)/orthanc-config-2.json:/etc/orthanc/orthanc.json \
  osimis/orthanc
```

### 4. Authentication Issues

**Issue:** Orthanc requires authentication for C-MOVE operations.

**Solution:** Configure proper authentication in DicomModalities or disable it for testing:
```json
{
  "DicomCheckCalledAet": false,
  "DicomCheckModalityHost": false,
  "DicomAlwaysAllowMove": true,
  "AuthenticationEnabled": false  // For testing only
}
```

## Testing Workflow

### 1. Verify Network Connectivity
```bash
# Test DICOM echo between PACS servers
docker exec orthanc-test-pacs echoscu -aet TESTPACS -aec TESTPACS2 orthanc-test-pacs-2 4242
```

### 2. Store a Study
```bash
# Store DICOM files to source PACS
storescu -aet DICOMFAB -aec TESTPACS localhost 4242 *.dcm

# Verify via HTTP API
curl -u test:test123 http://localhost:8042/studies
```

### 3. Query for Studies
```bash
# Query using findscu with correct model
findscu -S -aet DICOMFAB -aec TESTPACS localhost 4242 \
  -k QueryRetrieveLevel=STUDY \
  -k PatientName="*"
```

### 4. Perform C-MOVE
```bash
# Move study from TESTPACS to TESTPACS2
movescu -aet DICOMFAB -aec TESTPACS -aem TESTPACS2 localhost 4242 \
  -k StudyInstanceUID="1.2.826.0.1.3680043.8.498.11977308257654816997632722628335053414" \
  -k QueryRetrieveLevel=STUDY

# Verify on destination PACS
curl -u test2:test456 http://localhost:8043/studies
```

## Configuration Template

### Correct Orthanc Configuration for C-MOVE Support

```json
{
  "Name": "PACS Server Name",
  "DicomServerEnabled": true,
  "DicomAet": "MYAET",
  "DicomPort": 4242,
  "DicomCheckCalledAet": false,
  "DicomCheckModalityHost": false,
  
  // Enable all operations
  "DicomAlwaysAllowEcho": true,
  "DicomAlwaysAllowStore": true,
  "DicomAlwaysAllowFind": true,
  "DicomAlwaysAllowMove": true,
  
  // Accept unknown SOP classes
  "UnknownSopClassAccepted": true,
  
  // Configure remote modalities
  "DicomModalities": {
    "REMOTE_PACS": ["REMOTE_AET", "remote-hostname", 4242],
    "DESTINATION_FOR_MOVE": ["DEST_AET", "dest-hostname", 4242]
  },
  
  // Transfer syntaxes
  "AcceptedTransferSyntaxes": [
    "1.2.840.10008.1.2",      // Implicit VR Little Endian
    "1.2.840.10008.1.2.1",    // Explicit VR Little Endian
    "1.2.840.10008.1.2.2"     // Explicit VR Big Endian
  ]
}
```

## Application Configuration

Update `data/pacs_config.json` to use correct AE titles:

```json
{
  "configs": [
    {
      "name": "Test PACS 1",
      "aec": "TESTPACS",
      "aet_find": "DICOMFAB",
      "aet_store": "DICOMFAB",
      "host": "localhost",
      "port": 4242,
      "move_destinations": {
        "72a5301c-c774-4d73-af88-0ebb3acfc1b0": "TESTPACS2"
      }
    },
    {
      "name": "Test PACS 2",
      "aec": "TESTPACS2",
      "aet_find": "DICOMFAB",
      "aet_store": "DICOMFAB",
      "host": "localhost",
      "port": 4243,
      "move_destinations": {
        "338e008a-30a1-4e59-b9c6-df4d3b9b2d74": "TESTPACS"
      }
    }
  ]
}
```

## Debugging Commands

### Check Orthanc Logs
```bash
docker logs orthanc-test-pacs --tail 50
docker logs orthanc-test-pacs-2 --tail 50
```

### Test with Verbose Output
```bash
# Add -v for verbose, -d for debug
findscu -v -d -S -aet DICOMFAB -aec TESTPACS localhost 4242 \
  -k QueryRetrieveLevel=STUDY

movescu -v -d -aet DICOMFAB -aec TESTPACS -aem TESTPACS2 localhost 4242 \
  -k StudyInstanceUID="..." \
  -k QueryRetrieveLevel=STUDY
```

### Monitor Network Traffic
```bash
# Use tcpdump to monitor DICOM traffic
docker exec orthanc-test-pacs tcpdump -i any -n port 4242
```

## Common Error Codes

| Error | Code | Meaning | Solution |
|-------|------|---------|----------|
| No Acceptable Presentation Contexts | 2 | SOP class not supported | Use correct model flag (-S, -P, -W) |
| UnableToProcess | 69 | C-MOVE failed | Check network config and AE titles |
| Association Rejected | 1 | Connection refused | Verify PACS is running and ports are open |
| Timeout | 124 | Operation timed out | Increase timeout or check network |

## References

- [DCMTK Documentation](https://support.dcmtk.org/docs/)
- [Orthanc Book - DICOM Protocol](https://book.orthanc-server.com/users/lua.html)
- [DICOM Standard - C-MOVE Service](http://dicom.nema.org/medical/dicom/current/output/html/part04.html#sect_C.4)