#!/usr/bin/env python3
"""
Generate multiple test studies for PACS query limit testing
"""

import os
import sys
import json
from datetime import datetime, timedelta
import random

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dicom_fabricator import DICOMFabricator
from patient_config import PatientRegistry

def generate_test_studies(num_studies=50):
    """Generate multiple test studies for PACS testing"""
    
    print(f"Generating {num_studies} test studies...")
    
    # Initialize components
    patient_registry = PatientRegistry()
    fabricator = DICOMFabricator(patient_registry)
    
    # Create some test patients if they don't exist
    test_patients = [
        {"name": "TESTCASE^CLINICAL", "id": "PID100000"},
        {"name": "SMITH^JOHN", "id": "PID100001"},
        {"name": "JONES^MARY", "id": "PID100002"},
        {"name": "BROWN^DAVID", "id": "PID100003"},
        {"name": "WILSON^SARAH", "id": "PID100004"},
        {"name": "MILLER^JAMES", "id": "PID100005"},
        {"name": "DAVIS^LISA", "id": "PID100006"},
        {"name": "GARCIA^MICHAEL", "id": "PID100007"},
        {"name": "RODRIGUEZ^JENNIFER", "id": "PID100008"},
        {"name": "MARTINEZ^CHRISTOPHER", "id": "PID100009"},
    ]
    
    # Add patients to registry
    for patient in test_patients:
        if patient["id"] not in patient_registry.patients:
            patient_registry.generate_patient(
                patient_name=patient["name"],
                patient_id=patient["id"]
            )
    
    # Generate studies over the last 30 days
    base_date = datetime.now() - timedelta(days=30)
    
    modalities = ["DX", "CT", "MR", "US", "XA"]
    study_descriptions = [
        "Chest X-Ray",
        "Abdominal CT",
        "Brain MRI",
        "Ultrasound Abdomen",
        "Cardiac Angiography",
        "Spine X-Ray",
        "Pelvic CT",
        "Head MRI",
        "Thyroid Ultrasound",
        "Vascular Angiography"
    ]
    
    generated_studies = []
    
    for i in range(num_studies):
        # Random date within last 30 days
        study_date = base_date + timedelta(days=random.randint(0, 30))
        study_time = datetime.now().replace(
            hour=random.randint(8, 18),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        # Random patient
        patient = random.choice(test_patients)
        
        # Random modality and description
        modality = random.choice(modalities)
        description = random.choice(study_descriptions)
        
        # Generate unique accession number
        accession = f"ACC{study_date.strftime('%Y%m%d')}{i+1:04d}"
        
        # Create study parameters
        study_params = {
            "patient_name": patient["name"],
            "patient_id": patient["id"],
            "study_date": study_date.strftime("%Y%m%d"),
            "study_time": study_time.strftime("%H%M%S"),
            "study_description": f"{description} - Test Study {i+1}",
            "accession_number": accession,
            "modality": modality,
            "series_count": random.randint(1, 5),
            "images_per_series": random.randint(1, 10)
        }
        
        try:
            # Generate the study
            study_result = fabricator.create_dx_dicom_study(
                patient_name=study_params["patient_name"],
                patient_id=study_params["patient_id"],
                accession=study_params["accession_number"],
                study_desc=study_params["study_description"],
                study_date=study_params["study_date"],
                series_config=[{
                    'images': study_params["images_per_series"],
                    'procedure': f"{study_params['modality']}-{study_params['modality']}"
                }] * study_params["series_count"]
            )
            study_uid = study_result['study_uid']
            
            generated_studies.append({
                "study_uid": study_uid,
                "accession": accession,
                "patient": patient["name"],
                "modality": modality,
                "description": study_params["study_description"]
            })
            
            print(f"Generated study {i+1}/{num_studies}: {accession} - {patient['name']} - {modality}")
            
        except Exception as e:
            print(f"Error generating study {i+1}: {e}")
    
    print(f"\nSuccessfully generated {len(generated_studies)} studies")
    print("Studies are ready for PACS testing")
    
    # Save summary to file
    summary_file = "test_studies_summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_studies": len(generated_studies),
            "studies": generated_studies
        }, f, indent=2)
    
    print(f"Study summary saved to {summary_file}")
    
    return generated_studies

if __name__ == "__main__":
    num_studies = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    generate_test_studies(num_studies)
