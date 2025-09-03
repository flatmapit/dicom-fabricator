#!/bin/bash

# PACS Setup with Troubleshooting Container
echo "🔧 Setting up PACS with troubleshooting container..."

# Stop existing containers
echo "Stopping existing containers..."
docker stop orthanc-test-pacs orthanc-test-pacs-2 dicom-troubleshoot 2>/dev/null || true
docker rm orthanc-test-pacs orthanc-test-pacs-2 dicom-troubleshoot 2>/dev/null || true

# Start containers with troubleshooting
echo "Starting containers with troubleshooting..."
cd docker
docker-compose -f docker-compose.troubleshoot.yml up -d

# Wait for containers to start
echo "Waiting for containers to start..."
sleep 10

# Install DICOM tools in troubleshooting container
echo "Installing DICOM tools in troubleshooting container..."
docker exec dicom-troubleshoot apt-get update
docker exec dicom-troubleshoot apt-get install -y dcmtk iputils-ping netcat-openbsd curl

# Test connectivity
echo "Testing container connectivity..."
echo "Testing ping between containers:"
docker exec dicom-troubleshoot ping -c 2 orthanc-test-pacs
docker exec dicom-troubleshoot ping -c 2 orthanc-test-pacs-2

echo "Testing DICOM Echo:"
docker exec dicom-troubleshoot echoscu -v -aet DICOMFAB -aec TESTPACS orthanc-test-pacs 4242
docker exec dicom-troubleshoot echoscu -v -aet DICOMFAB -aec TESTPACS2 orthanc-test-pacs-2 4242

echo "Testing C-FIND:"
docker exec dicom-troubleshoot findscu -v -aet DICOMFAB -aec TESTPACS orthanc-test-pacs 4242 -k QueryRetrieveLevel=STUDY

echo "✅ PACS setup with troubleshooting complete!"
echo "Containers:"
echo "  - orthanc-test-pacs (localhost:4242, 8042)"
echo "  - orthanc-test-pacs-2 (localhost:4243, 8043)"
echo "  - dicom-troubleshoot (troubleshooting container)"
echo ""
echo "Use 'docker exec dicom-troubleshoot <command>' to run DICOM tools"
echo "Network: dicom-fabricator-network"
