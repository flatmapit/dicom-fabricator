#!/usr/bin/env python3
"""
Test C-MOVE with a study that we know exists
"""

import requests
import json
import time
import subprocess
import os

# Test configuration
BASE_URL = "http://localhost:5055"
TEST_USER = "admin"
TEST_PASSWORD = "admin123"

def login():
    """Login to the app and return session"""
    session = requests.Session()
    
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

def generate_study(session):
    """Generate a test study"""
    print("🔄 Generating test study...")
    
    study_data = {
        "patient_id": "TEST001",
        "patient_name": "Test Patient",
        "study_description": "C-MOVE Test Study",
        "modality": "CT",
        "series_count": 1,
        "images_per_series": 1
    }
    
    response = session.post(f"{BASE_URL}/api/generate", json=study_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"    ✅ Study generated: {result.get('message')}")
            study_data = result.get('study', {})
            return {
                'study_uid': study_data.get('study_uid'),
                'study_folder': study_data.get('study_folder')
            }
        else:
            print(f"    ❌ Study generation failed: {result.get('error')}")
            return None
    else:
        print(f"    ❌ HTTP error: {response.status_code}")
        return None

def send_study_to_pacs(session, study_info, pacs_id):
    """Send study to a PACS"""
    study_uid = study_info['study_uid']
    study_folder = study_info['study_folder']
    print(f"🔄 Sending study {study_uid} to PACS {pacs_id}...")
    
    send_data = {
        "study_folder": study_folder,
        "pacs_config_id": pacs_id
    }
    
    response = session.post(f"{BASE_URL}/api/pacs/send-study", json=send_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"    ✅ Study sent successfully")
            return True
        else:
            print(f"    ❌ Send failed: {result.get('error')}")
            return False
    else:
        print(f"    ❌ HTTP error: {response.status_code}")
        return False

def test_cmove_api(session, source_pacs_id, dest_pacs_id, study_uid):
    """Test C-MOVE using the app's API"""
    print(f"🔄 Testing C-MOVE via API...")
    print(f"    Source PACS ID: {source_pacs_id}")
    print(f"    Destination PACS ID: {dest_pacs_id}")
    print(f"    Study UID: {study_uid}")
    
    cmove_data = {
        "source_pacs_id": source_pacs_id,
        "destination_pacs_id": dest_pacs_id,
        "study_uid": study_uid
    }
    
    response = session.post(f"{BASE_URL}/api/pacs/c-move", json=cmove_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"    ✅ C-MOVE successful: {result.get('message')}")
            return True
        else:
            print(f"    ❌ C-MOVE failed: {result.get('error')}")
            if 'suggestion' in result:
                print(f"    💡 Suggestion: {result['suggestion']}")
            return False
    else:
        print(f"    ❌ HTTP error: {response.status_code}")
        try:
            error_data = response.json()
            print(f"    Error: {error_data.get('error', 'Unknown error')}")
        except:
            print(f"    Response: {response.text}")
        return False

def main():
    """Main test function"""
    print("🏥 C-MOVE Test with Study Generation")
    print("=" * 50)
    
    # Login
    session = login()
    if not session:
        print("❌ Cannot proceed without login")
        return
    
    # Get PACS configurations
    response = session.get(f"{BASE_URL}/api/pacs/configs")
    if response.status_code != 200:
        print("❌ Cannot get PACS configurations")
        return
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ API error: {data.get('error')}")
        return
    
    configs = data['configs']
    
    # Find test PACS
    test_pacs = [config for config in configs if config['environment'] == 'test']
    print(f"📊 Found {len(test_pacs)} test PACS:")
    for pacs in test_pacs:
        print(f"  - {pacs['name']} (ID: {pacs['id']})")
    
    if len(test_pacs) < 2:
        print("❌ Need at least 2 test PACS for C-MOVE testing")
        return
    
    # Generate a study
    study_info = generate_study(session)
    if not study_info:
        print("❌ Cannot proceed without a study")
        return
    
    study_uid = study_info['study_uid']
    
    # Send study to first test PACS
    source_pacs = test_pacs[0]
    dest_pacs = test_pacs[1]
    
    print(f"\n📤 Sending study to {source_pacs['name']}...")
    if not send_study_to_pacs(session, study_info, source_pacs['id']):
        print("❌ Cannot proceed without study in source PACS")
        return
    
    # Wait a moment for the study to be stored
    print("⏳ Waiting for study to be stored...")
    time.sleep(3)
    
    # Test C-MOVE from first test PACS to second
    print(f"\n🧪 Testing C-MOVE: {source_pacs['name']} → {dest_pacs['name']}")
    success = test_cmove_api(session, source_pacs['id'], dest_pacs['id'], study_uid)
    
    if success:
        print("\n🎉 C-MOVE test successful!")
        print("✅ The app can perform C-MOVE operations between test PACS!")
    else:
        print("\n⚠️  C-MOVE test failed.")
        print("💡 This indicates a configuration issue with the PACS servers.")
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    main()
