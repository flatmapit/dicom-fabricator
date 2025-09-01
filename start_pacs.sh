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

# Test PACS 2 on port 4243
docker run -d --name testpacs-2 \
  -p 8043:8042 \
  -p 4243:4242 \
  -v testpacs-2-db:/var/lib/orthanc/db \
  -v testpacs-2-config:/etc/orthanc \
  jodogne/orthanc-plugins:1.12.1

# Test PACS 3 on port 4244
docker run -d --name testpacs-3 \
  -p 8044:8042 \
  -p 4244:4242 \
  -v testpacs-3-db:/var/lib/orthanc/db \
  -v testpacs-3-config:/etc/orthanc \
  jodogne/orthanc-plugins:1.12.1

# Prod PACS 1 on port 4245
docker run -d --name prodpacs-1 \
  -p 8045:8042 \
  -p 4245:4242 \
  -v prodpacs-1-db:/var/lib/orthanc/db \
  -v prodpacs-1-config:/etc/orthanc \
  jodogne/orthanc-plugins:1.12.1

# Prod PACS 2 on port 4246
docker run -d --name prodpacs-2 \
  -p 8046:8042 \
  -p 4246:4242 \
  -v prodpacs-2-db:/var/lib/orthanc/db \
  -v prodpacs-2-config:/etc/orthanc \
  jodogne/orthanc-plugins:1.12.1

echo ""
echo "PACS servers starting. Access at:"
echo ""
echo "TEST ENVIRONMENT:"
echo "  Test PACS 1:"
echo "    Web UI: http://localhost:8042 (test/test123)"
echo "    DICOM:  localhost:4242"
echo "  Test PACS 2:"
echo "    Web UI: http://localhost:8043 (test/test123)"
echo "    DICOM:  localhost:4243"
echo "  Test PACS 3:"
echo "    Web UI: http://localhost:8044 (test/test123)"
echo "    DICOM:  localhost:4244"
echo ""
echo "PRODUCTION ENVIRONMENT:"
echo "  Prod PACS 1:"
echo "    Web UI: http://localhost:8045 (test/test123)"
echo "    DICOM:  localhost:4245"
echo "  Prod PACS 2:"
echo "    Web UI: http://localhost:8046 (test/test123)"
echo "    DICOM:  localhost:4246"
echo ""
echo "To stop all: ./stop_pacs.sh"