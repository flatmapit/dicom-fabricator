# Authentication Setup Guide

This guide explains how to configure and test the authentication system in DICOM Fabricator.

## Overview

The authentication system supports multiple modes:
- **No Authentication**: Run without any authentication (development/testing)
- **Local Authentication**: Simple username/password authentication
- **Enterprise Authentication**: Active Directory (AD) and SAML integration

## Configuration Files

### 1. Authentication Configuration (`config/auth_config.json`)

```json
{
  "auth_enabled": true,
  "enterprise_auth_enabled": false,
  "default_user_permissions": [
    "dicom_view",
    "pacs_query_test"
  ]
}
```

**Settings:**
- `auth_enabled`: Enable/disable authentication (default: `true`)
- `enterprise_auth_enabled`: Enable enterprise authentication (default: `false`)
- `default_user_permissions`: Permissions for anonymous users when auth is disabled

### 2. Enterprise Authentication (`config/enterprise_auth.json`)

```json
{
  "active_directory": {
    "enabled": false,
    "server": "dc.company.com",
    "port": 389,
    "use_ssl": false,
    "use_ntlm": true,
    "bind_dn": "CN=ServiceAccount,OU=ServiceAccounts,DC=company,DC=com",
    "bind_password": "your-service-account-password",
    "search_base": "DC=company,DC=com",
    "search_filter": "(sAMAccountName={username})"
  },
  "saml": {
    "enabled": false,
    "idp_entity_id": "https://sts.windows.net/your-tenant-id/",
    "idp_sso_url": "https://login.microsoftonline.com/your-tenant-id/saml2",
    "idp_x509_cert": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
  }
}
```

### 3. Group Mappings (`config/group_mappings.json`)

Maps enterprise groups to application permissions:

```json
{
  "default_role": "user",
  "default_permissions": [
    "dicom_view",
    "pacs_query_test"
  ],
  "mappings": {
    "DICOM_Administrators": {
      "enterprise_group": "DICOM_Administrators",
      "application_role": "admin",
      "permissions": ["system_admin"],
      "is_active": true,
      "description": "Full system administration access"
    }
  }
}
```

## Environment-Specific Permissions

The system supports granular permissions for test and production environments:

### Test Environment Permissions
- `pacs_query_test`: Query test PACS servers
- `pacs_move_test`: C-MOVE studies in test environment
- `pacs_configure_test`: Configure test PACS connections
- `pacs_test_test`: Test test PACS connections

### Production Environment Permissions
- `pacs_query_prod`: Query production PACS servers
- `pacs_move_prod`: C-MOVE studies in production environment
- `pacs_configure_prod`: Configure production PACS connections
- `pacs_test_prod`: Test production PACS connections

### Legacy Permissions (Backward Compatibility)
- `pacs_query`: Query PACS servers (all environments)
- `pacs_move`: C-MOVE studies (all environments)
- `pacs_configure`: Configure PACS connections (all environments)
- `pacs_test`: Test PACS connections (all environments)

## Setup Scenarios

### Scenario 1: No Authentication (Development/Testing)

**Use Case**: Quick development, testing, or single-user deployment

**Configuration**:
```json
{
  "auth_enabled": false,
  "enterprise_auth_enabled": false,
  "default_user_permissions": [
    "dicom_view",
    "pacs_query_test",
    "pacs_query_prod"
  ]
}
```

**Behavior**:
- No login required
- All users have full access
- Default permissions applied to anonymous user

### Scenario 2: Local Authentication

**Use Case**: Small team, simple username/password authentication

**Configuration**:
```json
{
  "auth_enabled": true,
  "enterprise_auth_enabled": false
}
```

**Setup Steps**:
1. Start the application (creates default admin user)
2. Default credentials: `admin` / `admin123`
3. Create additional users via the application interface

**Default Users Created**:
- **Admin**: `admin` / `admin123` (full system access)
- **Operator**: Create via interface (full operational access)
- **Viewer**: Create via interface (read-only access)

### Scenario 3: Active Directory Integration

**Use Case**: Enterprise environment with existing AD infrastructure

**Configuration**:
```json
{
  "auth_enabled": true,
  "enterprise_auth_enabled": true
}
```

**AD Configuration**:
```json
{
  "active_directory": {
    "enabled": true,
    "server": "dc.company.com",
    "port": 389,
    "use_ssl": false,
    "use_ntlm": true,
    "bind_dn": "CN=ServiceAccount,OU=ServiceAccounts,DC=company,DC=com",
    "bind_password": "your-service-account-password",
    "search_base": "DC=company,DC=com",
    "search_filter": "(sAMAccountName={username})"
  }
}
```

**Required AD Groups**:
- `DICOM_Administrators`: Full system access
- `DICOM_Operators`: Full operational access
- `Test_Environment_Users`: Test environment read/write
- `Production_Environment_Users`: Production environment read/write
- `Test_Environment_Viewers`: Test environment read-only
- `Production_Environment_Viewers`: Production environment read-only

### Scenario 4: SAML Integration

**Use Case**: Cloud-based identity provider (Azure AD, Okta, etc.)

**Configuration**:
```json
{
  "auth_enabled": true,
  "enterprise_auth_enabled": true
}
```

**SAML Configuration**:
```json
{
  "saml": {
    "enabled": true,
    "idp_entity_id": "https://sts.windows.net/your-tenant-id/",
    "idp_sso_url": "https://login.microsoftonline.com/your-tenant-id/saml2",
    "idp_x509_cert": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
    "sp_entity_id": "https://your-app.company.com",
    "sp_acs_url": "https://your-app.company.com/saml/acs"
  }
}
```

## Testing Authentication

### 1. Test No Authentication Mode

```bash
# Create config for no authentication
cat > config/auth_config.json << EOF
{
  "auth_enabled": false,
  "enterprise_auth_enabled": false,
  "default_user_permissions": [
    "dicom_view",
    "pacs_query_test",
    "pacs_query_prod"
  ]
}
EOF

# Start application
python3 app.py
```

**Expected Behavior**:
- No login page
- Direct access to all features
- User shows as "anonymous"

### 2. Test Local Authentication

```bash
# Create config for local authentication
cat > config/auth_config.json << EOF
{
  "auth_enabled": true,
  "enterprise_auth_enabled": false
}
EOF

# Start application
python3 app.py
```

**Expected Behavior**:
- Login page at `/login`
- Default admin user: `admin` / `admin123`
- Permission-based access control

### 3. Test Environment-Specific Access

Create test users with different permissions:

**Test Environment User**:
```json
{
  "username": "testuser",
  "password": "testpass123",
  "email": "test@company.com",
  "role": "test_user",
  "permissions": [
    "dicom_view",
    "pacs_query_test",
    "pacs_move_test",
    "patients_view"
  ]
}
```

**Production Environment User**:
```json
{
  "username": "produser",
  "password": "prodpass123",
  "email": "prod@company.com",
  "role": "prod_user",
  "permissions": [
    "dicom_view",
    "pacs_query_prod",
    "pacs_move_prod",
    "patients_view"
  ]
}
```

### 4. Test Permission Enforcement

**Test Environment Access**:
- User with `pacs_query_test` can query test PACS
- User without `pacs_query_prod` cannot query production PACS
- User with `pacs_move_test` can C-MOVE in test environment

**Production Environment Access**:
- User with `pacs_query_prod` can query production PACS
- User without `pacs_query_test` cannot query test PACS
- User with `pacs_move_prod` can C-MOVE in production environment

## API Authentication

### JWT Token Authentication

For API access, use JWT tokens:

```bash
# Get JWT token
curl -X POST http://localhost:5055/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token in API calls
curl -X GET http://localhost:5055/api/pacs/configs \
  -H "Authorization: Bearer <jwt_token>"
```

### Environment-Specific API Access

The API respects environment-specific permissions:

```python
# Test environment query (requires pacs_query_test permission)
response = requests.post('/api/pacs/query', json={
    'environment': 'test',
    'pacs_ids': ['test_pacs_1'],
    'query_level': 'STUDY'
})

# Production environment query (requires pacs_query_prod permission)
response = requests.post('/api/pacs/query', json={
    'environment': 'prod',
    'pacs_ids': ['prod_pacs_1'],
    'query_level': 'STUDY'
})
```

## Troubleshooting

### Common Issues

1. **Authentication Not Working**:
   - Check `auth_enabled` in `config/auth_config.json`
   - Verify user exists in `config/users.json`
   - Check password hashing

2. **AD Authentication Fails**:
   - Verify AD server connectivity
   - Check bind DN and password
   - Verify search base and filter
   - Check user group memberships

3. **SAML Authentication Fails**:
   - Verify IdP configuration
   - Check certificate validity
   - Verify ACS URL configuration
   - Check attribute mappings

4. **Permission Denied**:
   - Check user permissions in `config/users.json`
   - Verify group mappings in `config/group_mappings.json`
   - Check environment-specific permissions

### Debug Mode

Enable debug logging:

```bash
export FLASK_DEBUG=1
python3 app.py
```

Check application logs for authentication details.

## Security Considerations

1. **Change Default Passwords**: Always change default admin password
2. **Use HTTPS**: Enable SSL/TLS in production
3. **Secure Configuration**: Protect configuration files with appropriate permissions
4. **Regular Updates**: Keep dependencies updated
5. **Audit Logging**: Monitor authentication events
6. **Environment Separation**: Use different credentials for test/prod environments

## Migration Guide

### From No Auth to Local Auth

1. Create `config/auth_config.json` with `auth_enabled: true`
2. Restart application
3. Login with default admin credentials
4. Create additional users as needed

### From Local Auth to Enterprise Auth

1. Configure enterprise authentication settings
2. Set up group mappings
3. Test with enterprise credentials
4. Migrate existing users if needed

### From Legacy Permissions to Environment-Specific

1. Update user permissions to include environment-specific ones
2. Test access in each environment
3. Remove legacy permissions once confirmed working
