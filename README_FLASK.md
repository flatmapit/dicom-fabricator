# DICOM Fabricator - Flask Web Application

A Flask-based web interface for the DICOM Fabricator with patient management, DICOM generation, and file viewing capabilities. This application uses **tosijs** for advanced table handling and data management.

## Features

### Web Interface
- **Patient Management**: Create, view, search, and delete synthetic patient records
- **DICOM Generator**: Generate DICOM studies with customizable parameters
- **DICOM Viewer**: View DICOM files with metadata and image preview
- **PACS Integration**: Monitor PACS server status and connectivity
- **Table Management**: Powered by tosijs for sortable, searchable, paginated tables

## Installation

### 1. Install Python Dependencies
```bash
pip3 install -r config/requirements.txt
```

### 2. Start the Flask Application
```bash
python3 app.py
```

The application will be available at: http://localhost:5001

## Application Structure

```
DICOM_Fabricator/
├── app.py                  # Flask application main file
├── templates/              # HTML templates
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Home page
│   ├── patients.html      # Patient management interface
│   ├── generator.html     # DICOM generation interface
│   └── viewer.html        # DICOM viewer interface
├── static/                # Static assets
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       └── app.js         # JavaScript utilities
└── src/                   # Backend modules
    ├── dicom_fabricator.py
    ├── patient_config.py
    └── view_dicom.py
```

## Web Interface Pages

### Home Page (/)
- Dashboard with quick stats
- PACS server status monitoring
- Quick access to all features

### Patient Management (/patients)
- **Table Features** (powered by tosijs):
  - Sortable columns
  - Search functionality  
  - Pagination (10 records per page)
  - Responsive design
- **Actions**:
  - Add new patients with full demographics
  - Search patients by name, MRN, or other fields
  - Delete patient records

### DICOM Generator (/generator)
- Generate DICOM studies with:
  - Patient selection from registry
  - Custom patient name and ID
  - Accession number (auto-generated if empty)
  - Study description
  - Batch generation (1-10 studies)
- **File Management Table** (tosijs):
  - View all generated DICOM files
  - Sort by filename, patient, date, size
  - Search files
  - Quick actions: View, Download, Delete

### DICOM Viewer (/viewer)
- File browser with list of available DICOM files
- Metadata display showing:
  - Patient information
  - Study details
  - Technical parameters
  - UIDs
- Image preview (512x512 monochrome)
- Download and delete capabilities

## API Endpoints

### Patient Management
- `GET /api/patients` - List all patients
- `POST /api/patients` - Create new patient
- `DELETE /api/patients/<id>` - Delete patient
- `POST /api/patients/search` - Search patients

### DICOM Operations
- `POST /api/generate` - Generate DICOM files
- `GET /api/dicom/list` - List DICOM files
- `GET /api/dicom/view/<filename>` - View DICOM details
- `GET /api/dicom/download/<filename>` - Download DICOM file
- `DELETE /api/dicom/delete/<filename>` - Delete DICOM file

### System Status
- `GET /api/pacs/status` - Check PACS server status

## tosijs Integration

The application uses [tosijs](https://github.com/tonioloewald/tosijs) and [tosijs-ui](https://github.com/tonioloewald/tosijs-ui) for enhanced table functionality:

- **Automatic Features**:
  - Column sorting (click headers)
  - Global search box
  - Pagination controls
  - Responsive table layout
  - Enhanced UI components (tosijs-ui)

- **Configuration**:
  ```javascript
  new tosijs.Table('#tableId', {
      sortable: true,
      searchable: true,
      paginate: true,
      pageSize: 10,
      responsive: true
  });
  ```

- **Note**: tosijs-ui is currently disabled due to loading issues but may be re-enabled in future versions

## Running with Docker PACS

### Start PACS Server
```bash
./start_pacs.sh
```

### Access Points
- Web Interface: http://localhost:5001
- PACS Web UI: http://localhost:8042 (test/test123)
- DICOM Port: 4242

## Development

### Running in Debug Mode
The Flask app runs in debug mode by default, enabling:
- Auto-reload on code changes
- Detailed error messages
- Debug toolbar

### Custom Styling
- Bootstrap 5.1.3 for UI components
- Font Awesome 6.0 for icons
- Custom CSS in `/static/css/style.css`

### JavaScript Libraries
- jQuery 3.6.0
- Bootstrap Bundle 5.1.3
- tosijs (latest from CDN)
- tosijs-ui (currently disabled due to loading issues)

## Security Notes

- No authentication implemented (development use only)
- CORS enabled for API access
- 16MB max file upload size
- All generated data is synthetic/fake

## Browser Compatibility

Tested with:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (responsive design)

## Troubleshooting

### Port Already in Use
If port 5001 is in use, edit `app.py` and change the port number:
```python
app.run(debug=True, host='0.0.0.0', port=5002)
```

### Missing Dependencies
```bash
pip3 install Flask Flask-CORS
pip3 install -r config/requirements.txt
```

### PACS Connection Issues
Ensure Docker is running and the PACS server is started:
```bash
cd docker && docker-compose up -d
```