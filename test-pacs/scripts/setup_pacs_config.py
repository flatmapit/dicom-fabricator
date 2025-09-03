#!/usr/bin/env python3
"""
PACS Configuration Setup Script
Automatically configures PACS servers with C-MOVE routing between all test and production PACS
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any

def create_pacs_config() -> Dict[str, Any]:
    """Create a complete PACS configuration with C-MOVE routing between all PACS"""
    
    # Define all PACS configurations
    pacs_configs = {
        # Test PACS 1 (port 4242)
        "338e008a-30a1-4e59-b9c6-df4d3b9b2d74": {
            "id": "338e008a-30a1-4e59-b9c6-df4d3b9b2d74",
            "name": "Test PACS 1",
            "description": "Primary test PACS server",
            "host": "localhost",
            "port": 4242,
            "aet_find": "DICOMFAB",
            "aet_store": "DICOMFAB",
            "aet_echo": "DICOMFAB",
            "aec": "ORTHANC",
            "environment": "test",
            "is_default": True,
            "is_active": True,
            "created_date": datetime.now().isoformat(),
            "modified_date": datetime.now().isoformat(),
            "last_tested": "",
            "test_status": "unknown",
            "test_message": "",
            "move_routing": {}
        },
        # Test PACS 2 (port 4243)
        "72a5301c-c774-4d73-af88-0ebb3acfc1b0": {
            "id": "72a5301c-c774-4d73-af88-0ebb3acfc1b0",
            "name": "Test PACS 2",
            "description": "Secondary test PACS server",
            "host": "localhost",
            "port": 4243,
            "aet_find": "DICOMFAB",
            "aet_store": "DICOMFAB",
            "aet_echo": "DICOMFAB",
            "aec": "TESTPACS2",
            "environment": "test",
            "is_default": False,
            "is_active": True,
            "created_date": datetime.now().isoformat(),
            "modified_date": datetime.now().isoformat(),
            "last_tested": "",
            "test_status": "unknown",
            "test_message": "",
            "move_routing": {}
        },

        # Prod PACS 1 (port 4245)
        "f5c71abb-830c-4496-ad6d-c52965056509": {
            "id": "f5c71abb-830c-4496-ad6d-c52965056509",
            "name": "Prod PACS 1",
            "description": "Primary production PACS server",
            "host": "localhost",
            "port": 4245,
            "aet_find": "DICOMFAB",
            "aet_store": "DICOMFAB",
            "aet_echo": "DICOMFAB",
            "aec": "ORTHANC",
            "environment": "prod",
            "is_default": False,
            "is_active": True,
            "created_date": datetime.now().isoformat(),
            "modified_date": datetime.now().isoformat(),
            "last_tested": "",
            "test_status": "unknown",
            "test_message": "",
            "move_routing": {}
        },
        # Prod PACS 2 (port 4246)
        "9dbd2ccd-9986-49e6-b229-873813d178fa": {
            "id": "9dbd2ccd-9986-49e6-b229-873813d178fa",
            "name": "Prod PACS 2",
            "description": "Secondary production PACS server",
            "host": "localhost",
            "port": 4246,
            "aet_find": "DICOMFAB",
            "aet_store": "DICOMFAB",
            "aet_echo": "DICOMFAB",
            "aec": "PRODPACS2",
            "environment": "prod",
            "is_default": False,
            "is_active": True,
            "created_date": datetime.now().isoformat(),
            "modified_date": datetime.now().isoformat(),
            "last_tested": "",
            "test_status": "unknown",
            "test_message": "",
            "move_routing": {}
        }
    }
    
    # Configure C-MOVE routing between all PACS
    # Test PACS 1 routing
    pacs_configs["338e008a-30a1-4e59-b9c6-df4d3b9b2d74"]["move_routing"] = {
        "72a5301c-c774-4d73-af88-0ebb3acfc1b0": "TESTPACS2",  # Test PACS 2
        "f5c71abb-830c-4496-ad6d-c52965056509": "ORTHANC",    # Prod PACS 1
        "9dbd2ccd-9986-49e6-b229-873813d178fa": "PRODPACS2"   # Prod PACS 2
    }
    
    # Test PACS 2 routing
    pacs_configs["72a5301c-c774-4d73-af88-0ebb3acfc1b0"]["move_routing"] = {
        "338e008a-30a1-4e59-b9c6-df4d3b9b2d74": "ORTHANC",    # Test PACS 1
        "f5c71abb-830c-4496-ad6d-c52965056509": "ORTHANC",    # Prod PACS 1
        "9dbd2ccd-9986-49e6-b229-873813d178fa": "PRODPACS2"   # Prod PACS 2
    }
    
    # Prod PACS 1 routing
    pacs_configs["f5c71abb-830c-4496-ad6d-c52965056509"]["move_routing"] = {
        "338e008a-30a1-4e59-b9c6-df4d3b9b2d74": "ORTHANC",    # Test PACS 1
        "72a5301c-c774-4d73-af88-0ebb3acfc1b0": "TESTPACS2",  # Test PACS 2
        "9dbd2ccd-9986-49e6-b229-873813d178fa": "PRODPACS2"   # Prod PACS 2
    }
    
    # Prod PACS 2 routing
    pacs_configs["9dbd2ccd-9986-49e6-b229-873813d178fa"]["move_routing"] = {
        "338e008a-30a1-4e59-b9c6-df4d3b9b2d74": "ORTHANC",    # Test PACS 1
        "72a5301c-c774-4d73-af88-0ebb3acfc1b0": "TESTPACS2",  # Test PACS 2
        "f5c71abb-830c-4496-ad6d-c52965056509": "ORTHANC"     # Prod PACS 1
    }
    
    return pacs_configs

def main():
    """Main function to set up PACS configuration"""
    print("🏥 Setting up PACS configuration with C-MOVE routing...")
    
    # Create the configuration
    config = create_pacs_config()
    
    # Write to file
    config_file = "data/pacs_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ PACS configuration created: {config_file}")
    print(f"📊 Configured {len(config)} PACS servers:")
    
    for pacs_id, pacs_config in config.items():
        env_color = "🟢" if pacs_config["environment"] == "test" else "🔴"
        routing_count = len([ae for ae in pacs_config["move_routing"].values() if ae])
        print(f"  {env_color} {pacs_config['name']} ({pacs_config['environment']}) - {routing_count} C-MOVE routes")
    
    print("\n🔗 C-MOVE routing configured between all PACS servers")
    print("📖 See docs/PACS_SERVER_INFO.md for detailed routing information")

if __name__ == "__main__":
    main()
