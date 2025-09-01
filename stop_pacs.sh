#!/bin/bash
#
# Convenience script to stop all PACS servers
#

echo "Stopping all PACS servers..."

# Stop the main docker-compose
echo "Stopping Test PACS servers..."
cd docker && docker-compose down

# Stop additional PACS servers
echo "Stopping Production PACS servers..."
docker stop orthanc-prod testpacs-test testpacs-prod 2>/dev/null || true
docker rm orthanc-prod testpacs-test testpacs-prod 2>/dev/null || true

echo "All PACS servers stopped."
