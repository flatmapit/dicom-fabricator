#!/usr/bin/env python3
"""
Patient Configuration and ID Generation System
Copyright (c) 2025 Christopher Gentle <chris@flatmapit.com>
"""

import json
import string
import random
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PatientRecord:
    """Represents a generated patient record"""
    patient_id: str
    patient_name: str
    birth_date: str
    sex: str
    address: str
    phone: str
    created_date: str
    last_used: str
    study_count: int = 0


class PatientIDGenerator:
    """Generates patient IDs based on configurable schemes"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pattern = config.get('pattern', 'PID{6digits}')
        self.start_value = config.get('start_value', 1)
        self.increment = config.get('increment', 1)
        self.prefix = config.get('prefix', '')
        self.suffix = config.get('suffix', '')
        
    def generate(self, counter: int) -> str:
        """Generate a patient ID based on the configured pattern"""
        pattern = self.pattern
        
        # Replace pattern tokens
        if '{6letters}' in pattern:
            letters = ''.join(random.choices(string.ascii_uppercase, k=6))
            pattern = pattern.replace('{6letters}', letters)
            
        if '{6digits}' in pattern:
            digits = str(self.start_value + (counter * self.increment)).zfill(6)
            pattern = pattern.replace('{6digits}', digits)
            
        if '{7digits}' in pattern:
            digits = str(self.start_value + (counter * self.increment)).zfill(7)
            pattern = pattern.replace('{7digits}', digits)
            
        if '{8digits}' in pattern:
            digits = str(self.start_value + (counter * self.increment)).zfill(8)
            pattern = pattern.replace('{8digits}', digits)
            
        # Custom digit patterns like {5digits}, {10digits}
        digit_matches = re.findall(r'\{(\d+)digits\}', pattern)
        for match in digit_matches:
            width = int(match)
            digits = str(self.start_value + (counter * self.increment)).zfill(width)
            pattern = pattern.replace(f'{{{match}digits}}', digits)
            
        # Custom letter patterns like {4letters}, {8letters}
        letter_matches = re.findall(r'\{(\d+)letters\}', pattern)
        for match in letter_matches:
            width = int(match)
            letters = ''.join(random.choices(string.ascii_uppercase, k=width))
            pattern = pattern.replace(f'{{{match}letters}}', letters)
            
        # Random hex patterns
        hex_matches = re.findall(r'\{(\d+)hex\}', pattern)
        for match in hex_matches:
            width = int(match)
            hex_str = ''.join(random.choices('0123456789ABCDEF', k=width))
            pattern = pattern.replace(f'{{{match}hex}}', hex_str)
        
        return self.prefix + pattern + self.suffix


class PatientRegistry:
    """Manages patient records and generation"""
    
    def __init__(self, registry_path: str = "./data/patient_registry.json"):
        self.registry_path = Path(registry_path)
        self.patients: Dict[str, PatientRecord] = {}
        self.config = self._load_default_config()
        self.id_generator = PatientIDGenerator(self.config['id_generation'])
        self.load_registry()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default patient generation configuration"""
        return {
            "id_generation": {
                "pattern": "PID{6digits}",
                "start_value": 100000,
                "increment": 1,
                "prefix": "",
                "suffix": ""
            },
            "name_generation": {
                "use_realistic": False,
                "custom_names": [
                    {"first": "TEST", "last": "PATIENT"},
                    {"first": "DEMO", "last": "USER"},
                    {"first": "SAMPLE", "last": "PERSON"},
                    {"first": "FAKE", "last": "NAME"},
                    {"first": "SYNTHETIC", "last": "DATA"},
                    {"first": "CLINICAL", "last": "TESTCASE"},
                    {"first": "RADIOLOGY", "last": "PHANTOM"}
                ]
            },
            "demographics": {
                "birth_year_range": [1940, 2005],
                "sex_distribution": {"M": 0.45, "F": 0.45, "O": 0.1},
                "addresses": [
                    "123 Test Street, Sydney NSW 2000",
                    "456 Sample Road, Melbourne VIC 3000", 
                    "789 Fake Avenue, Brisbane QLD 4000",
                    "321 Mock Boulevard, Perth WA 6000",
                    "159 Demo Crescent, Adelaide SA 5000",
                    "742 Example Drive, Hobart TAS 7000",
                    "88 Synthetic Close, Darwin NT 0800",
                    "264 Clinical Way, Canberra ACT 2600"
                ],
                "phone_pattern": "04{2digits} {3digits} {3digits}"
            }
        }
        
    def load_config(self, config_path: str):
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.id_generator = PatientIDGenerator(self.config['id_generation'])
        
    def save_config(self, config_path: str):
        """Save current configuration to JSON file"""
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def load_registry(self):
        """Load existing patient registry"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
                for pid, record_dict in data.items():
                    self.patients[pid] = PatientRecord(**record_dict)
                    
    def save_registry(self):
        """Save patient registry to disk"""
        data = {}
        for pid, record in self.patients.items():
            data[pid] = {
                'patient_id': record.patient_id,
                'patient_name': record.patient_name,
                'birth_date': record.birth_date,
                'sex': record.sex,
                'address': record.address,
                'phone': record.phone,
                'created_date': record.created_date,
                'last_used': record.last_used,
                'study_count': record.study_count
            }
        
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def _generate_phone(self) -> str:
        """Generate phone number based on pattern"""
        pattern = self.config['demographics']['phone_pattern']
        
        # Replace digit patterns
        digit_matches = re.findall(r'\{(\d+)digits\}', pattern)
        for match in digit_matches:
            width = int(match)
            digits = ''.join(random.choices('0123456789', k=width))
            pattern = pattern.replace(f'{{{match}digits}}', digits)
            
        return pattern
        
    def _generate_birth_date(self) -> str:
        """Generate birth date in YYYYMMDD format"""
        year_range = self.config['demographics']['birth_year_range']
        year = random.randint(year_range[0], year_range[1])
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Safe day range
        return f"{year:04d}{month:02d}{day:02d}"
        
    def _select_sex(self) -> str:
        """Select sex based on distribution"""
        distribution = self.config['demographics']['sex_distribution']
        choices = list(distribution.keys())
        weights = list(distribution.values())
        return random.choices(choices, weights=weights)[0]
        
    def generate_patient(self, patient_name: Optional[str] = None, 
                        patient_id: Optional[str] = None) -> PatientRecord:
        """Generate a new patient record"""
        
        # Generate or use provided patient ID
        if not patient_id:
            counter = len(self.patients)
            patient_id = self.id_generator.generate(counter)
            
            # Ensure uniqueness
            while patient_id in self.patients:
                counter += 1
                patient_id = self.id_generator.generate(counter)
        
        # Generate or use provided patient name
        if not patient_name:
            names = self.config['name_generation']['custom_names']
            name_choice = random.choice(names)
            patient_name = f"{name_choice['last']}^{name_choice['first']}"
        
        # Generate other demographics
        birth_date = self._generate_birth_date()
        sex = self._select_sex()
        address = random.choice(self.config['demographics']['addresses'])
        phone = self._generate_phone()
        
        # Create record
        now = datetime.now().isoformat()
        record = PatientRecord(
            patient_id=patient_id,
            patient_name=patient_name,
            birth_date=birth_date,
            sex=sex,
            address=address,
            phone=phone,
            created_date=now,
            last_used=now,
            study_count=0
        )
        
        # Store and save
        self.patients[patient_id] = record
        self.save_registry()
        
        return record
        
    def get_patient(self, patient_id: str) -> Optional[PatientRecord]:
        """Get existing patient record"""
        return self.patients.get(patient_id)
        
    def update_patient_usage(self, patient_id: str):
        """Update last used timestamp and study count"""
        if patient_id in self.patients:
            self.patients[patient_id].last_used = datetime.now().isoformat()
            self.patients[patient_id].study_count += 1
            self.save_registry()
            
    def list_patients(self, limit: Optional[int] = None) -> List[PatientRecord]:
        """List all patients, optionally limited"""
        patients = list(self.patients.values())
        patients.sort(key=lambda p: p.last_used, reverse=True)
        
        if limit:
            patients = patients[:limit]
            
        return patients
        
    def search_patients(self, query: str) -> List[PatientRecord]:
        """Search patients by ID, name, or other fields"""
        query = query.lower()
        matches = []
        
        for record in self.patients.values():
            if (query in record.patient_id.lower() or 
                query in record.patient_name.lower() or
                query in record.address.lower()):
                matches.append(record)
                
        return matches
        
    def delete_patient(self, patient_id: str) -> bool:
        """Delete a patient record"""
        if patient_id in self.patients:
            del self.patients[patient_id]
            self.save_registry()
            return True
        return False
        
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        if not self.patients:
            return {"total_patients": 0}
            
        records = list(self.patients.values())
        total_studies = sum(r.study_count for r in records)
        
        return {
            "total_patients": len(self.patients),
            "total_studies_generated": total_studies,
            "most_recent_patient": max(records, key=lambda r: r.created_date).patient_id,
            "most_used_patient": max(records, key=lambda r: r.study_count).patient_id,
            "avg_studies_per_patient": total_studies / len(self.patients) if self.patients else 0
        }