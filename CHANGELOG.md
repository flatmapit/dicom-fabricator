# Changelog

All notable changes to DICOM Fabricator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.2] - 2025-09-03

### 🐛 Bug Fix Release

#### Environment Filter Fixes
- **C-MOVE Modal**: Fixed "Prod" filter not showing production PACS due to environment value mismatch
- **PACS Query Interface**: Corrected environment filter values from 'production' to 'prod'
- **PACS Management**: Fixed environment dropdown and color coding consistency
- **Study Operations**: Updated environment filter values for proper filtering

#### C-MOVE Configuration
- **Complete Routing Matrix**: Configured C-MOVE routing between all 4 PACS (2 test, 2 prod)
- **AE Title Management**: Proper C-MOVE AE titles configured for inter-PACS communication
- **Configuration Reload**: Added runtime configuration reload capability

#### Documentation & Media
- **Demo Video**: Uploaded DICOM Fabricator demo video to S3 for public access
- **CLAUDE.md**: Enhanced with detailed file structure and API documentation
- **Authentication Docs**: Updated with comprehensive RBAC and permission information


## [1.2.1] - 2025-09-03

### 🐛 Bug Fix Release

#### Recent Changes
- **Version Bump**: Automated version bump to 1.2.1
- **Change Summary**: This release includes recent improvements and bug fixes


## [1.2.0] - 2025-09-03

### ✨ Feature Release

#### Recent Changes
- **Version Bump**: Automated version bump to 1.2.0
- **Change Summary**: This release includes recent improvements and bug fixes


## [1.3.0] - 2025-01-XX

### Enhanced PACS AE Management Release

#### PACS Configuration Enhancement
- **Separate AE Titles**: Implemented separate Application Entity Titles for different DICOM operations
  - **C-FIND AET**: Dedicated AE for querying studies from PACS
  - **C-STORE AET**: Dedicated AE for sending studies to PACS (optional - can be disabled)
  - **C-ECHO AET**: Dedicated AE for connection testing
- **C-MOVE Routing Table**: Configurable routing table for C-MOVE operations between PACS servers
- **Enhanced PACS Manager**: Updated PACS configuration management with new AE fields and routing support
- **Migration Support**: Automatic migration script for existing PACS configurations

#### User Interface Improvements
- **Enhanced PACS Management UI**: Updated interface with separate AE fields and routing table management
- **C-MOVE Routing Interface**: New modal for configuring C-MOVE routing between PACS servers
- **Improved Table Display**: Updated PACS configuration table to show all AE types
- **Routing Table Editor**: Interactive interface for configuring C-MOVE routing with visual status indicators

#### API Enhancements
- **New API Endpoints**: Added endpoints for C-STORE enabled PACS and routing table management
- **Enhanced C-MOVE Operations**: Updated C-MOVE operations to use proper routing table
- **C-STORE Filtering**: PACS without C-STORE AE are filtered from send operations
- **Routing Table API**: RESTful API for managing C-MOVE routing configurations

#### Documentation Updates
- **Setup Instructions**: Updated PACS setup documentation for new AE model
- **Configuration Guide**: Enhanced configuration documentation with AE field explanations
- **Migration Guide**: Documentation for migrating from old to new configuration structure

#### Technical Improvements
- **Backward Compatibility**: Clean migration path from old single-AE model
- **Error Handling**: Improved error messages for missing C-MOVE routing configurations
- **Validation**: Enhanced validation for AE title configurations
- **Default Configurations**: Updated default PACS configurations with new naming scheme

## [1.2.0] - 2025-09-01

### Authentication & Authorization Release

#### Authentication System
- **Local Authentication**: Username/password authentication with configurable enable/disable
- **Enterprise Integration**: Active Directory (AD) and SAML 2.0 support for enterprise environments
- **Role-Based Access Control**: Granular permissions for test/production environments
- **User Management Interface**: Complete user administration with create, edit, delete operations
- **Session Management**: Secure session handling with configurable authentication modes
- **Password Security**: SHA-256 password hashing with secure user management

#### Environment-Specific Permissions
- **Test Environment Access**: Separate permissions for test PACS operations
- **Production Environment Access**: Separate permissions for production PACS operations
- **Read/Write Permissions**: Granular control over query, move, configure, and test operations
- **Admin Access**: System administrator role with full permissions
- **Permission Categories**: System, DICOM, PACS (Test/Prod), and Patient Management permissions

#### PACS Configuration Improvements
- **Consistent Naming Scheme**: Standardized PACS names (Test PACS 1/2/3, Prod PACS 1/2)
- **Footer Stats Accuracy**: Fixed footer to show actual successful PACS connections vs. total configs
- **Multi-PACS Support**: Enhanced support for multiple test and production PACS servers
- **Environment Filtering**: Test/Production environment filtering in PACS selection
- **Color-Coded PACS**: Visual distinction between test (green) and production (purple) PACS

#### User Interface Enhancements
- **User Management Page**: Complete user administration interface with statistics
- **Authentication Status**: User dropdown with role and permission display
- **Login/Logout Flow**: Secure authentication flow with proper redirection
- **Bootstrap Dropdown Fix**: Fixed dropdown functionality across all pages
- **Security Headers**: Added X-Frame-Options, X-Content-Type-Options, and X-XSS-Protection headers

#### Security Improvements
- **Sensitive Data Protection**: Updated .gitignore to exclude user data and auth configs
- **Session Security**: Secure session management with proper authentication checks
- **Route Protection**: All main pages and API endpoints protected with authentication
- **Enterprise Security**: Support for enterprise authentication systems (AD/SAML)

## [1.1.0] - 2025-09-01

### Feature Release

#### Recent Changes
- **Version Bump**: Automated version bump to 1.1.0
- **UID Copy Functionality**: Added copy-to-clipboard buttons for Study UIDs and Series UIDs throughout the interface
- **Documentation Enhancement**: Added comprehensive screenshot documentation covering all major application features
- **Change Summary**: This release includes recent improvements and bug fixes


## [1.0.2] - 2025-09-01

### Bug Fix Release

#### Recent Changes
- **Version Bump**: Automated version bump to 1.0.2
- **Time Formatting**: Improved PACS query time display from decimal format (073242.076) to readable 24-hour format (07:32:42)
- **UID Copy Functionality**: Added copy-to-clipboard buttons for Study UIDs and Series UIDs throughout the interface
- **Change Summary**: This release includes recent improvements and bug fixes


## [1.0.1] - 2025-01-XX

### Documentation Enhancement

#### Visual Documentation Framework
- **Feature Overview Document**: Created comprehensive visual feature overview with screenshot placeholders
- **Screenshot Directory**: Established organized structure for application screenshots
- **README Enhancement**: Added main dashboard screenshot placeholder and feature overview link
- **Documentation Guidelines**: Created screenshot capture guidelines and requirements
- **Issue Tracking**: Created GitHub issue #1 for tracking visual documentation progress

#### DICOM Tag Display Improvements
- **Tag ID Sorting**: Modified DICOM tag display to sort by tag ID (group, element) instead of alphabetically
- **Backend Sorting**: Updated `/api/dicom/headers/<filename>` endpoint to sort tags by group and element
- **Frontend Sorting**: Updated JavaScript to sort DICOM tags by tag ID for consistent display
- **Enhanced Readability**: Tags now display in logical DICOM order (0008, 0010, 0020, etc.)

#### Git Workflow Setup

#### Development Infrastructure
- **Git Flow Branching Strategy**: Implemented proper branching workflow with main, develop, and feature branches
- **Develop Branch**: Created integration branch for feature development
- **Feature Branch Workflow**: Established process for creating feature branches from develop
- **Git Workflow Documentation**: Comprehensive documentation of branching strategy and workflow
- **README Updates**: Added Git workflow section to main documentation

#### Branch Structure
- **`main`** - Production-ready code, stable releases
- **`develop`** - Integration branch for features, main development work  
- **`feature/*`** - Feature branches for individual development work

## [1.0.0] - 2025-08-29

### Initial Public Release

The first public open-source release of DICOM Fabricator - a complete Flask web application for generating synthetic DICOM studies for testing clinical radiology integrations.

### Features Added

#### Core DICOM Generation
- **Multi-Series DICOM Studies**: Generate 1-9 series with 1-10 configurable images per series
- **DX (Digital Radiography) Support**: Complete DICOM DX study generation with proper metadata
- **Visual DICOM Images**: 512x512 grayscale images with embedded metadata text and geometric symbols  
- **Folder Structure Organization**: Studies organized as `StudyUID/SeriesXXX_ProcedureCode/images`
- **DICOM Tag Display**: All major DICOM tags visible in images with tag IDs (e.g., "(0010,0010) Patient Name")

#### HL7 ORM Integration
- **Complete ORM Parser**: Parse MSH, PID, ORC, and OBR segments from HL7 ORM messages
- **Study Date Extraction**: Automatic extraction from OBR-7 (Observation Date/Time) field
- **Patient Demographics**: Extract patient name, ID, birth date, sex from PID segments
- **Series Descriptions**: Extract and edit series descriptions from OBR segments
- **Tabbed Generation Interface**: Dual workflow with "Manual Entry" and "Create study for ORM" tabs

#### Modern Web Interface  
- **Bootstrap 5 UI**: Responsive design with modern modal-based workflows
- **Patient Management**: Live search, bulk operations, click-to-edit functionality
- **Study Management**: Clickable table rows, bulk delete operations, comprehensive study details
- **Real-time Status**: PACS connectivity indicators and automatic testing
- **Custom Table Sorting**: Clickable headers with visual sort indicators

#### Advanced PACS Integration
- **Multi-PACS Support**: Configure and manage multiple PACS servers with full CRUD operations
- **DICOM Operations**: Complete C-STORE, C-FIND, and C-MOVE support
- **Advanced Querying**: Multi-criteria search (patient name, ID, accession, UIDs, date ranges)
- **Command Logging**: Real-time logging of all DICOM operations with full command details
- **Connection Testing**: Automatic echoscu testing of all configured PACS servers
- **C-MOVE Operations**: Transfer studies between PACS servers with smart destination selection

#### Data Management
- **Synthetic Patient Registry**: Persistent JSON-based patient database with Australian localization
- **PACS Configuration**: Persistent JSON-based PACS server configurations with test results
- **Sample Data**: Included sample configurations for easy setup
- **Safety Features**: All generated data clearly marked as "TEST DATA" - no real PHI/PII

#### Web Pages & API
- **Home (Query PACS)**: Search and query existing PACS servers with comprehensive results
- **Patients Page**: Manage synthetic patient database with live search and bulk operations
- **Generator Page**: Create DICOM studies with manual entry or HL7 ORM workflows
- **PACS Page**: Configure and test PACS server connections with real-time status
- **RESTful API**: Complete API with CORS support for all operations

### Technical Infrastructure

#### Backend Components
- **Flask Web Application**: Complete RESTful API with comprehensive endpoints
- **DICOM Engine**: Core DICOM file generation with pydicom integration
- **HL7 Parser**: Built-in parser for HL7 ORM message processing  
- **Patient Registry System**: Realistic synthetic patient data generation
- **PACS Configuration Manager**: Multi-PACS server management with testing

#### Optional PACS Servers
- **Primary Orthanc PACS**: Test server on ports 4242/8042 (test/test123)
- **Secondary Orthanc PACS**: Additional test server on ports 4243/8043 (test2/test456)
- **Docker Compose**: Easy PACS server deployment with persistent data volumes

#### Documentation & Legal
- **Comprehensive README**: Complete setup and usage instructions
- **MIT License**: Open source license for commercial and personal use
- **Third-Party Licenses**: Full documentation of all dependency licenses
- **API Documentation**: Complete endpoint documentation in CLAUDE.md

### Requirements
- Python 3.11+
- Modern web browser for interface
- Optional: Docker & Docker Compose for test PACS servers
- Optional: DCMTK tools for advanced DICOM operations

### 📁 Project Structure
```
DICOM_Fabricator/
├── app.py                          # Main Flask application
├── src/                           # Core Python modules
│   ├── dicom_fabricator.py       # DICOM generation engine
│   ├── patient_config.py         # Patient data management  
│   ├── pacs_config.py            # PACS configuration management
│   └── ...
├── templates/                     # HTML templates with Bootstrap 5
├── static/                       # CSS/JS assets
├── config/                       # Configuration files
├── data/                         # Runtime data and samples
├── docker/                       # PACS server configuration
└── docs/                         # Additional documentation
```

### 🎯 Use Cases
- PACS integration testing and validation
- DICOM viewer application development
- HL7 workflow testing and validation  
- Clinical system integration testing
- Educational and training purposes
- Quality assurance for system upgrades

### Safety & Legal
- All patient data is synthetic - no real PHI/PII
- Generated files clearly marked as "TEST DATA"
- Not for use in clinical environments
- Educational and testing purposes only
- MIT License for open source distribution

---

**🚀 Ready for Production Testing Environments!**

This release provides a complete, production-ready solution for generating synthetic DICOM data for testing clinical radiology integrations without any real patient information.