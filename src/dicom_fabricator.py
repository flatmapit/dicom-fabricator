#!/usr/bin/env python3
"""
DICOM Fabricator - Generate test DICOM studies without PHI
Copyright (c) 2025 Christopher Gentle <chris@flatmapit.com>
"""

import argparse
import os
import datetime
import random
import string
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ImplicitVRLittleEndian
import numpy as np
from patient_config import PatientRegistry, PatientRecord


class DICOMFabricator:
    """Generate synthetic DICOM studies for testing"""
    
    def __init__(self, patient_registry: PatientRegistry = None):
        self.patient_registry = patient_registry or PatientRegistry()
        
        # Legacy fallback names (kept for backward compatibility)
        self.fake_names = [
            ("TEST", "PATIENT"),
            ("DEMO", "USER"),
            ("SAMPLE", "PERSON"),
            ("FAKE", "NAME"),
            ("SYNTHETIC", "DATA"),
        ]
        self.fake_addresses = [
            "123 Test Street, Sydney NSW 2000",
            "456 Sample Road, Melbourne VIC 3000",
            "789 Fake Avenue, Brisbane QLD 4000",
        ]
        
    def generate_accession(self, pattern=None):
        """Generate accession number based on pattern"""
        if pattern:
            # Parse pattern like "YYYY{two letters}{seven digits starting from 0000001}"
            year = datetime.datetime.now().year
            letters = ''.join(random.choices(string.ascii_uppercase, k=2))
            number = str(random.randint(1, 9999999)).zfill(7)
            return f"{year}{letters}{number}"
        else:
            # Default pattern
            return f"ACC{datetime.datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
    
    def create_text_image(self, width, height, metadata, predetermined_items=None, series_number=None, instance_number=None):
        """Create a text-based image with study information and geometric shapes"""
        # Create white background
        image = Image.new('L', (width, height), color=255)
        draw = ImageDraw.Draw(image)
        
        # Try to use a monospace font, fallback to default if not available
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 20)
            small_font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
            large_font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 36)
        except:
            font = ImageFont.load_default()
            small_font = font
            large_font = font
        
        # Draw border
        draw.rectangle([0, 0, width-1, height-1], outline=0, width=2)
        
        # Add title content
        y_offset = 20
        
        # Title (with automatic wrapping)
        title = "DICOM TEST IMAGE - NOT FOR CLINICAL USE"
        y_offset = self._draw_wrapped_centered_text(draw, title, y_offset, width, font)
        
        y_offset += 30
        
        # Disclaimer text (with automatic wrapping)
        disclaimer1 = "Metadata shown below correct at time of generation"
        y_offset = self._draw_wrapped_centered_text(draw, disclaimer1, y_offset, width, small_font)
        
        y_offset += 5
        disclaimer2 = "PACS and integrations may change the dicom tags to contain different data than displayed here"
        y_offset = self._draw_wrapped_centered_text(draw, disclaimer2, y_offset, width, small_font)
        
        y_offset += 20
        draw.line([(20, y_offset), (width-20, y_offset)], fill=0, width=1)
        
        # Add metadata information
        y_offset += 30
        info_lines = [
            f"(0010,0010) Patient Name: {metadata.get('PatientName', 'N/A')}",
            f"(0010,0020) Patient ID: {metadata.get('PatientID', 'N/A')}",
            f"(0008,0050) Accession: {metadata.get('AccessionNumber', 'N/A')}",
            f"(0020,000D) Study UID: {metadata.get('StudyInstanceUID', 'N/A')}",
            f"(0020,000E) Series UID: {metadata.get('SeriesInstanceUID', 'N/A')}",
            f"(0008,0018) SOP UID: {metadata.get('SOPInstanceUID', 'N/A')}",
            f"(0008,0020) Study Date: {metadata.get('StudyDate', 'N/A')}",
            f"(0008,0030) Study Time: {metadata.get('StudyTime', 'N/A')}",
            f"(0008,0060) Modality: {metadata.get('Modality', 'N/A')}",
            f"(0008,1030) Study Description: {metadata.get('StudyDescription', 'N/A')}",
            f"(0008,103E) Series Description: {metadata.get('SeriesDescription', 'N/A')}",
        ]
        
        for line in info_lines:
            y_offset = self._draw_wrapped_text(draw, line, 30, y_offset, width - 60, small_font)
            y_offset += 5  # Small gap between lines
        
        # Use predetermined items or generate random ones
        if predetermined_items:
            all_items = predetermined_items
        else:
            # Generate random shapes from available options (fallback)
            available_shapes = ['triangle', 'star', 'circle', 'moon', 'square', 'pentagon', 'octagon']
            available_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            available_numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            
            # Select exactly 6 random items total (limit as requested)
            all_available = available_shapes + available_letters + available_numbers
            all_items = random.sample(all_available, 6)
            random.shuffle(all_items)
        
        # Available shapes for drawing logic
        available_shapes = ['triangle', 'star', 'circle', 'moon', 'square', 'pentagon', 'octagon']
        
        # Store items for description update (will be in display order)
        shape_items = []
        
        # Add extra spacing after metadata before symbols  
        y_offset += 40
        
        # Add separator line before symbols
        draw.line([(20, y_offset), (width-20, y_offset)], fill=0, width=1)
        y_offset += 30
        
        # Add "Series X Image Y" text if provided
        if series_number and instance_number:
            series_image_text = f"Series {series_number} Image {instance_number}"
            y_offset = self._draw_wrapped_centered_text(draw, series_image_text, y_offset, width, font)
            y_offset += 20  # Extra spacing after series/image text
        
        # Draw geometric shapes, letters, and numbers below the text
        item_size = 50
        items_per_row = 6
        
        # Calculate positioning (all 6 items will fit in one row)
        total_width = 6 * (item_size + 15) - 15  # 6 items with spacing
        x_start = (width - total_width) // 2  # Center horizontally
        y_start = y_offset
        
        for i, item in enumerate(all_items):
            row = i // items_per_row
            col = i % items_per_row
            x = x_start + col * (item_size + 15)
            y = y_start + row * (item_size + 10)
            
            # Add to shape_items in display order (left to right, top to bottom)
            shape_items.append(item)
                
            if item in available_shapes:
                self._draw_shape(draw, item, x, y, item_size)
            else:
                # Draw letter or number
                text_bbox = draw.textbbox((0, 0), item, font=large_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = x + (item_size - text_width) // 2
                text_y = y + (item_size - text_height) // 2
                draw.text((text_x, text_y), item, fill=0, font=large_font)
                
                # Add a border around letters/numbers
                draw.rectangle([x, y, x+item_size, y+item_size], outline=0, width=1)
        
        # Update metadata with shape information
        shapes_text = ", ".join(shape_items)
        metadata['shapes'] = shapes_text
        
        # Add footer text at the bottom
        footer_y = height - 30  # Position footer near bottom
        footer_text = "DICOM Fabricator - flatmapit.com"
        
        # Center the footer text
        text_bbox = draw.textbbox((0, 0), footer_text, font=small_font)
        text_width = text_bbox[2] - text_bbox[0]
        footer_x = (width - text_width) // 2
        
        draw.text((footer_x, footer_y), footer_text, fill=128, font=small_font)  # Use grey color (128)
        
        # Convert to numpy array
        return np.array(image), shape_items
    
    def _draw_wrapped_text(self, draw, text, x, y, max_width, font):
        """Draw text with word wrapping and return the new y position"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Single word too long, truncate it
                    while len(word) > 0:
                        text_bbox = draw.textbbox((0, 0), word, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        if text_width <= max_width:
                            break
                        word = word[:-1]
                    current_line = word + "..."
        
        if current_line:
            lines.append(current_line)
        
        # Draw all lines
        for line in lines:
            draw.text((x, y), line, fill=0, font=font)
            text_bbox = draw.textbbox((0, 0), line, font=font)
            line_height = text_bbox[3] - text_bbox[1]
            y += line_height + 2  # Small gap between wrapped lines
        
        return y
    
    def _draw_wrapped_centered_text(self, draw, text, y, width, font):
        """Draw wrapped text centered horizontally and return new y position"""
        words = text.split(' ')
        lines = []
        current_line = ""
        max_width = width - 40  # Leave margins
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Single word too long, truncate it
                    while len(word) > 0:
                        text_bbox = draw.textbbox((0, 0), word, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        if text_width <= max_width:
                            break
                        word = word[:-1]
                    current_line = word + "..."
        
        if current_line:
            lines.append(current_line)
        
        # Draw all lines centered
        for line in lines:
            text_bbox = draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            line_height = text_bbox[3] - text_bbox[1]
            x = (width - text_width) // 2
            draw.text((x, y), line, fill=0, font=font)
            y += line_height + 2
        
        return y
    
    def _draw_shape(self, draw, shape, x, y, size):
        """Draw a specific geometric shape"""
        center_x = x + size // 2
        center_y = y + size // 2
        radius = min(size // 3, 25)
        
        if shape == 'circle':
            draw.ellipse([center_x - radius, center_y - radius, 
                         center_x + radius, center_y + radius], outline=0, width=2)
        
        elif shape == 'square':
            draw.rectangle([center_x - radius, center_y - radius,
                           center_x + radius, center_y + radius], outline=0, width=2)
        
        elif shape == 'triangle':
            points = [
                (center_x, center_y - radius),
                (center_x - radius, center_y + radius),
                (center_x + radius, center_y + radius)
            ]
            draw.polygon(points, outline=0, width=2)
        
        elif shape == 'star':
            import math
            points = []
            for i in range(10):
                angle = i * math.pi / 5
                if i % 2 == 0:
                    r = radius
                else:
                    r = radius // 2
                px = center_x + r * math.cos(angle - math.pi/2)
                py = center_y + r * math.sin(angle - math.pi/2)
                points.append((px, py))
            draw.polygon(points, outline=0, width=2)
        
        elif shape == 'pentagon':
            import math
            points = []
            for i in range(5):
                angle = i * 2 * math.pi / 5 - math.pi/2
                px = center_x + radius * math.cos(angle)
                py = center_y + radius * math.sin(angle)
                points.append((px, py))
            draw.polygon(points, outline=0, width=2)
        
        elif shape == 'octagon':
            import math
            points = []
            for i in range(8):
                angle = i * 2 * math.pi / 8 - math.pi/2
                px = center_x + radius * math.cos(angle)
                py = center_y + radius * math.sin(angle)
                points.append((px, py))
            draw.polygon(points, outline=0, width=2)
        
        elif shape == 'moon':
            # Draw moon as a circle with a bite taken out
            draw.ellipse([center_x - radius, center_y - radius,
                         center_x + radius, center_y + radius], outline=0, width=2)
            # Fill part of it to create moon shape
            draw.ellipse([center_x - radius//2, center_y - radius,
                         center_x + radius, center_y + radius], fill=255, outline=0, width=1)
    
    def create_dx_dicom_study(self, patient_name=None, patient_id=None, accession=None,
                             study_desc=None, study_date=None, series_config=None, output_dir="./data/dicom_output"):
        """Create a multi-series DICOM study with folder structure"""
        
        if not series_config:
            series_config = [{'images': 1, 'procedure': 'PA-VIEW'}]
        
        patient_record = None
        
        # Try to use existing patient or generate new one
        if patient_id:
            # Look for existing patient
            patient_record = self.patient_registry.get_patient(patient_id)
            if not patient_record and not patient_name:
                # Patient ID provided but doesn't exist and no name given
                print(f"Warning: Patient ID {patient_id} not found. Generating new patient.")
        
        if not patient_record:
            # Generate new patient or use provided info
            patient_record = self.patient_registry.generate_patient(
                patient_name=patient_name,
                patient_id=patient_id
            )
        
        # Extract patient information
        patient_name = patient_record.patient_name
        patient_id = patient_record.patient_id
        
        # Update usage tracking
        self.patient_registry.update_patient_usage(patient_id)
        
        if not accession:
            accession = self.generate_accession()
        
        if not study_desc:
            study_desc = "Test Study"
        
        # Generate single study UID for all series
        study_uid = generate_uid()
        
        # Create study folder structure
        now = datetime.datetime.now()
        study_date = now.strftime('%Y%m%d')
        study_time = now.strftime('%H%M%S')
        study_folder = Path(output_dir) / f"{patient_id}_{study_date}_{study_time}"
        study_folder.mkdir(parents=True, exist_ok=True)
        
        result = {
            'study_uid': study_uid,
            'study_folder': str(study_folder),
            'patient_name': patient_name,
            'patient_id': patient_id,
            'accession': accession,
            'study_desc': study_desc,
            'series': []
        }
        
        # Generate each series
        for series_idx, series_info in enumerate(series_config, 1):
            series_uid = generate_uid()
            series_folder = study_folder / f"Series{series_idx:03d}_{series_info['procedure']}"
            series_folder.mkdir(exist_ok=True)
            
            # Generate consistent shapes/symbols for this entire series
            available_shapes = ['triangle', 'star', 'circle', 'moon', 'square', 'pentagon', 'octagon']
            available_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            available_numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            
            # Select exactly 6 random items total for this series
            all_available = available_shapes + available_letters + available_numbers
            series_shapes = random.sample(all_available, 6)
            random.shuffle(series_shapes)
            
            # Create the shapes description for this series
            shapes_text = ", ".join(series_shapes)
            series_description_with_shapes = f"Image: {shapes_text}"
            
            series_files = []
            
            # Generate images for this series (all using the same shapes)
            for image_idx in range(series_info['images']):
                image_result = self.create_dx_dicom(
                    patient_name=patient_name,
                    patient_id=patient_id,
                    accession=accession,  # Use study-level accession
                    study_desc=study_desc,
                    study_date=study_date,
                    study_uid=study_uid,
                    series_uid=series_uid,
                    series_number=series_idx,
                    instance_number=image_idx + 1,
                    procedure_code=series_info['procedure'],
                    modality=series_info.get('modality', 'DX'),
                    series_description=series_info.get('series_description'),
                    series_shapes=series_shapes,  # Pass consistent shapes
                    series_description_with_shapes=series_description_with_shapes,  # Pass consistent description
                    output_dir=str(series_folder)
                )
                
                series_files.append({
                    'filename': Path(image_result['filepath']).name,
                    'filepath': image_result['filepath'],
                    'instance_number': image_idx + 1
                })
            
            result['series'].append({
                'series_number': series_idx,
                'series_uid': series_uid,
                'procedure': series_info['procedure'],
                'modality': series_info.get('modality', 'DX'),
                'series_description': series_info.get('series_description', ''),
                'folder': str(series_folder),
                'files': series_files
            })
        
        return result
    
    def create_dx_dicom(self, patient_name=None, patient_id=None, accession=None, 
                       study_desc=None, study_date=None, study_uid=None, series_uid=None, series_number=1,
                       instance_number=1, procedure_code=None, modality="DX", series_description=None, series_shapes=None,
                       series_description_with_shapes=None, output_dir="./data/dicom_output", use_existing_patient=True):
        """Create a DX (Digital Radiography) DICOM file"""
        
        patient_record = None
        
        # Try to use existing patient or generate new one
        if patient_id:
            # Look for existing patient
            patient_record = self.patient_registry.get_patient(patient_id)
            if not patient_record and not patient_name:
                # Patient ID provided but doesn't exist and no name given
                print(f"Warning: Patient ID {patient_id} not found. Generating new patient.")
        
        if not patient_record:
            # Generate new patient or use provided info
            patient_record = self.patient_registry.generate_patient(
                patient_name=patient_name,
                patient_id=patient_id
            )
        
        # Extract patient information
        patient_name = patient_record.patient_name
        patient_id = patient_record.patient_id
        
        # Update usage tracking
        self.patient_registry.update_patient_usage(patient_id)
        
        if not accession:
            accession = self.generate_accession()
        
        if not study_desc:
            study_desc = "Chest PA View - TEST DATA"
        
        # Use provided series shapes or generate new ones (for backward compatibility)
        if series_shapes:
            all_items = series_shapes
            shapes_description = series_description_with_shapes
        else:
            # Generate shapes/letters/numbers BEFORE image creation (fallback for single image calls)
            available_shapes = ['triangle', 'star', 'circle', 'moon', 'square', 'pentagon', 'octagon']
            available_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            available_numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            
            # Select exactly 6 random items total (limit as requested)
            all_available = available_shapes + available_letters + available_numbers
            all_items = random.sample(all_available, 6)
            random.shuffle(all_items)
            
            # Create the shapes description
            shapes_text = ", ".join(all_items)
            shapes_description = f"Image: {shapes_text}"
        
        # Use provided series description or build default
        if series_description:
            # If series description is provided, use it with shapes appended
            series_desc = f"{series_description} - {shapes_description}"
        else:
            # Build comprehensive series description: Modality + Procedure Code + Image Content
            series_desc_parts = [modality]
            
            if procedure_code:
                series_desc_parts.append(procedure_code)
            
            series_desc_parts.append(shapes_description)
            
            # Final series description format: "DX PA-CHEST Image: circle, A, 5"
            series_desc = " ".join(series_desc_parts)
        
        # Generate UIDs if not provided
        if not study_uid:
            study_uid = generate_uid()
        if not series_uid:
            series_uid = generate_uid()
        sop_uid = generate_uid()
        
        # Create the file meta information
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = pydicom.uid.DigitalXRayImageStorageForPresentation
        file_meta.MediaStorageSOPInstanceUID = sop_uid
        file_meta.ImplementationClassUID = generate_uid()
        file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
        
        # Create the FileDataset
        ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)
        
        # Add required DICOM elements
        dt = datetime.datetime.now()
        
        # Patient Module
        ds.PatientName = patient_name
        ds.PatientID = patient_id
        ds.PatientBirthDate = patient_record.birth_date
        ds.PatientSex = patient_record.sex
        
        # Calculate age from birth date
        birth_year = int(patient_record.birth_date[:4])
        current_year = dt.year
        age = current_year - birth_year
        ds.PatientAge = f"{age}Y"
        
        # Study Module
        ds.StudyInstanceUID = study_uid
        # Use provided study_date or current date
        if study_date and len(study_date) >= 8:
            ds.StudyDate = study_date[:8]  # Ensure YYYYMMDD format
        else:
            ds.StudyDate = dt.strftime("%Y%m%d")
        ds.StudyTime = dt.strftime("%H%M%S.%f")[:-3]
        ds.StudyID = f"STU{random.randint(1000, 9999)}"
        ds.AccessionNumber = accession
        ds.StudyDescription = study_desc  # Clean study description without symbols
        ds.ReferringPhysicianName = "TEST^DOCTOR"
        
        # Series Module
        ds.SeriesInstanceUID = series_uid
        ds.SeriesNumber = series_number
        ds.SeriesDescription = series_desc  # Series description with symbols
        ds.Modality = modality
        
        # Equipment Module
        ds.Manufacturer = "DICOM Fabricator"
        ds.InstitutionName = "Test Hospital"
        ds.StationName = "TEST_STATION"
        ds.ManufacturerModelName = "Fabricator v1.0"
        ds.DeviceSerialNumber = "FAB12345"
        ds.SoftwareVersions = "1.0.0"
        
        # General Image Module
        ds.InstanceNumber = instance_number
        ds.ImageType = ["ORIGINAL", "PRIMARY"]
        ds.ContentDate = dt.strftime("%Y%m%d")
        ds.ContentTime = dt.strftime("%H%M%S.%f")[:-3]
        
        # Image Pixel Module
        image_width = 1024
        image_height = 768
        
        # Create metadata dict for image generation
        metadata = {
            'PatientName': patient_name,
            'PatientID': patient_id,
            'AccessionNumber': accession,
            'StudyInstanceUID': study_uid,
            'SeriesInstanceUID': series_uid,
            'SOPInstanceUID': sop_uid,
            'StudyDate': ds.StudyDate,
            'StudyTime': ds.StudyTime,
            'Modality': modality,
            'StudyDescription': study_desc,
            'SeriesDescription': series_desc
        }
        
        # Generate the image with predetermined shapes
        pixel_array, actual_shape_items = self.create_text_image(image_width, image_height, metadata, all_items, series_number, instance_number)
        
        # Set image pixel data
        ds.PixelData = pixel_array.tobytes()
        ds.Rows = image_height
        ds.Columns = image_width
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0  # unsigned
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        
        # DX specific attributes
        ds.PresentationIntentType = "FOR PRESENTATION"
        ds.BodyPartExamined = "CHEST"
        ds.ViewPosition = "PA"
        
        # SOP Common Module
        ds.SOPClassUID = pydicom.uid.DigitalXRayImageStorageForPresentation
        ds.SOPInstanceUID = sop_uid
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save the file with series and instance number
        filename = f"{modality}_{patient_id}_{accession}_S{series_number:03d}_I{instance_number:03d}_{dt.strftime('%Y%m%d_%H%M%S')}.dcm"
        filepath = output_path / filename
        
        ds.save_as(filepath, write_like_original=False)
        
        return {
            'filepath': str(filepath),
            'study_uid': study_uid,
            'series_uid': series_uid,
            'sop_uid': sop_uid,
            'accession': accession,
            'patient_name': patient_name,
            'patient_id': patient_id
        }


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic DICOM DX studies for testing')
    
    parser.add_argument('--patient-name', '-n', type=str, 
                       help='Patient name (format: LAST^FIRST)')
    parser.add_argument('--patient-id', '-p', type=str,
                       help='Patient ID (will look up existing patient if found)')
    parser.add_argument('--accession', '-a', type=str,
                       help='Accession number')
    parser.add_argument('--study-desc', '-d', type=str,
                       help='Study description')
    parser.add_argument('--output-dir', '-o', type=str, default='./data/dicom_output',
                       help='Output directory for DICOM files (default: ./data/dicom_output)')
    parser.add_argument('--count', '-c', type=int, default=1,
                       help='Number of studies to generate (default: 1)')
    parser.add_argument('--config', type=str, default='./config/patient_config.json',
                       help='Patient configuration file (default: ./config/patient_config.json)')
    parser.add_argument('--registry', type=str, default='./data/patient_registry.json',
                       help='Patient registry file (default: ./data/patient_registry.json)')
    parser.add_argument('--list-patients', action='store_true',
                       help='List existing patients and exit')
    parser.add_argument('--generate-patient', action='store_true',
                       help='Generate a new patient and exit')
    
    args = parser.parse_args()
    
    # Initialize patient registry
    registry = PatientRegistry(args.registry)
    if Path(args.config).exists():
        registry.load_config(args.config)
    
    # Handle special commands
    if args.list_patients:
        patients = registry.list_patients(limit=10)
        if patients:
            print("Recent patients:")
            for p in patients:
                print(f"  {p.patient_id}: {p.patient_name} (Studies: {p.study_count})")
        else:
            print("No patients found.")
        return
    
    if args.generate_patient:
        patient = registry.generate_patient(
            patient_name=args.patient_name,
            patient_id=args.patient_id
        )
        print(f"Generated patient: {patient.patient_id} - {patient.patient_name}")
        return
    
    fabricator = DICOMFabricator(registry)
    
    print("DICOM Fabricator - Generating DX studies...")
    print("-" * 50)
    
    for i in range(args.count):
        result = fabricator.create_dx_dicom(
            patient_name=args.patient_name,
            patient_id=args.patient_id,
            accession=args.accession,
            study_desc=args.study_desc,
            output_dir=args.output_dir
        )
        
        print(f"\nStudy {i+1} created:")
        print(f"  File: {result['filepath']}")
        print(f"  Patient: {result['patient_name']} (ID: {result['patient_id']})")
        print(f"  Accession: {result['accession']}")
        print(f"  Study UID: {result['study_uid']}")
    
    print("\n" + "-" * 50)
    print(f"✅ Generated {args.count} DICOM file(s) in {args.output_dir}")


if __name__ == "__main__":
    main()