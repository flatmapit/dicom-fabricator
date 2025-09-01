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
    permissions: List[str]
    is_active: bool = True
    description: str = ""

class GroupMapper:
    """Maps enterprise groups to application permissions and roles"""
    
    def __init__(self, config_file: str = 'config/group_mappings.json'):
        self.config_file = config_file
        self.mappings: Dict[str, GroupMapping] = {}
        self.default_role: str = 'user'
        self.default_permissions: List[str] = ['dicom_view', 'pacs_query_test']
        
        self.load_mappings()
        self._create_default_mappings()
    
    def _create_default_mappings(self):
        """Create default group mappings if none exist"""
        if not self.mappings:
            default_mappings = [
                GroupMapping(
                    enterprise_group="DICOM_Administrators",
                    application_role="admin",
                    permissions=["system_admin"],
                    description="Full system administration access"
                ),
                GroupMapping(
                    enterprise_group="DICOM_Operators",
                    application_role="operator",
                    permissions=[
                        "dicom_generate", "dicom_view", "dicom_export",
                        "pacs_query_test", "pacs_move_test", "pacs_configure_test", "pacs_test_test",
                        "pacs_query_prod", "pacs_move_prod", "pacs_configure_prod", "pacs_test_prod",
                        "patients_view", "patients_create", "patients_edit"
                    ],
                    description="Full operational access to DICOM features in all environments"
                ),
                GroupMapping(
                    enterprise_group="DICOM_Viewers",
                    application_role="viewer",
                    permissions=[
                        "dicom_view", "pacs_query_test", "pacs_query_prod", "patients_view"
                    ],
                    description="Read-only access to DICOM data in all environments"
                ),
                GroupMapping(
                    enterprise_group="PACS_Administrators",
                    application_role="pacs_admin",
                    permissions=[
                        "pacs_query_test", "pacs_move_test", "pacs_configure_test", "pacs_test_test",
                        "pacs_query_prod", "pacs_move_prod", "pacs_configure_prod", "pacs_test_prod",
                        "system_config"
                    ],
                    description="PACS management and configuration access in all environments"
                ),
                GroupMapping(
                    enterprise_group="Patient_Managers",
                    application_role="patient_manager",
                    permissions=[
                        "patients_view", "patients_create", "patients_edit", "patients_delete",
                        "dicom_view"
                    ],
                    description="Patient registry management access"
                ),
                GroupMapping(
                    enterprise_group="Test_Environment_Users",
                    application_role="test_user",
                    permissions=[
                        "dicom_view", "pacs_query_test", "pacs_move_test", "patients_view"
                    ],
                    description="Test environment access only - read and write"
                ),
                GroupMapping(
                    enterprise_group="Test_Environment_Viewers",
                    application_role="test_viewer",
                    permissions=[
                        "dicom_view", "pacs_query_test", "patients_view"
                    ],
                    description="Test environment read-only access"
                ),
                GroupMapping(
                    enterprise_group="Production_Environment_Users",
                    application_role="prod_user",
                    permissions=[
                        "dicom_view", "pacs_query_prod", "pacs_move_prod", "patients_view"
                    ],
                    description="Production environment access only - read and write"
                ),
                GroupMapping(
                    enterprise_group="Production_Environment_Viewers",
                    application_role="prod_viewer",
                    permissions=[
                        "dicom_view", "pacs_query_prod", "patients_view"
                    ],
                    description="Production environment read-only access"
                )
            ]
            
            for mapping in default_mappings:
                self.mappings[mapping.enterprise_group] = mapping
            
            self.save_mappings()
    
    def map_groups_to_permissions(self, groups: List[str]) -> Dict[str, any]:
        """Map enterprise groups to application permissions and role"""
        all_permissions: Set[str] = set()
        highest_role = self.default_role
        
        for group in groups:
            mapping = self.mappings.get(group)
            if mapping and mapping.is_active:
                # Add permissions
                all_permissions.update(mapping.permissions)
                
                # Determine highest role (admin > operator > pacs_admin > patient_manager > viewer > user)
                role_priority = {
                    'admin': 6,
                    'operator': 5,
                    'pacs_admin': 4,
                    'patient_manager': 3,
                    'test_user': 2,
                    'prod_user': 2,
                    'test_viewer': 1,
                    'prod_viewer': 1,
                    'viewer': 1,
                    'user': 1
                }
                
                current_priority = role_priority.get(mapping.application_role, 1)
                highest_priority = role_priority.get(highest_role, 1)
                
                if current_priority > highest_priority:
                    highest_role = mapping.application_role
        
        # Add default permissions if no specific permissions found
        if not all_permissions:
            all_permissions.update(self.default_permissions)
        
        return {
            'role': highest_role,
            'permissions': list(all_permissions)
        }
    
    def add_mapping(self, enterprise_group: str, application_role: str, 
                   permissions: List[str], description: str = "") -> bool:
        """Add a new group mapping"""
        if enterprise_group in self.mappings:
            return False
        
        mapping = GroupMapping(
            enterprise_group=enterprise_group,
            application_role=application_role,
            permissions=permissions,
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
