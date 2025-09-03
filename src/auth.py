#!/usr/bin/env python3
"""
Authentication and Authorization Module for DICOM Fabricator
Copyright (c) 2025 Christopher Gentle <chris@flatmapit.com>
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from functools import wraps
from flask import request, session, redirect, url_for, flash, current_app
import jwt

@dataclass
class User:
    """User data model with simplified role-based permissions"""
    username: str
    password_hash: str
    email: str
    role: str  # 'admin', 'test_write', 'test_read', 'prod_write', 'prod_read'
    is_active: bool = True
    created_at: str = None
    last_login: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary for JSON serialization"""
        return asdict(self)
    
    def set_password(self, password: str):
        """Set user password with SHA-256 hashing"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches stored hash"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create user from dictionary"""
        return cls(**data)

class RoleManager:
    """Manages role-based permissions for DICOM Fabricator"""
    
    # Define role capabilities
    ROLE_CAPABILITIES = {
        'admin': {
            'user_management': True,
            'dicom_generation': True,
            'pacs_view': True,
            'test_query': True,
            'test_write': True,
            'prod_query': True,
            'prod_write': True,
            'pacs_admin': True
        },
        'test_write': {
            'user_management': False,
            'dicom_generation': True,
            'pacs_view': True,
            'test_query': True,
            'test_write': True,
            'prod_query': False,
            'prod_write': False,
            'pacs_admin': False
        },
        'test_read': {
            'user_management': False,
            'dicom_generation': True,
            'pacs_view': True,
            'test_query': True,
            'test_write': False,
            'prod_query': False,
            'prod_write': False,
            'pacs_admin': False
        },
        'prod_write': {
            'user_management': False,
            'dicom_generation': True,
            'pacs_view': True,
            'test_query': False,
            'test_write': False,
            'prod_query': True,
            'prod_write': True,
            'pacs_admin': False
        },
        'prod_read': {
            'user_management': False,
            'dicom_generation': True,
            'pacs_view': True,
            'test_query': False,
            'test_write': False,
            'prod_query': True,
            'prod_write': False,
            'pacs_admin': False
        }
    }
    
    # Legacy permission to role capability mapping
    PERMISSION_TO_CAPABILITY = {
        'user_manage': 'user_management',
        'dicom_generate': 'dicom_generation',
        'dicom_view': 'dicom_generation',
        'pacs_query_test': 'test_query',
        'pacs_move_test': 'test_write',
        'pacs_store_test': 'test_write',
        'pacs_configure_test': 'pacs_admin',
        'pacs_query_prod': 'prod_query',
        'pacs_move_prod': 'prod_write',
        'pacs_store_prod': 'prod_write',
        'pacs_configure_prod': 'pacs_admin'
    }
    
    @classmethod
    def has_capability(cls, role: str, capability: str) -> bool:
        """Check if a role has a specific capability"""
        if role not in cls.ROLE_CAPABILITIES:
            return False
        return cls.ROLE_CAPABILITIES[role].get(capability, False)
    
    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        """Check if a role has a specific permission (legacy support)"""
        capability = cls.PERMISSION_TO_CAPABILITY.get(permission)
        if not capability:
            return False
        return cls.has_capability(role, capability)
    
    @classmethod
    def get_role_capabilities(cls, role: str) -> Dict[str, bool]:
        """Get all capabilities for a role"""
        return cls.ROLE_CAPABILITIES.get(role, {})
    
    @classmethod
    def get_available_roles(cls) -> List[str]:
        """Get list of available roles"""
        return list(cls.ROLE_CAPABILITIES.keys())
    
    @classmethod
    def get_role_description(cls, role: str) -> str:
        """Get human-readable description of a role"""
        descriptions = {
            'admin': 'Full system access - can do anything',
            'test_write': 'Test environment write access - can query, C-STORE and C-MOVE to test PACS',
            'test_read': 'Test environment read access - can view status and query test PACS',
            'prod_write': 'Production environment write access - can query, C-STORE and C-MOVE to production PACS',
            'prod_read': 'Production environment read access - can view status and query production PACS'
        }
        return descriptions.get(role, 'Unknown role')

@dataclass
class Permission:
    """Permission data model (legacy support)"""
    name: str
    description: str
    category: str
    is_active: bool = True

class AuthManager:
    """Authentication and authorization manager"""
    
    def __init__(self, config_file: str = 'config/auth_config.json'):
        self.config_file = config_file
        self.users: Dict[str, User] = {}
        self.permissions: Dict[str, Permission] = {}
        self.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
        self.auth_enabled = True
        self.enterprise_auth_enabled = False
        self.default_user_permissions = ['dicom_view', 'pacs_query_test']
        
        # Initialize default permissions
        self._init_default_permissions()
        
        # Load configuration
        self.load_config()
        
        # Load users from config
        self.load_users()
        
        # Create default admin user if no users exist and auth is enabled
        if self.auth_enabled and not self.users:
            self._create_default_admin()
    
    def _init_default_permissions(self):
        """Initialize default permissions for the application"""
        default_permissions = [
            # DICOM Generation permissions
            Permission("dicom_generate", "Generate DICOM studies", "dicom"),
            Permission("dicom_view", "View DICOM studies", "dicom"),
            Permission("dicom_export", "Export DICOM data", "dicom"),
            
            # PACS permissions - Test Environment
            Permission("pacs_query_test", "Query test PACS servers", "pacs_test"),
            Permission("pacs_move_test", "C-MOVE studies in test environment", "pacs_test"),
            Permission("pacs_configure_test", "Configure test PACS connections", "pacs_test"),
            Permission("pacs_test_test", "Test test PACS connections", "pacs_test"),
            
            # PACS permissions - Production Environment
            Permission("pacs_query_prod", "Query production PACS servers", "pacs_prod"),
            Permission("pacs_move_prod", "C-MOVE studies in production environment", "pacs_prod"),
            Permission("pacs_configure_prod", "Configure production PACS connections", "pacs_prod"),
            Permission("pacs_test_prod", "Test production PACS connections", "pacs_prod"),
            
            # PACS permissions - Legacy (for backward compatibility)
            Permission("pacs_query", "Query PACS servers (all environments)", "pacs"),
            Permission("pacs_move", "C-MOVE studies (all environments)", "pacs"),
            Permission("pacs_configure", "Configure PACS connections (all environments)", "pacs"),
            Permission("pacs_test", "Test PACS connections (all environments)", "pacs"),
            
            # Patient management permissions
            Permission("patients_view", "View patient registry", "patients"),
            Permission("patients_create", "Create new patients", "patients"),
            Permission("patients_edit", "Edit patient records", "patients"),
            Permission("patients_delete", "Delete patient records", "patients"),
            
            # System permissions
            Permission("system_admin", "Full system administration", "system"),
            Permission("system_config", "System configuration", "system"),
            Permission("system_logs", "View system logs", "system"),
        ]
        
        for perm in default_permissions:
            self.permissions[perm.name] = perm
    
    def _create_default_admin(self):
        """Create a default admin user"""
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin_user = User(
            username='admin',
            password_hash='',  # Will be set by set_password
            email='admin@dicom-fabricator.local',
            role='admin'
        )
        admin_user.set_password(admin_password)
        self.users['admin'] = admin_user
        self.save_users()
        print("⚠️  Default admin user created with username 'admin' and password 'admin123'")
        print("⚠️  Please change the default password immediately!")
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return self._hash_password(password) == password_hash
    
    def load_config(self):
        """Load authentication configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.auth_enabled = config.get('auth_enabled', True)
                    self.enterprise_auth_enabled = config.get('enterprise_auth_enabled', False)
                    self.default_user_permissions = config.get('default_user_permissions', ['dicom_view', 'pacs_query_test'])
        except Exception as e:
            print(f"Error loading auth config: {e}")
            # Use defaults
            self.auth_enabled = True
            self.enterprise_auth_enabled = False
            self.default_user_permissions = ['dicom_view', 'pacs_query_test']
    
    def save_config(self):
        """Save authentication configuration"""
        try:
            config = {
                'auth_enabled': self.auth_enabled,
                'enterprise_auth_enabled': self.enterprise_auth_enabled,
                'default_user_permissions': self.default_user_permissions
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Error saving auth config: {e}")
    
    def is_auth_enabled(self) -> bool:
        """Check if authentication is enabled"""
        return self.auth_enabled
    
    def is_enterprise_auth_enabled(self) -> bool:
        """Check if enterprise authentication is enabled"""
        return self.enterprise_auth_enabled
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        if not self.auth_enabled:
            # Return a default user when auth is disabled
            return self._get_default_user()
        
        user = self.users.get(username)
        if user and user.is_active and user.check_password(password):
            # Update last login
            user.last_login = datetime.now().isoformat()
            self.save_users()
            return user
        return None
    
    def _get_default_user(self) -> User:
        """Get default user when authentication is disabled"""
        return User(
            username='anonymous',
            password_hash='',
            email='anonymous@dicom-fabricator.local',
            role='test_read'  # Default role for anonymous users
        )
    
    def create_user(self, username: str, password: str, email: str, role: str = 'test_read') -> bool:
        """Create a new user with role-based permissions"""
        if username in self.users:
            return False
        
        # Validate role
        if role not in RoleManager.get_available_roles():
            role = 'test_read'  # Default role
        
        user = User(
            username=username,
            password_hash='',  # Will be set by set_password
            email=email,
            role=role
        )
        
        user.set_password(password)
        
        self.users[username] = user
        self.save_users()
        return True
    
    def update_user(self, username: str, **kwargs) -> bool:
        """Update user information"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        
        # Update allowed fields
        if 'email' in kwargs:
            user.email = kwargs['email']
        if 'role' in kwargs:
            user.role = kwargs['role']
        # Permissions are now handled by roles, so we ignore this field
        if 'is_active' in kwargs:
            user.is_active = kwargs['is_active']
        if 'password' in kwargs:
            user.set_password(kwargs['password'])
        
        self.save_users()
        return True
    
    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        if username not in self.users:
            return False
        
        del self.users[username]
        self.save_users()
        return True
    
    def has_permission(self, user: User, permission: str) -> bool:
        """Check if user has a specific permission (legacy support)"""
        if not self.auth_enabled:
            return True  # All permissions allowed when auth is disabled
        
        if not user or not user.is_active:
            return False
        
        # Use role-based permission checking
        return RoleManager.has_permission(user.role, permission)
    
    def has_any_permission(self, user: User, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions"""
        if not self.auth_enabled:
            return True  # All permissions allowed when auth is disabled
        
        return any(self.has_permission(user, perm) for perm in permissions)
    
    def has_all_permissions(self, user: User, permissions: List[str]) -> bool:
        """Check if user has all of the specified permissions"""
        if not self.auth_enabled:
            return True  # All permissions allowed when auth is disabled
        
        return all(self.has_permission(user, perm) for perm in permissions)
    
    def has_environment_access(self, user: User, environment: str, access_type: str = 'read') -> bool:
        """Check if user has access to a specific environment (test/prod)"""
        if not self.auth_enabled:
            return True
        
        if not user or not user.is_active:
            return False
        
        # Admin role has all permissions
        if user.role == 'admin':
            return True
        
        # Check environment-specific permissions
        if environment.lower() == 'test':
            if access_type.lower() == 'read':
                return self.has_permission(user, 'pacs_query_test')
            elif access_type.lower() == 'write':
                return self.has_permission(user, 'pacs_move_test')
        elif environment.lower() == 'prod':
            if access_type.lower() == 'read':
                return self.has_permission(user, 'pacs_query_prod')
            elif access_type.lower() == 'write':
                return self.has_permission(user, 'pacs_move_prod')
        
        # Fallback to legacy permissions
        if access_type.lower() == 'read':
            return self.has_permission(user, 'pacs_query')
        elif access_type.lower() == 'write':
            return self.has_permission(user, 'pacs_move')
        
        return False
    
    def get_users(self) -> List[User]:
        """Get all users"""
        return list(self.users.values())
    
    def get_user(self, username: str) -> Optional[User]:
        """Get a specific user"""
        return self.users.get(username)
    
    def get_permissions(self) -> List[Permission]:
        """Get all permissions"""
        return list(self.permissions.values())
    
    def load_users(self):
        """Load users from configuration file"""
        try:
            users_file = self.config_file.replace('auth_config.json', 'users.json')
            if os.path.exists(users_file):
                with open(users_file, 'r') as f:
                    data = json.load(f)
                    self.users = {
                        username: User.from_dict(user_data)
                        for username, user_data in data.items()
                    }
        except Exception as e:
            print(f"Error loading users: {e}")
            self.users = {}
    
    def save_users(self):
        """Save users to configuration file"""
        try:
            users_file = self.config_file.replace('auth_config.json', 'users.json')
            os.makedirs(os.path.dirname(users_file), exist_ok=True)
            with open(users_file, 'w') as f:
                json.dump({
                    username: user.to_dict()
                    for username, user in self.users.items()
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")

# Global auth manager instance
auth_manager = AuthManager()

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_manager.is_auth_enabled():
            return f(*args, **kwargs)  # Skip authentication check if disabled
        
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission: str):
    """Decorator to require specific permission for routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not auth_manager.is_auth_enabled():
                return f(*args, **kwargs)  # Skip permission check if auth disabled
            
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user = auth_manager.get_user(session['user_id'])
            if not auth_manager.has_permission(user, permission):
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def any_permission_required(permissions: List[str]):
    """Decorator to require any of the specified permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not auth_manager.is_auth_enabled():
                return f(*args, **kwargs)  # Skip permission check if auth disabled
            
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user = auth_manager.get_user(session['user_id'])
            if not auth_manager.has_any_permission(user, permissions):
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def all_permissions_required(permissions: List[str]):
    """Decorator to require all of the specified permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not auth_manager.is_auth_enabled():
                return f(*args, **kwargs)  # Skip permission check if auth disabled
            
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user = auth_manager.get_user(session['user_id'])
            if not auth_manager.has_all_permissions(user, permissions):
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def environment_access_required(environment: str, access_type: str = 'read'):
    """Decorator to require environment-specific access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not auth_manager.is_auth_enabled():
                return f(*args, **kwargs)  # Skip permission check if auth disabled
            
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user = auth_manager.get_user(session['user_id'])
            if not auth_manager.has_environment_access(user, environment, access_type):
                flash(f'Access denied. Insufficient {access_type} permissions for {environment} environment.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user() -> Optional[User]:
    """Get the currently logged in user"""
    if not auth_manager.is_auth_enabled():
        return auth_manager._get_default_user()
    
    if 'user_id' not in session:
        return None
    return auth_manager.get_user(session['user_id'])

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    if not auth_manager.is_auth_enabled():
        return True  # Always authenticated when auth is disabled
    return 'user_id' in session

def login_user(user: User):
    """Log in a user"""
    session['user_id'] = user.username
    session['user_role'] = user.role
    # Store role capabilities instead of individual permissions
    from src.auth import RoleManager
    session['user_capabilities'] = RoleManager.get_role_capabilities(user.role)

def logout_user():
    """Log out the current user"""
    session.clear()

def generate_jwt_token(user: User, expires_in: int = 3600) -> str:
    """Generate a JWT token for API authentication"""
    payload = {
        'user_id': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, auth_manager.secret_key, algorithm='HS256')

def verify_jwt_token(token: str) -> Optional[Dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, auth_manager.secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
