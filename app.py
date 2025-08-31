#!/usr/bin/env python3
"""
DICOM Fabricator Flask Web Application
Copyright (c) 2025 Christopher Gentle <chris@flatmapit.com>
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, make_response
from flask_cors import CORS
import os
import sys
import json
import base64
import csv
from pathlib import Path
from datetime import datetime
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dicom_fabricator import DICOMFabricator
from patient_config import PatientRegistry, PatientRecord
from pacs_config import PacsConfigManager
import pydicom
from PIL import Image
import numpy as np

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'dicom_output'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

patient_registry = PatientRegistry()
fabricator = DICOMFabricator(patient_registry)
pacs_manager = PacsConfigManager()

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('query_pacs.html')

@app.route('/patients')
def patients_page():
    return render_template('patients.html')

@app.route('/generator')
def generator_page():
    return render_template('generator.html')


@app.route('/pacs')
def pacs_page():
    return render_template('pacs.html')

@app.route('/query-pacs')
def query_pacs_page():
    return render_template('query_pacs.html')

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get all patients"""
    patients = []
    for patient_id, patient in patient_registry.patients.items():
        # Split patient_name into first and last names
        name_parts = patient.patient_name.split('^') if '^' in patient.patient_name else [patient.patient_name, '']
        last_name = name_parts[0] if len(name_parts) > 0 else ''
        first_name = name_parts[1] if len(name_parts) > 1 else ''
        
        patients.append({
            'id': patient_id,
            'mrn': patient.patient_id,  # Use patient_id as MRN
            'name': patient.patient_name,
            'first_name': first_name,
            'last_name': last_name,
            'birth_date': patient.birth_date,
            'sex': patient.sex,
            'address': patient.address,
            'phone': patient.phone,
            'email': '',  # PatientRecord doesn't have email field
            'created_at': patient.created_date
        })
    return jsonify(patients)

@app.route('/api/patients/export/csv', methods=['GET'])
def export_patients_csv():
    """Export patients list to CSV"""
    patients = []
    for patient_id, patient in patient_registry.patients.items():
        # Split patient_name into first and last names
        name_parts = patient.patient_name.split('^') if '^' in patient.patient_name else [patient.patient_name, '']
        last_name = name_parts[0] if len(name_parts) > 0 else ''
        first_name = name_parts[1] if len(name_parts) > 1 else ''
        
        patients.append({
            'patient_id': patient_id,
            'mrn': patient.patient_id,
            'first_name': first_name,
            'last_name': last_name,
            'full_name': patient.patient_name,
            'birth_date': patient.birth_date,
            'sex': patient.sex,
            'address': patient.address,
            'phone': patient.phone,
            'created_date': patient.created_date,
            'last_used': patient.last_used,
            'study_count': patient.study_count
        })
    
    # Create CSV content
    output = io.StringIO()
    if patients:
        writer = csv.DictWriter(output, fieldnames=patients[0].keys())
        writer.writeheader()
        writer.writerows(patients)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=patients_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/api/patients', methods=['POST'])
def create_patient():
    """Create a new patient"""
    data = request.json
    
    # Create patient manually using the expected format
    patient_id = data.get('mrn') or f"P{len(patient_registry.patients) + 1:06d}"
    patient_name = f"{data.get('last_name', 'DOE')}^{data.get('first_name', 'JOHN')}"
    
    # Create patient record directly
    from src.patient_config import PatientRecord
    from datetime import datetime
    
    patient = PatientRecord(
        patient_id=patient_id,
        patient_name=patient_name,
        birth_date=data.get('birth_date', '1990-01-01'),
        sex=data.get('sex', 'M'),
        address=data.get('address', ''),
        phone=data.get('phone', ''),
        created_date=datetime.now().isoformat(),
        last_used=None,
        study_count=0
    )
    
    # Add to registry
    patient_registry.patients[patient_id] = patient
    
    patient_registry.save_registry()
    
    return jsonify({
        'id': patient.patient_id,
        'patient_name': patient.patient_name,
        'birth_date': patient.birth_date,
        'sex': patient.sex,
        'message': 'Patient created successfully'
    })

@app.route('/api/patients/<patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update a patient"""
    if patient_id not in patient_registry.patients:
        return jsonify({'error': 'Patient not found'}), 404
    
    data = request.json
    patient = patient_registry.patients[patient_id]
    
    # Update patient fields
    # Note: PatientRecord uses patient_name (LAST^FIRST) and patient_id instead of separate fields
    if 'first_name' in data and 'last_name' in data:
        patient.patient_name = f"{data['last_name']}^{data['first_name']}"
    elif 'first_name' in data or 'last_name' in data:
        # Parse current name if only one part is being updated
        name_parts = patient.patient_name.split('^') if '^' in patient.patient_name else [patient.patient_name, '']
        current_last = name_parts[0] if len(name_parts) > 0 else ''
        current_first = name_parts[1] if len(name_parts) > 1 else ''
        
        new_last = data.get('last_name', current_last)
        new_first = data.get('first_name', current_first)
        patient.patient_name = f"{new_last}^{new_first}"
    
    if 'mrn' in data:
        patient.patient_id = data['mrn']
    if 'birth_date' in data:
        patient.birth_date = data['birth_date']
    if 'sex' in data:
        patient.sex = data['sex']
    if 'address' in data:
        patient.address = data['address']
    if 'phone' in data:
        patient.phone = data['phone']
    # Note: PatientRecord doesn't have email field, so we ignore it
    
    try:
        patient_registry.save_registry()
        return jsonify({
            'id': patient.patient_id,
            'message': 'Patient updated successfully'
        })
    except Exception as e:
        return jsonify({'error': f'Error saving patient: {str(e)}'}), 500

@app.route('/api/patients/<patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete a patient"""
    if patient_id in patient_registry.patients:
        del patient_registry.patients[patient_id]
        patient_registry.save_registry()
        return jsonify({'message': 'Patient deleted successfully'})
    return jsonify({'error': 'Patient not found'}), 404

@app.route('/api/patients/batch-delete', methods=['POST'])
def batch_delete_patients():
    """Delete multiple patients at once"""
    try:
        patient_ids = request.json.get('patient_ids', [])
        print(f"DEBUG: Received batch delete request for IDs: {patient_ids}")
        
        if not patient_ids:
            return jsonify({'error': 'No patient IDs provided'}), 400
        
        deleted_count = 0
        not_found_count = 0
        errors = []
        
        for patient_id in patient_ids:
            try:
                if patient_id in patient_registry.patients:
                    del patient_registry.patients[patient_id]
                    deleted_count += 1
                    print(f"DEBUG: Deleted patient {patient_id}")
                else:
                    not_found_count += 1
                    print(f"DEBUG: Patient {patient_id} not found")
            except Exception as e:
                errors.append(f"Error deleting patient {patient_id}: {str(e)}")
                print(f"DEBUG: Error deleting patient {patient_id}: {str(e)}")
        
        if deleted_count > 0:
            try:
                patient_registry.save_registry()
                print("DEBUG: Successfully saved patient registry")
            except Exception as e:
                print(f"DEBUG: Error saving registry: {str(e)}")
                return jsonify({'error': f'Error saving changes: {str(e)}'}), 500
        
        result = {
            'success': True,
            'deleted': deleted_count,
            'not_found': not_found_count,
            'message': f'Successfully deleted {deleted_count} patient(s)'
        }
        
        if errors:
            result['errors'] = errors
        
        print(f"DEBUG: Returning result: {result}")
        return jsonify(result)
        
    except Exception as e:
        error_msg = f'Unexpected error in batch delete: {str(e)}'
        print(f"DEBUG: {error_msg}")
        return jsonify({'error': error_msg}), 500

@app.route('/api/patients/search', methods=['POST'])
def search_patients():
    """Search patients"""
    query = request.json.get('query', '')
    results = patient_registry.search_patients(query)
    
    patients = []
    for patient_id, patient in results.items() if hasattr(results, 'items') else [(p.patient_id, p) for p in results]:
        # Split patient_name into first and last names
        name_parts = patient.patient_name.split('^') if '^' in patient.patient_name else [patient.patient_name, '']
        last_name = name_parts[0] if len(name_parts) > 0 else ''
        first_name = name_parts[1] if len(name_parts) > 1 else ''
        
        patients.append({
            'id': patient_id if isinstance(patient_id, str) else patient.patient_id,
            'mrn': patient.patient_id,  # Use patient_id as MRN
            'name': patient.patient_name,
            'first_name': first_name,
            'last_name': last_name,
            'birth_date': patient.birth_date,
            'sex': patient.sex,
            'address': patient.address,
            'phone': patient.phone,
            'email': '',  # PatientRecord doesn't have email field
            'created_at': patient.created_date
        })
    
    return jsonify(patients)

@app.route('/api/generate', methods=['POST'])
def generate_dicom():
    """Generate multi-series DICOM study"""
    data = request.json
    
    try:
        # Parse parameters
        patient_name = data.get('patient_name', '')
        patient_id = data.get('patient_id', '')
        accession = data.get('accession', '')
        study_desc = data.get('study_desc', 'Test Study')
        study_date = data.get('study_date', '')
        series_config = data.get('series', [{'images': 1, 'procedure': 'PA-VIEW'}])
        
        # Generate DICOM
        if patient_name:
            parts = patient_name.split('^')
            if len(parts) == 2:
                last_name, first_name = parts
            else:
                last_name = patient_name
                first_name = 'TEST'
        else:
            last_name = None
            first_name = None
        
        output_dir = Path(app.config['UPLOAD_FOLDER'])
        output_dir.mkdir(exist_ok=True)
        
        # Construct patient name for the method
        if last_name and first_name:
            patient_name_param = f"{last_name}^{first_name}"
        elif patient_name:
            patient_name_param = patient_name
        else:
            patient_name_param = None
        
        result = fabricator.create_dx_dicom_study(
            patient_name=patient_name_param,
            patient_id=patient_id if patient_id else None,
            accession=accession if accession else None,
            study_desc=study_desc,
            study_date=study_date if study_date else None,
            series_config=series_config,
            output_dir=str(output_dir)
        )
        
        return jsonify({
            'success': True,
            'study': result,
            'message': f'Generated study with {len(result["series"])} series ({sum(len(s["files"]) for s in result["series"])} total images)'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dicom/list', methods=['GET'])
def list_dicom_files():
    """List all DICOM files (including those in series subdirectories)"""
    output_dir = Path(app.config['UPLOAD_FOLDER'])
    files = []
    
    if output_dir.exists():
        # Search recursively for all DICOM files
        for dcm_file in output_dir.rglob('*.dcm'):
            try:
                ds = pydicom.dcmread(str(dcm_file))
                # Get creation time from file stats
                creation_time = datetime.fromtimestamp(dcm_file.stat().st_ctime)
                created_compact = creation_time.strftime('%Y%m%d%H%M%S')
                
                # Get relative path for display
                relative_path = dcm_file.relative_to(output_dir)
                display_filename = str(relative_path) if relative_path.parent != Path('.') else dcm_file.name
                
                files.append({
                    'filename': dcm_file.name,
                    'filepath': str(relative_path),
                    'full_path': str(dcm_file),
                    'display_name': display_filename,
                    'patient_name': str(getattr(ds, 'PatientName', 'Unknown')),
                    'patient_id': str(getattr(ds, 'PatientID', 'Unknown')),
                    'study_date': str(getattr(ds, 'StudyDate', 'Unknown')),
                    'study_description': str(getattr(ds, 'StudyDescription', 'Unknown')),
                    'series_description': str(getattr(ds, 'SeriesDescription', 'Unknown')),
                    'series_number': str(getattr(ds, 'SeriesNumber', 'Unknown')),
                    'instance_number': str(getattr(ds, 'InstanceNumber', 'Unknown')),
                    'modality': str(getattr(ds, 'Modality', 'Unknown')),
                    'accession_number': str(getattr(ds, 'AccessionNumber', 'Unknown')),
                    'study_instance_uid': str(getattr(ds, 'StudyInstanceUID', 'Unknown')),
                    'size': dcm_file.stat().st_size,
                    'created': created_compact,
                    'created_iso': creation_time.isoformat(),
                    'modified': datetime.fromtimestamp(dcm_file.stat().st_mtime).isoformat()
                })
            except Exception as e:
                files.append({
                    'filename': dcm_file.name,
                    'filepath': str(dcm_file.relative_to(output_dir)) if dcm_file.is_relative_to(output_dir) else str(dcm_file),
                    'error': str(e)
                })
    
    return jsonify(files)

@app.route('/api/dicom/tree', methods=['GET'])
def list_dicom_tree():
    """List DICOM files organized as hierarchical tree structure"""
    output_dir = Path(app.config['UPLOAD_FOLDER'])
    studies = {}
    
    if output_dir.exists():
        # Search recursively for all DICOM files
        for dcm_file in output_dir.rglob('*.dcm'):
            try:
                ds = pydicom.dcmread(str(dcm_file))
                
                # Get key identifiers
                study_uid = str(getattr(ds, 'StudyInstanceUID', 'Unknown'))
                series_uid = str(getattr(ds, 'SeriesInstanceUID', 'Unknown'))
                instance_uid = str(getattr(ds, 'SOPInstanceUID', 'Unknown'))
                
                # Get relative path for display
                relative_path = dcm_file.relative_to(output_dir)
                creation_time = datetime.fromtimestamp(dcm_file.stat().st_ctime)
                
                # Create study entry if not exists
                if study_uid not in studies:
                    studies[study_uid] = {
                        'id': study_uid,
                        'type': 'study',
                        'label': f"{getattr(ds, 'PatientName', 'Unknown Patient')} - {getattr(ds, 'StudyDescription', 'Unknown Study')}",
                        'patient_name': str(getattr(ds, 'PatientName', 'Unknown')),
                        'patient_id': str(getattr(ds, 'PatientID', 'Unknown')),
                        'study_date': str(getattr(ds, 'StudyDate', 'Unknown')),
                        'study_time': str(getattr(ds, 'StudyTime', 'Unknown')),
                        'study_description': str(getattr(ds, 'StudyDescription', 'Unknown')),
                        'modality': str(getattr(ds, 'Modality', 'Unknown')),
                        'created_iso': creation_time.isoformat(),
                        'series': {},
                        'searchable': f"{getattr(ds, 'PatientName', '')} {getattr(ds, 'PatientID', '')} {getattr(ds, 'StudyDescription', '')} {getattr(ds, 'StudyDate', '')}".lower()
                    }
                
                # Create series entry if not exists
                if series_uid not in studies[study_uid]['series']:
                    studies[study_uid]['series'][series_uid] = {
                        'id': series_uid,
                        'type': 'series',
                        'label': f"Series {getattr(ds, 'SeriesNumber', '?')}: {getattr(ds, 'SeriesDescription', 'Unknown Series')}",
                        'series_number': str(getattr(ds, 'SeriesNumber', 'Unknown')),
                        'series_description': str(getattr(ds, 'SeriesDescription', 'Unknown')),
                        'modality': str(getattr(ds, 'Modality', 'Unknown')),
                        'images': {},
                        'searchable': f"{getattr(ds, 'SeriesDescription', '')} {getattr(ds, 'SeriesNumber', '')} {getattr(ds, 'Modality', '')}".lower()
                    }
                
                # Add image entry
                studies[study_uid]['series'][series_uid]['images'][instance_uid] = {
                    'id': instance_uid,
                    'type': 'image',
                    'label': f"Image {getattr(ds, 'InstanceNumber', '?')} ({dcm_file.name})",
                    'filename': dcm_file.name,
                    'filepath': str(relative_path),
                    'full_path': str(dcm_file),
                    'instance_number': str(getattr(ds, 'InstanceNumber', 'Unknown')),
                    'size': dcm_file.stat().st_size,
                    'created_iso': creation_time.isoformat(),
                    'searchable': f"{dcm_file.name} {getattr(ds, 'InstanceNumber', '')}".lower()
                }
                
            except Exception as e:
                # Handle files that can't be read as DICOM
                relative_path = dcm_file.relative_to(output_dir) if dcm_file.is_relative_to(output_dir) else dcm_file
                creation_time = datetime.fromtimestamp(dcm_file.stat().st_ctime)
                error_uid = f"error_{dcm_file.name}"
                
                if error_uid not in studies:
                    studies[error_uid] = {
                        'id': error_uid,
                        'type': 'study',
                        'label': f"Error Files",
                        'patient_name': 'Error',
                        'patient_id': 'Error',
                        'study_description': 'Files that could not be read',
                        'created_iso': creation_time.isoformat(),
                        'series': {},
                        'searchable': 'error files'
                    }
                
                error_series_uid = f"error_series_{dcm_file.parent.name}"
                if error_series_uid not in studies[error_uid]['series']:
                    studies[error_uid]['series'][error_series_uid] = {
                        'id': error_series_uid,
                        'type': 'series',
                        'label': f"Error Files",
                        'series_description': f"Error reading files",
                        'images': {},
                        'searchable': 'error'
                    }
                
                studies[error_uid]['series'][error_series_uid]['images'][dcm_file.name] = {
                    'id': dcm_file.name,
                    'type': 'image',
                    'label': f"{dcm_file.name} (Error)",
                    'filename': dcm_file.name,
                    'filepath': str(relative_path),
                    'error': str(e),
                    'size': dcm_file.stat().st_size,
                    'created_iso': creation_time.isoformat(),
                    'searchable': f"{dcm_file.name} error".lower()
                }
    
    # Convert to hierarchical list format for tosijs tree
    tree_data = []
    for study in sorted(studies.values(), key=lambda x: x.get('created_iso', ''), reverse=True):
        study_node = {
            'id': study['id'],
            'type': 'study',
            'label': study['label'],
            'data': study,
            'children': []
        }
        
        for series in sorted(study['series'].values(), key=lambda x: int(x.get('series_number', 999))):
            series_node = {
                'id': series['id'],
                'type': 'series',
                'label': series['label'],
                'data': series,
                'children': []
            }
            
            for image in sorted(series['images'].values(), key=lambda x: int(x.get('instance_number', 999))):
                image_node = {
                    'id': image['id'],
                    'type': 'image',
                    'label': image['label'],
                    'data': image
                }
                series_node['children'].append(image_node)
            
            study_node['children'].append(series_node)
        
        tree_data.append(study_node)
    
    return jsonify({
        'success': True,
        'tree': tree_data,
        'stats': {
            'total_studies': len([s for s in studies.values() if not s['id'].startswith('error_')]),
            'total_series': sum([len(s['series']) for s in studies.values() if not s['id'].startswith('error_')]),
            'total_images': sum([len(series['images']) for s in studies.values() for series in s['series'].values()]),
            'error_files': len([s for s in studies.values() if s['id'].startswith('error_')])
        }
    })

@app.route('/api/dicom/export/csv', methods=['GET', 'POST'])
def export_dicom_csv():
    """Export DICOM files list or PACS query results to CSV"""
    import csv
    from io import StringIO
    
    if request.method == 'POST':
        # Handle PACS query results export
        data = request.json
        results = data.get('results', [])
        
        if not results:
            return jsonify({'error': 'No results to export'}), 400
            
        # Create CSV content
        output = StringIO()
        
        # Determine columns from first result
        if results:
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\n')
            writer.writeheader()
            writer.writerows(results)
        
        csv_content = output.getvalue()
        output.close()
        
        # Return CSV as downloadable file
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=pacs_query_results.csv'
        return response
    
    else:
        # Handle local DICOM files export (GET request)
        output_dir = Path(app.config['UPLOAD_FOLDER'])
        files = []
        
        if output_dir.exists():
            # Search recursively for all DICOM files
            for dcm_file in output_dir.rglob('*.dcm'):
                try:
                    ds = pydicom.dcmread(str(dcm_file))
                    creation_time = datetime.fromtimestamp(dcm_file.stat().st_ctime)
                    created_compact = creation_time.strftime('%Y%m%d%H%M%S')
                    
                    # Get relative path for display
                    relative_path = dcm_file.relative_to(output_dir)
                    display_filename = str(relative_path) if relative_path.parent != Path('.') else dcm_file.name
                    
                    files.append({
                        'filename': dcm_file.name,
                        'filepath': str(relative_path),
                        'full_path': str(dcm_file),
                        'display_name': display_filename,
                        'patient_name': str(getattr(ds, 'PatientName', 'Unknown')),
                        'patient_id': str(getattr(ds, 'PatientID', 'Unknown')),
                        'study_date': str(getattr(ds, 'StudyDate', 'Unknown')),
                        'study_description': str(getattr(ds, 'StudyDescription', 'Unknown')),
                        'series_description': str(getattr(ds, 'SeriesDescription', 'Unknown')),
                        'series_number': str(getattr(ds, 'SeriesNumber', 'Unknown')),
                        'instance_number': str(getattr(ds, 'InstanceNumber', 'Unknown')),
                        'modality': str(getattr(ds, 'Modality', 'Unknown')),
                        'accession_number': str(getattr(ds, 'AccessionNumber', 'Unknown')),
                        'study_instance_uid': str(getattr(ds, 'StudyInstanceUID', 'Unknown')),
                        'size': dcm_file.stat().st_size,
                        'created': created_compact,
                        'created_iso': creation_time.isoformat(),
                        'modified': datetime.fromtimestamp(dcm_file.stat().st_mtime).isoformat()
                    })
                except Exception as e:
                    files.append({
                        'created': '',
                        'filename': dcm_file.name,
                        'filepath': str(dcm_file.relative_to(output_dir)) if dcm_file.is_relative_to(output_dir) else str(dcm_file),
                        'display_name': dcm_file.name,
                        'patient_name': 'ERROR',
                        'patient_id': 'ERROR',
                        'study_date': 'ERROR',
                        'study_description': 'ERROR',
                        'series_description': 'ERROR',
                        'series_number': 'ERROR',
                        'instance_number': 'ERROR',
                        'modality': 'ERROR',
                        'size_kb': 0,
                    'created_iso': '',
                    'modified_iso': '',
                    'error': str(e)
                })
    
        # Create CSV content  
        output = StringIO()
        if files:
            writer = csv.DictWriter(output, fieldnames=files[0].keys(), lineterminator='\n')
            writer.writeheader()
            writer.writerows(files)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=dicom_files_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/api/dicom/view/<path:filename>', methods=['GET'])
def view_dicom(filename):
    """View DICOM file details and image"""
    output_dir = Path(app.config['UPLOAD_FOLDER'])
    
    # First try direct path
    filepath = output_dir / filename
    
    # If not found, search recursively for the filename
    if not filepath.exists():
        # Extract just the filename from the path for searching
        from pathlib import Path as PathLib
        base_filename = PathLib(filename).name
        found_files = list(output_dir.rglob(base_filename))
        if found_files:
            filepath = found_files[0]  # Use the first match
        else:
            return jsonify({'error': 'File not found'}), 404
    
    try:
        ds = pydicom.dcmread(str(filepath))
        
        # Extract metadata
        metadata = {
            'PatientName': str(getattr(ds, 'PatientName', 'Unknown')),
            'PatientID': str(getattr(ds, 'PatientID', 'Unknown')),
            'PatientBirthDate': str(getattr(ds, 'PatientBirthDate', 'Unknown')),
            'PatientSex': str(getattr(ds, 'PatientSex', 'Unknown')),
            'StudyDate': str(getattr(ds, 'StudyDate', 'Unknown')),
            'StudyTime': str(getattr(ds, 'StudyTime', 'Unknown')),
            'StudyDescription': str(getattr(ds, 'StudyDescription', 'Unknown')),
            'SeriesDescription': str(getattr(ds, 'SeriesDescription', 'Unknown')),
            'SeriesNumber': str(getattr(ds, 'SeriesNumber', 'Unknown')),
            'InstanceNumber': str(getattr(ds, 'InstanceNumber', 'Unknown')),
            'AccessionNumber': str(getattr(ds, 'AccessionNumber', 'Unknown')),
            'Modality': str(getattr(ds, 'Modality', 'Unknown')),
            'StudyInstanceUID': str(getattr(ds, 'StudyInstanceUID', 'Unknown')),
            'SeriesInstanceUID': str(getattr(ds, 'SeriesInstanceUID', 'Unknown')),
            'SOPInstanceUID': str(getattr(ds, 'SOPInstanceUID', 'Unknown')),
            'InstitutionName': str(getattr(ds, 'InstitutionName', 'Unknown')),
            'Manufacturer': str(getattr(ds, 'Manufacturer', 'Unknown'))
        }
        
        # Convert pixel data to base64 image
        image_data = None
        if hasattr(ds, 'pixel_array'):
            pixel_array = ds.pixel_array
            
            # Normalize to 8-bit
            if pixel_array.dtype != np.uint8:
                pixel_array = ((pixel_array - pixel_array.min()) / 
                              (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
            
            # Convert to PIL Image
            img = Image.fromarray(pixel_array)
            
            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            image_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return jsonify({
            'metadata': metadata,
            'image': f'data:image/png;base64,{image_data}' if image_data else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dicom/download/<filename>', methods=['GET'])
def download_dicom(filename):
    """Download DICOM file"""
    output_dir = Path(app.config['UPLOAD_FOLDER'])
    
    # First try direct path
    filepath = output_dir / filename
    
    # If not found, search recursively for the filename
    if not filepath.exists():
        found_files = list(output_dir.rglob(filename))
        if found_files:
            filepath = found_files[0]  # Use the first match
        else:
            return jsonify({'error': 'File not found'}), 404
    
    # Send file from its actual directory
    directory = filepath.parent
    filename_only = filepath.name
    return send_from_directory(str(directory), filename_only, as_attachment=True)

@app.route('/api/dicom/headers/<path:filename>', methods=['GET'])
def get_dicom_headers(filename):
    """Get DICOM file headers in formatted text"""
    output_dir = Path(app.config['UPLOAD_FOLDER'])
    
    # First try direct path
    filepath = output_dir / filename
    
    # If not found, search recursively for the filename
    if not filepath.exists():
        # Extract just the filename from the path for searching
        from pathlib import Path as PathLib
        base_filename = PathLib(filename).name
        found_files = list(output_dir.rglob(base_filename))
        if found_files:
            filepath = found_files[0]  # Use the first match
        else:
            return jsonify({'error': 'File not found'}), 404
    
    try:
        ds = pydicom.dcmread(str(filepath))
        
        # Build a dictionary of DICOM tags with standard names
        headers = {}
        
        # Define standard DICOM tags we want to display
        standard_tags = {
            (0x0008, 0x0005): 'SpecificCharacterSet',
            (0x0008, 0x0008): 'ImageType',
            (0x0008, 0x0012): 'InstanceCreationDate',
            (0x0008, 0x0013): 'InstanceCreationTime',
            (0x0008, 0x0014): 'InstanceCreatorUID',
            (0x0008, 0x0016): 'SOPClassUID',
            (0x0008, 0x0018): 'SOPInstanceUID',
            (0x0008, 0x0020): 'StudyDate',
            (0x0008, 0x0021): 'SeriesDate',
            (0x0008, 0x0022): 'AcquisitionDate',
            (0x0008, 0x0030): 'StudyTime',
            (0x0008, 0x0031): 'SeriesTime',
            (0x0008, 0x0032): 'AcquisitionTime',
            (0x0008, 0x0050): 'AccessionNumber',
            (0x0008, 0x0060): 'Modality',
            (0x0008, 0x0070): 'Manufacturer',
            (0x0008, 0x0080): 'InstitutionName',
            (0x0008, 0x0090): 'ReferringPhysicianName',
            (0x0008, 0x103E): 'SeriesDescription',
            (0x0008, 0x1030): 'StudyDescription',
            (0x0010, 0x0010): 'PatientName',
            (0x0010, 0x0020): 'PatientID',
            (0x0010, 0x0030): 'PatientBirthDate',
            (0x0010, 0x0040): 'PatientSex',
            (0x0018, 0x0050): 'SliceThickness',
            (0x0018, 0x0060): 'KVP',
            (0x0018, 0x1000): 'DeviceSerialNumber',
            (0x0018, 0x1020): 'SoftwareVersions',
            (0x0020, 0x000D): 'StudyInstanceUID',
            (0x0020, 0x000E): 'SeriesInstanceUID',
            (0x0020, 0x0010): 'StudyID',
            (0x0020, 0x0011): 'SeriesNumber',
            (0x0020, 0x0013): 'InstanceNumber',
            (0x0028, 0x0002): 'SamplesPerPixel',
            (0x0028, 0x0004): 'PhotometricInterpretation',
            (0x0028, 0x0010): 'Rows',
            (0x0028, 0x0011): 'Columns',
            (0x0028, 0x0100): 'BitsAllocated',
            (0x0028, 0x0101): 'BitsStored',
            (0x0028, 0x0102): 'HighBit',
            (0x0028, 0x0103): 'PixelRepresentation',
        }
        
        # Extract all available tags from the dataset
        for elem in ds:
            tag_tuple = (elem.tag.group, elem.tag.element)
            tag_str = f"{elem.tag.group:04X},{elem.tag.element:04X}"
            
            # Get the standard name if available, otherwise use the keyword or tag
            if tag_tuple in standard_tags:
                tag_name = standard_tags[tag_tuple]
            else:
                tag_name = elem.keyword if hasattr(elem, 'keyword') and elem.keyword else elem.name
            
            # Get the value and convert to string
            try:
                if elem.VR == 'SQ':  # Sequence
                    value = f"[Sequence with {len(elem.value)} item(s)]"
                elif hasattr(elem, 'value') and elem.value is not None:
                    value = str(elem.value)
                else:
                    value = ""
            except:
                value = "[Unable to read value]"
            
            headers[tag_str] = {
                'name': tag_name,
                'value': value,
                'vr': elem.VR if hasattr(elem, 'VR') else 'UN',
                'group': elem.tag.group,
                'element': elem.tag.element
            }
        
        # Sort headers by tag ID (group, then element)
        sorted_headers = dict(sorted(headers.items(), key=lambda x: (x[1]['group'], x[1]['element'])))
        
        return jsonify({
            'success': True,
            'filename': filename,
            'headers': sorted_headers
        })
        
    except Exception as e:
        return jsonify({'error': f'Error reading DICOM file: {str(e)}'}), 500

@app.route('/api/dicom/delete/<filename>', methods=['DELETE'])
def delete_dicom(filename):
    """Delete DICOM file"""
    output_dir = Path(app.config['UPLOAD_FOLDER'])
    
    # First try direct path
    filepath = output_dir / filename
    
    # If not found, search recursively for the filename
    if not filepath.exists():
        found_files = list(output_dir.rglob(filename))
        if found_files:
            filepath = found_files[0]  # Use the first match
        else:
            return jsonify({'error': 'File not found'}), 404
    
    if filepath.exists():
        filepath.unlink()
        return jsonify({'message': 'File deleted successfully'})
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/dicom/studies/delete', methods=['DELETE'])
def delete_studies():
    """Delete multiple DICOM studies and their associated files"""
    import shutil
    
    data = request.get_json()
    if not data or 'study_uids' not in data:
        return jsonify({'error': 'No study UIDs provided'}), 400
    
    study_uids = data['study_uids']
    if not isinstance(study_uids, list) or len(study_uids) == 0:
        return jsonify({'error': 'Invalid study UIDs format'}), 400
    
    output_dir = Path(app.config['UPLOAD_FOLDER'])
    deleted_count = 0
    errors = []
    
    # Get all studies first to find the folders to delete
    # We need to recreate the logic from list_dicom_studies since it's a route function
    studies = {}
    if output_dir.exists():
        # Search recursively for all DICOM files
        for dcm_file in output_dir.rglob('*.dcm'):
            try:
                ds = pydicom.dcmread(str(dcm_file))
                study_uid = str(getattr(ds, 'StudyInstanceUID', 'Unknown'))
                
                if study_uid not in studies:
                    from datetime import datetime
                    creation_time = datetime.fromtimestamp(dcm_file.stat().st_ctime)
                    
                    # Determine study folder (for newer generated studies)
                    study_folder = None
                    file_parts = dcm_file.relative_to(output_dir).parts
                    if len(file_parts) > 1:  # File is in a subdirectory
                        study_folder = file_parts[0]
                    
                    studies[study_uid] = {
                        'study_uid': study_uid,
                        'study_folder': study_folder,
                        'created': creation_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'created_iso': creation_time.isoformat()
                    }
            except Exception as e:
                # Skip files that can't be read as DICOM
                continue
    
    studies_by_uid = studies
    
    for study_uid in study_uids:
        try:
            if study_uid in studies_by_uid:
                study = studies_by_uid[study_uid]
                if 'study_folder' in study and study['study_folder']:
                    # Delete the entire study folder
                    study_path = output_dir / study['study_folder']
                    if study_path.exists() and study_path.is_dir():
                        shutil.rmtree(study_path)
                        deleted_count += 1
                    else:
                        errors.append(f"Study folder not found: {study['study_folder']}")
                else:
                    # Fallback: try to find and delete individual files
                    # This handles older generated studies without folder structure
                    found_files = list(output_dir.rglob(f"*{study_uid}*"))
                    if found_files:
                        for file_path in found_files:
                            if file_path.is_file():
                                file_path.unlink()
                        deleted_count += 1
                    else:
                        errors.append(f"No files found for study: {study_uid}")
            else:
                errors.append(f"Study not found: {study_uid}")
        except Exception as e:
            errors.append(f"Error deleting study {study_uid}: {str(e)}")
    
    response = {
        'success': deleted_count > 0,
        'deleted_count': deleted_count,
        'total_requested': len(study_uids)
    }
    
    if errors:
        response['errors'] = errors
        response['message'] = f"Deleted {deleted_count} of {len(study_uids)} studies. Some errors occurred."
    else:
        response['message'] = f"Successfully deleted {deleted_count} study(ies)"
    
    return jsonify(response)

@app.route('/api/dicom/launch/<filename>', methods=['POST'])
def launch_dicom_viewer(filename):
    """Launch external DICOM viewer with the specified file"""
    import subprocess
    import platform
    
    output_dir = Path(app.config['UPLOAD_FOLDER'])
    
    # First try direct path
    filepath = output_dir / filename
    
    # If not found, search recursively for the filename
    if not filepath.exists():
        found_files = list(output_dir.rglob(filename))
        if found_files:
            filepath = found_files[0]  # Use the first match
        else:
            return jsonify({'error': 'File not found'}), 404
    
    try:
        system = platform.system()
        absolute_path = str(filepath.absolute())
        
        if system == 'Darwin':  # macOS
            # Try common macOS DICOM viewers in order of preference
            viewers = [
                ['open', '-a', 'OsiriX Lite', absolute_path],
                ['open', '-a', 'OsiriX MD', absolute_path], 
                ['open', '-a', 'Horos', absolute_path],
                ['open', '-a', 'RadiAnt DICOM Viewer', absolute_path],
                ['open', '-a', 'DICOM Viewer', absolute_path],
                ['open', absolute_path]  # Default system handler
            ]
        elif system == 'Windows':
            # Try common Windows DICOM viewers
            viewers = [
                ['start', '', absolute_path],  # Default system handler
                # Add specific Windows DICOM viewer paths here if needed
            ]
        else:  # Linux
            # Try common Linux DICOM viewers
            viewers = [
                ['xdg-open', absolute_path],  # Default system handler
                ['aeskulap', absolute_path],
                ['ginkgocadx', absolute_path]
            ]
        
        # Try each viewer until one works
        for viewer_cmd in viewers:
            try:
                if system == 'Windows' and viewer_cmd[0] == 'start':
                    subprocess.run(viewer_cmd, shell=True, check=True)
                else:
                    subprocess.run(viewer_cmd, check=True)
                
                return jsonify({
                    'success': True,
                    'message': f'Launched DICOM viewer for {filename}',
                    'viewer': ' '.join(viewer_cmd)
                })
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        # If no viewers worked, return error
        return jsonify({
            'success': False,
            'error': 'No suitable DICOM viewer found on system',
            'suggestion': 'Please install OsiriX, Horos, or another DICOM viewer'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error launching DICOM viewer: {str(e)}'
        }), 500

@app.route('/api/pacs/status', methods=['GET'])
def pacs_status():
    """Check PACS server status using default configuration"""
    import subprocess
    
    # Get default PACS configuration
    default_config = pacs_manager.get_default_config()
    if not default_config:
        return jsonify({
            'status': 'offline',
            'message': 'No default PACS configuration found',
            'details': {}
        })
    
    try:
        # Try to connect to PACS using echoscu with default config
        result = subprocess.run(
            ['echoscu', '-aet', default_config.aet, '-aec', default_config.aec, 
             default_config.host, str(default_config.port)],
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return jsonify({
                'status': 'online',
                'message': f'PACS server "{default_config.name}" is running',
                'details': {
                    'name': default_config.name,
                    'aet': default_config.aec,
                    'host': default_config.host,
                    'port': default_config.port,
                    'our_aet': default_config.aet
                }
            })
        else:
            return jsonify({
                'status': 'offline',
                'message': 'PACS server is not responding'
            })
    except Exception as e:
        return jsonify({
            'status': 'unknown',
            'message': 'Could not check PACS status',
            'error': str(e)
        })

@app.route('/api/dicom/studies', methods=['GET'])
def list_dicom_studies():
    """List DICOM studies (grouped by StudyInstanceUID)"""
    output_dir = Path(app.config['UPLOAD_FOLDER'])
    studies = {}
    
    if output_dir.exists():
        # Search recursively for all DICOM files
        for dcm_file in output_dir.rglob('*.dcm'):
            try:
                ds = pydicom.dcmread(str(dcm_file))
                study_uid = str(getattr(ds, 'StudyInstanceUID', 'Unknown'))
                
                if study_uid not in studies:
                    creation_time = datetime.fromtimestamp(dcm_file.stat().st_ctime)
                    studies[study_uid] = {
                        'study_uid': study_uid,
                        'patient_name': str(getattr(ds, 'PatientName', 'Unknown')),
                        'patient_id': str(getattr(ds, 'PatientID', 'Unknown')),
                        'study_date': str(getattr(ds, 'StudyDate', 'Unknown')),
                        'study_time': str(getattr(ds, 'StudyTime', 'Unknown')),
                        'study_description': str(getattr(ds, 'StudyDescription', 'Unknown')),
                        'accession_number': str(getattr(ds, 'AccessionNumber', 'Unknown')),
                        'modality': str(getattr(ds, 'Modality', 'Unknown')),
                        'created': creation_time.strftime('%Y%m%d%H%M%S'),
                        'created_iso': creation_time.isoformat(),
                        'series': {},
                        'total_files': 0,
                        'total_size': 0,
                        'study_folder': None
                    }
                
                # Add series information
                series_uid = str(getattr(ds, 'SeriesInstanceUID', 'Unknown'))
                series_number = str(getattr(ds, 'SeriesNumber', 'Unknown'))
                
                if series_uid not in studies[study_uid]['series']:
                    studies[study_uid]['series'][series_uid] = {
                        'series_uid': series_uid,
                        'series_number': series_number,
                        'series_description': str(getattr(ds, 'SeriesDescription', 'Unknown')),
                        'modality': str(getattr(ds, 'Modality', 'Unknown')),
                        'files': 0
                    }
                
                studies[study_uid]['series'][series_uid]['files'] += 1
                studies[study_uid]['total_files'] += 1
                studies[study_uid]['total_size'] += dcm_file.stat().st_size
                
                # Determine study folder (parent directory structure)
                relative_path = dcm_file.relative_to(output_dir)
                if len(relative_path.parts) > 1:
                    studies[study_uid]['study_folder'] = str(relative_path.parts[0])
                    
            except Exception as e:
                print(f"Error reading DICOM file {dcm_file}: {e}")
                continue
    
    # Convert to list and sort by creation date (newest first)
    studies_list = list(studies.values())
    studies_list.sort(key=lambda s: s.get('created', ''), reverse=True)
    
    return jsonify(studies_list)

@app.route('/api/pacs/query-study', methods=['POST'])
def query_study_on_pacs():
    """Query if a study exists on PACS by StudyInstanceUID"""
    import subprocess
    
    data = request.json
    study_uid = data.get('study_uid')
    pacs_config_id = data.get('pacs_config_id')
    
    if not study_uid:
        return jsonify({
            'success': False,
            'error': 'StudyInstanceUID is required'
        }), 400
    
    # Get PACS configuration
    if pacs_config_id:
        pacs_config = pacs_manager.get_config(pacs_config_id)
        if not pacs_config:
            return jsonify({
                'success': False,
                'error': 'PACS configuration not found'
            }), 404
    else:
        # Use default PACS config
        pacs_config = pacs_manager.get_default_config()
        if not pacs_config:
            return jsonify({
                'success': False,
                'error': 'No PACS configuration available'
            }), 400
    
    try:
        # Use findscu to query for the study
        cmd = [
            'findscu',
            '-aet', pacs_config.aet,
            '-aec', pacs_config.aec,
            pacs_config.host, str(pacs_config.port),
            '-S',  # Study level query
            '-k', 'QueryRetrieveLevel=STUDY',
            '-k', f'StudyInstanceUID={study_uid}',
            '-k', 'PatientName',
            '-k', 'StudyDate',
            '-k', 'StudyDescription',
            '-k', 'NumberOfStudyRelatedSeries',
            '-k', 'NumberOfStudyRelatedInstances'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"DEBUG: query-study command: {' '.join(cmd)}")
        print(f"DEBUG: query-study exit code: {result.returncode}")
        print(f"DEBUG: query-study stdout: {result.stdout[:500]}...")
        print(f"DEBUG: query-study stderr: {result.stderr[:500]}...")
        
        # Parse the DICOM query response (findscu outputs to stderr)
        output_to_parse = result.stderr if result.stderr else result.stdout
        lines = output_to_parse.strip().split('\n') if output_to_parse else []
        study_info = {}
        study_found = False
        
        print(f"DEBUG: Parsing {len(lines)} lines of output")
        print(f"DEBUG: First few lines: {lines[:5]}")
        
        for line in lines:
            if '(0010,0010)' in line and 'PN' in line:  # Patient Name
                study_info['patient_name'] = line.split('[')[1].split(']')[0] if '[' in line else 'Unknown'
                study_found = True
                print(f"DEBUG: Found patient name: {study_info['patient_name']}")
            elif '(0008,0020)' in line and 'DA' in line:  # Study Date
                study_info['study_date'] = line.split('[')[1].split(']')[0] if '[' in line else 'Unknown'
                study_found = True
            elif '(0008,1030)' in line and 'LO' in line:  # Study Description
                study_info['study_description'] = line.split('[')[1].split(']')[0] if '[' in line else 'Unknown'
                study_found = True
            elif '(0020,1206)' in line and 'IS' in line:  # Number of Study Related Series
                study_info['series_count'] = line.split('[')[1].split(']')[0] if '[' in line else '0'
                study_found = True
            elif '(0020,1208)' in line and 'IS' in line:  # Number of Study Related Instances
                study_info['instance_count'] = line.split('[')[1].split(']')[0] if '[' in line else '0'
                study_found = True
            elif '(0020,000d)' in line and 'UI' in line:  # Study Instance UID
                study_found = True
        
        if study_found:
            return jsonify({
                'success': True,
                'exists': True,
                'study_uid': study_uid,
                'study_info': study_info,
                'pacs_response': result.stdout,
                'command_output': {
                    'command': ' '.join(cmd),
                    'output': result.stdout,
                    'exit_code': result.returncode
                }
            })
        else:
            return jsonify({
                'success': True,
                'exists': False,
                'study_uid': study_uid,
                'message': 'Study not found on PACS',
                'pacs_response': result.stdout or result.stderr,
                'command_output': {
                    'command': ' '.join(cmd),
                    'output': result.stdout or result.stderr,
                    'exit_code': result.returncode
                }
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Timeout querying PACS server'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error querying PACS: {str(e)}'
        }), 500

@app.route('/api/pacs/send-study', methods=['POST'])
def send_study_to_pacs():
    """Send an entire study (all series) to PACS"""
    import subprocess
    import glob
    
    data = request.json
    study_folder = data.get('study_folder')
    pacs_config_id = data.get('pacs_config_id')
    
    if not study_folder:
        return jsonify({
            'success': False,
            'error': 'Study folder path is required'
        }), 400
    
    # Get PACS configuration
    if pacs_config_id:
        pacs_config = pacs_manager.get_config(pacs_config_id)
        if not pacs_config:
            return jsonify({
                'success': False,
                'error': 'PACS configuration not found'
            }), 404
    else:
        # Use default PACS config
        pacs_config = pacs_manager.get_default_config()
        if not pacs_config:
            return jsonify({
                'success': False,
                'error': 'No PACS configuration available'
            }), 400
    
    # Convert relative path to absolute if needed
    if not study_folder.startswith('/'):
        study_folder = Path(app.config['UPLOAD_FOLDER']) / study_folder
    else:
        study_folder = Path(study_folder)
    
    if not study_folder.exists():
        return jsonify({
            'success': False,
            'error': 'Study folder not found'
        }), 404
    
    try:
        # Find all DICOM files in the study folder (all series)
        dcm_files = list(study_folder.rglob('*.dcm'))
        
        if not dcm_files:
            return jsonify({
                'success': False,
                'error': 'No DICOM files found in study folder'
            }), 404
        
        # Get study info from first file for confirmation
        import pydicom
        first_file = pydicom.dcmread(str(dcm_files[0]))
        study_info = {
            'patient_name': str(getattr(first_file, 'PatientName', 'Unknown')),
            'patient_id': str(getattr(first_file, 'PatientID', 'Unknown')),
            'study_description': str(getattr(first_file, 'StudyDescription', 'Unknown')),
            'accession_number': str(getattr(first_file, 'AccessionNumber', 'Unknown')),
            'study_uid': str(getattr(first_file, 'StudyInstanceUID', 'Unknown')),
            'file_count': len(dcm_files),
            'series_count': len(set(str(pydicom.dcmread(str(f)).SeriesInstanceUID) for f in dcm_files))
        }
        
        # Send files to PACS using storescu with dynamic config
        cmd = [
            'storescu', 
            '-aet', pacs_config.aet,  # Our Application Entity Title
            '-aec', pacs_config.aec,  # PACS Application Entity Title
            pacs_config.host, str(pacs_config.port)  # PACS host and port
        ] + [str(f) for f in dcm_files]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout for large studies
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': f'Successfully sent study to PACS',
                'study_info': study_info,
                'details': {
                    'files_sent': len(dcm_files),
                    'series_count': study_info['series_count'],
                    'pacs_output': result.stdout
                },
                'command_log': {
                    'command': ' '.join(cmd),
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode,
                    'pacs_config': {
                        'name': pacs_config.name,
                        'host': pacs_config.host,
                        'port': pacs_config.port,
                        'aet': pacs_config.aet,
                        'aec': pacs_config.aec
                    }
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send study to PACS',
                'details': {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                },
                'command_log': {
                    'command': ' '.join(cmd),
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode,
                    'pacs_config': {
                        'name': pacs_config.name,
                        'host': pacs_config.host,
                        'port': pacs_config.port,
                        'aet': pacs_config.aet,
                        'aec': pacs_config.aec
                    }
                }
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Timeout sending study to PACS (study too large or PACS not responding)'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error sending study to PACS: {str(e)}'
        }), 500

# PACS Configuration Management Endpoints
@app.route('/api/pacs/configs', methods=['GET'])
def list_pacs_configs():
    """List all PACS configurations"""
    try:
        configs = pacs_manager.list_configs()
        return jsonify({
            'success': True,
            'configs': [
                {
                    'id': config.id,
                    'name': config.name,
                    'description': config.description,
                    'host': config.host,
                    'port': config.port,
                    'aet': config.aet,
                    'aec': config.aec,
                    'is_default': config.is_default,
                    'is_active': config.is_active,
                    'created_date': config.created_date,
                    'modified_date': config.modified_date,
                    'last_tested': config.last_tested,
                    'test_status': config.test_status,
                    'test_message': config.test_message
                } for config in configs
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error listing PACS configurations: {str(e)}'
        }), 500

@app.route('/api/pacs/configs', methods=['POST'])
def create_pacs_config():
    """Create a new PACS configuration"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'host', 'port', 'aet', 'aec']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create configuration
        config = pacs_manager.create_config(
            name=data['name'],
            description=data.get('description', ''),
            host=data['host'],
            port=int(data['port']),
            aet=data['aet'],
            aec=data['aec'],
            is_default=data.get('is_default', False)
        )
        
        return jsonify({
            'success': True,
            'message': 'PACS configuration created successfully',
            'config': {
                'id': config.id,
                'name': config.name,
                'description': config.description,
                'host': config.host,
                'port': config.port,
                'aet': config.aet,
                'aec': config.aec,
                'is_default': config.is_default,
                'is_active': config.is_active,
                'created_date': config.created_date,
                'modified_date': config.modified_date
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid port number: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error creating PACS configuration: {str(e)}'
        }), 500

@app.route('/api/pacs/configs/<config_id>', methods=['GET'])
def get_pacs_config(config_id):
    """Get a specific PACS configuration"""
    try:
        config = pacs_manager.get_config(config_id)
        if not config:
            return jsonify({
                'success': False,
                'error': 'PACS configuration not found'
            }), 404
        
        return jsonify({
            'success': True,
            'config': {
                'id': config.id,
                'name': config.name,
                'description': config.description,
                'host': config.host,
                'port': config.port,
                'aet': config.aet,
                'aec': config.aec,
                'is_default': config.is_default,
                'is_active': config.is_active,
                'created_date': config.created_date,
                'modified_date': config.modified_date,
                'last_tested': config.last_tested,
                'test_status': config.test_status,
                'test_message': config.test_message
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting PACS configuration: {str(e)}'
        }), 500

@app.route('/api/pacs/configs/<config_id>', methods=['PUT'])
def update_pacs_config(config_id):
    """Update a PACS configuration"""
    try:
        data = request.json
        
        # Convert port to int if provided
        if 'port' in data:
            data['port'] = int(data['port'])
        
        config = pacs_manager.update_config(config_id, **data)
        if not config:
            return jsonify({
                'success': False,
                'error': 'PACS configuration not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'PACS configuration updated successfully',
            'config': {
                'id': config.id,
                'name': config.name,
                'description': config.description,
                'host': config.host,
                'port': config.port,
                'aet': config.aet,
                'aec': config.aec,
                'is_default': config.is_default,
                'is_active': config.is_active,
                'created_date': config.created_date,
                'modified_date': config.modified_date
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid port number: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error updating PACS configuration: {str(e)}'
        }), 500

@app.route('/api/pacs/configs/<config_id>', methods=['DELETE'])
def delete_pacs_config(config_id):
    """Delete a PACS configuration"""
    try:
        success = pacs_manager.delete_config(config_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'PACS configuration not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'PACS configuration deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error deleting PACS configuration: {str(e)}'
        }), 500

@app.route('/api/pacs/configs/<config_id>/test', methods=['POST'])
def test_pacs_config(config_id):
    """Test connection to a PACS configuration"""
    try:
        result = pacs_manager.test_connection(config_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'output': result.get('output', '')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Connection test failed'),
                'message': result.get('message', '')
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error testing PACS configuration: {str(e)}'
        }), 500

@app.route('/api/pacs/stats', methods=['GET'])
def get_pacs_stats():
    """Get PACS configuration statistics"""
    try:
        stats = pacs_manager.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting PACS statistics: {str(e)}'
        }), 500

@app.route('/api/pacs/query-series', methods=['POST'])
def query_series_details():
    """Query for series-level details for a specific study"""
    import subprocess
    
    data = request.json
    pacs_config_id = data.get('pacs_config_id')
    study_uid = data.get('study_uid')
    
    if not study_uid:
        return jsonify({
            'success': False,
            'error': 'Study UID is required'
        }), 400
    
    # Get PACS configuration
    if pacs_config_id:
        pacs_config = pacs_manager.get_config(pacs_config_id)
        if not pacs_config:
            return jsonify({
                'success': False,
                'error': 'PACS configuration not found'
            }), 404
    else:
        # Use default PACS config
        pacs_config = pacs_manager.get_default_config()
        if not pacs_config:
            return jsonify({
                'success': False,
                'error': 'No PACS configuration available'
            }), 400
    
    try:
        # Build findscu command for series-level query
        cmd = [
            'findscu',
            '-aet', pacs_config.aet,
            '-aec', pacs_config.aec,
            pacs_config.host, str(pacs_config.port),
            '-S',  # Study Root Query/Retrieve Information Model
            '-k', 'QueryRetrieveLevel=SERIES',
            '-k', f'StudyInstanceUID={study_uid}',
            '-k', 'SeriesNumber',
            '-k', 'SeriesDescription',
            '-k', 'SeriesInstanceUID',
            '-k', 'Modality',
            '-k', 'NumberOfSeriesRelatedInstances',
            '-k', 'PerformedProcedureStepDescription',
            '-k', 'RequestedProcedureDescription'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Parse series results
            series_details = []
            current_series = {}
            
            lines = result.stderr.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('I: '):
                    line = line[3:]
                    
                import re
                tag_match = re.match(r'^\(([0-9a-fA-F]{4}),([0-9a-fA-F]{4})\)\s+(\w+)\s+\[([^\]]*)\]\s*#\s*\d+,\s*\d+\s+(.+)$', line)
                
                if tag_match:
                    group, element, vr, value, description = tag_match.groups()
                    tag_name = description.strip()
                    
                    if tag_name == 'SeriesNumber':
                        current_series['series_number'] = value.strip()
                    elif tag_name == 'SeriesDescription':
                        current_series['series_description'] = value.strip()
                    elif tag_name == 'SeriesInstanceUID':
                        current_series['series_uid'] = value.strip()
                    elif tag_name == 'Modality':
                        current_series['modality'] = value.strip()
                    elif tag_name == 'NumberOfSeriesRelatedInstances':
                        current_series['instance_count'] = value.strip()
                    elif tag_name in ['PerformedProcedureStepDescription', 'RequestedProcedureDescription']:
                        # Use whichever procedure description is available
                        if 'procedure_code' not in current_series or not current_series['procedure_code']:
                            current_series['procedure_code'] = value.strip()
                
                elif (line.startswith('--') or 'Find Response:' in line) and current_series:
                    series_details.append(current_series)
                    current_series = {}
            
            # Handle last series
            if current_series:
                series_details.append(current_series)
            
            return jsonify({
                'success': True,
                'series_details': series_details,
                'study_uid': study_uid,
                'command_output': {
                    'command': ' '.join(cmd),
                    'output': result.stderr or result.stdout,
                    'exit_code': result.returncode
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to query series details',
                'command_output': {
                    'command': ' '.join(cmd),
                    'output': result.stderr or result.stdout,
                    'exit_code': result.returncode
                }
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error querying series: {str(e)}'
        }), 500

@app.route('/api/pacs/query', methods=['POST'])
def query_pacs():
    """Comprehensive PACS query with multiple search criteria"""
    import subprocess
    from datetime import datetime, timedelta
    
    data = request.json
    pacs_config_id = data.get('pacs_config_id')
    max_results = data.get('max_results', 100)  # Default to 100 results
    
    # Validate max_results
    if not isinstance(max_results, int) or max_results < 1 or max_results > 1000:
        max_results = 100
    
    # Get PACS configuration
    if pacs_config_id:
        pacs_config = pacs_manager.get_config(pacs_config_id)
        if not pacs_config:
            return jsonify({
                'success': False,
                'error': 'PACS configuration not found'
            }), 404
    else:
        # Use default PACS config
        pacs_config = pacs_manager.get_default_config()
        if not pacs_config:
            return jsonify({
                'success': False,
                'error': 'No PACS configuration available'
            }), 400
    
    # Build query parameters
    search_params = []
    
    # Patient Name
    patient_name = data.get('patient_name', '').strip()
    if patient_name:
        # Support wildcard matching
        if '*' not in patient_name and '?' not in patient_name:
            patient_name = f"*{patient_name}*"
        search_params.extend(['-k', f'PatientName={patient_name}'])
    
    # Patient ID
    patient_id = data.get('patient_id', '').strip()
    if patient_id:
        if '*' not in patient_id and '?' not in patient_id:
            patient_id = f"*{patient_id}*"
        search_params.extend(['-k', f'PatientID={patient_id}'])
    
    # Accession Number
    accession = data.get('accession_number', '').strip()
    if accession:
        if '*' not in accession and '?' not in accession:
            accession = f"*{accession}*"
        search_params.extend(['-k', f'AccessionNumber={accession}'])
    
    # Study Instance UID
    study_uid = data.get('study_uid', '').strip()
    if study_uid:
        search_params.extend(['-k', f'StudyInstanceUID={study_uid}'])
    
    # Series Instance UID  
    series_uid = data.get('series_uid', '').strip()
    if series_uid:
        search_params.extend(['-k', f'SeriesInstanceUID={series_uid}'])
    
    # Date range
    days_ago = data.get('days_ago', 0)
    if days_ago and days_ago > 0:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_ago)
        
        # DICOM date format: YYYYMMDD
        date_range = f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"
        search_params.extend(['-k', f'StudyDate={date_range}'])
    
    # If no search criteria provided, add a default wildcard search to ensure PACS returns results
    if not search_params:
        search_params.extend(['-k', 'PatientName=*'])
    
    # Default query fields to retrieve (only add if not already present as search criteria)
    # Include more fields to match the local DICOM table display
    default_fields = [
        'PatientName',
        'PatientID', 
        'StudyDate',
        'StudyTime',
        'StudyDescription',
        'AccessionNumber',
        'StudyInstanceUID',
        'Modality',
        'SeriesInstanceUID',
        'SeriesNumber',
        'SeriesDescription',
        'NumberOfStudyRelatedSeries',
        'NumberOfStudyRelatedInstances'
    ]
    
    # Check which fields are already present as search criteria
    existing_params = ' '.join(search_params)
    for field in default_fields:
        # Only add as retrieval field if not already present with a value (search criteria)
        if f'-k {field}=' not in existing_params:
            search_params.extend(['-k', field])
    
    try:
        # Determine query level based on search criteria
        query_level = 'STUDY'  # Default to study level
        if series_uid:
            query_level = 'SERIES'
        
        # Add QueryRetrieveLevel parameter 
        search_params.extend(['-k', f'QueryRetrieveLevel={query_level}'])
        
        # Build findscu command
        cmd = [
            'findscu',
            '-aet', pacs_config.aet,
            '-aec', pacs_config.aec,
            pacs_config.host, str(pacs_config.port),
        ]
        
        # Only add --cancel for PACS servers that support it
        # Orthanc Test PACS 2 doesn't support --cancel properly
        if pacs_config.name != "Orthanc Test PACS 2":
            cmd.insert(3, '--cancel')
            cmd.insert(4, str(max_results))
        
        # Add query level flag
        if query_level == 'STUDY':
            cmd.append('-S')  # Study level query flag
        
        cmd.extend(search_params)
        
        # Store command for logging
        cmd_string = ' '.join(cmd)
        print(f"DEBUG: Executing PACS query command: {cmd_string}")
        print(f"DEBUG: Max results requested: {max_results}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"DEBUG: Command exit code: {result.returncode}")
        print(f"DEBUG: Command stdout: {result.stdout[:1000]}...")
        print(f"DEBUG: Command stderr: {result.stderr[:1000]}...")
        
        # Count actual results returned
        stdout_lines = result.stdout.split('\n') if result.stdout else []
        study_count = stdout_lines.count('# Dicom-Data-Set') if stdout_lines else 0
        print(f"DEBUG: Actual studies returned: {study_count}")
        
        if result.returncode == 0:
            # Parse DICOM query results (findscu outputs to stderr)
            studies = parse_dicom_query_output(result.stderr, query_level)
            
            print(f"DEBUG: Parsed {len(studies)} studies from PACS response")
            
            return jsonify({
                'success': True,
                'results': studies,
                'query_info': {
                    'pacs_name': pacs_config.name,
                    'query_level': query_level,
                    'total_results': len(studies),
                    'search_criteria': {
                        'patient_name': data.get('patient_name', ''),
                        'patient_id': data.get('patient_id', ''),
                        'accession_number': data.get('accession_number', ''),
                        'study_uid': data.get('study_uid', ''),
                        'series_uid': data.get('series_uid', ''),
                        'days_ago': days_ago
                    }
                },
                'command_output': {
                    'command': cmd_string,
                    'output': result.stdout,
                    'stderr': result.stderr,
                    'exit_code': result.returncode
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'PACS query failed',
                'details': {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                },
                'command_output': {
                    'command': cmd_string,
                    'output': result.stdout,
                    'stderr': result.stderr,
                    'exit_code': result.returncode
                }
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'PACS query timeout - query took too long to complete'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error querying PACS: {str(e)}'
        }), 500

def parse_dicom_query_output(output, query_level):
    """Parse findscu output into structured data"""
    results = []
    current_study = {}
    
    lines = output.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and certain headers
        if not line or line.startswith('E:'):
            continue
            
        # Handle lines that start with 'I:' - remove the prefix
        if line.startswith('I: '):
            line = line[3:]  # Remove 'I: ' prefix
            
        # Look for DICOM tag patterns: (0010,0010) PN [RISPACSNEW^IMEDONENEW ] #  22, 1 PatientName
        import re
        
        # More flexible regex that handles the actual findscu output format
        tag_match = re.match(r'^\(([0-9a-fA-F]{4}),([0-9a-fA-F]{4})\)\s+(\w+)\s+\[([^\]]*)\]\s*#\s*\d+,\s*\d+\s*(.+)$', line)
        
        if tag_match:
            group, element, vr, value, description = tag_match.groups()
            tag_name = description.strip()
            
            # Map common DICOM tags
            field_mapping = {
                'PatientName': 'patient_name',
                'PatientID': 'patient_id',
                'PatientBirthDate': 'patient_birth_date',
                'PatientSex': 'patient_sex',
                'StudyDate': 'study_date',
                'StudyTime': 'study_time',
                'StudyDescription': 'study_description',
                'AccessionNumber': 'accession_number',
                'StudyInstanceUID': 'study_uid',
                'SeriesInstanceUID': 'series_uid',
                'SeriesNumber': 'series_number',
                'SeriesDescription': 'series_description',
                'Modality': 'modality',
                'NumberOfStudyRelatedSeries': 'series_count',
                'NumberOfStudyRelatedInstances': 'instance_count',
                'ReferringPhysicianName': 'referring_physician',
                'InstitutionName': 'institution_name'
            }
            
            if tag_name in field_mapping:
                field_name = field_mapping[tag_name]
                current_study[field_name] = value.strip()
                print(f"DEBUG: Parsed field {tag_name} = {value.strip()}")
        
        # Also look for lines that might have just the tag and value without full description
        # Format: (0010,0010) PN [RISPACSNEW^IMEDONEW]
        simple_tag_match = re.match(r'^\(([0-9a-fA-F]{4}),([0-9a-fA-F]{4})\)\s+(\w+)\s+\[([^\]]*)\]$', line)
        
        if simple_tag_match:
            group, element, vr, value = simple_tag_match.groups()
            
            # Try to infer the field name from the tag coordinates
            tag_coords = f"({group},{element})"
            tag_mapping = {
                "(0010,0010)": "patient_name",      # PatientName
                "(0010,0020)": "patient_id",        # PatientID
                "(0008,0020)": "study_date",        # StudyDate
                "(0008,0030)": "study_time",        # StudyTime
                "(0008,1030)": "study_description", # StudyDescription
                "(0008,0050)": "accession_number",  # AccessionNumber
                "(0008,0060)": "modality",          # Modality
                "(0020,000d)": "study_uid",         # StudyInstanceUID
                "(0020,000e)": "series_uid",        # SeriesInstanceUID
                "(0020,0011)": "series_number",     # SeriesNumber
                "(0008,103e)": "series_description" # SeriesDescription
            }
            
            if tag_coords in tag_mapping:
                field_name = tag_mapping[tag_coords]
                current_study[field_name] = value.strip()
                print(f"DEBUG: Parsed simple field {field_name} = {value.strip()}")
        
        # End of a result set (look for separator or new study)
        elif (line.startswith('--') or 'Find Response:' in line) and current_study:
            # Format the study data
            formatted_study = format_study_result(current_study)
            if formatted_study:
                results.append(formatted_study)
            current_study = {}
    
    # Handle last study if exists
    if current_study:
        formatted_study = format_study_result(current_study)
        if formatted_study:
            results.append(formatted_study)
    
    return results

def format_study_result(study_data):
    """Format and validate study result data"""
    if not study_data:
        return None
        
    # Format date if present
    study_date = study_data.get('study_date', '')
    if study_date and len(study_date) == 8:
        try:
            # Convert YYYYMMDD to readable format
            date_obj = datetime.strptime(study_date, '%Y%m%d')
            study_data['formatted_date'] = date_obj.strftime('%Y-%m-%d')
        except:
            study_data['formatted_date'] = study_date
    else:
        study_data['formatted_date'] = study_date
    
    # Format time if present
    study_time = study_data.get('study_time', '')
    if study_time and len(study_time) >= 6:
        try:
            # Convert HHMMSS to readable format
            time_obj = datetime.strptime(study_time[:6], '%H%M%S')
            formatted_time = time_obj.strftime('%H:%M:%S')
            study_data['formatted_time'] = formatted_time
            # Replace the original time with formatted version for display
            study_data['study_time'] = formatted_time
        except:
            study_data['formatted_time'] = study_time
    else:
        study_data['formatted_time'] = study_time
    
    # Format patient birth date if present
    birth_date = study_data.get('patient_birth_date', '')
    if birth_date and len(birth_date) == 8:
        try:
            # Convert YYYYMMDD to readable format
            date_obj = datetime.strptime(birth_date, '%Y%m%d')
            study_data['patient_birth_date'] = date_obj.strftime('%Y-%m-%d')
        except:
            pass  # Keep original value if parsing fails
    
    # Convert numeric fields
    for field in ['series_count', 'instance_count']:
        if field in study_data:
            try:
                study_data[field] = int(study_data[field])
            except:
                study_data[field] = 0
    
    # Ensure modality is properly set
    if 'modality' not in study_data or not study_data['modality']:
        # Try to get modality from series if available
        if 'series_description' in study_data and study_data['series_description']:
            # Extract modality from series description if it contains modality info
            series_desc = study_data['series_description'].upper()
            if 'CT' in series_desc:
                study_data['modality'] = 'CT'
            elif 'MR' in series_desc:
                study_data['modality'] = 'MR'
            elif 'DX' in series_desc or 'CR' in series_desc:
                study_data['modality'] = 'DX'
            elif 'US' in series_desc:
                study_data['modality'] = 'US'
            else:
                study_data['modality'] = 'Unknown'
        else:
            study_data['modality'] = 'Unknown'
    
    # Ensure series and instance counts are set
    if 'series_count' not in study_data or not study_data['series_count']:
        study_data['series_count'] = 0
    if 'instance_count' not in study_data or not study_data['instance_count']:
        study_data['instance_count'] = 0
    
    return study_data

@app.route('/api/pacs/c-move', methods=['POST'])
def c_move_study():
    """Perform C-MOVE operation to transfer study between PACS servers"""
    import subprocess
    
    data = request.json
    source_pacs_id = data.get('source_pacs_id')
    destination_pacs_id = data.get('destination_pacs_id')
    study_uid = data.get('study_uid')
    patient_id = data.get('patient_id')
    
    if not all([source_pacs_id, destination_pacs_id, study_uid]):
        return jsonify({
            'success': False,
            'error': 'Missing required parameters: source_pacs_id, destination_pacs_id, study_uid'
        }), 400
    
    # Get PACS configurations
    source_pacs = pacs_manager.get_config(source_pacs_id)
    destination_pacs = pacs_manager.get_config(destination_pacs_id)
    
    if not source_pacs:
        return jsonify({
            'success': False,
            'error': 'Source PACS configuration not found'
        }), 404
    
    if not destination_pacs:
        return jsonify({
            'success': False,
            'error': 'Destination PACS configuration not found'
        }), 404
    
    try:
        # Build movescu command for C-MOVE operation
        # movescu connects to source PACS and requests it to send study to destination
        cmd = [
            'movescu',
            '-v',  # Verbose output
            '-aet', 'DICOMFAB',  # Our AE title
            '-aec', source_pacs.aec,  # Source PACS AE title
            '-aem', destination_pacs.aec,  # Destination AE title (move destination)
            source_pacs.host, str(source_pacs.port),  # Source PACS connection
            '-k', f'StudyInstanceUID={study_uid}',  # Study to move
            '-k', 'QueryRetrieveLevel=STUDY'  # Query/retrieve level
        ]
        
        # Add patient ID if provided for additional filtering
        if patient_id:
            cmd.extend(['-k', f'PatientID={patient_id}'])
        
        print(f"DEBUG: C-MOVE command: {' '.join(cmd)}")
        
        # Execute the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout for C-MOVE operations
        )
        
        print(f"DEBUG: C-MOVE exit code: {result.returncode}")
        print(f"DEBUG: C-MOVE stdout: {result.stdout[:1000]}...")
        print(f"DEBUG: C-MOVE stderr: {result.stderr[:1000]}...")
        
        # Check for success - movescu typically returns 0 on success
        # Also look for success indicators in the output
        success_indicators = [
            'Move operation completed successfully',
            'C-MOVE-RSP',
            'Status: Success'
        ]
        
        error_indicators = [
            'Association Request Failed',
            'No Move Destination',
            'Move SCP Failed',
            'Connection refused',
            'Timeout'
        ]
        
        output_text = result.stdout + result.stderr
        has_success = any(indicator.lower() in output_text.lower() for indicator in success_indicators)
        has_error = any(indicator.lower() in output_text.lower() for indicator in error_indicators)
        
        # Determine success based on exit code and output content
        is_success = (result.returncode == 0) or has_success
        
        if has_error:
            is_success = False
        
        if is_success:
            return jsonify({
                'success': True,
                'message': f'C-MOVE operation completed - study transferred from {source_pacs.name} to {destination_pacs.name}',
                'source_pacs': source_pacs.name,
                'destination_pacs': destination_pacs.name,
                'study_uid': study_uid,
                'command_output': {
                    'command': ' '.join(cmd),
                    'output': result.stdout,
                    'stderr': result.stderr,
                    'exit_code': result.returncode
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'C-MOVE operation failed - check command output for details',
                'details': {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                },
                'command_output': {
                    'command': ' '.join(cmd),
                    'output': result.stdout,
                    'stderr': result.stderr,
                    'exit_code': result.returncode
                }
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'C-MOVE operation timeout - operation took too long to complete'
        }), 500
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'movescu command not found - please install DCMTK tools'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error executing C-MOVE: {str(e)}'
        }), 500

@app.route('/api/parse-orm', methods=['POST'])
def parse_orm_message():
    """Parse ORM HL7 message and extract patient and order data"""
    
    data = request.json
    orm_message = data.get('orm_message', '').strip()
    
    if not orm_message:
        return jsonify({
            'success': False,
            'error': 'No ORM message provided'
        }), 400
    
    try:
        parsed_data = parse_hl7_orm(orm_message)
        return jsonify({
            'success': True,
            'parsed_data': parsed_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error parsing ORM message: {str(e)}'
        }), 500

def infer_modality_from_procedure(procedure_name, procedure_code):
    """Infer DICOM modality from procedure name and code"""
    
    # Convert to lowercase for pattern matching
    text = f"{procedure_name} {procedure_code}".lower()
    
    # Define modality inference patterns
    modality_patterns = {
        'CT': [
            'ct', 'computed tomography', 'cat scan', 'axial', 'spiral', 'helical',
            'contrast ct', 'ct scan', 'cta', 'ct angiogram', 'ct head', 'ct chest',
            'ct abdomen', 'ct pelvis', 'ct brain', 'ct spine'
        ],
        'MR': [
            'mr', 'mri', 'magnetic resonance', 'nmr', 'flair', 't1', 't2', 'dwi',
            'diffusion', 'gradient echo', 'spin echo', 'mr angiogram', 'mra',
            'mr brain', 'mr spine', 'mr knee', 'mr shoulder'
        ],
        'US': [
            'us', 'ultrasound', 'sonography', 'sono', 'echo', 'doppler', 
            'obstetric', 'ob', 'fetal', 'echocardiogram', 'cardiac echo',
            'abdominal us', 'pelvic us', 'renal us', 'thyroid us'
        ],
        'XA': [
            'angio', 'angiography', 'angiogram', 'catheter', 'interventional',
            'fluoroscopy', 'cath', 'cardiac cath', 'coronary', 'peripheral',
            'cerebral angio', 'carotid', 'renal angio'
        ],
        'RF': [
            'fluoroscopy', 'fluoro', 'barium', 'contrast study', 'upper gi',
            'lower gi', 'small bowel', 'esophagram', 'swallow study',
            'defecography', 'cystography', 'urethrography'
        ],
        'NM': [
            'nuclear', 'scintigraphy', 'scan', 'bone scan', 'thyroid scan',
            'liver scan', 'kidney scan', 'gallium', 'technetium', 'spect',
            'myocardial perfusion', 'stress test', 'thallium'
        ],
        'PT': [
            'pet', 'positron emission', 'fdg', 'glucose', 'pet scan',
            'pet/ct', 'oncology', 'tumor', 'metabolic'
        ],
        'MG': [
            'mammo', 'mammography', 'mammogram', 'breast', 'tomosynthesis',
            'breast imaging', 'screening mammo', 'diagnostic mammo'
        ],
        'CR': [
            'computed radiography', 'digital radiography', 'portable',
            'bedside', 'mobile'
        ],
        'DX': [
            'x-ray', 'xray', 'radiography', 'plain film', 'chest', 'abdomen',
            'pelvis', 'extremity', 'spine', 'skull', 'rib', 'pa', 'ap', 'lateral',
            'pa chest', 'ap chest', 'lat chest', 'cxr', 'kub', 'bone',
            'joint', 'hand', 'foot', 'ankle', 'knee', 'shoulder', 'elbow'
        ]
    }
    
    # Check each modality pattern
    for modality, patterns in modality_patterns.items():
        for pattern in patterns:
            if pattern in text:
                return modality
    
    # Default to DX if no pattern matches
    return 'DX'

def parse_hl7_orm(orm_message):
    """Parse HL7 ORM message and extract studies data (one study per OBR)"""
    
    # Split message into segments
    segments = [line.strip() for line in orm_message.split('\n') if line.strip()]
    
    # Initialize data structure - changed to support multiple studies
    result = {
        'patient_name': '',
        'patient_id': '', 
        'birth_date': '',
        'sex': '',
        'studies': []  # Changed from 'series' to 'studies'
    }
    
    current_accession = None
    
    for segment in segments:
        if not segment:
            continue
            
        fields = segment.split('|')
        segment_type = fields[0] if fields else ''
        
        if segment_type == 'MSH':
            # Message header - could extract sending facility, timestamp, etc.
            pass
            
        elif segment_type == 'PID':
            # Patient identification segment
            if len(fields) > 5:
                # PID|1||PatientID^^^System^Type|InternalID|LastName^FirstName||YYYYMMDD|Sex
                if len(fields) > 3 and fields[3]:
                    # Extract patient ID from PID-3 (Patient Identifier List)
                    patient_id_field = fields[3].split('^^^')
                    result['patient_id'] = patient_id_field[0] if patient_id_field else ''
                
                if len(fields) > 5 and fields[5]:
                    # Extract patient name from PID-5 (Patient Name)
                    name_parts = fields[5].split('^')
                    if len(name_parts) >= 2:
                        result['patient_name'] = f"{name_parts[0]}^{name_parts[1]}"
                    else:
                        result['patient_name'] = fields[5]
                
                if len(fields) > 7 and fields[7]:
                    # Extract birth date from PID-7 (Date/Time of Birth)
                    birth_date = fields[7]
                    # Convert YYYYMMDD to DICOM format if needed
                    if len(birth_date) >= 8:
                        result['birth_date'] = birth_date[:8]
                
                if len(fields) > 8 and fields[8]:
                    # Extract sex from PID-8 (Administrative Sex)
                    result['sex'] = fields[8]
        
        elif segment_type == 'ORC':
            # Order common segment
            if len(fields) > 3 and fields[3]:
                # Extract accession number from ORC-3 (Filler Order Number)
                current_accession = fields[3]
        
        elif segment_type == 'OBR':
            # Order detail segment - each OBR becomes a separate study
            
            # Extract study accession from OBR-3 (Filler Order Number) 
            study_accession = None
            if len(fields) > 3 and fields[3]:
                study_accession = fields[3]
            else:
                study_accession = current_accession
            
            # Extract study date from OBR-7 (Observation Date/Time)
            study_date = ''
            if len(fields) > 7 and fields[7]:
                observation_date = fields[7]
                # Convert HL7 datetime (YYYYMMDDHHMMSS) to DICOM date format (YYYYMMDD)
                if len(observation_date) >= 8:
                    study_date = observation_date[:8]
            
            if len(fields) > 4 and fields[4]:
                # Extract procedure from OBR-4 (Universal Service Identifier)
                procedure_field = fields[4]
                procedure_parts = procedure_field.split('^')
                
                procedure_code = procedure_parts[0] if procedure_parts else 'UNKNOWN'
                procedure_name = procedure_parts[1] if len(procedure_parts) > 1 else procedure_code
                
                # Clean up procedure name - remove HL7 formatting
                procedure_name = procedure_name.replace('\\S\\', ' ')
                
                # Infer modality from procedure name/code
                inferred_modality = infer_modality_from_procedure(procedure_name, procedure_code)
                
                # Create a study for this OBR
                study_data = {
                    'accession_number': study_accession,
                    'study_date': study_date,
                    'study_description': procedure_name,
                    'procedure_code': procedure_code,
                    'procedure_name': procedure_name,
                    'modality': inferred_modality,
                    'series': [
                        {
                            'images': 1,  # Default to 1 image per series
                            'modality': inferred_modality,
                            'series_description': procedure_name,
                            'compression': 'uncompressed'
                        }
                    ]
                }
                
                result['studies'].append(study_data)
    
    return result

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5055)