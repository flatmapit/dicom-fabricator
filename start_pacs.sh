#!/bin/bash
#
# Convenience script to start the PACS servers for test and production environments
#

echo "Starting PACS servers for test and production environments..."

# Start the main docker-compose (test PACS on port 4242)
echo "Starting Test PACS servers..."
cd docker && docker-compose up -d

# Start additional production PACS servers
echo "Starting Production PACS servers..."

# Production Orthanc on port 4243
docker run -d --name orthanc-prod \
  -p 8043:8042 \
  -p 4243:4242 \
  -v orthanc-prod-db:/var/lib/orthanc/db \
  -v orthanc-prod-config:/etc/orthanc \
  jodogne/orthanc-plugins:1.12.1

# Test PACS 2 on port 4244
docker run -d --name testpacs-test \
  -p 8044:8042 \
  -p 4244:4242 \
  -v testpacs-test-db:/var/lib/orthanc/db \
  -v testpacs-test-config:/etc/orthanc \
  jodogne/orthanc-plugins:1.12.1

# Production PACS on port 4245
docker run -d --name testpacs-prod \
  -p 8045:8042 \
  -p 4245:4242 \
  -v testpacs-prod-db:/var/lib/orthanc/db \
  -v testpacs-prod-config:/etc/orthanc \
  jodogne/orthanc-plugins:1.12.1

echo ""
echo "PACS servers starting. Access at:"
echo ""
echo "TEST ENVIRONMENT:"
echo "  Orthanc Test PACS:"
echo "    Web UI: http://localhost:8042 (test/test123)"
echo "    DICOM:  localhost:4242"
echo "  Test PACS:"
echo "    Web UI: http://localhost:8044 (test/test123)"
echo "    DICOM:  localhost:4244"
echo ""
echo "PRODUCTION ENVIRONMENT:"
echo "  Orthanc Production PACS:"
echo "    Web UI: http://localhost:8043 (test/test123)"
echo "    DICOM:  localhost:4243"
echo "  Production PACS:"
echo "    Web UI: http://localhost:8045 (test/test123)"
echo "    DICOM:  localhost:4245"
echo ""
echo "To stop all: ./stop_pacs.sh"