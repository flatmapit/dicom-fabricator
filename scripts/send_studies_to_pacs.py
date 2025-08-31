#!/usr/bin/env python3
"""
Send generated studies to PACS for testing query limits
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def send_studies_to_pacs(pacs_host="localhost", pacs_port=4242, pacs_aec="ORTHANC", aet="DICOMFAB"):
    """Send all studies from dicom_output directory to PACS"""
    
    print(f"Sending studies to PACS: {pacs_aec}@{pacs_host}:{pacs_port}")
    
    # Find all DICOM files in the output directory
    dicom_output_dir = Path("dicom_output")
    if not dicom_output_dir.exists():
        print("Error: dicom_output directory not found")
        return False
    
    # Find all .dcm files recursively
    dicom_files = list(dicom_output_dir.rglob("*.dcm"))
    
    if not dicom_files:
        print("No DICOM files found in dicom_output directory")
        return False
    
    print(f"Found {len(dicom_files)} DICOM files to send")
    
    successful_sends = 0
    failed_sends = 0
    
    for i, dicom_file in enumerate(dicom_files):
        try:
            # Use storescu to send the DICOM file
            cmd = [
                'storescu',
                '-aet', aet,
                '-aec', pacs_aec,
                pacs_host, str(pacs_port),
                str(dicom_file)
            ]
            
            print(f"Sending {i+1}/{len(dicom_files)}: {dicom_file.name}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                successful_sends += 1
                print(f"  ✓ Successfully sent {dicom_file.name}")
            else:
                failed_sends += 1
                print(f"  ✗ Failed to send {dicom_file.name}: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            failed_sends += 1
            print(f"  ✗ Timeout sending {dicom_file.name}")
        except Exception as e:
            failed_sends += 1
            print(f"  ✗ Error sending {dicom_file.name}: {e}")
    
    print(f"\nSend operation completed:")
    print(f"  Successful: {successful_sends}")
    print(f"  Failed: {failed_sends}")
    print(f"  Total: {len(dicom_files)}")
    
    return successful_sends > 0

def test_pacs_query_limits(pacs_host="localhost", pacs_port=4242, pacs_aec="ORTHANC", aet="DICOMFAB"):
    """Test PACS query with different result limits"""
    
    print("\nTesting PACS query limits...")
    
    test_limits = [5, 10, 25, 50, 100]
    
    for limit in test_limits:
        print(f"\nTesting with limit={limit}:")
        
        try:
            # Query with specific limit
            cmd = [
                'findscu',
                '-aet', aet,
                '--cancel', str(limit),
                '-aec', pacs_aec,
                pacs_host, str(pacs_port),
                '-S',  # Study level
                '-k', 'PatientName=*',
                '-k', 'PatientID',
                '-k', 'StudyDate',
                '-k', 'StudyDescription',
                '-k', 'AccessionNumber',
                '-k', 'StudyInstanceUID'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Count studies in output
                stdout_lines = result.stdout.split('\n') if result.stdout else []
                study_count = stdout_lines.count('# Dicom-Data-Set') if stdout_lines else 0
                
                print(f"  Requested limit: {limit}")
                print(f"  Actual results: {study_count}")
                print(f"  Limit working: {'✓' if study_count <= limit else '✗'}")
            else:
                print(f"  Query failed: {result.stderr}")
                
        except Exception as e:
            print(f"  Error testing limit {limit}: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Send studies to PACS and test query limits")
    parser.add_argument("--host", default="localhost", help="PACS host (default: localhost)")
    parser.add_argument("--port", type=int, default=4242, help="PACS port (default: 4242)")
    parser.add_argument("--aec", default="ORTHANC", help="PACS AEC (default: ORTHANC)")
    parser.add_argument("--aet", default="DICOMFAB", help="Local AET (default: DICOMFAB)")
    parser.add_argument("--send-only", action="store_true", help="Only send studies, don't test limits")
    parser.add_argument("--test-only", action="store_true", help="Only test limits, don't send studies")
    
    args = parser.parse_args()
    
    if not args.test_only:
        print("Step 1: Sending studies to PACS...")
        success = send_studies_to_pacs(args.host, args.port, args.aec, args.aet)
        
        if not success:
            print("Failed to send studies to PACS")
            sys.exit(1)
    
    if not args.send_only:
        print("\nStep 2: Testing query limits...")
        test_pacs_query_limits(args.host, args.port, args.aec, args.aet)
    
    print("\nPACS testing completed!")
