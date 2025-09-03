#!/usr/bin/env python3
"""
PACS Configuration Management System
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class PacsConfiguration:
    """Represents a PACS configuration"""
    id: str
    name: str
    description: str
    host: str
    port: int
    aet_find: str  # AE for C-FIND queries
    aet_store: str  # AE for C-STORE operations (optional)
    aet_echo: str  # AE for C-ECHO tests
    aec: str  # Called Application Entity (PACS AET)
    environment: str = "test"  # test, production, or both
    is_default: bool = False
    is_active: bool = True
    created_date: str = ""
    modified_date: str = ""
    last_tested: str = ""
    test_status: str = "unknown"  # unknown, success, failed
    test_message: str = ""
    move_routing: Dict[str, str] = field(default_factory=dict)  # Map of destination PACS ID -> AE for C-MOVE
    
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
            orthanc_test_config = PacsConfiguration(
                id=str(uuid.uuid4()),
                name="Test PACS 1",
                description="Primary test PACS server",
                host="localhost",
                port=4242,
                aet_find="DICOMFAB",
                aet_store="DICOMFAB",
                aet_echo="DICOMFAB",
                aec="ORTHANC",
                environment="test",
                is_default=True,
                is_active=True
            )
            
            orthanc_prod_config = PacsConfiguration(
                id=str(uuid.uuid4()),
                name="Test PACS 2",
                description="Secondary test PACS server",
                host="localhost",
                port=4243,
                aet_find="DICOMFAB",
                aet_store="DICOMFAB",
                aet_echo="DICOMFAB",
                aec="TESTPACS2",
                environment="test",
                is_default=False,
                is_active=True
            )
            
            testpacs_test_config = PacsConfiguration(
                id=str(uuid.uuid4()),
                name="Test PACS 3",
                description="Tertiary test PACS server",
                host="localhost",
                port=4244,
                aet_find="DICOMFAB",
                aet_store="DICOMFAB",
                aet_echo="DICOMFAB",
                aec="TESTPACS3",
                environment="test",
                is_default=False,
                is_active=True
            )
            
            testpacs_prod_config = PacsConfiguration(
                id=str(uuid.uuid4()),
                name="Prod PACS 1",
                description="Primary production PACS server",
                host="localhost",
                port=4245,
                aet_find="DICOMFAB",
                aet_store="DICOMFAB",
                aet_echo="DICOMFAB",
                aec="ORTHANC",
                environment="prod",
                is_default=False,
                is_active=True
            )
            
            self.configs[orthanc_test_config.id] = orthanc_test_config
            self.configs[orthanc_prod_config.id] = orthanc_prod_config
            self.configs[testpacs_test_config.id] = testpacs_test_config
            self.configs[testpacs_prod_config.id] = testpacs_prod_config
            self.save_configs()
    
    def load_configs(self):
        """Load PACS configurations from disk"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    for config_id, config_dict in data.items():
                        config = PacsConfiguration(**config_dict)
                        # Fix any null move_routing fields
                        if config.move_routing is None:
                            config.move_routing = {}
                        self.configs[config_id] = config
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
                     aet_find: str, aet_store: str, aet_echo: str, aec: str, 
                     environment: str = "test", is_default: bool = False) -> PacsConfiguration:
        """Create a new PACS configuration"""
        # Validate required fields
        if not name or not name.strip():
            raise ValueError("PACS name cannot be empty")
        if not host or not host.strip():
            raise ValueError("Host cannot be empty")
        if port <= 0 or port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        if not aet_find or not aet_find.strip():
            raise ValueError("C-FIND AE cannot be empty")
        if not aet_echo or not aet_echo.strip():
            raise ValueError("C-ECHO AE cannot be empty")
        if not aec or not aec.strip():
            raise ValueError("PACS AEC cannot be empty")
        
        # If this is set as default, unset other defaults
        if is_default:
            self._unset_all_defaults()
        
        config = PacsConfiguration(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            host=host,
            port=port,
            aet_find=aet_find,
            aet_store=aet_store,
            aet_echo=aet_echo,
            aec=aec,
            environment=environment,
            is_default=is_default
        )
        
        # Pre-populate routing table with other PACS
        self._populate_routing_table(config)
        
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
    
    def _populate_routing_table(self, new_config: PacsConfiguration):
        """Pre-populate routing table with other PACS"""
        for other_config in self.configs.values():
            if other_config.id != new_config.id:
                # Add empty entry for manual configuration
                new_config.move_routing[other_config.id] = ""
        
        # Also update existing configs to include the new one
        for existing_config in self.configs.values():
            if existing_config.id != new_config.id:
                existing_config.move_routing[new_config.id] = ""
    
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
                '-aet', config.aet_echo,
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
        active = len([c for c in self.configs.values() if c.test_status == "success"])
        down = len([c for c in self.configs.values() if c.test_status == "failed"])
        tested = len([c for c in self.configs.values() if c.last_tested])
        successful = len([c for c in self.configs.values() if c.test_status == "success"])
        
        # Find the most recent test time
        last_test_times = [c.last_tested for c in self.configs.values() if c.last_tested]
        last_test_time = max(last_test_times) if last_test_times else None
        
        # Calculate time since last test
        time_since_last_test = None
        if last_test_time:
            try:
                from datetime import datetime
                last_test_dt = datetime.fromisoformat(last_test_time.replace('Z', '+00:00'))
                now = datetime.now()
                time_diff = now - last_test_dt
                if time_diff.total_seconds() < 60:
                    time_since_last_test = "just now"
                elif time_diff.total_seconds() < 3600:
                    minutes = int(time_diff.total_seconds() / 60)
                    time_since_last_test = f"{minutes}m ago"
                else:
                    hours = int(time_diff.total_seconds() / 3600)
                    time_since_last_test = f"{hours}h ago"
            except:
                time_since_last_test = "recently"
        
        return {
            "total_configs": total,
            "active_configs": active,
            "down_configs": down,
            "tested_configs": tested,
            "successful_tests": successful,
            "default_config": self.get_default_config().name if self.get_default_config() else None,
            "last_test_time": last_test_time,
            "time_since_last_test": time_since_last_test
        }
    
    def get_store_enabled_configs(self) -> List[PacsConfiguration]:
        """Get PACS configurations that support C-STORE (have aet_store configured)"""
        return [c for c in self.configs.values() if c.is_active and c.aet_store and c.aet_store.strip()]
    
    def get_move_ae(self, source_config_id: str, destination_config_id: str) -> Optional[str]:
        """Get the AE title to use for C-MOVE from source to destination PACS"""
        source_config = self.get_config(source_config_id)
        if not source_config:
            return None
        
        # Check if destination config exists
        dest_config = self.get_config(destination_config_id)
        if not dest_config:
            return None
        
        return source_config.move_routing.get(destination_config_id, "")
    
    def reload_configs(self) -> bool:
        """Reload configurations from the file"""
        try:
            self.configs.clear()
            self.load_configs()
            self._ensure_default_configs()
            return True
        except Exception as e:
            print(f"Error reloading PACS configurations: {e}")
            return False
    
    def update_routing_table(self, config_id: str, routing_updates: Dict[str, str]) -> bool:
        """Update the C-MOVE routing table for a PACS configuration"""
        config = self.get_config(config_id)
        if not config:
            return False
        
        # Validate routing updates
        if not routing_updates:
            return True  # Empty updates are valid (no-op)
        
        # Update routing table with validation
        for dest_id, ae in routing_updates.items():
            # Validate destination exists
            if dest_id and dest_id != config_id:  # Can't route to self
                dest_config = self.get_config(dest_id)
                if dest_config:
                    # Convert None to empty string
                    config.move_routing[dest_id] = ae if ae is not None else ""
        
        config.modified_date = datetime.now().isoformat()
        self.save_configs()
        return True