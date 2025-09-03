# Command Line Usage Guide

This guide explains how to use DICOM Fabricator from the command line.

## Related Documents
- [Web Interface Guide](../user-guides/web-interface.md) - Graphical interface
- [Installation Guide](../getting-started/installation.md) - Setup instructions
- [First Steps](../getting-started/first-steps.md) - Getting started
- [Glossary](../glossary.md) - Technical terms explained

## Quick Start

### 1. Install Dependencies
```bash
pip3 install -r config/requirements.txt
```

### 2. Generate Your First DICOM
```bash
# Generate a DICOM with random patient
python3 dicom_fabricator.py

# View the generated DICOM
python3 view_dicom.py data/dicom_output/*.dcm
```

## Patient Management

### Generating Patients

```bash
# Generate a patient with default settings
python3 patient_manager.py generate

# Generate patient with custom name
python3 patient_manager.py generate --name "DOE^JANE"

# Generate patient with specific ID (if pattern allows)
python3 patient_manager.py generate --id "CUSTOM001"
```

### Viewing Patients

```bash
# List all patients
python3 patient_manager.py list

# Show detailed patient info
python3 patient_manager.py show PID100000

# Search patients by name or ID
python3 patient_manager.py search "JANE"
```

### Registry Statistics

```bash
# Show registry statistics
python3 patient_manager.py stats
```

## DICOM Generation

### Basic Usage

```bash
# Generate DICOM with new random patient
python3 dicom_fabricator.py

# Generate DICOM for existing patient
python3 dicom_fabricator.py --patient-id PID100000

# Generate multiple studies for same patient
python3 dicom_fabricator.py --patient-id PID100000 --count 3

# Generate with custom accession
python3 dicom_fabricator.py --accession "ACC20250824001"
```

### Advanced Options

```bash
# Custom study description
python3 dicom_fabricator.py --study-desc "Chest X-Ray Follow-up"

# Different output directory
python3 dicom_fabricator.py --output-dir "./my_dicoms"

# Use custom patient configuration
python3 dicom_fabricator.py --config "./config/my_config.json"
```

## Patient ID Configuration

### Understanding Patterns

The system supports flexible patient ID patterns defined in `patient_config.json`:

```json
{
  "id_generation": {
    "pattern": "PID{6digits}",
    "start_value": 100000,
    "increment": 1
  }
}
```

### Available Pattern Types

| Pattern | Example Output | Description |
|---------|---------------|-------------|
| `{6digits}` | `100000` | 6-digit number, zero-padded |
| `{6letters}` | `ABCDEF` | 6 random uppercase letters |
| `{4hex}` | `A1B2` | 4 random hex characters |
| `PID{5digits}` | `PID10000` | Prefix + digits |
| `HSP{3letters}{4digits}` | `HSPXYZ1000` | Mixed patterns |

### Testing ID Patterns

```bash
# Test current pattern
python3 patient_manager.py test-ids --count 10

# View current configuration
python3 patient_manager.py config
```

## Configuration Management

### Editing Configuration

1. **Export current config:**
```bash
python3 patient_manager.py edit-config --config my_config.json
```

2. **Edit the JSON file:**
```json
{
  "id_generation": {
    "pattern": "{6letters}",
    "start_value": 1,
    "increment": 1
  },
  "demographics": {
    "birth_year_range": [1950, 2000],
    "sex_distribution": {"M": 0.5, "F": 0.5, "O": 0.0}
  }
}
```

3. **Load the new configuration:**
```bash
python3 patient_manager.py load-config my_config.json
```

### Common Configuration Examples

#### Hospital-style IDs
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

## DICOM Viewing

### Basic Viewing
```bash
# View specific DICOM file
python3 view_dicom.py dicom_output/DX_PID100000_ACC20250824001.dcm

# List all DICOM files in directory
python3 view_dicom.py --list --dir ./dicom_output
```

## Workflow Examples

### Testing Integration with New Patient Types

1. **Configure patient IDs for your system:**
```bash
# Edit patient_config.json to match your hospital's ID format
python3 patient_manager.py edit-config
```

2. **Generate test patients:**
```bash
python3 patient_manager.py generate --name "TEST^PATIENT001"
python3 patient_manager.py generate --name "TEST^PATIENT002"
```

3. **Create multiple studies per patient:**
```bash
python3 dicom_fabricator.py --patient-id TEST001 --study-desc "Chest PA"
python3 dicom_fabricator.py --patient-id TEST001 --study-desc "Chest Lateral"
```

4. **Verify patient tracking:**
```bash
python3 patient_manager.py show TEST001
python3 patient_manager.py stats
```

### Batch DICOM Generation

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

# Delete a patient (removes from registry only)
python3 patient_manager.py delete PID100000 --force

# View registry statistics
python3 patient_manager.py stats
```

## Integration with PACS

### Starting Test PACS Server

```bash
# Start Orthanc PACS server (easy way)
./start_pacs.sh

# Or manually:
cd docker && docker-compose up -d

# Check if server is running
curl http://localhost:8042/system
```

### Sending DICOMs to PACS

```bash
# Generate DICOM
python3 dicom_fabricator.py --patient-id PID100000

# Send to PACS (requires additional DICOM networking tools)
# Example with storescu (if available):
# storescu localhost 4242 dicom_output/*.dcm
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
# Show available commands
python3 dicom_fabricator.py --help
python3 patient_manager.py --help
python3 view_dicom.py --help
```