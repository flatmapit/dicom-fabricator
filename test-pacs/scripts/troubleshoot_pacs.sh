#!/bin/bash

# PACS Troubleshooting Script
echo "🔍 PACS Troubleshooting Tool"
echo "=============================="

# Check if enhanced containers are running
if ! docker ps | grep -q "orthanc-test-pacs-enhanced"; then
    echo "❌ Enhanced containers not running. Run ./setup_enhanced_pacs.sh first."
    exit 1
fi

echo "✅ Enhanced containers detected"
echo ""

# Test 1: Basic connectivity
echo "1. Testing basic connectivity..."
docker exec orthanc-test-pacs-enhanced ping -c 2 orthanc-test-pacs-2-enhanced
echo ""

# Test 2: Port connectivity
echo "2. Testing port connectivity..."
docker exec orthanc-test-pacs-enhanced netcat -zv orthanc-test-pacs-2-enhanced 4242
echo ""

# Test 3: DICOM Echo
echo "3. Testing DICOM Echo..."
docker exec orthanc-test-pacs-enhanced echoscu -v -aet TESTPACS -aec TESTPACS2 orthanc-test-pacs-2-enhanced 4242
echo ""

# Test 4: DICOM Echo (reverse)
echo "4. Testing DICOM Echo (reverse)..."
docker exec orthanc-test-pacs-2-enhanced echoscu -v -aet TESTPACS2 -aec TESTPACS orthanc-test-pacs-enhanced 4242
echo ""

# Test 5: C-FIND
echo "5. Testing C-FIND..."
docker exec orthanc-test-pacs-enhanced findscu -v -aet TESTPACS -aec TESTPACS2 orthanc-test-pacs-2-enhanced 4242 -k QueryRetrieveLevel=STUDY
echo ""

# Test 6: C-FIND (reverse)
echo "6. Testing C-FIND (reverse)..."
docker exec orthanc-test-pacs-2-enhanced findscu -v -aet TESTPACS2 -aec TESTPACS orthanc-test-pacs-enhanced 4242 -k QueryRetrieveLevel=STUDY
echo ""

# Test 7: HTTP API
echo "7. Testing HTTP API..."
echo "Test PACS 1 studies:"
curl -s "http://localhost:8042/studies" | jq '.[] | {StudyInstanceUID: .MainDicomTags.StudyInstanceUID}' 2>/dev/null || echo "No studies or jq not available"
echo ""
echo "Test PACS 2 studies:"
curl -s "http://localhost:8043/studies" | jq '.[] | {StudyInstanceUID: .MainDicomTags.StudyInstanceUID}' 2>/dev/null || echo "No studies or jq not available"
echo ""

# Test 8: Container network info
echo "8. Container network information..."
echo "Test PACS 1 IP:"
docker exec orthanc-test-pacs-enhanced ip addr show eth0 | grep "inet " | awk '{print $2}'
echo "Test PACS 2 IP:"
docker exec orthanc-test-pacs-2-enhanced ip addr show eth0 | grep "inet " | awk '{print $2}'
echo ""

echo "✅ Troubleshooting complete!"
