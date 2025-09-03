#!/usr/bin/env python3
"""
Migration script to convert existing users from permission-based to role-based system
Copyright (c) 2025 Christopher Gentle <chris@flatmapit.com>
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth import AuthManager, User, RoleManager

def backup_users_file(users_file):
    """Create a backup of the users file"""
    if os.path.exists(users_file):
        backup_file = f"{users_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(users_file, backup_file)
        print(f"✓ Created backup: {backup_file}")
        return backup_file
    return None

def migrate_user_permissions_to_role(user_data):
    """Convert user permissions to appropriate role"""
    permissions = user_data.get('permissions', [])
    
    # Define permission to role mapping
    permission_to_role = {
        # Admin permissions
        'system_admin': 'admin',
        
        # Test environment permissions
        'pacs_query_test': 'test_read',
        'pacs_move_test': 'test_write',
        'pacs_store_test': 'test_write',
        'pacs_configure_test': 'admin',  # PACS config requires admin
        'pacs_test_test': 'test_read',
        
        # Production environment permissions
        'pacs_query_prod': 'prod_read',
        'pacs_move_prod': 'prod_write',
        'pacs_store_prod': 'prod_write',
        'pacs_configure_prod': 'admin',  # PACS config requires admin
        'pacs_test_prod': 'prod_read',
        
        # DICOM permissions (all roles have these)
        'dicom_generate': 'test_read',  # Default to test_read
        'dicom_view': 'test_read',
        'dicom_export': 'test_read',
        
        # Patient permissions (all roles have these)
        'patients_view': 'test_read',
        'patients_create': 'test_read',
        'patients_edit': 'test_read',
        'patients_delete': 'test_read',
        
        # System config
        'system_config': 'admin'
    }
    
    # Determine the highest role based on permissions
    role_priority = {
        'admin': 5,
        'prod_write': 4,
        'prod_read': 3,
        'test_write': 2,
        'test_read': 1
    }
    
    highest_priority = 0
    assigned_role = 'test_read'  # Default role
    
    for permission in permissions:
        role = permission_to_role.get(permission, 'test_read')
        priority = role_priority.get(role, 0)
        
        if priority > highest_priority:
            highest_priority = priority
            assigned_role = role
    
    return assigned_role

def migrate_users():
    """Migrate all users from permission-based to role-based system"""
    print("🔄 Starting user migration from permission-based to role-based system...")
    
    # Initialize auth manager
    auth_manager = AuthManager()
    users_file = auth_manager.users_file
    
    # Create backup
    backup_file = backup_users_file(users_file)
    
    if not os.path.exists(users_file):
        print("ℹ️  No users file found, nothing to migrate")
        return
    
    # Load existing users
    try:
        with open(users_file, 'r') as f:
            users_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading users file: {e}")
        return
    
    migrated_count = 0
    skipped_count = 0
    
    print(f"📊 Found {len(users_data)} users to migrate")
    
    # Migrate each user
    for username, user_data in users_data.items():
        print(f"\n👤 Migrating user: {username}")
        
        # Check if user already has a role (skip if already migrated)
        if 'role' in user_data and user_data['role'] in RoleManager.get_available_roles():
            print(f"   ⏭️  Already has valid role: {user_data['role']}")
            skipped_count += 1
            continue
        
        # Get old permissions
        old_permissions = user_data.get('permissions', [])
        print(f"   📋 Old permissions: {old_permissions}")
        
        # Determine new role
        new_role = migrate_user_permissions_to_role(user_data)
        print(f"   🎭 New role: {new_role}")
        
        # Update user data
        user_data['role'] = new_role
        
        # Remove permissions field (no longer needed)
        if 'permissions' in user_data:
            del user_data['permissions']
        
        migrated_count += 1
        print(f"   ✅ Migrated successfully")
    
    # Save migrated users
    try:
        with open(users_file, 'w') as f:
            json.dump(users_data, f, indent=2)
        print(f"\n💾 Saved migrated users to {users_file}")
    except Exception as e:
        print(f"❌ Error saving users file: {e}")
        return
    
    # Summary
    print(f"\n📈 Migration Summary:")
    print(f"   ✅ Migrated: {migrated_count} users")
    print(f"   ⏭️  Skipped: {skipped_count} users")
    print(f"   💾 Backup: {backup_file}")
    
    if migrated_count > 0:
        print(f"\n🎉 Migration completed successfully!")
        print(f"   Users now use role-based permissions:")
        for role in RoleManager.get_available_roles():
            description = RoleManager.get_role_description(role)
            print(f"   - {role}: {description}")
    else:
        print(f"\nℹ️  No users needed migration")

def main():
    """Main migration function"""
    print("=" * 60)
    print("DICOM Fabricator - User Migration Script")
    print("Permission-based → Role-based System")
    print("=" * 60)
    
    try:
        migrate_users()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
