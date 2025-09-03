# Command Line Guide

This guide explains how to use DICOM Fabricator from the command line.

## Related Documents
- [Installation Guide](../getting-started/installation.md) - Setup instructions
- [Web Interface Guide](web-interface.md) - Graphical interface
- [First Steps](../getting-started/first-steps.md) - Getting started
- [Glossary](../glossary.md) - Technical terms explained

## Available Tools

DICOM Fabricator includes several command-line tools:

- **`dicom_fabricator.py`** - Generate DICOM studies
- **`patient_manager.py`** - Manage patient records
- **`view_dicom.py`** - View DICOM files
- **`app.py`** - Start the web interface

## DICOM Generation

### Basic Usage
```bash
# Generate a DICOM study with a random patient
python3 dicom_fabricator.py

# Generate for a specific patient
python3 dicom_fabricator.py --patient-id PID100000

# Generate multiple studies for the same patient
python3 dicom_fabricator.py --patient-id PID100000 --count 3
```

### Advanced Options
```bash
# Custom study description
python3 dicom_fabricator.py --study-desc "Chest X-Ray Follow-up"

# Custom accession number
python3 dicom_fabricator.py --accession "ACC20250824001"

# Different output directory
python3 dicom_fabricator.py --output-dir "./my_dicoms"

# Use custom patient configuration
python3 dicom_fabricator.py --config "./config/my_config.json"
```

### Command Options
| Option | Description | Example |
|--------|-------------|---------|
| `--patient-id` | Use existing patient | `--patient-id PID100000` |
| `--count` | Generate multiple studies | `--count 5` |
| `--study-desc` | Study description | `--study-desc "CT Chest"` |
| `--accession` | Accession number | `--accession "ACC001"` |
| `--output-dir` | Output directory | `--output-dir "./output"` |
| `--config` | Patient config file | `--config "./my_config.json"` |

## Patient Management

### Creating Patients
```bash
# Generate a patient with default settings
python3 patient_manager.py generate

# Generate patient with custom name
python3 patient_manager.py generate --name "DOE^JANE"

# Generate patient with specific ID
python3 patient_manager.py generate --id "CUSTOM001"
```

### Viewing Patients
```bash
# List all patients
python3 patient_manager.py list

# Show detailed patient information
python3 patient_manager.py show PID100000

# Search patients by name or ID
python3 patient_manager.py search "JANE"
```

### Patient Statistics
```bash
# Show registry statistics
python3 patient_manager.py stats

# Test ID pattern generation
python3 patient_manager.py test-ids --count 10
```

### Patient Commands
| Command | Description | Example |
|---------|-------------|---------|
| `generate` | Create new patient | `generate --name "DOE^JANE"` |
| `list` | List all patients | `list` |
| `show` | Show patient details | `show PID100000` |
| `search` | Search patients | `search "JANE"` |
| `stats` | Show statistics | `stats` |
| `test-ids` | Test ID patterns | `test-ids --count 10` |

## DICOM Viewing

### View DICOM Files
```bash
# View specific DICOM file
python3 view_dicom.py dicom_output/DX_PID100000_ACC20250824001.dcm

# List all DICOM files in directory
python3 view_dicom.py --list --dir ./dicom_output

# View multiple files
python3 view_dicom.py dicom_output/*.dcm
```

### Viewing Options
| Option | Description | Example |
|--------|-------------|---------|
| `--list` | List files without viewing | `--list` |
| `--dir` | Specify directory | `--dir ./output` |
| `--tags` | Show specific tags | `--tags "PatientName,StudyDate"` |

## Configuration Management

### Patient Configuration
```bash
# View current configuration
python3 patient_manager.py config

# Edit configuration
python3 patient_manager.py edit-config --config my_config.json

# Load new configuration
python3 patient_manager.py load-config my_config.json
```

### Configuration Examples

#### Hospital-style Patient IDs
```json
{
  "id_generation": {
    "pattern": "HSP{7digits}",
    "start_value": 1000000,
    "increment": 1
  }
}
```

#### Research Study IDs
```json
{
  "id_generation": {
    "pattern": "STUDY2025{4digits}",
    "start_value": 1,
    "increment": 1
  }
}
```

#### Random Letter IDs
```json
{
  "id_generation": {
    "pattern": "{8letters}",
    "start_value": 1,
    "increment": 1
  }
}
```

## Common Workflows

### Testing Integration
```bash
# 1. Configure patient IDs for your system
python3 patient_manager.py edit-config

# 2. Generate test patients
python3 patient_manager.py generate --name "TEST^PATIENT001"
python3 patient_manager.py generate --name "TEST^PATIENT002"

# 3. Create multiple studies per patient
python3 dicom_fabricator.py --patient-id TEST001 --study-desc "Chest PA"
python3 dicom_fabricator.py --patient-id TEST001 --study-desc "Chest Lateral"

# 4. Verify patient tracking
python3 patient_manager.py show TEST001
python3 patient_manager.py stats
```

### Batch Generation
```bash
# Generate 10 DICOMs with different patients
for i in {1..10}; do
    python3 dicom_fabricator.py
done

# Generate multiple studies for existing patient
python3 dicom_fabricator.py --patient-id PID100000 --count 5
```

### Cleanup and Management
```bash
# Search for specific patient
python3 patient_manager.py search "TEST"

# View registry statistics
python3 patient_manager.py stats

# List all generated DICOM files
python3 view_dicom.py --list --dir ./dicom_output
```

## Integration with PACS

### Starting Test PACS Server
```bash
# Start Orthanc PACS server
./start_pacs.sh

# Or manually with Docker
cd docker && docker-compose up -d

# Check if server is running
curl http://localhost:8042/system
```

### Sending DICOMs to PACS
```bash
# Generate DICOM
python3 dicom_fabricator.py --patient-id PID100000

# Send to PACS (requires DCMTK tools)
storescu localhost 4242 dicom_output/*.dcm
```

## Troubleshooting

### Common Issues

**"Patient not found" warning:**
- The system will automatically generate a new patient if the ID doesn't exist
- Use `python3 patient_manager.py list` to see available patients

**"Invalid VR AS" warning:**
- This is a pydicom warning about age formatting - can be safely ignored
- Ages are calculated correctly from birth dates

**Permission errors:**
- Ensure write permissions to current directory for registry files
- Check that output directory exists and is writable

### File Locations
- **Patient Registry:** `./patient_registry.json` (auto-created)
- **Configuration:** `./patient_config.json`
- **Generated DICOMs:** `./dicom_output/`
- **PACS Data:** `./orthanc-data/` (when using Docker)

### Getting Help
```bash
# Show available commands and options
python3 dicom_fabricator.py --help
python3 patient_manager.py --help
python3 view_dicom.py --help
```

## Next Steps

- [Web Interface Guide](web-interface.md) - Learn the graphical interface
- [PACS Setup](../configuration/pacs-setup.md) - Configure image servers
- [Troubleshooting](../troubleshooting/common-issues.md) - Common problems
