#!/usr/bin/env python3
"""
Authentication Test Script for DICOM Fabricator
Tests different authentication configurations and scenarios
"""

import os
import sys
import json
import requests
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth import AuthManager, User
from enterprise_auth import EnterpriseAuthManager
from group_mapper import GroupMapper

def test_no_auth_mode():
    """Test running without authentication"""
    print("🔧 Testing No Authentication Mode...")
    
    # Create config for no authentication
    config = {
        "auth_enabled": False,
        "enterprise_auth_enabled": False,
        "default_user_permissions": [
            "dicom_view",
            "pacs_query_test",
            "pacs_query_prod"
        ]
    }
    
    os.makedirs('config', exist_ok=True)
    with open('config/auth_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Test auth manager
    auth_manager = AuthManager('config/auth_config.json')
    
    assert not auth_manager.is_auth_enabled()
    
    default_user = auth_manager._get_default_user()
    assert default_user.username == 'anonymous'
    assert 'dicom_view' in default_user.permissions
    assert 'pacs_query_test' in default_user.permissions
    
    print("✅ No authentication mode works correctly")

def test_local_auth_mode():
    """Test local authentication"""
    print("🔧 Testing Local Authentication Mode...")
    
    # Create config for local authentication
    config = {
        "auth_enabled": True,
        "enterprise_auth_enabled": False
    }
    
    with open('config/auth_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Test auth manager
    auth_manager = AuthManager('config/auth_config.json')
    
    assert auth_manager.is_auth_enabled()
    
    # Test default admin user
    admin_user = auth_manager.authenticate('admin', 'admin123')
    assert admin_user is not None
    assert admin_user.username == 'admin'
    assert admin_user.role == 'admin'
    assert 'system_admin' in admin_user.permissions
    
    # Test invalid credentials
    invalid_user = auth_manager.authenticate('admin', 'wrongpassword')
    assert invalid_user is None
    
    print("✅ Local authentication mode works correctly")

def test_environment_permissions():
    """Test environment-specific permissions"""
    print("🔧 Testing Environment-Specific Permissions...")
    
    # Create test users with different permissions
    auth_manager = AuthManager('config/auth_config.json')
    
    # Test environment user
    test_user = User(
        username='testuser',
        password_hash='',
        email='test@company.com',
        role='test_user',
        permissions=['dicom_view', 'pacs_query_test', 'pacs_move_test']
    )
    
    # Test production user
    prod_user = User(
        username='produser',
        password_hash='',
        email='prod@company.com',
        role='prod_user',
        permissions=['dicom_view', 'pacs_query_prod', 'pacs_move_prod']
    )
    
    # Test environment access
    assert auth_manager.has_environment_access(test_user, 'test', 'read')
    assert auth_manager.has_environment_access(test_user, 'test', 'write')
    assert not auth_manager.has_environment_access(test_user, 'prod', 'read')
    assert not auth_manager.has_environment_access(test_user, 'prod', 'write')
    
    assert auth_manager.has_environment_access(prod_user, 'prod', 'read')
    assert auth_manager.has_environment_access(prod_user, 'prod', 'write')
    assert not auth_manager.has_environment_access(prod_user, 'test', 'read')
    assert not auth_manager.has_environment_access(prod_user, 'test', 'write')
    
    print("✅ Environment-specific permissions work correctly")

def test_group_mapping():
    """Test group mapping functionality"""
    print("🔧 Testing Group Mapping...")
    
    group_mapper = GroupMapper('config/group_mappings.json')
    
    # Test default mappings
    mappings = group_mapper.get_all_mappings()
    assert len(mappings) > 0
    
    # Test group to permission mapping
    test_groups = ['DICOM_Administrators']
    result = group_mapper.map_groups_to_permissions(test_groups)
    assert result['role'] == 'admin'
    assert 'system_admin' in result['permissions']
    
    # Test multiple groups
    test_groups = ['Test_Environment_Users', 'Production_Environment_Viewers']
    result = group_mapper.map_groups_to_permissions(test_groups)
    assert 'pacs_query_test' in result['permissions']
    assert 'pacs_query_prod' in result['permissions']
    
    print("✅ Group mapping works correctly")

def test_enterprise_auth_config():
    """Test enterprise authentication configuration"""
    print("🔧 Testing Enterprise Authentication Configuration...")
    
    # Create sample enterprise auth config
    config = {
        "active_directory": {
            "enabled": True,
            "server": "dc.company.com",
            "port": 389,
            "use_ssl": False,
            "use_ntlm": True,
            "bind_dn": "CN=ServiceAccount,OU=ServiceAccounts,DC=company,DC=com",
            "bind_password": "test-password",
            "search_base": "DC=company,DC=com"
        },
        "saml": {
            "enabled": True,
            "idp_entity_id": "https://sts.windows.net/test-tenant/",
            "idp_sso_url": "https://login.microsoftonline.com/test-tenant/saml2"
        }
    }
    
    os.makedirs('config', exist_ok=True)
    with open('config/enterprise_auth.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Test enterprise auth manager
    enterprise_auth_manager = EnterpriseAuthManager('config/enterprise_auth.json')
    
    assert enterprise_auth_manager.is_method_enabled('ad')
    assert enterprise_auth_manager.is_method_enabled('saml')
    
    print("✅ Enterprise authentication configuration works correctly")

def test_permission_decorators():
    """Test permission decorators"""
    print("🔧 Testing Permission Decorators...")
    
    from auth import permission_required, environment_access_required
    
    # Test that decorators can be created
    test_decorator = permission_required('dicom_view')
    assert callable(test_decorator)
    
    env_decorator = environment_access_required('test', 'read')
    assert callable(env_decorator)
    
    print("✅ Permission decorators work correctly")

def cleanup():
    """Clean up test files"""
    print("🧹 Cleaning up test files...")
    
    test_files = [
        'config/auth_config.json',
        'config/enterprise_auth.json',
        'config/group_mappings.json',
        'config/users.json'
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Remove config directory if empty
    if os.path.exists('config') and not os.listdir('config'):
        os.rmdir('config')

def main():
    """Run all authentication tests"""
    print("🚀 Starting Authentication System Tests\n")
    
    try:
        test_no_auth_mode()
        test_local_auth_mode()
        test_environment_permissions()
        test_group_mapping()
        test_enterprise_auth_config()
        test_permission_decorators()
        
        print("\n🎉 All authentication tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        cleanup()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
