# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DICOM Fabricator is a Flask web application for generating synthetic DICOM studies for testing clinical radiology integrations without PHI/PII. It creates fake medical imaging data with embedded metadata for testing PACS servers, DICOM viewers, and clinical system integrations. The web interface includes comprehensive PACS configuration management with multi-criteria querying capabilities and role-based access control.

Copyright (c) 2025 Christopher Gentle <chris@flatmapit.com>

## Key Commands

### Web Application (Primary Interface)

```bash
# Install dependencies
pip3 install -r config/requirements.txt

# Start Flask web application
python3 app.py                                           # Runs on http://localhost:5001

# Alternative: Run on different port if 5001 is in use
# Edit app.py and change port in: app.run(debug=True, host='0.0.0.0', port=5002)
```

**Web Interface Features:**
- **Authentication & Authorization**: Role-based access control with admin, test_write, test_read, prod_write, prod_read roles
- **Patient Management**: Live searchable interface, click-to-edit patients, bulk delete with checkboxes
- **Multi-Series DICOM Generator**: Modal-based generation interface with up to 9 series, each with 1-10 images
- **HL7 ORM Integration**: Complete ORM message parser with tabbed generation interface (Manual + ORM tabs)
- **Study Date Support**: Extract study dates from OBR-7 field and use in DICOM generation
- **Study Management**: Bulk delete operations with checkboxes, modal-based study details viewer
- **Modal-Based UI**: Generation parameters and study details in pop-over modals
- **DICOM Headers Export**: Comprehensive DICOM tag display with standard names and copyable text format
- **Comprehensive PACS Management**: Full CRUD operations for PACS configurations (admin only)
- **Advanced PACS Querying**: Multi-criteria search (name, ID, accession, UIDs, date ranges)
- **C-MOVE Support**: Transfer studies between PACS servers with proper routing configuration
- **DICOM Command Logging**: Real-time logging of C-STORE/C-FIND/C-MOVE operations with command details
- **Environment-Based Access**: Separate permissions for test and production PACS environments
- **PACS Query Status Notes**: Visual indicators showing whether studies exist on selected PACS
- **Automatic PACS Testing**: Auto-test all PACS configurations based on user activity
- **Australian Localization**: Patient addresses and phone numbers in Australian format
- **Custom Table Sorting**: Clickable headers with visual sort indicators
- **Footer Statistics**: Real-time PACS status display with connection health indicators

### Command Line Tools (Legacy)

```bash
# Generate DICOM studies via CLI
python3 src/dicom_fabricator.py                          # Generate with random data
python3 src/dicom_fabricator.py -n "DOE^JANE" -p "PID123" -a "ACC001"  # Custom parameters
python3 src/dicom_fabricator.py --count 5                # Generate multiple studies

# View generated DICOM files via CLI
python3 src/view_dicom.py --list                         # List available files
python3 src/view_dicom.py dicom_output/filename.dcm      # View specific file

# Manage patient database via CLI
python3 src/patient_manager.py --list                    # List all patients
python3 src/patient_manager.py --add                     # Add new patient interactively
python3 src/patient_manager.py --search "DOE"            # Search patients
```

### PACS Server Operations

```bash
# Start/stop PACS server (requires Docker)
./start_pacs.sh                                          # Start Orthanc PACS server
cd docker && docker-compose down                         # Stop PACS server

# Send DICOM to PACS
storescu -aet DICOMFAB -aec TESTPACS localhost 4242 dicom_output/*.dcm
```

## Architecture

### Project Structure

#### Web Application
- **app.py** - Flask application with API endpoints and web routes
- **templates/** - HTML templates with modal-based interface
  - `base.html` - Base template with navigation and footer
  - `index.html` - Dashboard redirect to query_pacs.html
  - `login.html` - Authentication login page
  - `patients.html` - Patient management with live search and bulk operations
  - `generator.html` - Modal-based DICOM generation and study management interface
  - `pacs.html` - Comprehensive PACS management and querying interface
  - `query_pacs.html` - Main PACS query interface (home page)
  - `users.html` - User management interface (admin only)
  - `viewer.html` - Legacy DICOM viewer page (deprecated)
- **static/** - Frontend assets
  - `css/style.css` - Custom styling
  - `js/app.js` - JavaScript utilities and API wrapper
  - `js/user-management.js` - User management functionality

#### Core Modules
- **src/** - Backend Python modules
  - `auth.py` - Authentication and authorization with role-based access control
  - `dicom_fabricator.py` - Main DICOM generation logic, creates synthetic DICOM files with embedded text/shapes
  - `enterprise_auth.py` - Enterprise authentication integration (AD/SAML)
  - `group_mapper.py` - AD group to role mapping functionality
  - `patient_config.py` - Patient data models and registry management
  - `pacs_config.py` - PACS configuration management with CRUD operations and testing
  - `patient_manager.py` - CLI for managing patient database
  - `view_dicom.py` - DICOM viewer utility for reviewing generated files

#### Configuration & Data
- **test-pacs/docker/** - Test PACS server configurations
  - `docker-compose.yml` - Multi-PACS Orthanc setup
  - `orthanc-config.json` - TESTPACS1 configuration
  - `orthanc-config-2.json` - TESTPACS2 configuration
  - `orthanc-prod-config.json` - PRODPACS1 configuration
  - `orthanc-prod-config-2.json` - PRODPACS2 configuration
- **config/** - Configuration files
  - `patient_config.json` - Patient configuration patterns and defaults
  - `requirements.txt` - Python dependencies
  - `auth_config.json` - Authentication settings (created at runtime)
  - `users.json` - User database (created at runtime)
  - `group_mappings.json` - AD group mappings (optional)
- **data/** - Runtime data
  - `patient_registry.json` - Persistent patient database
  - `pacs_config.json` - PACS configurations with connection test results
- **dicom_output/** - Generated DICOM files (created at runtime)
- **docs/** - Documentation
  - `AUTHENTICATION_SETUP.md` - Auth configuration guide
  - `PERMISSIONS_TO_FEATURES.md` - Feature-role mapping matrix
  - `C-MOVE_TROUBLESHOOTING.md` - PACS operation debugging
  - `feature_overview.md` - Visual feature guide

### Key Components

**Flask Web Application** (app.py)
- RESTful API endpoints for all operations
- Modal-based UI for generation and study details
- Live patient search with click-to-edit functionality
- Bulk operations with select-for-delete checkboxes
- DICOM headers API with comprehensive tag extraction
- Real-time PACS status monitoring and async progress tracking
- Comprehensive PACS configuration management (CRUD)
- Advanced DICOM querying with multiple search criteria
- CORS-enabled for API access

**Custom Table Management**
- Custom JavaScript sorting implementation (replaced tosijs)
- Clickable headers with visual sort indicators
- Select-all checkbox functionality with indeterminate states
- Responsive table layouts with search filtering
- Default sorting by newest files first

**DICOMFabricator Class** (src/dicom_fabricator.py)
- Generates synthetic DICOM DX (Digital Radiography) studies
- Creates 512x512 monochrome images with embedded metadata text
- Supports configurable accession number patterns
- Integrates with PatientRegistry for consistent patient data

**PatientRegistry System** (src/patient_config.py)
- Manages persistent patient database in data/patient_registry.json
- Supports creation, retrieval, and search of patient records
- Generates realistic synthetic patient data (names, MRNs, demographics)
- Configuration loaded from config/patient_config.json

**Image Generation**
- Creates 512x512 grayscale images with text overlay showing all DICOM metadata
- Includes geometric shapes, letters, and numbers at bottom of image
- Comprehensive text wrapping for long metadata and descriptions
- Multi-line title and disclaimer text for clinical safety
- DICOM tag IDs displayed with metadata (e.g., "(0010,0010) Patient Name")
- Footer branding with "DICOM Fabricator - flatmapit.com"
- All metadata visible directly in the image for easy debugging
- Base64 encoding for web display
- Shape descriptions appended to study description (e.g., "Test Study - Image: circle, A, 5")

### API Endpoints

#### Web Pages
- `GET /` - Home dashboard (redirects to query_pacs.html)
- `GET /login` - Authentication login page
- `GET /logout` - Logout and session cleanup
- `GET /patients` - Patient management page with live search and edit capabilities
- `GET /generator` - DICOM generation page with modal-based interface
- `GET /pacs` - PACS management and querying interface
- `GET /query-pacs` - Main PACS query interface
- `GET /users` - User management interface (admin only)

#### Authentication & User Management
- `POST /login` - Authenticate user with username/password
- `GET /api/users` - List all users (admin only)
- `POST /api/users` - Create new user (admin only)
- `PUT /api/users/<username>` - Update user (admin only)
- `DELETE /api/users/<username>` - Delete user (admin only)

#### Patient Management
- `GET /api/patients` - List all patients
- `POST /api/patients` - Create patient
- `PUT /api/patients/<id>` - Update patient
- `DELETE /api/patients/<id>` - Delete patient
- `POST /api/patients/batch-delete` - Bulk delete patients
- `POST /api/patients/search` - Search patients
- `GET /api/patients/export/csv` - Export patients to CSV

#### DICOM Generation & Files
- `POST /api/generate` - Generate multi-series DICOM studies (1-9 series) with study_date support
- `POST /api/parse-orm` - Parse HL7 ORM messages for automated DICOM generation
- `GET /api/dicom/list` - List DICOM files
- `GET /api/dicom/studies` - List DICOM studies (grouped by StudyInstanceUID)
- `GET /api/dicom/view/<filename>` - View DICOM details with metadata
- `GET /api/dicom/headers/<filename>` - Get comprehensive DICOM headers
- `GET /api/dicom/download/<filename>` - Download file
- `DELETE /api/dicom/delete/<filename>` - Delete file
- `POST /api/dicom/studies/delete` - Bulk delete studies
- `GET /api/dicom/export/csv` - Export DICOM files to CSV

#### PACS Management
- `GET /api/pacs/status` - PACS server status using default config
- `GET /api/pacs/configs` - List all PACS configurations
- `POST /api/pacs/configs` - Create PACS configuration
- `GET /api/pacs/configs/<id>` - Get specific PACS configuration
- `PUT /api/pacs/configs/<id>` - Update PACS configuration
- `DELETE /api/pacs/configs/<id>` - Delete PACS configuration
- `POST /api/pacs/configs/<id>/test` - Test PACS connection
- `GET /api/pacs/stats` - Get PACS configuration statistics

#### PACS Operations
- `POST /api/pacs/send-study` - Send study to PACS with progress tracking and command logging
- `POST /api/pacs/query-study` - Query specific study on PACS with command logging
- `POST /api/pacs/query` - Comprehensive PACS query with multiple criteria
- `POST /api/pacs/c-move` - Perform C-MOVE operation to transfer studies between PACS servers

### PACS Integration

**Test PACS Servers (Docker)**
- **TESTPACS1**: Port 4242 (DICOM), 8042 (HTTP), credentials: test/test123
- **TESTPACS2**: Port 4243 (DICOM), 8043 (HTTP), credentials: test2/test456
- **PRODPACS1**: Port 4245 (DICOM), 8045 (HTTP), credentials: prod1/prod123
- **PRODPACS2**: Port 4246 (DICOM), 8046 (HTTP), credentials: prod2/prod456
- All support C-STORE, C-FIND, C-MOVE operations
- Simplified DicomModalities configuration for inter-PACS communication
- Started with `docker compose up` in test-pacs/docker directory

**PACS Configuration Management**
- Dynamic PACS configurations stored in data/pacs_config.json
- Default configurations: Orthanc Test PACS, Test PACS, and Orthanc Test PACS 2
- Automatic connectivity testing with echoscu on page load
- Real-time status updates and connection validation
- Support for multiple PACS servers with different AE titles

**Advanced PACS Querying**
- Multi-criteria search: Patient Name, Patient ID, Accession Number, Study UID, Series UID
- Date range filtering: 1 day to 365 days ago
- DICOM C-FIND protocol using findscu
- Wildcard support (*) for partial matching
- Clickable results table rows for study details (no separate action buttons needed)
- CSV export functionality with timestamped files
- C-MOVE functionality for transferring studies between PACS servers

**DICOM Command Logging**
- Real-time logging of all DICOM operations (C-STORE, C-FIND, and C-MOVE commands)
- Command details: Full command executed with parameters
- PACS information: Server name, host, port, AET/AEC details  
- Output capture: Complete stdout/stderr from DICOM tools
- Exit codes and success/failure status tracking
- Auto-scrolling log panel with timestamped entries
- Available in Generator page PACS modal and PACS management page
- Clear log functionality for session management
- Enhanced debugging and operation transparency

## Authentication & Authorization

**Role-Based Access Control:**
- **admin**: Full system access, user management, PACS configuration
- **test_write**: Test PACS write access (C-STORE, C-MOVE, C-FIND)
- **test_read**: Test PACS read-only access (C-FIND only)
- **prod_write**: Production PACS write access (C-STORE, C-MOVE, C-FIND)
- **prod_read**: Production PACS read-only access (C-FIND only)

**Default Credentials:**
- Username: `admin`
- Password: `admin123`
- Change immediately after first login!

**Permission Documentation:**
- See `docs/PERMISSIONS_TO_FEATURES.md` for complete feature-to-role mapping
- See `docs/AUTHENTICATION_SETUP.md` for configuration guide

## Important Notes

- Flask app runs on port 5001 by default (change in app.py if needed)
- Web interface accessible at http://localhost:5001
- All generated data is synthetic - no real patient information
- Generated files are clearly marked as test data in metadata
- Default output directory is ./dicom_output/
- Patient registry persisted in data/patient_registry.json
- PACS configurations persisted in data/pacs_config.json
- User database persisted in config/users.json
- DCMTK tools (storescu, echoscu, findscu, movescu) required for PACS operations
- Bootstrap 5.1.3 and Font Awesome 6.0 for UI components
- Automatic PACS testing runs based on user activity (active: every 30s, inactive: every 5 min)
- All tooltips added for accessibility and user guidance
- Push after any change of more than 10 lines

## Recent Major Features Added

### Authentication & Authorization System (2025-01)
- **Role-Based Access Control**: Five roles with environment-specific permissions
- **User Management**: Admin-only user creation, editing, and deletion
- **Environment Isolation**: Separate permissions for test and production PACS
- **Session Management**: Secure login/logout with session persistence
- **Permission Documentation**: Comprehensive feature-to-role mapping matrix

### HL7 ORM Integration & Multi-Series Generation
- **HL7 ORM Message Parser**: Complete parser for MSH, PID, ORC, and OBR segments
- **Tabbed Generation Interface**: Two-tab modal with "Enter Study Data" and "Create study for ORM"
- **Study Date Extraction**: Automatic extraction from OBR-7 (Observation Date/Time) field
- **Series Description Support**: Extract and edit series descriptions from OBR segments
- **Multi-Series DICOM Studies**: Generate 1-9 series with configurable images per series (1-10)
- **Folder Structure Organization**: StudyUID/SeriesXXX_ProcedureCode/ directory structure
- **Fixed Series Descriptions**: Resolved "undefined" series descriptions in study details
- **Fixed Manual Form Generation**: Corrected JavaScript element ID references for manual form tab
- **Improved Footer Layout**: Changed from floating overlay to bottom-positioned footer (no longer obscures tables)

### C-MOVE Implementation & Image Generation Improvements
- **C-MOVE Functionality**: Complete DICOM C-MOVE implementation for transferring studies between PACS servers
- **Smart PACS Selection**: C-MOVE dialog excludes source PACS from destination options
- **Clickable Query Results**: Table rows clickable for study details, removed separate action buttons
- **Enhanced Image Generation**: Added DICOM tag IDs to metadata display (e.g., "(0010,0010) Patient Name")
- **Updated Disclaimer Text**: Improved clarity about PACS modifications to DICOM tags
- **Footer Branding**: Added "DICOM Fabricator - flatmapit.com" footer to generated images
- **C-MOVE Command Logging**: Full integration with DICOM Command Log for transfer operations
- **Modal-Based C-MOVE**: Intuitive workflow from study details → PACS selection → execution

### PACS Query Enhancements & UI Improvements
- **Removed Incorrect Study Alert**: Removed misleading "Study NOT found" alert that was incorrectly triggered
- **Custom Table Sorting**: Replaced failing tosijs CDN with custom JavaScript sorting implementation
- **Enhanced Visual Feedback**: Added sort indicators (⇅, ↑, ↓) and hover effects for table headers
- **Enhanced PACS Command Logging**: Smaller, more readable font for DICOM Command Log with better spacing
- **Fixed findscu Command Syntax**: Corrected study/series query commands with proper -S flag usage
- **Improved Study Detection**: Enhanced parsing to check for DICOM tag presence rather than exit codes
- **Comprehensive Series Information**: Detailed series display with UIDs, procedure codes, and image counts
- **Auto-Query Series Details**: Automatic series querying with command log output for debugging
- **Study Information Popup**: Modal dialog with comprehensive study, patient, and series details
- **Button Text Updates**: Changed "Send Study to PACS" to "Send or Query For Study on PACS"
- **Enhanced Layout**: Improved horizontal space utilization across all pages with responsive breakpoints
- **Unified Study Details**: Consistent display function for generated DICOM and table row clicks
- **Full Command Visibility**: Show complete findscu commands without truncation for better debugging

### Enhanced Study Generator & UI Improvements
- **Query PACS as Home Page**: Main landing page now shows PACS querying interface
- **Study Generator Enhancements**: Renamed from "DICOM Generator", improved UI and functionality
- **Clickable Study Table**: Click any study row to view detailed information in Details panel
- **Study Details View**: Comprehensive study information with files, series, and metadata
- **Improved Footer**: Semi-transparent floating footer with PACS/patient/study statistics
- **File Loading Fixes**: Proper handling of files in nested series folders with full path resolution
- **Removed Progress Monitoring**: Cleaned up disconnected progress UI components
- **Search Functionality**: Live search across studies table with real-time filtering
- **Tabbed File Interface**: tosijs-style tabs for viewing individual study files
- **Full Study UID Display**: Fixed truncated Study UID display with proper text wrapping

### Comprehensive PACS Management
- **Full CRUD Operations**: Create, Read, Update, Delete PACS configurations
- **Automatic Testing**: Auto-test all PACS on page load with status indicators
- **Multi-Criteria Querying**: Search by patient name, ID, accession, UIDs, date ranges
- **Advanced Results**: Sortable tables with CSV export and comprehensive metadata
- **Dynamic Configuration**: All PACS operations use configurable endpoints
- **Professional UI**: Enhanced tooltips, proper navigation, optimized table layouts

### Recent Improvements (2025-01)
- **Authentication System**: Complete role-based access control implementation
- **PACS Configuration Simplification**: Streamlined DicomModalities to use direct AE titles
- **C-MOVE Troubleshooting**: Comprehensive documentation for C-FIND and C-MOVE issues
- **Footer Statistics**: Real-time PACS health monitoring with down server indicators
- **Permission Documentation**: Complete feature-to-role mapping matrix
- **Custom Table Sorting**: Replaced tosijs with custom JavaScript sorting implementation
- **License Modal**: MIT License popup accessible from footer
- **Test Data Cleanup**: Removed all test DICOM files and Orthanc data from repository

## Troubleshooting

- **C-FIND Errors**: Use `-S` flag for STUDY queries, `-P` for PATIENT queries
- **C-MOVE Failures**: Check DicomModalities configuration uses container names not localhost
- **Authentication Issues**: Default admin/admin123, change immediately after first login
- **Permission Denied**: Check user role has required environment access (test/prod, read/write)
- See `docs/C-MOVE_TROUBLESHOOTING.md` for detailed PACS operation debugging

## Licensing & Legal
- **License**: MIT License (see LICENSE file)
- **Copyright**: Christopher Gentle <chris@flatmapit.com>
- **Third-Party Dependencies**: All documented in THIRD-PARTY-LICENSES.md
- **License Compatibility**: All dependencies use permissive licenses (MIT, BSD, CC BY)
- **No Copyleft**: No GPL or other restrictive licenses that would affect commercial use