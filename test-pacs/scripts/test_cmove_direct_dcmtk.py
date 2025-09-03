#!/usr/bin/env python3
"""
Test C-MOVE using DCMTK directly to bypass app issues
"""

import subprocess
import tempfile
import os
import uuid

def create_simple_dicom():
    """Create a simple DICOM file using dcmtk"""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    dicom_file = os.path.join(temp_dir, "test.dcm")
    
    # Use dcmtk to create a simple DICOM file
    # We'll create a minimal DICOM file with required tags
    study_uid = f"1.2.826.0.1.3680043.8.498.{uuid.uuid4().hex[:20]}"
    series_uid = f"1.2.826.0.1.3680043.8.498.{uuid.uuid4().hex[:20]}"
    instance_uid = f"1.2.826.0.1.3680043.8.498.{uuid.uuid4().hex[:20]}"
    
    print(f"🔄 Creating DICOM file with Study UID: {study_uid}")
    
    # Create a simple DICOM file using dcmtk
    cmd = [
        "dcmodify",
        "-i", f"StudyInstanceUID={study_uid}",
        "-i", f"SeriesInstanceUID={series_uid}",
        "-i", f"SOPInstanceUID={instance_uid}",
        "-i", "PatientName=TEST^PATIENT",
        "-i", "PatientID=TEST001",
        "-i", "StudyDescription=Test Study",
        "-i", "SeriesDescription=Test Series",
        "-i", "Modality=DX",
        "-i", "StudyDate=20250903",
        "-i", "StudyTime=120000",
        "-i", "SeriesNumber=1",
        "-i", "InstanceNumber=1",
        "-i", "QueryRetrieveLevel=STUDY",
        dicom_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"    ✅ DICOM file created: {dicom_file}")
            return dicom_file, study_uid
        else:
            print(f"    ❌ Failed to create DICOM file: {result.stderr}")
            return None, None
    except subprocess.TimeoutExpired:
        print("    ❌ Timeout creating DICOM file")
        return None, None
    except Exception as e:
        print(f"    ❌ Error creating DICOM file: {e}")
        return None, None

def send_to_pacs(dicom_file, pacs_host, pacs_port, pacs_aet, our_aet):
    """Send DICOM file to PACS using storescu"""
    print(f"🔄 Sending DICOM to PACS {pacs_aet}@{pacs_host}:{pacs_port}")
    
    cmd = [
        "storescu",
        "-v",
        "-aet", our_aet,
        "-aec", pacs_aet,
        pacs_host,
        str(pacs_port),
        dicom_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"    ✅ DICOM sent successfully")
            return True
        else:
            print(f"    ❌ Failed to send DICOM: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("    ❌ Timeout sending DICOM")
        return False
    except Exception as e:
        print(f"    ❌ Error sending DICOM: {e}")
        return False

def test_cmove(source_host, source_port, source_aet, dest_aet, move_aet, study_uid):
    """Test C-MOVE operation"""
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
    print("🏥 Direct DCMTK C-MOVE Test")
    print("=" * 40)
    
    # Test configuration
    source_pacs = {
        "host": "localhost",
        "port": 4242,
        "aet": "TESTPACS"
    }
    
    dest_pacs = {
        "host": "localhost", 
        "port": 4243,
        "aet": "TESTPACS2"
    }
    
    # Create a DICOM file
    dicom_file, study_uid = create_simple_dicom()
    if not dicom_file:
        print("❌ Cannot proceed without DICOM file")
        return
    
    # Send to source PACS
    if not send_to_pacs(dicom_file, source_pacs["host"], source_pacs["port"], 
                       source_pacs["aet"], "DICOMFAB"):
        print("❌ Cannot proceed without study in source PACS")
        return
    
    # Wait a moment
    import time
    time.sleep(2)
    
    # Test C-MOVE with corrected AE title
    print(f"\n🧪 Testing C-MOVE with corrected AE title...")
    success = test_cmove(
        source_pacs["host"], source_pacs["port"], source_pacs["aet"],
        dest_pacs["aet"], "CMOVE_TO_TESTPACS2", study_uid
    )
    
    if success:
        print("\n🎉 C-MOVE test successful!")
        print("✅ The corrected C-MOVE AE configuration works!")
    else:
        print("\n⚠️  C-MOVE test failed.")
        print("💡 This indicates there may still be configuration issues.")
    
    # Cleanup
    try:
        os.unlink(dicom_file)
        os.rmdir(os.path.dirname(dicom_file))
    except:
        pass
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    main()
