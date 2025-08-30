# Changelog

All notable changes to DICOM Fabricator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### 🛠️ Technical Infrastructure

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

### 🔧 Requirements
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

### ⚠️ Safety & Legal
- All patient data is synthetic - no real PHI/PII
- Generated files clearly marked as "TEST DATA"
- Not for use in clinical environments
- Educational and testing purposes only
- MIT License for open source distribution

---

**🚀 Ready for Production Testing Environments!**

This release provides a complete, production-ready solution for generating synthetic DICOM data for testing clinical radiology integrations without any real patient information.