# Glossary

This glossary explains technical terms used in DICOM Fabricator documentation.

## A

**AE Title (Application Entity Title)**
- A unique identifier for DICOM network connections
- Used to identify PACS servers and applications
- Example: "TESTPACS", "ORTHANC"

**Accession Number**
- A unique identifier for a medical imaging study
- Used to track studies across different systems
- Format varies by institution (e.g., "ACC20250824001")

## C

**C-ECHO**
- DICOM service that tests connectivity between systems
- Used to verify PACS server is reachable
- Also called "ping" for DICOM networks

**C-FIND**
- DICOM service for querying/ searching for studies
- Used to find studies on PACS servers
- Returns study metadata without transferring images

**C-MOVE**
- DICOM service for transferring studies between PACS servers
- Moves studies from one server to another
- Requires proper AE title configuration

**C-STORE**
- DICOM service for sending studies to PACS servers
- Used to upload DICOM files to a server
- Requires proper AE title configuration

## D

**DCMTK**
- DICOM Toolkit - open-source software for DICOM operations
- Provides command-line tools (findscu, storescu, movescu)
- Required for PACS communication

**DICOM (Digital Imaging and Communications in Medicine)**
- Standard for medical imaging data exchange
- Defines how medical images are stored and transmitted
- Used by all major medical imaging systems

**DICOM Study**
- A collection of related medical images
- Contains one or more series of images
- Has metadata like patient info, study description, etc.

## E

**Enterprise Authentication**
- Authentication using corporate systems (Active Directory, SAML)
- Allows integration with existing user management
- Supports group-based role assignment

## H

**HL7 ORM (Health Level 7 Order Entry Message)**
- Standard message format for medical orders
- Contains patient info, study details, and ordering physician
- Can be used to automatically generate DICOM studies

## I

**Image Server**
- Alternative term for PACS server
- Stores and manages medical images
- Provides DICOM services for query and retrieval

## L

**Local Authentication**
- Simple username/password authentication
- Users managed within DICOM Fabricator
- Good for small teams or testing

## M

**Metadata**
- Information about DICOM studies (patient name, study date, etc.)
- Stored as DICOM tags
- Used for searching and organizing studies

## O

**Orthanc**
- Open-source PACS server
- Used for testing and development
- Provides web interface and DICOM services

## P

**PACS (Picture Archiving and Communication System)**
- System for storing and managing medical images
- Provides DICOM services for query, store, and move
- Also called "image server" or "DICOM server"

**Patient ID**
- Unique identifier for a patient
- Used to group studies for the same patient
- Format varies by institution

**pydicom**
- Python library for working with DICOM files
- Used by DICOM Fabricator for file manipulation
- Handles reading, writing, and modifying DICOM data

## R

**Role-Based Access Control (RBAC)**
- Security model using roles instead of individual permissions
- Users are assigned roles (admin, test_write, etc.)
- Roles determine what features users can access

## S

**Series**
- A collection of related images within a study
- Example: all images from a CT scan
- Each series has its own metadata

**Synthetic Data**
- Artificially generated data for testing
- No real patient information
- Safe for development and testing

## T

**Transfer Syntax**
- Method for encoding DICOM data for transmission
- Determines compression and encoding format
- Must be supported by both sender and receiver

## U

**UID (Unique Identifier)**
- Globally unique identifier for DICOM objects
- Used to identify studies, series, and instances
- Format: numbers separated by dots (e.g., "1.2.3.4.5")

## V

**VR (Value Representation)**
- Data type for DICOM tags
- Examples: "AS" (Age String), "PN" (Person Name), "DA" (Date)
- Determines how data is stored and interpreted
