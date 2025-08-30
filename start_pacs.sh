#!/bin/bash
#
# Convenience script to start the PACS server
#

echo "Starting Orthanc PACS server..."
cd docker && docker-compose up -d

echo "PACS server starting. Access at:"
echo "  Web UI: http://localhost:8042 (test/test123)"
echo "  DICOM:  localhost:4242"
echo ""
echo "To stop: cd docker && docker-compose down"