#!/usr/bin/env python3
"""
Enterprise Authentication Module for DICOM Fabricator
Supports Microsoft Active Directory and SAML authentication
Copyright (c) 2025 Christopher Gentle <chris@flatmapit.com>
"""

import os
import json
import base64
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
import requests
from ldap3 import Server, Connection, ALL, NTLM, SIMPLE, ANONYMOUS
try:
    from onelogin.saml2.auth import OneLogin_Saml2_Auth
    from onelogin.saml2.utils import OneLogin_Saml2_Utils
    from onelogin.saml2.settings import OneLogin_Saml2_Settings
    SAML_AVAILABLE = True
except ImportError:
    SAML_AVAILABLE = False
    print("Warning: SAML dependencies not installed. SAML authentication will not be available.")
from flask import request, session, redirect, url_for, flash, current_app
import xml.etree.ElementTree as ET

@dataclass
class ADConfig:
    """Active Directory configuration"""
    server: str
    port: int = 389
    use_ssl: bool = False
    use_ntlm: bool = True
    bind_dn: str = None
    bind_password: str = None
    search_base: str = None
    search_filter: str = "(sAMAccountName={username})"
    user_attributes: List[str] = None
    group_attributes: List[str] = None
    
    def __post_init__(self):
        if self.user_attributes is None:
            self.user_attributes = ['sAMAccountName', 'mail', 'displayName', 'memberOf']
        if self.group_attributes is None:
            self.group_attributes = ['cn', 'description']

@dataclass
class SAMLConfig:
    """SAML configuration"""
    idp_entity_id: str
    idp_sso_url: str
    idp_slo_url: str = None
    idp_x509_cert: str = None
    sp_entity_id: str = None
    sp_acs_url: str = None
    sp_slo_url: str = None
    sp_x509_cert: str = None
    sp_private_key: str = None
    name_id_format: str = "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
    attribute_mapping: Dict[str, str] = None
    
    def __post_init__(self):
        if self.attribute_mapping is None:
            self.attribute_mapping = {
                'username': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name',
                'email': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
                'display_name': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name',
                'groups': 'http://schemas.microsoft.com/ws/2008/06/identity/claims/groups'
            }

class EnterpriseAuthManager:
    """Enterprise authentication manager supporting AD and SAML"""
    
    def __init__(self, config_file: str = 'config/enterprise_auth.json'):
        self.config_file = config_file
        self.ad_config: Optional[ADConfig] = None
        self.saml_config: Optional[SAMLConfig] = None
        self.enabled_methods: List[str] = []
        
        self.load_config()
    
    def load_config(self):
        """Load enterprise authentication configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                    # Load AD configuration
                    if config.get('active_directory', {}).get('enabled', False):
                        ad_data = config['active_directory']
                        self.ad_config = ADConfig(
                            server=ad_data['server'],
                            port=ad_data.get('port', 389),
                            use_ssl=ad_data.get('use_ssl', False),
                            use_ntlm=ad_data.get('use_ntlm', True),
                            bind_dn=ad_data.get('bind_dn'),
                            bind_password=ad_data.get('bind_password'),
                            search_base=ad_data.get('search_base'),
                            search_filter=ad_data.get('search_filter', "(sAMAccountName={username})"),
                            user_attributes=ad_data.get('user_attributes'),
                            group_attributes=ad_data.get('group_attributes')
                        )
                        self.enabled_methods.append('ad')
                    
                    # Load SAML configuration
                    if config.get('saml', {}).get('enabled', False):
                        saml_data = config['saml']
                        self.saml_config = SAMLConfig(
                            idp_entity_id=saml_data['idp_entity_id'],
                            idp_sso_url=saml_data['idp_sso_url'],
                            idp_slo_url=saml_data.get('idp_slo_url'),
                            idp_x509_cert=saml_data.get('idp_x509_cert'),
                            sp_entity_id=saml_data.get('sp_entity_id'),
                            sp_acs_url=saml_data.get('sp_acs_url'),
                            sp_slo_url=saml_data.get('sp_slo_url'),
                            sp_x509_cert=saml_data.get('sp_x509_cert'),
                            sp_private_key=saml_data.get('sp_private_key'),
                            name_id_format=saml_data.get('name_id_format'),
                            attribute_mapping=saml_data.get('attribute_mapping')
                        )
                        self.enabled_methods.append('saml')
                        
        except Exception as e:
            print(f"Error loading enterprise auth config: {e}")
    
    def save_config(self):
        """Save enterprise authentication configuration"""
        try:
            config = {
                'active_directory': {
                    'enabled': 'ad' in self.enabled_methods,
                    'server': self.ad_config.server if self.ad_config else '',
                    'port': self.ad_config.port if self.ad_config else 389,
                    'use_ssl': self.ad_config.use_ssl if self.ad_config else False,
                    'use_ntlm': self.ad_config.use_ntlm if self.ad_config else True,
                    'bind_dn': self.ad_config.bind_dn if self.ad_config else None,
                    'bind_password': self.ad_config.bind_password if self.ad_config else None,
                    'search_base': self.ad_config.search_base if self.ad_config else None,
                    'search_filter': self.ad_config.search_filter if self.ad_config else "(sAMAccountName={username})",
                    'user_attributes': self.ad_config.user_attributes if self.ad_config else None,
                    'group_attributes': self.ad_config.group_attributes if self.ad_config else None
                },
                'saml': {
                    'enabled': 'saml' in self.enabled_methods,
                    'idp_entity_id': self.saml_config.idp_entity_id if self.saml_config else '',
                    'idp_sso_url': self.saml_config.idp_sso_url if self.saml_config else '',
                    'idp_slo_url': self.saml_config.idp_slo_url if self.saml_config else None,
                    'idp_x509_cert': self.saml_config.idp_x509_cert if self.saml_config else None,
                    'sp_entity_id': self.saml_config.sp_entity_id if self.saml_config else None,
                    'sp_acs_url': self.saml_config.sp_acs_url if self.saml_config else None,
                    'sp_slo_url': self.saml_config.sp_slo_url if self.saml_config else None,
                    'sp_x509_cert': self.saml_config.sp_x509_cert if self.saml_config else None,
                    'sp_private_key': self.saml_config.sp_private_key if self.saml_config else None,
                    'name_id_format': self.saml_config.name_id_format if self.saml_config else None,
                    'attribute_mapping': self.saml_config.attribute_mapping if self.saml_config else None
                }
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Error saving enterprise auth config: {e}")
    
    def authenticate_ad(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user against Active Directory"""
        if not self.ad_config:
            return None
        
        try:
            # Create server connection
            server = Server(
                self.ad_config.server,
                port=self.ad_config.port,
                use_ssl=self.ad_config.use_ssl,
                get_info=ALL
            )
            
            # Try to bind with user credentials
            if self.ad_config.use_ntlm:
                # NTLM authentication
                conn = Connection(
                    server,
                    user=f"{self.ad_config.server}\\{username}",
                    password=password,
                    authentication=NTLM,
                    auto_bind=True
                )
            else:
                # Simple bind authentication
                user_dn = self._get_user_dn(username)
                if not user_dn:
                    return None
                
                conn = Connection(
                    server,
                    user=user_dn,
                    password=password,
                    authentication=SIMPLE,
                    auto_bind=True
                )
            
            if not conn.bound:
                return None
            
            # Get user information
            user_info = self._get_ad_user_info(conn, username)
            if not user_info:
                return None
            
            # Get user groups
            groups = self._get_ad_user_groups(conn, user_info.get('distinguishedName'))
            
            return {
                'username': username,
                'email': user_info.get('mail', ''),
                'display_name': user_info.get('displayName', username),
                'groups': groups,
                'auth_method': 'ad'
            }
            
        except Exception as e:
            print(f"AD authentication error: {e}")
            return None
    
    def _get_user_dn(self, username: str) -> Optional[str]:
        """Get user distinguished name from AD"""
        if not self.ad_config.bind_dn or not self.ad_config.bind_password:
            return None
        
        try:
            server = Server(self.ad_config.server, port=self.ad_config.port, use_ssl=self.ad_config.use_ssl)
            conn = Connection(
                server,
                user=self.ad_config.bind_dn,
                password=self.ad_config.bind_password,
                authentication=SIMPLE,
                auto_bind=True
            )
            
            if not conn.bound:
                return None
            
            search_filter = self.ad_config.search_filter.format(username=username)
            conn.search(
                self.ad_config.search_base,
                search_filter,
                attributes=['distinguishedName']
            )
            
            if conn.entries:
                return conn.entries[0].entry_dn
            
            return None
            
        except Exception as e:
            print(f"Error getting user DN: {e}")
            return None
    
    def _get_ad_user_info(self, conn: Connection, username: str) -> Optional[Dict]:
        """Get user information from AD"""
        try:
            search_filter = self.ad_config.search_filter.format(username=username)
            conn.search(
                self.ad_config.search_base,
                search_filter,
                attributes=self.ad_config.user_attributes
            )
            
            if conn.entries:
                entry = conn.entries[0]
                return {
                    'distinguishedName': entry.entry_dn,
                    'sAMAccountName': entry.sAMAccountName.value if hasattr(entry, 'sAMAccountName') else username,
                    'mail': entry.mail.value if hasattr(entry, 'mail') else '',
                    'displayName': entry.displayName.value if hasattr(entry, 'displayName') else username
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def _get_ad_user_groups(self, conn: Connection, user_dn: str) -> List[str]:
        """Get user groups from AD"""
        try:
            conn.search(
                user_dn,
                '(objectClass=user)',
                attributes=['memberOf']
            )
            
            if conn.entries:
                entry = conn.entries[0]
                groups = []
                for group_dn in entry.memberOf.values:
                    # Extract CN from DN
                    cn = group_dn.split(',')[0].replace('CN=', '')
                    groups.append(cn)
                return groups
            
            return []
            
        except Exception as e:
            print(f"Error getting user groups: {e}")
            return []
    
    def initiate_saml_login(self) -> str:
        """Initiate SAML login and return redirect URL"""
        if not SAML_AVAILABLE:
            raise ValueError("SAML dependencies not installed")
        
        if not self.saml_config:
            raise ValueError("SAML not configured")
        
        try:
            # Prepare SAML request
            req = self._prepare_saml_request()
            auth = OneLogin_Saml2_Auth(req, self._get_saml_settings())
            
            # Build login URL
            login_url = auth.login()
            return login_url
            
        except Exception as e:
            print(f"SAML login initiation error: {e}")
            raise
    
    def process_saml_response(self, saml_response: str) -> Optional[Dict]:
        """Process SAML response and extract user information"""
        if not SAML_AVAILABLE:
            return None
        
        if not self.saml_config:
            return None
        
        try:
            # Prepare SAML request
            req = self._prepare_saml_request()
            auth = OneLogin_Saml2_Auth(req, self._get_saml_settings())
            
            # Process response
            auth.process_response()
            
            if auth.is_authenticated():
                # Extract user information
                attributes = auth.get_attributes()
                name_id = auth.get_nameid()
                
                # Map attributes
                username = self._get_saml_attribute(attributes, 'username', name_id)
                email = self._get_saml_attribute(attributes, 'email', '')
                display_name = self._get_saml_attribute(attributes, 'display_name', username)
                groups = self._get_saml_groups(attributes)
                
                return {
                    'username': username,
                    'email': email,
                    'display_name': display_name,
                    'groups': groups,
                    'auth_method': 'saml'
                }
            
            return None
            
        except Exception as e:
            print(f"SAML response processing error: {e}")
            return None
    
    def _prepare_saml_request(self) -> Dict:
        """Prepare SAML request data"""
        return {
            'https': 'on' if request.is_secure else 'off',
            'http_host': request.host,
            'server_port': request.environ.get('SERVER_PORT', '80'),
            'script_name': request.path,
            'get_data': dict(request.args),
            'post_data': dict(request.form),
            'query_string': request.query_string.decode('utf-8')
        }
    
    def _get_saml_settings(self) -> Dict:
        """Get SAML settings configuration"""
        return {
            'strict': True,
            'debug': True,
            'sp': {
                'entityId': self.saml_config.sp_entity_id,
                'assertionConsumerService': {
                    'url': self.saml_config.sp_acs_url,
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
                },
                'singleLogoutService': {
                    'url': self.saml_config.sp_slo_url,
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                } if self.saml_config.sp_slo_url else None,
                'NameIDFormat': self.saml_config.name_id_format,
                'x509cert': self.saml_config.sp_x509_cert,
                'privateKey': self.saml_config.sp_private_key
            },
            'idp': {
                'entityId': self.saml_config.idp_entity_id,
                'singleSignOnService': {
                    'url': self.saml_config.idp_sso_url,
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                },
                'singleLogoutService': {
                    'url': self.saml_config.idp_slo_url,
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                } if self.saml_config.idp_slo_url else None,
                'x509cert': self.saml_config.idp_x509_cert
            },
            'security': {
                'nameIdEncrypted': False,
                'authnRequestsSigned': False,
                'logoutRequestSigned': False,
                'logoutResponseSigned': False,
                'signMetadata': False,
                'wantMessagesSigned': False,
                'wantAssertionsSigned': False,
                'wantNameIdEncrypted': False,
                'wantNameId': True,
                'wantAssertionsEncrypted': False,
                'allowSingleLabelDomains': False,
                'wantAttributeStatement': True,
                'signatureAlgorithm': 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
            }
        }
    
    def _get_saml_attribute(self, attributes: Dict, attr_name: str, default: str = '') -> str:
        """Get SAML attribute value"""
        mapping = self.saml_config.attribute_mapping.get(attr_name, attr_name)
        if mapping in attributes:
            values = attributes[mapping]
            if values:
                return values[0] if isinstance(values, list) else str(values)
        return default
    
    def _get_saml_groups(self, attributes: Dict) -> List[str]:
        """Get SAML groups attribute"""
        groups_attr = self.saml_config.attribute_mapping.get('groups', 'groups')
        if groups_attr in attributes:
            groups = attributes[groups_attr]
            if isinstance(groups, list):
                return groups
            elif isinstance(groups, str):
                return [groups]
        return []
    
    def get_enabled_methods(self) -> List[str]:
        """Get list of enabled authentication methods"""
        return self.enabled_methods.copy()
    
    def is_method_enabled(self, method: str) -> bool:
        """Check if authentication method is enabled"""
        return method in self.enabled_methods

# Global enterprise auth manager instance
enterprise_auth_manager = EnterpriseAuthManager()

def get_enterprise_auth_manager() -> EnterpriseAuthManager:
    """Get the global enterprise authentication manager"""
    return enterprise_auth_manager
