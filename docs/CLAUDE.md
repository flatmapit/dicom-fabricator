# Project Specification

## Project Overview
**Project Name:** DICOM Fabricator
**Version:** 1.0.0
**Date:** 2025-08-23
**Author:** Chris Gentle chris@flatmapit.com

## Problem Statement

I want a desktop UI application/web app written in python that can generate and send DICOM (and query to verify that the DICOM was received).

For testing clinical radiology integrations it is important to be able to create and send fake DICOM studies that do not have PII or PHI. 

The DICOM should contain metadata and images that are simple text.

Names, addresses, can be fixed or generated.
Instance UIDs should be generated to be realistic.
Accessions should be able to be generated from configurable rules (e.g. generate accessions with YYYY{two letters}{seven digits starting from 0000001})
The number of images in a series and the number of series in a study should be configurable.
I should be able to review the metadata and images used in the generated dicom.
The generated dicom should contain text with the UIDs, accessions and fake patient names


## Goals & Objectives
### Primary Goals
- [ ] Create DICOM studies and series with options for a variety of different modalities and sizes
- [ ] I should be able to generate a typical x-ray dicom series and send them, and check they're in PACS with very little input


### Success Metrics
- Is the code simple and easy to maintain
- Can it be run on a local PC without admin access


## Scope
### In Scope
- Create and send 
- [Core features included]

### Out of Scope
- [What this project WON'T do]
- [Features excluded from this phase]

## Users & Stakeholders
### Primary Users
- **User Type 1:** Clinical systems integrator 


### Stakeholders
- **Stakeholder 1:** Integration 
- **Stakeholder 2:** [Role and interest]

## Requirements
### Functional Requirements
1. **[Feature Name]**
   - Description: [What it does]
   - Priority: [High/Medium/Low]
   - Acceptance Criteria: [How to verify it works]

2. **[Feature Name]**
   - Description: [What it does]
   - Priority: [High/Medium/Low]
   - Acceptance Criteria: [How to verify it works]

### Non-Functional Requirements
- **Performance:** [Response time, throughput needs]
- **Security:** [Authentication, authorization, data protection]
- **Scalability:** [Expected load, growth projections]
- **Usability:** [User experience requirements]
- **Reliability:** [Uptime requirements, error handling]

## Technical Architecture
### Technology Stack
- **Frontend:** [Framework/libraries]
- **Backend:** [Language/framework]
- **Database:** [Type and system]
- **Infrastructure:** [Hosting/deployment]

### System Architecture
[Describe the high-level architecture - monolith, microservices, etc.]

### Integration Points
- **External System 1:** [How it connects]
- **External System 2:** [How it connects]

## Constraints & Assumptions
### Constraints
- **Budget:** [Financial limitations]
- **Timeline:** [Deadlines and milestones]
- **Technical:** [Platform/technology limitations]
- **Regulatory:** [Compliance requirements]

### Assumptions
- [Assumption about users, systems, or environment]
- [Dependencies on other systems or teams]

## Risks & Mitigation
| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|-------------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [How to handle] |
| [Risk 2] | High/Med/Low | High/Med/Low | [How to handle] |

## Development Approach
### Methodology
[Agile/Waterfall/Hybrid - and why]

### Phases
1. **Phase 1:** [Name] - [Timeline]
   - Deliverables: [What will be completed]
2. **Phase 2:** [Name] - [Timeline]
   - Deliverables: [What will be completed]

### Testing Strategy
- **Unit Testing:** [Approach and coverage goals]
- **Integration Testing:** [What to test]
- **User Acceptance Testing:** [How and when]

## Commands & Scripts
### Development
```bash
# Install dependencies
pip3 install -r config/requirements.txt

# Generate a DICOM with default settings
python3 dicom_fabricator.py

# Generate DICOM with specific patient
python3 dicom_fabricator.py --patient-id PID100000

# Generate patient only
python3 dicom_fabricator.py --generate-patient

# View DICOM file
python3 view_dicom.py <dicom-file>
```

### Patient Management
```bash
# List all patients
python3 patient_manager.py list

# Generate new patient
python3 patient_manager.py generate

# Generate patient with custom name
python3 patient_manager.py generate --name "LAST^FIRST"

# Show patient details
python3 patient_manager.py show <patient-id>

# Search patients
python3 patient_manager.py search <query>

# Show statistics
python3 patient_manager.py stats

# Test ID generation patterns
python3 patient_manager.py test-ids --count 5

# View current configuration
python3 patient_manager.py config

# Load configuration from file
python3 patient_manager.py load-config <config-file>
```

### Configuration Examples
```bash
# Patient ID Patterns:
# {6letters} -> ABCDEF (6 random uppercase letters)
# {7digits} -> 0000100 (7 digits starting from configured value)
# PID{6digits} -> PID100000 (prefix + digits)
# HSP{5digits} -> HSP00001 (hospital prefix + 5 digits)
# {4hex} -> A1B2 (4 random hex characters)

# Edit patient_config.json to change:
# - ID generation patterns
# - Starting values and increments
# - Name lists
# - Demographics (birth year ranges, addresses, phone patterns)
```

## Project Structure
```
DICOM_Fabricator/
├── README.md               # Project overview
├── dicom_fabricator.py     # Main DICOM generation script (wrapper)
├── patient_manager.py      # Patient management CLI tool (wrapper)
├── view_dicom.py           # DICOM viewer (wrapper)
├── start_pacs.sh           # PACS server startup script
├── src/                    # Python source code
│   ├── dicom_fabricator.py # Main DICOM generation implementation
│   ├── patient_config.py   # Patient management system
│   ├── patient_manager.py  # Patient management CLI implementation
│   └── view_dicom.py       # DICOM viewer implementation
├── config/                 # Configuration files
│   ├── patient_config.json # Patient generation configuration
│   └── requirements.txt    # Python dependencies
├── data/                   # Runtime data (auto-created)
│   ├── patient_registry.json  # Patient database
│   └── dicom_output/       # Generated DICOM files
├── docker/                 # Docker and PACS setup
│   ├── docker-compose.yml  # Orthanc PACS server
│   ├── orthanc-config.json # Orthanc configuration
│   └── orthanc-data/       # PACS database (auto-created)
└── docs/                   # Documentation
    ├── USAGE.md            # Usage guide
    ├── CLAUDE.md           # Project specification
    ├── DOCKER_INSTALL.md   # Docker setup
    ├── PACS_SERVER_INFO.md # PACS information
    └── PACS_SETUP.md       # PACS setup guide
```

## Key Features Added

### Patient ID Generation System
- **Configurable patterns**: Support for letters, digits, hex, and custom formats
- **Examples**: `{6letters}` → `ABCDEF`, `PID{7digits}` → `PID0000100`
- **Incremental IDs**: Starting values and increment rules
- **Uniqueness**: Automatic collision detection and handling

### Patient Registry & Tracking
- **Persistent storage**: JSON-based patient database
- **Demographics**: Realistic birth dates, addresses, phone numbers
- **Usage tracking**: Study counts and last-used timestamps
- **Search & lookup**: Find patients by ID, name, or other fields

### Enhanced DICOM Generation
- **Patient reuse**: Generate multiple studies for same patient
- **Consistent demographics**: Age calculated from birth date
- **Metadata integration**: Patient info embedded in DICOM images
- **Registry updates**: Automatic tracking when DICOMs are created

## Additional Notes
[Any other important information about the project]

---
*This specification is a living document and should be updated as the project evolves.*