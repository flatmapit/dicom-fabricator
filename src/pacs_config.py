#!/usr/bin/env python3
"""
PACS Configuration Management System
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PacsConfiguration:
    """Represents a PACS configuration"""
    id: str
    name: str
    description: str
    host: str
    port: int
    aet: str  # Application Entity Title (our AET when connecting)
    aec: str  # Called Application Entity (PACS AET)
    is_default: bool = False
    is_active: bool = True
    created_date: str = ""
    modified_date: str = ""
    last_tested: str = ""
    test_status: str = "unknown"  # unknown, success, failed
    test_message: str = ""

    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()


class PacsConfigManager:
    """Manages PACS configurations with persistence"""
    
    def __init__(self, config_path: str = "./data/pacs_config.json"):
        self.config_path = Path(config_path)
        self.configs: Dict[str, PacsConfiguration] = {}
        self.load_configs()
        self._ensure_default_configs()
        
    def _ensure_default_configs(self):
        """Ensure default PACS configurations exist"""
        if not self.configs:
            # Add default configurations
            orthanc_config = PacsConfiguration(
                id=str(uuid.uuid4()),
                name="Orthanc Test PACS",
                description="Local Orthanc PACS server for testing",
                host="localhost",
                port=4242,
                aet="DICOMFAB",
                aec="ORTHANC",
                is_default=True,
                is_active=True
            )
            
            testpacs_config = PacsConfiguration(
                id=str(uuid.uuid4()),
                name="Test PACS",
                description="Generic test PACS configuration",
                host="localhost",
                port=4242,
                aet="DICOMFAB", 
                aec="TESTPACS",
                is_default=False,
                is_active=True
            )
            
            self.configs[orthanc_config.id] = orthanc_config
            self.configs[testpacs_config.id] = testpacs_config
            self.save_configs()
    
    def load_configs(self):
        """Load PACS configurations from disk"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    for config_id, config_dict in data.items():
                        self.configs[config_id] = PacsConfiguration(**config_dict)
            except Exception as e:
                print(f"Error loading PACS configs: {e}")
                self.configs = {}
    
    def save_configs(self):
        """Save PACS configurations to disk"""
        # Create directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            data = {}
            for config_id, config in self.configs.items():
                data[config_id] = asdict(config)
            
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving PACS configs: {e}")
    
    def create_config(self, name: str, description: str, host: str, port: int,
                     aet: str, aec: str, is_default: bool = False) -> PacsConfiguration:
        """Create a new PACS configuration"""
        # If this is set as default, unset other defaults
        if is_default:
            self._unset_all_defaults()
        
        config = PacsConfiguration(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            host=host,
            port=port,
            aet=aet,
            aec=aec,
            is_default=is_default
        )
        
        self.configs[config.id] = config
        self.save_configs()
        return config
    
    def get_config(self, config_id: str) -> Optional[PacsConfiguration]:
        """Get a PACS configuration by ID"""
        return self.configs.get(config_id)
    
    def get_config_by_name(self, name: str) -> Optional[PacsConfiguration]:
        """Get a PACS configuration by name"""
        for config in self.configs.values():
            if config.name == name:
                return config
        return None
    
    def update_config(self, config_id: str, **kwargs) -> Optional[PacsConfiguration]:
        """Update a PACS configuration"""
        if config_id not in self.configs:
            return None
        
        config = self.configs[config_id]
        
        # If setting as default, unset other defaults
        if kwargs.get('is_default', False):
            self._unset_all_defaults()
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        config.modified_date = datetime.now().isoformat()
        self.save_configs()
        return config
    
    def delete_config(self, config_id: str) -> bool:
        """Delete a PACS configuration"""
        if config_id in self.configs:
            del self.configs[config_id]
            self.save_configs()
            return True
        return False
    
    def list_configs(self, active_only: bool = False) -> List[PacsConfiguration]:
        """List all PACS configurations"""
        configs = list(self.configs.values())
        if active_only:
            configs = [c for c in configs if c.is_active]
        
        # Sort by name
        configs.sort(key=lambda c: c.name.lower())
        return configs
    
    def get_default_config(self) -> Optional[PacsConfiguration]:
        """Get the default PACS configuration"""
        for config in self.configs.values():
            if config.is_default:
                return config
        
        # If no default set, return first active config
        active_configs = self.list_configs(active_only=True)
        return active_configs[0] if active_configs else None
    
    def _unset_all_defaults(self):
        """Unset default flag on all configurations"""
        for config in self.configs.values():
            config.is_default = False
    
    def test_connection(self, config_id: str) -> Dict[str, Any]:
        """Test connection to a PACS configuration"""
        import subprocess
        
        config = self.get_config(config_id)
        if not config:
            return {"success": False, "error": "Configuration not found"}
        
        try:
            # Use echoscu to test connection
            cmd = [
                'echoscu',
                '-aet', config.aet,
                '-aec', config.aec,
                config.host, str(config.port)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            success = result.returncode == 0
            message = "Connection successful" if success else f"Connection failed: {result.stderr}"
            
            # Update test status
            config.last_tested = datetime.now().isoformat()
            config.test_status = "success" if success else "failed"
            config.test_message = message
            self.save_configs()
            
            return {
                "success": success,
                "message": message,
                "output": result.stdout,
                "error": result.stderr if not success else None
            }
            
        except subprocess.TimeoutExpired:
            message = "Connection timeout"
            config.last_tested = datetime.now().isoformat()
            config.test_status = "failed"
            config.test_message = message
            self.save_configs()
            
            return {
                "success": False,
                "error": message
            }
        except Exception as e:
            message = f"Test error: {str(e)}"
            config.last_tested = datetime.now().isoformat()
            config.test_status = "failed"
            config.test_message = message
            self.save_configs()
            
            return {
                "success": False,
                "error": message
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get PACS configuration statistics"""
        total = len(self.configs)
        active = len([c for c in self.configs.values() if c.is_active])
        tested = len([c for c in self.configs.values() if c.last_tested])
        successful = len([c for c in self.configs.values() if c.test_status == "success"])
        
        return {
            "total_configs": total,
            "active_configs": active,
            "tested_configs": tested,
            "successful_tests": successful,
            "default_config": self.get_default_config().name if self.get_default_config() else None
        }