#!/usr/bin/env python3
"""
Simple C-MOVE test using the app's generated studies
"""

import requests
import json
import time
import subprocess
import os
import glob

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

def send_study_to_pacs_direct(study_folder, pacs_host, pacs_port, pacs_aet):
    """Send study to PACS using storescu directly"""
    print(f"🔄 Sending study folder {study_folder} to PACS {pacs_aet}@{pacs_host}:{pacs_port}")
    
    # Find DICOM files in the study folder
    dicom_files = glob.glob(f"data/dicom_output/{study_folder}/**/*.dcm", recursive=True)
    if not dicom_files:
        print(f"    ❌ No DICOM files found in {study_folder}")
        return False
    
    print(f"    Found {len(dicom_files)} DICOM files")
    
    # Send each DICOM file
    for dicom_file in dicom_files:
        cmd = [
            "storescu",
            "-v",
            "-aet", "DICOMFAB",
            "-aec", pacs_aet,
            pacs_host,
            str(pacs_port),
            dicom_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                print(f"    ❌ Failed to send {dicom_file}: {result.stderr}")
                return False
        except Exception as e:
            print(f"    ❌ Error sending {dicom_file}: {e}")
            return False
    
    print(f"    ✅ All DICOM files sent successfully")
    return True

def test_cmove_direct(source_host, source_port, source_aet, dest_aet, move_aet, study_uid):
    """Test C-MOVE operation directly"""
    print(f"🔄 Testing C-MOVE: {source_aet}@{source_host}:{source_port} → {dest_aet}")
    print(f"    Using C-MOVE AE: {move_aet}")
    print(f"    Study UID: {study_uid}")
    
    cmd = [
        "movescu",
        "-v",
        "-aet", "DICOMFAB",
        "-aec", source_aet,
        "-aem", move_aet,
        source_host,
        str(source_port),
        "-k", f"StudyInstanceUID={study_uid}",
        "-k", "QueryRetrieveLevel=STUDY"
    ]
    
    print(f"    Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        print(f"    Exit code: {result.returncode}")
        if result.stdout:
            print(f"    stdout: {result.stdout[:500]}...")
        if result.stderr:
            print(f"    stderr: {result.stderr[:500]}...")
        
        if result.returncode == 0:
            print(f"    ✅ C-MOVE successful!")
            return True
        else:
            print(f"    ❌ C-MOVE failed")
            return False
    except subprocess.TimeoutExpired:
        print("    ❌ C-MOVE timeout")
        return False
    except Exception as e:
        print(f"    ❌ C-MOVE error: {e}")
        return False

def main():
    """Main test function"""
    print("🏥 Simple C-MOVE Test with App-Generated Study")
    print("=" * 50)
    
    # Login
    session = login()
    if not session:
        print("❌ Cannot proceed without login")
        return
    
    # Generate a study
    study_info = generate_study(session)
    if not study_info:
        print("❌ Cannot proceed without a study")
        return
    
    study_uid = study_info['study_uid']
    study_folder = study_info['study_folder']
    
    # Send study to source PACS using storescu directly
    source_pacs = {
        "host": "localhost",
        "port": 4242,
        "aet": "TESTPACS"
    }
    
    print(f"\n📤 Sending study to {source_pacs['aet']}...")
    if not send_study_to_pacs_direct(study_folder, source_pacs["host"], 
                                   source_pacs["port"], source_pacs["aet"]):
        print("❌ Cannot proceed without study in source PACS")
        return
    
    # Wait a moment for the study to be stored
    print("⏳ Waiting for study to be stored...")
    time.sleep(3)
    
    # Test C-MOVE with corrected AE title
    print(f"\n🧪 Testing C-MOVE with corrected AE title...")
    success = test_cmove_direct(
        source_pacs["host"], source_pacs["port"], source_pacs["aet"],
        "TESTPACS2", "CMOVE_TO_TESTPACS2", study_uid
    )
    
    if success:
        print("\n🎉 C-MOVE test successful!")
        print("✅ The corrected C-MOVE AE configuration works!")
    else:
        print("\n⚠️  C-MOVE test failed.")
        print("💡 This indicates there may still be configuration issues.")
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    main()