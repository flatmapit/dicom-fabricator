# Installation Guide

This guide provides detailed installation instructions for DICOM Fabricator.

## Prerequisites

- **Python 3.8+** (Python 3.11 recommended)
- **DCMTK tools** (findscu, storescu, movescu, echoscu)
- **Docker and Docker Compose** (optional, for test PACS servers)

## Python Environment Setup

### Option A: Using pyenv (Recommended)

**Install pyenv:**

**macOS:**
```bash
brew install pyenv
```

**Ubuntu/Debian:**
```bash
curl https://pyenv.run | bash
```

**Windows:**
```bash
pip install pyenv-win
```

**Create Python environment:**
```bash
# Install Python 3.11 (recommended)
pyenv install 3.11.0

# Set local Python version for this project
pyenv local 3.11.0

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### Option B: Using System Python

```bash
# Create virtual environment with system Python
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r config/requirements.txt
```

## Install DCMTK Tools

### macOS
```bash
brew install dcmtk
```

### Ubuntu/Debian
```bash
sudo apt-get install dcmtk
```

### Windows
Download from [DCMTK website](https://dcmtk.org/en/dcmtk/dcmtk-downloads/)

## Test PACS Servers (Optional)

### Automated Setup (Recommended)
```bash
# Start all 4 PACS (2 test + 2 prod) with correct configurations
cd test-pacs
./setup_all_pacs.sh start

# Check status of all PACS
./setup_all_pacs.sh status

# Stop all PACS
./setup_all_pacs.sh stop
```

This will start 4 Orthanc PACS servers with full C-MOVE routing:
- **Test PACS 1**: localhost:4242 (DICOM), localhost:8042 (HTTP) - AEC: TESTPACS
- **Test PACS 2**: localhost:4243 (DICOM), localhost:8043 (HTTP) - AEC: TESTPACS2
- **Prod PACS 1**: localhost:4245 (DICOM), localhost:8045 (HTTP) - AEC: ORTHANC
- **Prod PACS 2**: localhost:4246 (DICOM), localhost:8046 (HTTP) - AEC: PRODPACS2

### Available Options
- `./setup_all_pacs.sh start` - Start all 4 PACS (2 test + 2 prod)
- `./setup_all_pacs.sh status` - Check status of all PACS containers
- `./setup_all_pacs.sh stop` - Stop all PACS containers
- `./setup_all_pacs.sh restart` - Restart all PACS containers
- `./setup_all_pacs.sh clean` - Stop and remove all containers and data

## Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5001`

## Verify Installation

1. **Check Python environment:**
   ```bash
   python --version  # Should show Python 3.8+
   pip list | grep -E "(flask|pydicom)"  # Should show installed packages
   ```

2. **Check DCMTK tools:**
   ```bash
   findscu --version  # Should show DCMTK version
   storescu --version
   movescu --version
   ```

3. **Test web interface:**
   - Open `http://localhost:5001` in your browser
   - You should see the DICOM Fabricator dashboard

## Next Steps

- [First Steps](first-steps.md) - Create your first DICOM study
- [Quick Tour](quick-tour.md) - Explore the features
- [Authentication Setup](../configuration/authentication.md) - Configure user access

## Troubleshooting

### Common Issues

**"Command not found: findscu"**
- DCMTK tools are not installed or not in PATH
- Install DCMTK using the instructions above

**"Module not found" errors**
- Virtual environment is not activated
- Run `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows)

**"Port already in use"**
- Another application is using port 5001
- Change the port in `app.py` or stop the conflicting application

**"Permission denied" errors**
- Check file permissions in the project directory
- Ensure you have write access to create configuration files

### Getting Help

- Check the [Common Issues](../troubleshooting/common-issues.md) guide
- Review [GitHub Issues](https://github.com/flatmapit/dicom-fabricator/issues)
- Create a new issue with detailed error information
