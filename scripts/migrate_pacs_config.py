#!/usr/bin/env python3
"""
Migration script for PACS configurations to new AE title structure
"""

import json
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pacs_config import PacsConfigManager, PacsConfiguration


def migrate_pacs_configs():
    """Migrate existing PACS configurations to new structure"""
    
    config_path = project_root / "data" / "pacs_config.json"
    backup_path = project_root / "data" / "pacs_config.json.backup"
    
    print("PACS Configuration Migration Script")
    print("=" * 40)
    
    # Check if config file exists
    if not config_path.exists():
        print("No existing PACS configuration found. Nothing to migrate.")
        return
    
    # Create backup
    print(f"Creating backup: {backup_path}")
    with open(config_path, 'r') as f:
        backup_data = f.read()
    with open(backup_path, 'w') as f:
        f.write(backup_data)
    
    # Load existing configurations
    print("Loading existing configurations...")
    with open(config_path, 'r') as f:
        old_configs = json.load(f)
    
    print(f"Found {len(old_configs)} existing configurations")
    
    # Migrate each configuration
    migrated_configs = {}
    for config_id, config_data in old_configs.items():
        print(f"Migrating: {config_data.get('name', 'Unknown')}")
        
        # Extract old fields
        old_aet = config_data.get('aet', 'DICOMFAB')
        old_aec = config_data.get('aec', 'ORTHANC')
        
        # Create new configuration structure
        new_config = {
            'id': config_id,
            'name': config_data.get('name', 'Unknown PACS'),
            'description': config_data.get('description', ''),
            'host': config_data.get('host', 'localhost'),
            'port': config_data.get('port', 4242),
            'aet_find': old_aet,  # Migrate old aet to aet_find
            'aet_store': old_aet,  # Set aet_store to same value initially
            'aet_echo': old_aet,   # Set aet_echo to same value initially
            'aec': old_aec,
            'environment': config_data.get('environment', 'test'),
            'is_default': config_data.get('is_default', False),
            'is_active': config_data.get('is_active', True),
            'created_date': config_data.get('created_date', ''),
            'modified_date': config_data.get('modified_date', ''),
            'last_tested': config_data.get('last_tested', ''),
            'test_status': config_data.get('test_status', 'unknown'),
            'test_message': config_data.get('test_message', ''),
            'move_routing': {}  # Empty routing table to be configured manually
        }
        
        migrated_configs[config_id] = new_config
    
    # Pre-populate routing tables
    print("Pre-populating routing tables...")
    for source_id, source_config in migrated_configs.items():
        for dest_id, dest_config in migrated_configs.items():
            if source_id != dest_id:
                # Add empty entry for manual configuration
                source_config['move_routing'][dest_id] = ""
    
    # Save migrated configurations
    print(f"Saving migrated configurations to: {config_path}")
    with open(config_path, 'w') as f:
        json.dump(migrated_configs, f, indent=2)
    
    print("Migration completed successfully!")
    print(f"Backup saved to: {backup_path}")
    print("\nNext steps:")
    print("1. Review the migrated configurations")
    print("2. Configure C-STORE AE titles for PACS that should receive studies")
    print("3. Configure C-MOVE routing table entries")
    print("4. Test the new configuration")


if __name__ == "__main__":
    migrate_pacs_configs()
