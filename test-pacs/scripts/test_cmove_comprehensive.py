#!/usr/bin/env python3
"""
Comprehensive C-MOVE test using the DICOM Fabricator app
"""

import requests
import json
import time
import subprocess
import os
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:5055"
TEST_USER = "admin"
TEST_PASSWORD = "admin123"

def login():
    """Login to the app and return session cookies"""
    session = requests.Session()
    
    # Login
    login_data = {
        "username": TEST_USER,
        "password": TEST_PASSWORD
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Successfully logged in")
        return session
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

def get_pacs_configs(session):
    """Get PACS configurations"""
    response = session.get(f"{BASE_URL}/api/pacs/configs")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            return data['configs']
        else:
            print(f"❌ API error: {data.get('error')}")
            return None
    else:
        print(f"❌ HTTP error: {response.status_code}")
        return None

def generate_test_studies(session):
    """Generate test studies using the DICOM fabricator"""
    print("\n📁 Generating test studies...")
    
    # Generate studies for each test PACS
    test_pacs = [
        {"name": "Test PACS 1", "port": 4242},
        {"name": "Test PACS 2", "port": 4243}
    ]
    
    for pacs in test_pacs:
        print(f"  📤 Generating study for {pacs['name']}...")
        
        # Generate a simple study
        study_data = {
            "patient_name": f"TestPatient_{pacs['name'].replace(' ', '')}",
            "patient_id": f"TEST_{pacs['port']}",
            "study_description": f"Test Study for {pacs['name']}",
            "modality": "CT",
            "num_series": 1,
            "num_images": 5,
            "send_to_pacs": True,
            "pacs_id": None  # Will be determined by port
        }
        
        # Find the PACS ID by port
        configs = get_pacs_configs(session)
        if configs:
            for config in configs:
                if config['port'] == pacs['port']:
                    study_data['pacs_id'] = config['id']
                    break
        
        if study_data['pacs_id']:
            response = session.post(f"{BASE_URL}/api/generate", json=study_data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"    ✅ Generated study for {pacs['name']}")
                else:
                    print(f"    ❌ Generation failed: {result.get('error')}")
            else:
                print(f"    ❌ HTTP error: {response.status_code}")
        else:
            print(f"    ⚠️  Could not find PACS ID for {pacs['name']}")

def test_pacs_connectivity(session):
    """Test PACS connectivity"""
    print("\n🔍 Testing PACS connectivity...")
    
    configs = get_pacs_configs(session)
    if not configs:
        return
    
    for config in configs:
        print(f"  🧪 Testing {config['name']}...")
        
        # Test connection
        test_data = {
            "id": config['id']
        }
        
        response = session.post(f"{BASE_URL}/api/pacs/test", json=test_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"    ✅ {config['name']}: {result.get('message', 'Connection successful')}")
            else:
                print(f"    ❌ {config['name']}: {result.get('error', 'Connection failed')}")
        else:
            print(f"    ❌ {config['name']}: HTTP error {response.status_code}")

def test_cmove_operations(session):
    """Test C-MOVE operations between PACS"""
    print("\n🔄 Testing C-MOVE operations...")
    
    configs = get_pacs_configs(session)
    if not configs:
        return
    
    # Find test PACS
    test_pacs = [config for config in configs if config['environment'] == 'test']
    
    if len(test_pacs) < 2:
        print("  ⚠️  Need at least 2 test PACS for C-MOVE testing")
        return
    
    # Test C-MOVE from first test PACS to second
    source_pacs = test_pacs[0]
    dest_pacs = test_pacs[1]
    
    print(f"  🧪 Testing C-MOVE: {source_pacs['name']} → {dest_pacs['name']}")
    
    # Get studies from source PACS
    studies_response = session.get(f"{BASE_URL}/api/pacs/studies/{source_pacs['id']}")
    if studies_response.status_code == 200:
        studies_data = studies_response.json()
        if studies_data.get('success') and studies_data.get('studies'):
            study = studies_data['studies'][0]  # Use first study
            study_uid = study.get('StudyInstanceUID')
            
            print(f"    📋 Using study: {study_uid}")
            
            # Perform C-MOVE
            cmove_data = {
                "source_pacs_id": source_pacs['id'],
                "dest_pacs_id": dest_pacs['id'],
                "study_uid": study_uid
            }
            
            response = session.post(f"{BASE_URL}/api/pacs/cmove", json=cmove_data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"    ✅ C-MOVE successful: {result.get('message', 'Study moved successfully')}")
                else:
                    print(f"    ❌ C-MOVE failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"    ❌ C-MOVE HTTP error: {response.status_code}")
        else:
            print(f"    ⚠️  No studies found in {source_pacs['name']}")
    else:
        print(f"    ❌ Could not get studies from {source_pacs['name']}")

def check_studies_in_pacs(session):
    """Check studies in each PACS"""
    print("\n📊 Checking studies in each PACS...")
    
    configs = get_pacs_configs(session)
    if not configs:
        return
    
    for config in configs:
        print(f"  📁 {config['name']}:")
        
        response = session.get(f"{BASE_URL}/api/pacs/studies/{config['id']}")
        if response.status_code == 200:
            studies_data = response.json()
            if studies_data.get('success'):
                studies = studies_data.get('studies', [])
                print(f"    📋 {len(studies)} studies found")
                for study in studies[:3]:  # Show first 3 studies
                    patient_name = study.get('PatientName', 'Unknown')
                    study_desc = study.get('StudyDescription', 'Unknown')
                    print(f"      - {patient_name}: {study_desc}")
            else:
                print(f"    ❌ Error: {studies_data.get('error')}")
        else:
            print(f"    ❌ HTTP error: {response.status_code}")

def main():
    """Main test function"""
    print("🏥 DICOM C-MOVE Comprehensive Test Suite")
    print("=" * 60)
    
    # Login
    session = login()
    if not session:
        print("❌ Cannot proceed without login")
        return
    
    # Test PACS connectivity
    test_pacs_connectivity(session)
    
    # Check initial studies
    check_studies_in_pacs(session)
    
    # Generate test studies
    generate_test_studies(session)
    
    # Wait for studies to be processed
    print("\n⏳ Waiting for studies to be processed...")
    time.sleep(5)
    
    # Check studies after generation
    check_studies_in_pacs(session)
    
    # Test C-MOVE operations
    test_cmove_operations(session)
    
    # Final check
    print("\n📊 Final study count:")
    check_studies_in_pacs(session)
    
    print("\n✅ C-MOVE testing completed!")

if __name__ == "__main__":
    main()
