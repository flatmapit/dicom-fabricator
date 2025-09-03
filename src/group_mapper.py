#!/usr/bin/env python3
"""
Group Mapping Module for DICOM Fabricator
Maps enterprise groups to application permissions and roles
Copyright (c) 2025 Christopher Gentle <chris@flatmapit.com>
"""

import os
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict

@dataclass
class GroupMapping:
    """Group mapping configuration"""
    enterprise_group: str
    application_role: str
    is_active: bool = True
    description: str = ""

class GroupMapper:
    """Maps enterprise groups to application permissions and roles"""
    
    def __init__(self, config_file: str = 'config/group_mappings.json'):
        self.config_file = config_file
        self.mappings: Dict[str, GroupMapping] = {}
        self.default_role: str = 'test_read'
        self.require_df_prefix: bool = True
        
        self.load_mappings()
        self._create_default_mappings()
    
    def _create_default_mappings(self):
        """Create default group mappings if none exist"""
        if not self.mappings:
            default_mappings = [
                GroupMapping(
                    enterprise_group="DF-Admin",
                    application_role="admin",
                    description="Full system administration access"
                ),
                GroupMapping(
                    enterprise_group="DF-TestWrite",
                    application_role="test_write",
                    description="Test environment write access - can query, C-STORE and C-MOVE to test PACS"
                ),
                GroupMapping(
                    enterprise_group="DF-TestRead",
                    application_role="test_read",
                    description="Test environment read access - can view status and query test PACS"
                ),
                GroupMapping(
                    enterprise_group="DF-ProdWrite",
                    application_role="prod_write",
                    description="Production environment write access - can query, C-STORE and C-MOVE to production PACS"
                ),
                GroupMapping(
                    enterprise_group="DF-ProdRead",
                    application_role="prod_read",
                    description="Production environment read access - can view status and query production PACS"
                )
            ]
            
            for mapping in default_mappings:
                self.mappings[mapping.enterprise_group] = mapping
            
            self.save_mappings()
    
    def map_groups_to_role(self, groups: List[str]) -> str:
        """Map enterprise groups to application role with DF- prefix support"""
        # Filter for DF- prefixed groups if required
        if self.require_df_prefix:
            df_groups = [group for group in groups if group.startswith('DF-')]
            if not df_groups:
                return self.default_role
            groups = df_groups
        
        # Role priority (highest to lowest)
        role_priority = {
            'admin': 5,
            'prod_write': 4,
            'prod_read': 3,
            'test_write': 2,
            'test_read': 1
        }
        
        highest_priority = 0
        assigned_role = self.default_role
        
        for group in groups:
            mapping = self.mappings.get(group)
            if mapping and mapping.is_active:
                role = mapping.application_role
                priority = role_priority.get(role, 0)
                
                if priority > highest_priority:
                    highest_priority = priority
                    assigned_role = role
        
        return assigned_role
    
    def map_groups_to_permissions(self, groups: List[str]) -> Dict[str, any]:
        """Map enterprise groups to application permissions and role (legacy support)"""
        role = self.map_groups_to_role(groups)
        
        # Convert role to legacy permissions format for backward compatibility
        from src.auth import RoleManager
        capabilities = RoleManager.get_role_capabilities(role)
        
        # Map capabilities back to legacy permissions
        legacy_permissions = []
        for capability, has_access in capabilities.items():
            if has_access:
                # Find legacy permissions that map to this capability
                for perm, cap in RoleManager.PERMISSION_TO_CAPABILITY.items():
                    if cap == capability and perm not in legacy_permissions:
                        legacy_permissions.append(perm)
        
        return {
            'role': role,
            'permissions': legacy_permissions
        }
    
    def add_mapping(self, enterprise_group: str, application_role: str, 
                   description: str = "") -> bool:
        """Add a new group mapping"""
        if enterprise_group in self.mappings:
            return False
        
        mapping = GroupMapping(
            enterprise_group=enterprise_group,
            application_role=application_role,
            description=description
        )
        
        self.mappings[enterprise_group] = mapping
        self.save_mappings()
        return True
    
    def update_mapping(self, enterprise_group: str, **kwargs) -> bool:
        """Update an existing group mapping"""
        if enterprise_group not in self.mappings:
            return False
        
        mapping = self.mappings[enterprise_group]
        
        if 'application_role' in kwargs:
            mapping.application_role = kwargs['application_role']
        if 'permissions' in kwargs:
            mapping.permissions = kwargs['permissions']
        if 'is_active' in kwargs:
            mapping.is_active = kwargs['is_active']
        if 'description' in kwargs:
            mapping.description = kwargs['description']
        
        self.save_mappings()
        return True
    
    def delete_mapping(self, enterprise_group: str) -> bool:
        """Delete a group mapping"""
        if enterprise_group not in self.mappings:
            return False
        
        del self.mappings[enterprise_group]
        self.save_mappings()
        return True
    
    def get_mapping(self, enterprise_group: str) -> Optional[GroupMapping]:
        """Get a specific group mapping"""
        return self.mappings.get(enterprise_group)
    
    def get_all_mappings(self) -> List[GroupMapping]:
        """Get all group mappings"""
        return list(self.mappings.values())
    
    def get_active_mappings(self) -> List[GroupMapping]:
        """Get all active group mappings"""
        return [mapping for mapping in self.mappings.values() if mapping.is_active]
    
    def load_mappings(self):
        """Load group mappings from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load default settings
                    self.default_role = data.get('default_role', 'user')
                    self.default_permissions = data.get('default_permissions', ['dicom_view', 'pacs_query_test'])
                    
                    # Load mappings
                    mappings_data = data.get('mappings', {})
                    self.mappings = {}
                    
                    for group_name, mapping_data in mappings_data.items():
                        mapping = GroupMapping(
                            enterprise_group=mapping_data['enterprise_group'],
                            application_role=mapping_data['application_role'],
                            permissions=mapping_data['permissions'],
                            is_active=mapping_data.get('is_active', True),
                            description=mapping_data.get('description', '')
                        )
                        self.mappings[group_name] = mapping
                        
        except Exception as e:
            print(f"Error loading group mappings: {e}")
            self.mappings = {}
    
    def save_mappings(self):
        """Save group mappings to configuration file"""
        try:
            config = {
                'default_role': self.default_role,
                'default_permissions': self.default_permissions,
                'mappings': {
                    mapping.enterprise_group: asdict(mapping)
                    for mapping in self.mappings.values()
                }
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Error saving group mappings: {e}")
    
    def get_available_roles(self) -> List[str]:
        """Get list of available application roles"""
        return ['admin', 'operator', 'pacs_admin', 'patient_manager', 'test_user', 'prod_user', 'test_viewer', 'prod_viewer', 'viewer', 'user']
    
    def get_available_permissions(self) -> List[str]:
        """Get list of available permissions"""
        return [
            # DICOM permissions
            'dicom_generate', 'dicom_view', 'dicom_export',
            # PACS permissions - Test Environment
            'pacs_query_test', 'pacs_move_test', 'pacs_configure_test', 'pacs_test_test',
            # PACS permissions - Production Environment
            'pacs_query_prod', 'pacs_move_prod', 'pacs_configure_prod', 'pacs_test_prod',
            # PACS permissions - Legacy (for backward compatibility)
            'pacs_query', 'pacs_move', 'pacs_configure', 'pacs_test',
            # Patient permissions
            'patients_view', 'patients_create', 'patients_edit', 'patients_delete',
            # System permissions
            'system_admin', 'system_config', 'system_logs'
        ]

# Global group mapper instance
group_mapper = GroupMapper()

def get_group_mapper() -> GroupMapper:
    """Get the global group mapper instance"""
    return group_mapper
