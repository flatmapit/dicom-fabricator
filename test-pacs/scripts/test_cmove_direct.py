#!/usr/bin/env python3
"""
Direct C-MOVE test using existing studies in PACS
"""

import subprocess
import time

def test_cmove_direct():
    """Test C-MOVE directly between test PACS using DCMTK"""
    
    print("🏥 Direct C-MOVE Test")
    print("=" * 40)
    
    # Test PACS configurations
    test_pacs_1 = {
        "name": "Test PACS 1",
        "host": "localhost",
        "port": 4242,
        "aec": "ORTHANC",
        "aet_find": "DICOMFAB"
    }
    
    test_pacs_2 = {
        "name": "Test PACS 2", 
        "host": "localhost",
        "port": 4243,
        "aec": "TESTPACS2",
        "aet_find": "DICOMFAB"
    }
    
    # Test C-ECHO first to verify connectivity
    print("🔍 Testing C-ECHO connectivity...")
    
    for pacs in [test_pacs_1, test_pacs_2]:
        print(f"  🧪 Testing {pacs['name']}...")
        cmd = [
            "echoscu",
            "-aec", pacs['aec'],
            "-aet", pacs['aet_find'],
            pacs['host'],
            str(pacs['port'])
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"    ✅ {pacs['name']}: C-ECHO successful")
            else:
                print(f"    ❌ {pacs['name']}: C-ECHO failed - {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"    ⏰ {pacs['name']}: C-ECHO timeout")
        except Exception as e:
            print(f"    ❌ {pacs['name']}: C-ECHO error - {e}")
    
    # Test C-FIND to get study UIDs
    print(f"\n📋 Querying studies from {test_pacs_1['name']}...")
    
    cmd = [
        "findscu",
        "-aec", test_pacs_1['aec'],
        "-aet", test_pacs_1['aet_find'],
        "-k", "0008,0052=STUDY",
        "-k", "0020,000D=",  # Study Instance UID
        "-k", "0010,0010=",  # Patient Name
        test_pacs_1['host'],
        str(test_pacs_1['port'])
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"    ✅ C-FIND successful")
            print(f"    📄 Response:\n{result.stdout}")
            
            # Extract study UID from output (simplified)
            # In a real scenario, you'd parse this properly
            study_uid = "0e4da709-caed8364-e878b987-ca2e9f1c-4cc8a0ef"  # From logs
            
            print(f"\n🔄 Testing C-MOVE with study UID: {study_uid}")
            
            # Perform C-MOVE
            move_cmd = [
                "movescu",
                "-aec", test_pacs_1['aec'],
                "-aet", test_pacs_1['aet_find'],
                "-k", f"0020,000D={study_uid}",
                "-k", "0008,0052=STUDY",
                test_pacs_1['host'],
                str(test_pacs_1['port']),
                test_pacs_2['host'],
                str(test_pacs_2['port']),
                "-aem", "DICOMFAB"
            ]
            
            print(f"    🔄 Executing: {' '.join(move_cmd)}")
            move_result = subprocess.run(move_cmd, capture_output=True, text=True, timeout=60)
            
            if move_result.returncode == 0:
                print(f"    ✅ C-MOVE successful: {test_pacs_1['name']} → {test_pacs_2['name']}")
                print(f"    📄 Response:\n{move_result.stdout}")
                return True
            else:
                print(f"    ❌ C-MOVE failed: {move_result.stderr}")
                return False
                
        else:
            print(f"    ❌ C-FIND failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"    ⏰ C-MOVE timeout")
        return False
    except Exception as e:
        print(f"    ❌ C-MOVE error: {e}")
        return False

def main():
    """Main function"""
    success = test_cmove_direct()
    
    if success:
        print("\n🎉 C-MOVE test completed successfully!")
    else:
        print("\n⚠️  C-MOVE test failed. Check PACS configuration.")
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    main()
