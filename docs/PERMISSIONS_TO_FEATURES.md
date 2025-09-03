# DICOM Fabricator - Feature Permission Matrix

This document provides a comprehensive mapping of application features to user roles and their corresponding permissions in the DICOM Fabricator application.

## Table of Contents
- [Permission Matrix](#permission-matrix)
- [Role Descriptions](#role-descriptions)
- [Key Permission Rules](#key-permission-rules)
- [Feature Categories](#feature-categories)
- [Environment Access](#environment-access)
- [API Endpoint Permissions](#api-endpoint-permissions)

## Permission Matrix

**Note**: Features marked with * do not currently require authentication in the implementation but are accessed through authenticated pages.

| **Feature** | **Admin** | **Test Write** | **Test Read** | **Prod Write** | **Prod Read** |
|------------|-----------|----------------|---------------|----------------|---------------|
| **Navigation & Pages** |
| View Query PACS page | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| View Local DICOM page | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| View PACS page | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| View Patients page | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| View Users page | ✅ Permit | ❌ Deny | ❌ Deny | ❌ Deny | ❌ Deny |
| **User Management** |
| Create users | ✅ Permit | ❌ Deny | ❌ Deny | ❌ Deny | ❌ Deny |
| Edit users | ✅ Permit | ❌ Deny | ❌ Deny | ❌ Deny | ❌ Deny |
| Delete users | ✅ Permit | ❌ Deny | ❌ Deny | ❌ Deny | ❌ Deny |
| View user list | ✅ Permit | ❌ Deny | ❌ Deny | ❌ Deny | ❌ Deny |
| **DICOM Generation** |
| Generate DICOM studies | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| Parse HL7 ORM messages | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| View generated DICOMs* | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| Delete DICOM studies* | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| Export DICOM data* | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| **Patient Management** |
| View patients | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| Create patients | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| Edit patients | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| Delete patients | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| Export patients CSV | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| **PACS Configuration** |
| View PACS configs | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| Create PACS config | ✅ Permit | ❌ Deny | ❌ Deny | ❌ Deny | ❌ Deny |
| Edit PACS config | ✅ Permit | ❌ Deny | ❌ Deny | ❌ Deny | ❌ Deny |
| Delete PACS config | ✅ Permit | ❌ Deny | ❌ Deny | ❌ Deny | ❌ Deny |
| Test PACS connection | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit | ✅ Permit |
| **Test Environment PACS Operations** |
| Query Test PACS (C-FIND) | ✅ Permit | ✅ Permit | ✅ Permit | ❌ Deny | ❌ Deny |
| Send to Test PACS (C-STORE) | ✅ Permit | ✅ Permit | ❌ Deny | ❌ Deny | ❌ Deny |
| Move in Test PACS (C-MOVE) | ✅ Permit | ✅ Permit | ❌ Deny | ❌ Deny | ❌ Deny |
| **Production Environment PACS Operations** |
| Query Prod PACS (C-FIND) | ✅ Permit | ❌ Deny | ❌ Deny | ✅ Permit | ✅ Permit |
| Send to Prod PACS (C-STORE) | ✅ Permit | ❌ Deny | ❌ Deny | ✅ Permit | ❌ Deny |
| Move in Prod PACS (C-MOVE) | ✅ Permit | ❌ Deny | ❌ Deny | ✅ Permit | ❌ Deny |

## Role Descriptions

### Admin
- **Description**: Full system access - can do anything
- **Capabilities**: Complete control over all features including user management and PACS administration
- **Use Case**: System administrators and super users

### Test Write
- **Description**: Test environment write access
- **Capabilities**: Can query, C-STORE and C-MOVE to test PACS, generate DICOM, manage patients
- **Use Case**: Developers and testers working with test PACS servers

### Test Read
- **Description**: Test environment read access
- **Capabilities**: Can view status and query test PACS, generate DICOM, manage patients
- **Use Case**: Read-only access for test environment monitoring

### Prod Write
- **Description**: Production environment write access
- **Capabilities**: Can query, C-STORE and C-MOVE to production PACS, generate DICOM, manage patients
- **Use Case**: Production operators with write permissions

### Prod Read
- **Description**: Production environment read access
- **Capabilities**: Can view status and query production PACS, generate DICOM, manage patients
- **Use Case**: Production monitoring and read-only access

## Key Permission Rules

### 1. User Management
- **Exclusive to Admin**: Only the admin role has access to user management features
- **Navigation Control**: Users page is hidden from non-admin users in the navigation menu
- **API Protection**: User management API endpoints require admin role

### 2. PACS Administration
- **Admin Only**: Creating, editing, and deleting PACS configurations requires admin role
- **View Access**: All roles can view PACS configurations and test connections
- **Environment Enforcement**: PACS operations respect environment boundaries

### 3. Environment Isolation
- **Strict Separation**: Test roles cannot access production PACS and vice versa
- **Write Permissions**: Write operations (C-STORE, C-MOVE) require write-level role for the environment
- **Read Permissions**: Query operations (C-FIND) require at least read-level role for the environment
- **PACS-Level Configuration**: Each PACS configuration specifies its environment (test/prod) which determines access requirements

### 4. C-MOVE Special Requirements
- **Dual Environment Access**: C-MOVE operations require write access to both source and destination environments
- **Permission Check**: System validates permissions for both environments before allowing transfer

## Feature Categories

### Core Features (All Authenticated Users)
- DICOM study generation (requires login)
- HL7 ORM message parsing (requires login)
- Patient management - CRUD operations (requires login)
- Viewing locally generated DICOM studies (no authentication required for API)
- Exporting data to CSV (no authentication required for API)

**Important**: While DICOM file operations don't require authentication at the API level, they are typically accessed through authenticated pages in the web interface.

### Restricted Features

#### Admin-Only Features
- User management (create, edit, delete users)
- PACS configuration management (create, edit, delete)
- Access to Users navigation page

#### Environment-Specific Features
- PACS queries limited to assigned environment
- C-STORE operations limited to write-enabled roles
- C-MOVE operations require write access to both environments

## Environment Access

### Test Environment
| Operation | Test Write | Test Read | Others |
|-----------|------------|-----------|--------|
| C-FIND (Query) | ✅ Permit | ✅ Permit | ❌ Deny |
| C-STORE (Send) | ✅ Permit | ❌ Deny | ❌ Deny |
| C-MOVE (Transfer) | ✅ Permit | ❌ Deny | ❌ Deny |

### Production Environment
| Operation | Prod Write | Prod Read | Others |
|-----------|------------|-----------|--------|
| C-FIND (Query) | ✅ Permit | ✅ Permit | ❌ Deny |
| C-STORE (Send) | ✅ Permit | ❌ Deny | ❌ Deny |
| C-MOVE (Transfer) | ✅ Permit | ❌ Deny | ❌ Deny |

## API Endpoint Permissions

### Public Endpoints (No Authentication Required)
- `/login` - Login page
- `/api/pacs/configs/<id>/test` - Test PACS connection
- `/api/dicom/list` - List DICOM files
- `/api/dicom/view/<filename>` - View DICOM file details
- `/api/dicom/download/<filename>` - Download DICOM file
- `/api/dicom/headers/<filename>` - Get DICOM headers
- `/api/dicom/delete/<filename>` - Delete DICOM file
- `/api/dicom/studies` - List DICOM studies
- `/api/dicom/studies/delete` - Delete DICOM studies
- `/api/dicom/export/csv` - Export DICOM data to CSV

### Authenticated Endpoints (Login Required)
The following endpoints require authentication. Additional role-based restrictions apply:

#### Admin-Only Endpoints
- `POST /api/users` - Create user
- `PUT /api/users/<username>` - Update user
- `DELETE /api/users/<username>` - Delete user
- `POST /api/pacs/configs` - Create PACS config
- `PUT /api/pacs/configs/<id>` - Update PACS config
- `DELETE /api/pacs/configs/<id>` - Delete PACS config

#### Environment-Restricted Endpoints
- `POST /api/pacs/send-study` - Requires write access to target environment
- `POST /api/pacs/query` - Requires read access to target environment
- `POST /api/pacs/c-move` - Requires write access to both source and destination environments

### Special Behaviors

#### Authentication Disabled Mode
When authentication is disabled (`auth_enabled: false`):
- All features are accessible to all users
- No login required
- Navigation shows "No Auth Mode" indicator
- Default anonymous user with `test_read` role is used internally

#### Implementation Notes
- **DICOM File Operations**: Currently do not enforce authentication at the API level, though they are accessed through authenticated pages
- **Patient Management**: All operations require authentication (login)
- **PACS Operations**: Environment-based access control is strictly enforced based on PACS configuration

#### Permission Enforcement
- Permissions are checked at both route and operation levels
- Environment access is validated dynamically based on PACS configuration
- Failed permission checks return HTTP 403 (Forbidden) responses

## Related Documentation
- [Authentication Setup Guide](AUTHENTICATION_SETUP.md) - Complete authentication configuration guide
- [Feature Overview](feature_overview.md) - Detailed description of all application features
- [API Documentation](api_documentation.md) - Complete API endpoint reference