# Web Interface Guide

This guide explains how to use DICOM Fabricator's web interface.

## Related Documents
- [First Steps](../getting-started/first-steps.md) - Getting started
- [Command Line Guide](command-line.md) - Command-line tools
- [Authentication Setup](../configuration/authentication.md) - User access
- [PACS Setup](../configuration/pacs-setup.md) - Server configuration

## Accessing the Web Interface

1. Start DICOM Fabricator:
   ```bash
   python app.py
   ```

2. Open your web browser and go to:
   ```
   http://localhost:5001
   ```

3. If authentication is enabled, log in with your credentials

## Main Dashboard

The dashboard provides an overview of the system and quick access to all features.

![Dashboard](images/dashboard.png)

### Dashboard Features
- **System Status**: Shows PACS server connectivity
- **Quick Stats**: Overview of generated studies and patients
- **Feature Cards**: Direct access to main features
- **Quick Actions**: Start common tasks

### Navigation Menu
- **Dashboard**: Main overview page
- **Patient Management**: Create and manage patients
- **DICOM Generator**: Generate DICOM studies
- **DICOM Viewer**: View and manage generated studies
- **PACS Management**: Configure image servers
- **Query PACS**: Search studies on servers
- **Users**: Manage user accounts (admin only)

## Patient Management

Create and manage synthetic patient records.

![Patient Management](images/patient-management.png)

### Adding Patients
1. Click **"Patient Management"** in the dashboard
2. Click **"Add New Patient"**
3. Fill in patient information:
   - **Patient Name**: Enter name (e.g., "DOE^JANE")
   - **Patient ID**: Leave blank for auto-generation
   - **Birth Date**: Select date
   - **Sex**: Choose Male, Female, or Other
4. Click **"Save Patient"**

### Managing Patients
- **Search**: Use the search box to find patients
- **Edit**: Click the edit button to modify patient information
- **Delete**: Click delete to remove patient (removes from registry only)
- **Export**: Download patient list as CSV

### Patient Features
- **Auto-generated IDs**: System creates unique patient IDs
- **Realistic Demographics**: Synthetic but realistic patient data
- **Search and Filter**: Find patients quickly
- **Bulk Operations**: Work with multiple patients

## DICOM Generation

Generate synthetic DICOM studies from HL7 messages or manual input.

![DICOM Generation](images/dicom-generation.png)

### Manual Generation
1. Click **"DICOM Generator"** in the dashboard
2. Fill in study information:
   - **Study Description**: Enter description (e.g., "Chest X-Ray")
   - **Accession Number**: Leave blank for auto-generation
   - **Patient**: Select from existing patients or create new
3. Click **"Generate DICOM"**

### HL7 ORM Processing
1. In the DICOM Generator, paste an HL7 ORM message
2. The system will automatically extract:
   - Patient information
   - Study details
   - Accession number
3. Review and edit the extracted information
4. Click **"Generate DICOM"**

### Generation Features
- **Study Preview**: View metadata before saving
- **Batch Generation**: Create multiple studies
- **Template Management**: Save and reuse configurations
- **Validation**: Verify studies meet DICOM standards

## DICOM Viewer

View and manage generated DICOM files.

![DICOM Viewer](images/dicom-viewer.png)

### Viewing Studies
1. Click **"DICOM Viewer"** in the dashboard
2. Browse through generated studies
3. Click on a study to view detailed metadata
4. Use the file browser to navigate through studies

### Study Operations
- **View Metadata**: See all DICOM tags and values
- **Download**: Save DICOM files locally
- **Send to PACS**: Transfer studies to image servers
- **Delete**: Remove studies from the system

### Viewer Features
- **File Browser**: Navigate through DICOM files
- **Metadata Display**: View detailed DICOM information
- **Search and Filter**: Find specific studies
- **Export Options**: Download files or metadata

## PACS Management

Configure and manage image server connections.

![PACS Management](images/pacs-management.png)

### Adding PACS Servers
1. Click **"PACS Management"** in the dashboard
2. Click **"Add New PACS"**
3. Fill in server information:
   - **Name**: Friendly name for the server
   - **Host**: Server address (IP or hostname)
   - **Port**: DICOM port (usually 104)
   - **AEC**: Server's connection name
   - **Environment**: Choose "test" or "prod"
4. Click **"Save PACS"**

### Managing PACS Servers
- **Test Connection**: Verify server connectivity
- **Edit Configuration**: Modify server settings
- **C-MOVE Routing**: Configure study transfers
- **Delete**: Remove server configuration

### PACS Features
- **Connection Testing**: Verify server accessibility
- **Environment Separation**: Test vs. production servers
- **C-MOVE Configuration**: Set up study transfers
- **Status Monitoring**: Real-time connection status

## Query PACS

Search and retrieve studies from connected image servers.

![PACS Query](images/pacs-query.png)

### Searching Studies
1. Click **"Query PACS"** in the dashboard
2. Select PACS servers to search
3. Enter search criteria:
   - **Patient Name**: Search by patient
   - **Study Date**: Date range for studies
   - **Accession Number**: Specific study identifier
4. Click **"Query PACS"**

### Query Results
- **Study List**: View matching studies
- **Study Details**: Click to see full information
- **Export Results**: Download as CSV
- **C-MOVE**: Transfer studies between servers

### Query Features
- **Multi-PACS Search**: Query multiple servers at once
- **Advanced Filters**: Use multiple criteria
- **Result Export**: Save search results
- **Study Transfer**: Move studies between servers

## User Management (Admin Only)

Manage user accounts and permissions.

### Adding Users
1. Click **"Users"** in the navigation (admin only)
2. Click **"Add New User"**
3. Fill in user information:
   - **Username**: Login name
   - **Password**: User password
   - **Email**: User email address
   - **Role**: Select appropriate role
4. Click **"Save User"**

### Managing Users
- **Edit Users**: Modify user information
- **Change Roles**: Update user permissions
- **Delete Users**: Remove user accounts
- **Reset Passwords**: Change user passwords

## Keyboard Shortcuts

### Navigation
- **Ctrl+1**: Dashboard
- **Ctrl+2**: Patient Management
- **Ctrl+3**: DICOM Generator
- **Ctrl+4**: DICOM Viewer
- **Ctrl+5**: PACS Management
- **Ctrl+6**: Query PACS

### Common Actions
- **Ctrl+N**: New item (patient, study, etc.)
- **Ctrl+S**: Save current form
- **Ctrl+F**: Search/filter
- **Ctrl+E**: Export data
- **Esc**: Cancel current action

## Tips and Best Practices

### Efficient Workflow
1. **Start with Patients**: Create patient records first
2. **Generate Studies**: Create DICOM studies for patients
3. **Review Results**: Use the viewer to check generated studies
4. **Test PACS**: Send studies to test servers
5. **Query and Transfer**: Search and move studies between servers

### Data Management
- **Regular Cleanup**: Remove old test data periodically
- **Backup Configurations**: Save PACS and patient configurations
- **Monitor Storage**: Check disk space for generated studies
- **Export Important Data**: Download studies and configurations

### Security
- **Use Strong Passwords**: Especially for admin accounts
- **Regular User Review**: Remove unused accounts
- **Environment Separation**: Keep test and production separate
- **Monitor Access**: Check user activity logs

## Troubleshooting

### Common Issues

**"Page not loading" errors:**
- Check if the application is running
- Verify the correct URL (http://localhost:5001)
- Check browser console for errors

**"Permission denied" errors:**
- Verify you're logged in
- Check your user role and permissions
- Contact administrator for access issues

**"Connection failed" errors:**
- Check PACS server configuration
- Verify network connectivity
- Test server connection manually

### Getting Help
- Check the [Common Issues](../troubleshooting/common-issues.md) guide
- Review browser console for error messages
- Check application logs for detailed errors
- Create a GitHub issue with detailed information

## Next Steps

- [Command Line Guide](command-line.md) - Command-line tools
- [PACS Setup](../configuration/pacs-setup.md) - Server configuration
- [Troubleshooting](../troubleshooting/common-issues.md) - Common problems
