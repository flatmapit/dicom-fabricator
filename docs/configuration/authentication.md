# Authentication Setup

This guide explains how to set up user authentication and access control in DICOM Fabricator.

## Related Documents
- [Installation Guide](../getting-started/installation.md) - Basic setup instructions
- [PACS Setup](pacs-setup.md) - Image server configuration
- [Glossary](../glossary.md) - Technical terms explained

## Authentication Options

DICOM Fabricator supports three authentication modes:

### 1. No Authentication (Default)
Run without any login requirements - perfect for testing and development.

**When to use:** Development, testing, single-user setups

### 2. Local Authentication
Simple username and password login managed within DICOM Fabricator.

**When to use:** Small teams, simple setups, when you don't have enterprise systems

### 3. Enterprise Authentication
Connect to your company's user system (Active Directory or SAML).

**When to use:** Large organizations, corporate environments, when you need centralized user management

## Quick Setup

### Option 1: No Authentication (Default)
No setup required - just run the application:
```bash
python app.py
```

### Option 2: Local Authentication
1. **Create authentication configuration:**
```bash
cp config/auth_config.json.sample config/auth_config.json
```

2. **Edit the configuration file:**
```json
{
  "auth_enabled": true,
  "enterprise_auth_enabled": false
}
```

3. **Create your first admin user:**
```bash
python3 -c "
from src.auth import AuthManager
auth = AuthManager()
auth.create_user('admin', 'admin123', 'admin@example.com', 'admin')
print('Admin user created: admin/admin123')
"
```

4. **Start the application:**
```bash
python app.py
```

5. **Login with your credentials:**
- Username: `admin`
- Password: `admin123`

### Option 3: Enterprise Authentication
1. **Enable enterprise authentication:**
```json
{
  "auth_enabled": true,
  "enterprise_auth_enabled": true
}
```

2. **Configure your enterprise system:**
```bash
cp config/enterprise_auth.json.sample config/enterprise_auth.json
# Edit with your server details
```

3. **Set up group mappings:**
```bash
cp config/group_mappings.json.sample config/group_mappings.json
# Map your groups to application roles
```

## User Roles Explained

DICOM Fabricator uses simple roles to control what users can do:

| Role | What They Can Do | Best For |
|------|------------------|----------|
| **admin** | Everything - manage users, configure servers, access all features | System administrators |
| **test_write** | Work with test image servers - query, send, and move studies | Test environment users |
| **test_read** | View test image servers - can only look, not make changes | Test environment viewers |
| **prod_write** | Work with production image servers - query, send, and move studies | Production users |
| **prod_read** | View production image servers - can only look, not make changes | Production viewers |

## Enterprise Integration

### Active Directory Setup
If your organization uses Active Directory, you can connect DICOM Fabricator to it:

1. **Configure Active Directory connection:**
```json
{
  "active_directory": {
    "enabled": true,
    "server": "your-ad-server.company.com",
    "port": 389,
    "use_ssl": false,
    "bind_dn": "CN=ServiceAccount,OU=ServiceAccounts,DC=company,DC=com",
    "bind_password": "your-service-account-password",
    "search_base": "DC=company,DC=com"
  }
}
```

2. **Map AD groups to roles:**
```json
{
  "mappings": {
    "DF-Admin": {
      "application_role": "admin",
      "description": "Full system access"
    },
    "DF-TestWrite": {
      "application_role": "test_write",
      "description": "Test environment access"
    }
  }
}
```

### SAML Setup
For SAML-based authentication (like Microsoft Azure AD):

1. **Configure SAML provider:**
```json
{
  "saml": {
    "enabled": true,
    "idp_entity_id": "https://sts.windows.net/your-tenant-id/",
    "idp_sso_url": "https://login.microsoftonline.com/your-tenant-id/saml2",
    "idp_x509_cert": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
  }
}
```

2. **Set up group mappings the same way as Active Directory**

## Security Best Practices

### For Local Authentication
- Use strong passwords
- Change default admin password immediately
- Regularly review user accounts
- Remove unused accounts

### For Enterprise Authentication
- Use the `DF-` prefix for all group names to avoid conflicts
- Test group mappings thoroughly
- Monitor authentication logs
- Keep service account credentials secure

## Troubleshooting

### Common Issues

**"Authentication failed" errors:**
- Check username and password
- Verify authentication is enabled in configuration
- Check server logs for detailed error messages

**"Group not found" errors:**
- Verify group names in your enterprise system
- Check group mapping configuration
- Ensure service account has permission to read groups

**"Permission denied" errors:**
- Check user role assignments
- Verify group mappings are correct
- Ensure user has appropriate permissions for the action

### Getting Help
- Check the [Common Issues](../troubleshooting/common-issues.md) guide
- Review authentication logs in the application
- Create a GitHub issue with detailed error information

## Next Steps

- [PACS Setup](pacs-setup.md) - Configure image servers
- [Web Interface Guide](../user-guides/web-interface.md) - Learn the interface
- [Troubleshooting](../troubleshooting/common-issues.md) - Common problems
