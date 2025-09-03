# DICOM Fabricator

DICOM Fabricator (DF) is a tool for PACS administrators and radiology clinical integrations developers and maintainers. DF is a DICOM study test data generation and PACS query system built with Python and Flask. DF allows you to query and C-MOVE across multiple PACS, create synthetic DICOM studies from user input or based on an HL7 ORM order message, and to monitor PACS status with C-ECHO.

Note: This tool works in test, but exercise caution with live/prod PACS and test in your environment carefully. 

## 🎥 Quick Start Demo

<div align="center">


**[▶️ Watch Demo Video (2 minutes)](https://flatmapit-com-videos.s3.amazonaws.com/20250903DicomFab.mov)**

*Complete walkthrough of DICOM Fabricator features and workflows*

</div>

> **💡 Can't play the video?** Right-click the link above and select "Save link as..." to download the MP4 file locally.


## Example Screens


![Dashboard Screenshot](docs/images/dashboard.png)

![PACS Context](docs/images/pacs-context-diag.png)


*For a detailed visual overview of features and common activities, see [Feature Overview](docs/feature_overview.md)*

## Features

- **Authentication & Authorization**: Local authentication, Active Directory, and SAML 2.0 support with simplified role-based access control
- **Environment-Specific Roles**: Separate roles for test and production PACS operations with clear capability boundaries
- **User Management**: Complete user administration interface with role-based permissions
- **HL7 ORM Integration**: Parse HL7 ORM messages and generate corresponding DICOM studies
- **DICOM Generation**: Create synthetic DICOM files with realistic metadata
- **Multi-PACS Integration**: Send studies to PACS servers, query studies on one or more PACS, and perform C-MOVE operations
- **Patient Management**: Comprehensive patient registry with synthetic data generation
- **Web Interface**: Modern Flask-based web application with Bootstrap UI
- **Docker Support**: Easy deployment with Docker Compose for example test PACS servers

## Role-Based Access Control

DICOM Fabricator uses a simplified role-based permission system with the following roles:

### Available Roles

- **`admin`**: Full system access - can do anything including user management, PACS configuration, and all DICOM operations in both test and production environments
- **`test_write`**: Test environment write access - can query, C-STORE and C-MOVE to test PACS, generate DICOM, and manage users
- **`test_read`**: Test environment read access - can view status and query test PACS, generate DICOM, and manage users
- **`prod_write`**: Production environment write access - can query, C-STORE and C-MOVE to production PACS, generate DICOM, and manage users
- **`prod_read`**: Production environment read access - can view status and query production PACS, generate DICOM, and manage users

### Enterprise Integration

For Active Directory and SAML integration, use the following group naming convention with the `DF-` prefix:

- `DF-Admin` → `admin` role
- `DF-TestWrite` → `test_write` role
- `DF-TestRead` → `test_read` role
- `DF-ProdWrite` → `prod_write` role
- `DF-ProdRead` → `prod_read` role

The `DF-` prefix ensures namespace isolation and prevents accidental permission grants from similar group names in enterprise environments.

### Migration from Permission-Based System

If you're upgrading from a previous version that used individual permissions, run the migration script:

```bash
python3 scripts/migrate_users_to_roles.py
```

This script will:
- Create a backup of your existing users file
- Convert user permissions to appropriate roles
- Remove the old permissions field
- Preserve all other user data

## Architecture

- **Backend**: Python Flask application
- **DICOM Processing**: pydicom library for DICOM manipulation
- **PACS Communication**: DCMTK tools (findscu, storescu, movescu)
- **Frontend**: HTML templates with Bootstrap 5 and JavaScript
- **Database**: JSON-based storage for configurations and patient data

## Prerequisites

- Python 3.8+ (3.11 recommended)
- pyenv (optional, for Python version management)
- DCMTK tools (findscu, storescu, movescu, echoscu, movescu)
- Docker and Docker Compose (for PACS servers)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/flatmapit/dicom-fabricator.git
cd dicom-fabricator
```

### 2. Set Up Python Environment

#### Option A: Using pyenv (Recommended for advanced users)

**Install pyenv (if not already installed):**

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
# Install via pip
pip install pyenv-win
```

**Create and activate Python environment with pyenv:**
```bash
# Install Python 3.11 (recommended version)
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

#### Option B: Using System Python (Quick setup)

**Create and activate Python environment with system Python:**
```bash
# Create virtual environment with system Python
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

**Note:** This option works if you have Python 3.8+ installed on your system. Check your version with `python3 --version`.

### 3. Install Dependencies

```bash
pip install -r config/requirements.txt
```

### 4. Install DCMTK

#### macOS
```bash
brew install dcmtk
```

#### Ubuntu/Debian
```bash
sudo apt-get install dcmtk
```

#### Windows
Download from [DCMTK website](https://dcmtk.org/en/dcmtk/dcmtk-downloads/)

### 5. Start Test PACS Servers (Optional)

#### Automated Setup (Recommended)
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

#### Available Options
- `./setup_all_pacs.sh start` - Start all 4 PACS (2 test + 2 prod)
- `./setup_all_pacs.sh status` - Check status of all PACS containers
- `./setup_all_pacs.sh stop` - Stop all PACS containers
- `./setup_all_pacs.sh restart` - Restart all PACS containers
- `./setup_all_pacs.sh clean` - Stop and remove all containers and data
- `./setup.sh stop` - Stop all test PACS containers
- `./setup.sh clean` - Stop and remove all containers and data

#### Legacy Setup (Alternative)
```bash
# Start all PACS servers (test and production)
./start_pacs.sh
```

### 6. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5001`

## Configuration

### Authentication Setup

DICOM Fabricator supports multiple authentication modes:

#### Option 1: No Authentication (Default)
The application runs without authentication for development and testing:

```bash
# No additional setup required
python app.py
```

#### Option 2: Local Authentication
Enable username/password authentication:

1. **Create authentication configuration:**
```bash
cp config/auth_config.json.sample config/auth_config.json
```

2. **Edit `config/auth_config.json`:**
```json
{
  "auth_enabled": true,
  "enterprise_auth_enabled": false,
  "default_user_permissions": [
    "dicom_view",
    "pacs_query_test"
  ]
}
```

3. **Create initial admin user:**
```bash
python3 -c "
from src.auth import AuthManager
auth = AuthManager()
auth.create_user('admin', 'admin123', 'admin@example.com', 'admin')
print('Admin user created: admin/admin123')
"
```

#### Option 3: Enterprise Authentication (AD/SAML)
For enterprise environments with Active Directory or SAML:

1. **Enable enterprise authentication:**
```json
{
  "auth_enabled": true,
  "enterprise_auth_enabled": true,
  "default_user_permissions": [
    "dicom_view",
    "pacs_query_test"
  ]
}
```

2. **Configure Active Directory:**
```bash
cp config/enterprise_auth.json.sample config/enterprise_auth.json
# Edit with your AD server details
```

3. **Configure SAML:**
```bash
cp config/enterprise_auth.json.sample config/enterprise_auth.json
# Edit with your SAML provider details
```

4. **Set up group mappings:**
```bash
cp config/group_mappings.json.sample config/group_mappings.json
# Map AD/SAML groups to application roles
```

For detailed authentication setup, see [Authentication Setup Guide](docs/AUTHENTICATION_SETUP.md).

### PACS Configuration

The DICOM Fabricator uses an enhanced PACS configuration model with separate Application Entity Titles (AETs) for different operations:

#### New AE Model
- **C-FIND AET**: Used for querying studies from PACS
- **C-STORE AET**: Used for sending studies to PACS (optional - leave blank to disable C-STORE)
- **C-ECHO AET**: Used for connection testing
- **C-MOVE Routing**: Configurable routing table for C-MOVE operations between PACS

#### Configuration Setup

1. **Set up PACS configuration with C-MOVE routing:**
```bash
python3 test-pacs/scripts/setup_pacs_config.py
```

2. **Or copy the sample configuration:**
```bash
cp data/pacs_config.json.sample data/pacs_config.json
```

3. **Edit `data/pacs_config.json` with your PACS server information:**
```json
{
  "pacs-server-id": {
    "name": "Your PACS Server",
    "host": "pacs.example.com",
    "port": 104,
    "aet_find": "DICOMFAB",
    "aet_store": "DICOMFAB",
    "aet_echo": "DICOMFAB",
    "aec": "PACS",
    "environment": "test",
    "move_routing": {
      "other-pacs-id": "MOVE_AE_TITLE"
    }
  }
}
```

4. **Configure C-MOVE routing:**
   - Use the PACS management interface to configure C-MOVE routing tables
   - Each PACS can have different AE titles for C-MOVE to other PACS
   - Leave blank if C-MOVE is not supported to a particular destination

#### Migration from Old Configuration
If you have an existing configuration, run the migration script:
```bash
python3 scripts/migrate_pacs_config.py
```

### Patient Configuration

Copy the sample patient configuration:

```bash
cp data/patient_config.json.sample data/patient_config.json
```

## Usage

### 1. Generate DICOM Studies

1. Navigate to the Generator page
2. Paste an HL7 ORM message
3. Click "Generate DICOM"
4. View and manage the generated studies

### 2. Send to PACS

1. Select a study from the generated list
2. Choose a PACS server
3. Click "Send to PACS"
4. Monitor the transfer status

### 3. Query PACS

1. Go to the Query PACS page
2. Select a PACS server
3. Enter search criteria
4. View and export results

### 4. Manage PACS Servers

1. Navigate to the PACS Management page
2. Add, edit, or remove PACS configurations
3. Test connectivity
4. View server status

## HL7 ORM Message Format

The application expects HL7 ORM (Order Entry) messages. Key fields:

- **Patient Information**: PID segment
- **Order Information**: OBR segment
- **Accession Number**: OBR-3 (Filler Order Number)
- **Study Description**: OBR-4 (Universal Service ID)

## 🔒 Security Notes

- This tool generates **synthetic data only** - no real patient information
- All generated DICOM files contain fictional data
- PACS credentials and configurations are stored locally
- No data is transmitted to external services

## 🤝 Contributing

### Git Workflow

This project follows a structured Git branching strategy:

- **`main`** - Production-ready code, stable releases
- **`develop`** - Integration branch for features, main development work
- **`feature/*`** - Feature branches for individual development work

#### For New Features:

1. **Start from develop:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Work on your feature:**
   - Make commits with clear, descriptive messages
   - Update CHANGELOG.md for significant changes
   - Keep commits atomic and focused

3. **Complete and merge:**
   ```bash
   git checkout develop
   git merge feature/your-feature-name
   git push origin develop
   ```

For detailed workflow information, see [Git Workflow Documentation](docs/GIT_WORKFLOW.md).

#### General Contributing Guidelines:

1. Fork the repository
2. Create a feature branch from develop
3. Make your changes
4. Add tests if applicable
5. Update CHANGELOG.md
6. Submit a pull request to develop

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for **educational and testing purposes only**. It generates synthetic DICOM data and should not be used in production healthcare environments. Always ensure compliance with local healthcare regulations and data protection laws.

## 🆘 Support

For issues and questions:
- Check the [documentation](docs/)
- Review existing [issues](https://github.com/flatmapit/dicom-fabricator/issues)
- Create a new issue with detailed information

## 🔗 Related Projects

- [Orthanc](https://www.orthanc-server.com/) - Open-source PACS server
- [DCMTK](https://dcmtk.org/) - DICOM toolkit
- [pydicom](https://pydicom.github.io/) - Python DICOM library