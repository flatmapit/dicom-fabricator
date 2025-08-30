#!/usr/bin/env python3
"""
DICOM Viewer - Main entry point
Wrapper script that calls the main implementation in src/
"""

import sys
import os
from pathlib import Path

# Add src directory to path so we can import the modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main function
from view_dicom import main

if __name__ == "__main__":
    main()