#!/bin/bash

# DICOM Fabricator Setup Script
# Automates the initial setup process for new users

set -e  # Exit on any error

echo "🏥 DICOM Fabricator Setup"
echo "========================="
echo

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected (>= $required_version required)"
else
    echo "❌ Python $python_version detected, but $required_version or higher is required"
    echo "   Please install Python $required_version or higher and try again"
    exit 1
fi

# Install dependencies
echo
echo "📦 Installing Python dependencies..."
pip3 install -r config/requirements.txt

# Initialize data directories and sample files
echo
echo "📁 Setting up data directories..."
mkdir -p dicom_output data backups logs

# Copy sample files if actual files don't exist
if [ ! -f "data/patient_registry.json" ]; then
    echo "👥 Creating initial patient registry from sample..."
    cp data/patient_registry.json.sample data/patient_registry.json
else
    echo "✅ Patient registry already exists"
fi

if [ ! -f "data/pacs_config.json" ]; then
    echo "🖥️ Creating initial PACS configuration from sample..."
    cp data/pacs_config.json.sample data/pacs_config.json
else
    echo "✅ PACS configuration already exists"
fi

# Check for DCMTK tools (REQUIRED for PACS operations)
echo
echo "🔧 Checking DCMTK Command-Line Tools..."

dcmtk_missing=false
if command -v storescu &> /dev/null; then
    echo "✅ storescu detected (C-STORE operations)"
else
    echo "❌ storescu not found - required for sending studies to PACS"
    dcmtk_missing=true
fi

if command -v findscu &> /dev/null; then
    echo "✅ findscu detected (C-FIND operations)"
else
    echo "❌ findscu not found - required for querying PACS"
    dcmtk_missing=true
fi

if command -v echoscu &> /dev/null; then
    echo "✅ echoscu detected (C-ECHO operations)"
else
    echo "❌ echoscu not found - required for testing PACS connectivity"
    dcmtk_missing=true
fi

if command -v movescu &> /dev/null; then
    echo "✅ movescu detected (C-MOVE operations)"
else
    echo "⚠️ movescu not found - optional, needed for transferring between PACS servers"
fi

if [ "$dcmtk_missing" = true ]; then
    echo
    echo "⚠️ DCMTK tools are REQUIRED for PACS operations"
    echo "The web interface uses these tools to communicate with PACS servers."
    echo
    echo "To install DCMTK:"
    echo "  macOS:    brew install dcmtk"
    echo "  Ubuntu:   sudo apt-get install dcmtk"
    echo "  Windows:  Download from https://dicom.offis.de/dcmtk/"
    echo
    echo "Without DCMTK, you can still:"
    echo "  • Generate DICOM files"
    echo "  • Manage patients"
    echo "  • View generated studies"
    echo "But you CANNOT:"
    echo "  • Send studies to PACS servers"
    echo "  • Query PACS servers"
    echo "  • Test PACS connectivity"
fi

# Check for optional Docker
echo
echo "🐳 Checking Docker (optional)..."
if command -v docker &> /dev/null; then
    echo "✅ Docker detected - test PACS servers available"
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        echo "✅ Docker Compose detected - ready for PACS server startup"
    else
        echo "⚠️ Docker Compose not detected - test PACS servers may not work"
    fi
else
    echo "ℹ️ Docker not detected - test PACS servers will not be available"
    echo "   (Optional - only needed for local test PACS servers)"
fi

echo
echo "🚀 Setup Complete!"
echo
echo "Next steps:"
echo "1. Start the web application:  python3 app.py"
echo "2. Open browser to:            http://localhost:5001"
echo "3. Optional - Start PACS:      cd docker && docker compose up -d"
echo
echo "📖 For more information, see README.md"
echo "🐛 Issues? https://github.com/brainsnorkel/DICOM_Fabricator/issues"
echo