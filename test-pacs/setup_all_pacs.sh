#!/bin/bash

# Comprehensive PACS Setup Script
# Sets up all 4 PACS (2 test + 2 prod) with correct configurations

set -e

echo "🏥 DICOM Fabricator - Complete PACS Setup"
echo "=========================================="
echo

# Check if we're in the right directory
if [ ! -f "docker/docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the test-pacs directory"
    echo "   Expected: test-pacs/docker/docker-compose.yml"
    exit 1
fi

# Function to show usage
show_usage() {
    echo ""
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  start       - Start all 4 PACS (2 test + 2 prod)"
    echo "  stop        - Stop all PACS containers"
    echo "  restart     - Restart all PACS containers"
    echo "  clean       - Stop and remove all containers and data"
    echo "  status      - Show status of all PACS containers"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start              # Start all 4 PACS"
    echo "  $0 stop               # Stop all containers"
    echo "  $0 status             # Check container status"
    echo ""
}

# Function to start all PACS
start_all_pacs() {
    echo "🚀 Starting all PACS servers..."
    
    # Start Test PACS (using docker-compose)
    echo "📋 Starting Test PACS (docker-compose)..."
    cd docker
    docker-compose up -d
    cd ..
    
    # Start Prod PACS 1
    echo "📋 Starting Prod PACS 1..."
    docker run -d --name prodpacs-1 \
        --network docker_default \
        -p 8045:8042 \
        -p 4245:4242 \
        -v prodpacs-1-db:/var/lib/orthanc/db \
        -v $(pwd)/docker/orthanc-prod-config.json:/etc/orthanc/orthanc.json:ro \
        jodogne/orthanc-plugins:latest
    
    # Start Prod PACS 2
    echo "📋 Starting Prod PACS 2..."
    docker run -d --name prodpacs-2 \
        --network docker_default \
        -p 8046:8042 \
        -p 4246:4242 \
        -v prodpacs-2-db:/var/lib/orthanc/db \
        -v $(pwd)/docker/orthanc-prod-config-2.json:/etc/orthanc/orthanc.json:ro \
        jodogne/orthanc-plugins:latest
    
    echo "✅ All PACS servers started!"
    echo
    show_pacs_info
}

# Function to stop all PACS
stop_all_pacs() {
    echo "🛑 Stopping all PACS containers..."
    
    # Stop Test PACS
    cd docker
    docker-compose down 2>/dev/null || true
    cd ..
    
    # Stop Prod PACS
    docker stop prodpacs-1 prodpacs-2 2>/dev/null || true
    docker rm prodpacs-1 prodpacs-2 2>/dev/null || true
    
    echo "✅ All PACS containers stopped"
}

# Function to restart all PACS
restart_all_pacs() {
    echo "🔄 Restarting all PACS containers..."
    stop_all_pacs
    sleep 2
    start_all_pacs
}

# Function to clean everything
clean_all() {
    echo "🧹 Cleaning all PACS containers and data..."
    stop_all_pacs
    
    # Remove volumes
    docker volume rm prodpacs-1-db prodpacs-2-db 2>/dev/null || true
    docker volume rm docker_orthanc-data docker_orthanc-data-2 2>/dev/null || true
    
    echo "✅ Cleanup complete"
}

# Function to show status
show_status() {
    echo "📊 PACS Container Status:"
    echo "========================"
    
    # Check Test PACS
    echo "Test PACS:"
    cd docker
    docker-compose ps
    cd ..
    
    echo
    echo "Prod PACS:"
    docker ps --filter "name=prodpacs" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo
    show_pacs_info
}

# Function to show PACS information
show_pacs_info() {
    echo "🌐 PACS Access Information:"
    echo "=========================="
    echo
    echo "TEST ENVIRONMENT:"
    echo "  Test PACS 1:"
    echo "    Web UI: http://localhost:8042 (test/test123)"
    echo "    DICOM:  localhost:4242 (AEC: TESTPACS)"
    echo "  Test PACS 2:"
    echo "    Web UI: http://localhost:8043 (test2/test456)"
    echo "    DICOM:  localhost:4243 (AEC: TESTPACS2)"
    echo
    echo "PRODUCTION ENVIRONMENT:"
    echo "  Prod PACS 1:"
    echo "    Web UI: http://localhost:8045 (orthanc/orthanc)"
    echo "    DICOM:  localhost:4245 (AEC: ORTHANC)"
    echo "  Prod PACS 2:"
    echo "    Web UI: http://localhost:8046 (orthanc/orthanc)"
    echo "    DICOM:  localhost:4246 (AEC: PRODPACS2)"
    echo
    echo "🔗 All PACS are configured with C-MOVE routing between each other"
    echo "📖 See docs/PACS_SERVER_INFO.md for detailed routing information"
}

# Main logic
case "${1:-start}" in
    "start")
        start_all_pacs
        ;;
    "stop")
        stop_all_pacs
        ;;
    "restart")
        restart_all_pacs
        ;;
    "clean")
        clean_all
        ;;
    "status")
        show_status
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo "❌ Unknown option: $1"
        show_usage
        exit 1
        ;;
esac
