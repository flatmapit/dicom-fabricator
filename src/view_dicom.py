#!/usr/bin/env python3
"""
Simple DICOM viewer for testing
Copyright (c) 2025 Christopher Gentle <chris@flatmapit.com>
"""

import sys
import pydicom
from PIL import Image
import matplotlib.pyplot as plt
import argparse
from pathlib import Path


def view_dicom(filepath):
    """Display a DICOM image with metadata"""
    
    # Read DICOM file
    ds = pydicom.dcmread(filepath)
    
    # Extract metadata
    print("\n" + "="*60)
    print("DICOM METADATA")
    print("="*60)
    print(f"Patient Name: {ds.PatientName if 'PatientName' in ds else 'N/A'}")
    print(f"Patient ID: {ds.PatientID if 'PatientID' in ds else 'N/A'}")
    print(f"Accession Number: {ds.AccessionNumber if 'AccessionNumber' in ds else 'N/A'}")
    print(f"Study Date: {ds.StudyDate if 'StudyDate' in ds else 'N/A'}")
    print(f"Modality: {ds.Modality if 'Modality' in ds else 'N/A'}")
    print(f"Study Description: {ds.StudyDescription if 'StudyDescription' in ds else 'N/A'}")
    print(f"Study UID: {ds.StudyInstanceUID if 'StudyInstanceUID' in ds else 'N/A'}")
    print(f"Image Size: {ds.Rows}x{ds.Columns}")
    print("="*60)
    
    # Get pixel data
    pixel_array = ds.pixel_array
    
    # Create figure with metadata
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    # Display image
    ax1.imshow(pixel_array, cmap='gray')
    ax1.set_title(f"DICOM Image: {Path(filepath).name}")
    ax1.axis('off')
    
    # Display metadata in text panel
    metadata_text = f"""
    DICOM File Information
    ----------------------
    Patient: {ds.PatientName if 'PatientName' in ds else 'N/A'}
    ID: {ds.PatientID if 'PatientID' in ds else 'N/A'}
    Accession: {ds.AccessionNumber if 'AccessionNumber' in ds else 'N/A'}
    
    Study Date: {ds.StudyDate if 'StudyDate' in ds else 'N/A'}
    Study Time: {ds.StudyTime if 'StudyTime' in ds else 'N/A'}
    Modality: {ds.Modality if 'Modality' in ds else 'N/A'}
    
    Study Description:
    {ds.StudyDescription if 'StudyDescription' in ds else 'N/A'}
    
    Body Part: {ds.BodyPartExamined if 'BodyPartExamined' in ds else 'N/A'}
    View Position: {ds.ViewPosition if 'ViewPosition' in ds else 'N/A'}
    
    Image Dimensions: {ds.Rows}x{ds.Columns}
    Bits Stored: {ds.BitsStored if 'BitsStored' in ds else 'N/A'}
    
    Institution: {ds.InstitutionName if 'InstitutionName' in ds else 'N/A'}
    Manufacturer: {ds.Manufacturer if 'Manufacturer' in ds else 'N/A'}
    """
    
    ax2.text(0.05, 0.95, metadata_text, transform=ax2.transAxes,
             fontsize=10, verticalalignment='top', fontfamily='monospace')
    ax2.set_title("DICOM Metadata")
    ax2.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return ds


def list_dicom_files(directory):
    """List all DICOM files in a directory"""
    path = Path(directory)
    dcm_files = list(path.glob("*.dcm"))
    
    if not dcm_files:
        print(f"No DICOM files found in {directory}")
        return []
    
    print(f"\nFound {len(dcm_files)} DICOM file(s):")
    for i, f in enumerate(dcm_files, 1):
        try:
            ds = pydicom.dcmread(f, stop_before_pixels=True)
            patient = ds.PatientName if 'PatientName' in ds else 'Unknown'
            accession = ds.AccessionNumber if 'AccessionNumber' in ds else 'N/A'
            print(f"  {i}. {f.name}")
            print(f"     Patient: {patient}, Accession: {accession}")
        except:
            print(f"  {i}. {f.name} (unable to read)")
    
    return dcm_files


def main():
    parser = argparse.ArgumentParser(description='View DICOM images')
    parser.add_argument('filepath', nargs='?', help='Path to DICOM file')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List all DICOM files in directory')
    parser.add_argument('--dir', '-d', default='./data/dicom_output',
                       help='Directory to search for DICOM files')
    
    args = parser.parse_args()
    
    if args.list or not args.filepath:
        dcm_files = list_dicom_files(args.dir)
        
        if dcm_files and not args.filepath:
            print("\nTo view a file, run:")
            print(f"  python3 view_dicom.py {dcm_files[0]}")
            
            if len(dcm_files) == 1:
                response = input("\nView this file now? (y/n): ")
                if response.lower() == 'y':
                    view_dicom(dcm_files[0])
    else:
        filepath = Path(args.filepath)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        
        view_dicom(filepath)


if __name__ == "__main__":
    main()