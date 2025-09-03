#!/bin/bash

# Enhanced PACS Setup with Troubleshooting Tools
echo "🔧 Setting up Enhanced PACS with troubleshooting tools..."

# Stop existing containers
echo "Stopping existing containers..."
docker stop orthanc-test-pacs orthanc-test-pacs-2 2>/dev/null || true
docker rm orthanc-test-pacs orthanc-test-pacs-2 2>/dev/null || true

# Build enhanced containers
echo "Building enhanced containers with DICOM tools..."
cd docker
docker-compose -f docker-compose.enhanced.yml build

# Start enhanced containers
echo "Starting enhanced containers..."
docker-compose -f docker-compose.enhanced.yml up -d

# Wait for containers to start
echo "Waiting for containers to start..."
sleep 10

# Test connectivity
echo "Testing container connectivity..."
echo "Testing ping between containers:"
docker exec orthanc-test-pacs-enhanced ping -c 2 orthanc-test-pacs-2-enhanced

echo "Testing DICOM tools availability:"
docker exec orthanc-test-pacs-enhanced which findscu
docker exec orthanc-test-pacs-enhanced which movescu
docker exec orthanc-test-pacs-enhanced which echoscu

echo "Testing internal DICOM connectivity:"
docker exec orthanc-test-pacs-enhanced echoscu -v -aet TESTPACS -aec TESTPACS2 orthanc-test-pacs-2-enhanced 4242

echo "✅ Enhanced PACS setup complete!"
echo "Containers:"
echo "  - orthanc-test-pacs-enhanced (localhost:4242, 8042)"
echo "  - orthanc-test-pacs-2-enhanced (localhost:4243, 8043)"
echo ""
echo "Available tools in containers:"
echo "  - ping, netcat, curl, wget"
echo "  - findscu, movescu, echoscu, storescu"
echo ""
echo "Network: dicom-fabricator-network"
