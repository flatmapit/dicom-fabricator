#!/bin/bash

# Test PACS Setup Script
# This script sets up the test PACS environment for DICOM Fabricator

echo "🔧 DICOM Fabricator Test PACS Setup"
echo "===================================="

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
    echo "  basic       - Start basic test PACS (default)"
    echo "  troubleshoot - Start PACS with troubleshooting container"
    echo "  enhanced    - Start enhanced PACS with DICOM tools"
    echo "  stop        - Stop all test PACS containers"
    echo "  clean       - Stop and remove all containers and data"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start basic test PACS"
    echo "  $0 troubleshoot       # Start with troubleshooting tools"
    echo "  $0 stop               # Stop all containers"
    echo ""
}

# Function to start basic PACS
start_basic() {
    echo "🚀 Starting basic test PACS..."
    cd docker
    docker-compose up -d
    cd ..
    echo "✅ Basic test PACS started"
    echo "   - Test PACS 1: localhost:4242 (HTTP: 8042)"
    echo "   - Test PACS 2: localhost:4243 (HTTP: 8043)"
}

# Function to start troubleshooting PACS
start_troubleshoot() {
    echo "🔍 Starting PACS with troubleshooting tools..."
    ./scripts/setup_troubleshoot_pacs.sh
}

# Function to start enhanced PACS
start_enhanced() {
    echo "⚡ Starting enhanced PACS with DICOM tools..."
    ./scripts/setup_enhanced_pacs.sh
}

# Function to stop containers
stop_containers() {
    echo "🛑 Stopping test PACS containers..."
    cd docker
    docker-compose -f docker-compose.yml down 2>/dev/null || true
    docker-compose -f docker-compose.troubleshoot.yml down 2>/dev/null || true
    docker-compose -f docker-compose.enhanced.yml down 2>/dev/null || true
    cd ..
    echo "✅ All test PACS containers stopped"
}

# Function to clean everything
clean_all() {
    echo "🧹 Cleaning all test PACS containers and data..."
    stop_containers
    docker system prune -f
    echo "✅ Cleanup complete"
}

# Main logic
case "${1:-basic}" in
    "basic")
        start_basic
        ;;
    "troubleshoot")
        start_troubleshoot
        ;;
    "enhanced")
        start_enhanced
        ;;
    "stop")
        stop_containers
        ;;
    "clean")
        clean_all
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
