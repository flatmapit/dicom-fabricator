#!/usr/bin/env python3
"""
Patient Management CLI Tool
Copyright (c) 2025 Christopher Gentle <chris@flatmapit.com>
"""

import argparse
import json
import sys
from pathlib import Path
from patient_config import PatientRegistry, PatientRecord
from tabulate import tabulate


def list_patients(registry: PatientRegistry, args):
    """List all patients with details"""
    patients = registry.list_patients(limit=args.limit)
    
    if not patients:
        print("No patients found in registry.")
        return
        
    headers = ["Patient ID", "Name", "Sex", "Birth Date", "Studies", "Last Used", "Created"]
    rows = []
    
    for patient in patients:
        rows.append([
            patient.patient_id,
            patient.patient_name,
            patient.sex,
            patient.birth_date,
            patient.study_count,
            patient.last_used[:19] if patient.last_used else "Never",
            patient.created_date[:19] if patient.created_date else "Unknown"
        ])
    
    print(f"\nFound {len(patients)} patient(s):")
    print(tabulate(rows, headers=headers, tablefmt="grid"))


def search_patients(registry: PatientRegistry, args):
    """Search patients by query"""
    patients = registry.search_patients(args.query)
    
    if not patients:
        print(f"No patients found matching '{args.query}'")
        return
        
    headers = ["Patient ID", "Name", "Address", "Studies"]
    rows = []
    
    for patient in patients:
        rows.append([
            patient.patient_id,
            patient.patient_name, 
            patient.address,
            patient.study_count
        ])
    
    print(f"\nFound {len(patients)} patient(s) matching '{args.query}':")
    print(tabulate(rows, headers=headers, tablefmt="grid"))


def show_patient(registry: PatientRegistry, args):
    """Show detailed patient information"""
    patient = registry.get_patient(args.patient_id)
    
    if not patient:
        print(f"Patient {args.patient_id} not found.")
        return
        
    print(f"\nPatient Details:")
    print(f"  ID: {patient.patient_id}")
    print(f"  Name: {patient.patient_name}")
    print(f"  Sex: {patient.sex}")
    print(f"  Birth Date: {patient.birth_date}")
    print(f"  Address: {patient.address}")
    print(f"  Phone: {patient.phone}")
    print(f"  Studies Generated: {patient.study_count}")
    print(f"  Created: {patient.created_date}")
    print(f"  Last Used: {patient.last_used}")


def generate_patient(registry: PatientRegistry, args):
    """Generate a new patient"""
    patient = registry.generate_patient(
        patient_name=args.name,
        patient_id=args.id
    )
    
    print(f"\nGenerated new patient:")
    print(f"  ID: {patient.patient_id}")
    print(f"  Name: {patient.patient_name}")
    print(f"  Sex: {patient.sex}")
    print(f"  Birth Date: {patient.birth_date}")
    print(f"  Address: {patient.address}")
    print(f"  Phone: {patient.phone}")


def delete_patient(registry: PatientRegistry, args):
    """Delete a patient"""
    if not args.force:
        response = input(f"Are you sure you want to delete patient {args.patient_id}? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
            
    success = registry.delete_patient(args.patient_id)
    if success:
        print(f"Patient {args.patient_id} deleted.")
    else:
        print(f"Patient {args.patient_id} not found.")


def show_stats(registry: PatientRegistry, args):
    """Show registry statistics"""
    stats = registry.get_stats()
    
    print("\nPatient Registry Statistics:")
    print(f"  Total Patients: {stats['total_patients']}")
    
    if stats['total_patients'] > 0:
        print(f"  Total Studies Generated: {stats['total_studies_generated']}")
        print(f"  Average Studies per Patient: {stats['avg_studies_per_patient']:.1f}")
        print(f"  Most Recent Patient: {stats['most_recent_patient']}")
        print(f"  Most Used Patient: {stats['most_used_patient']}")


def show_config(registry: PatientRegistry, args):
    """Show current configuration"""
    print("\nCurrent Patient Configuration:")
    print(json.dumps(registry.config, indent=2))


def edit_config(registry: PatientRegistry, args):
    """Edit configuration"""
    config_file = args.config or "patient_config.json"
    
    # Save current config
    registry.save_config(config_file)
    print(f"Configuration saved to {config_file}")
    print("Edit the file and use --load-config to apply changes.")


def load_config(registry: PatientRegistry, args):
    """Load configuration from file"""
    try:
        registry.load_config(args.config_file)
        print(f"Configuration loaded from {args.config_file}")
    except Exception as e:
        print(f"Error loading config: {e}")


def test_id_generation(registry: PatientRegistry, args):
    """Test ID generation patterns"""
    print(f"\nTesting ID generation with current pattern: {registry.config['id_generation']['pattern']}")
    print("Sample IDs:")
    
    for i in range(args.count):
        test_id = registry.id_generator.generate(len(registry.patients) + i)
        print(f"  {i+1}: {test_id}")


def main():
    parser = argparse.ArgumentParser(description='Manage DICOM Fabricator patients')
    parser.add_argument('--registry', '-r', default='./data/patient_registry.json',
                       help='Path to patient registry file')
    parser.add_argument('--config', '-c', default='./config/patient_config.json',
                       help='Path to configuration file')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List patients
    list_parser = subparsers.add_parser('list', help='List all patients')
    list_parser.add_argument('--limit', '-l', type=int, help='Limit number of results')
    
    # Search patients
    search_parser = subparsers.add_parser('search', help='Search patients')
    search_parser.add_argument('query', help='Search query')
    
    # Show patient
    show_parser = subparsers.add_parser('show', help='Show patient details')
    show_parser.add_argument('patient_id', help='Patient ID to show')
    
    # Generate patient
    gen_parser = subparsers.add_parser('generate', help='Generate new patient')
    gen_parser.add_argument('--name', '-n', help='Patient name (format: LAST^FIRST)')
    gen_parser.add_argument('--id', '-i', help='Specific patient ID to use')
    
    # Delete patient
    del_parser = subparsers.add_parser('delete', help='Delete patient')
    del_parser.add_argument('patient_id', help='Patient ID to delete')
    del_parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation')
    
    # Statistics
    subparsers.add_parser('stats', help='Show registry statistics')
    
    # Configuration
    subparsers.add_parser('config', help='Show current configuration')
    subparsers.add_parser('edit-config', help='Save config to file for editing')
    
    load_parser = subparsers.add_parser('load-config', help='Load configuration from file')
    load_parser.add_argument('config_file', help='Configuration file to load')
    
    # Test ID generation
    test_parser = subparsers.add_parser('test-ids', help='Test ID generation pattern')
    test_parser.add_argument('--count', '-n', type=int, default=5, help='Number of test IDs to generate')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize registry
    registry = PatientRegistry(args.registry)
    
    # Load config if specified
    if Path(args.config).exists():
        registry.load_config(args.config)
    
    # Execute command
    commands = {
        'list': list_patients,
        'search': search_patients,
        'show': show_patient,
        'generate': generate_patient,
        'delete': delete_patient,
        'stats': show_stats,
        'config': show_config,
        'edit-config': edit_config,
        'load-config': load_config,
        'test-ids': test_id_generation
    }
    
    try:
        commands[args.command](registry, args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()