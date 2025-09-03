#!/usr/bin/env python3
"""
Test C-MOVE using the app's API endpoint
"""

import requests
import json
import time

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
    print("🏥 C-MOVE API Test")
    print("=" * 40)
    
    # Login
    session = login()
    if not session:
        print("❌ Cannot proceed without login")
        return
    
    # Get PACS configurations
    configs = get_pacs_configs(session)
    if not configs:
        print("❌ Cannot get PACS configurations")
        return
    
    # Find test PACS
    test_pacs = [config for config in configs if config['environment'] == 'test']
    print(f"📊 Found {len(test_pacs)} test PACS:")
    for pacs in test_pacs:
        print(f"  - {pacs['name']} (ID: {pacs['id']})")
    
    if len(test_pacs) < 2:
        print("❌ Need at least 2 test PACS for C-MOVE testing")
        return
    
    # Use a known study UID from the PACS logs
    study_uid = "0e4da709-caed8364-e878b987-ca2e9f1c-4cc8a0ef"
    
    # Test C-MOVE from first test PACS to second
    source_pacs = test_pacs[0]
    dest_pacs = test_pacs[1]
    
    print(f"\n🧪 Testing C-MOVE: {source_pacs['name']} → {dest_pacs['name']}")
    success = test_cmove_api(session, source_pacs['id'], dest_pacs['id'], study_uid)
    
    if success:
        print("\n🎉 C-MOVE API test successful!")
        print("✅ The app can perform C-MOVE operations between test PACS!")
    else:
        print("\n⚠️  C-MOVE API test failed.")
        print("💡 This might be due to the C-FIND presentation context issues we discovered.")
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    main()
