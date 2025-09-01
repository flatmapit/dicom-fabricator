# Third-Party Licenses

This project uses the following third-party libraries and frameworks. This file acknowledges their licenses and attribution requirements.

## Frontend Dependencies (CDN)

### Bootstrap 5.1.3
- **License**: MIT License
- **Copyright**: Copyright (c) 2011-2025 The Bootstrap Authors
- **Source**: https://getbootstrap.com/
- **License URL**: https://github.com/twbs/bootstrap/blob/main/LICENSE
- **Usage**: CSS framework and JavaScript components

### Font Awesome 6.0.0
- **License**: Multiple licenses
  - Icons: CC BY 4.0 License
  - Fonts: SIL OFL 1.1 License  
  - Code: MIT License
- **Copyright**: Fonticons, Inc.
- **Source**: https://fontawesome.com/
- **License URL**: https://github.com/FortAwesome/Font-Awesome/blob/master/LICENSE.txt
- **Usage**: Icon fonts and CSS
- **Note**: Attribution embedded in downloaded files

### tosijs
- **License**: BSD-3-Clause License
- **Source**: https://github.com/sumn2u/tosijs
- **Usage**: Table sorting and management (currently replaced with custom implementation)



## Python Dependencies

### pydicom >=2.4.0
- **License**: MIT License
- **Copyright**: Copyright (c) 2008-2020 Darcy Mason and pydicom contributors
- **Source**: https://github.com/pydicom/pydicom
- **License URL**: https://github.com/pydicom/pydicom/blob/main/LICENSE
- **Usage**: DICOM file reading and writing
- **Note**: Includes portions from GDCM library (BSD-style license)

### Pillow >=10.0.0
- **License**: MIT-CMU License (PIL Software License)
- **Copyright**: 
  - Copyright © 1997-2011 by Secret Labs AB
  - Copyright © 1995-2011 by Fredrik Lundh and contributors
  - Copyright © 2010 by Jeffrey A. Clark and contributors
- **Source**: https://github.com/python-pillow/Pillow
- **License URL**: https://github.com/python-pillow/Pillow/blob/main/LICENSE
- **Usage**: Image processing and manipulation

### Flask >=3.0.0
- **License**: BSD 3-Clause License
- **Copyright**: Copyright 2010 Pallets
- **Source**: https://github.com/pallets/flask
- **License URL**: https://github.com/pallets/flask/blob/main/LICENSE.txt
- **Usage**: Web application framework

### Flask-CORS >=4.0.0
- **License**: MIT License
- **Copyright**: Copyright (c) 2013 Cory Dolphin
- **Source**: https://github.com/corydolphin/flask-cors
- **Usage**: Cross-Origin Resource Sharing support for Flask

### NumPy >=1.24.0
- **License**: BSD 3-Clause License
- **Copyright**: Copyright (c) 2005-2023, NumPy Developers
- **Source**: https://github.com/numpy/numpy
- **Usage**: Numerical computing support

### matplotlib >=3.5.0
- **License**: PSF-based License (similar to BSD)
- **Copyright**: Copyright (c) 2002-2023 Matplotlib Development Team
- **Source**: https://github.com/matplotlib/matplotlib
- **Usage**: Plotting and visualization (optional, for CLI viewer)

### pydicom-seg >=0.4.0
- **License**: MIT License
- **Source**: https://github.com/razorx89/pydicom-seg
- **Usage**: DICOM segmentation support

### pynetdicom >=2.0.0
- **License**: MIT License
- **Source**: https://github.com/pydicom/pynetdicom
- **Usage**: DICOM networking and PACS communication

## License Compatibility

All dependencies use permissive licenses (MIT, BSD, CC BY) that are compatible with the MIT License of this project. The primary requirements are:

1. **Attribution**: Copyright notices must be preserved in redistributions
2. **No Warranty**: All software is provided "as is" without warranty
3. **No Endorsement**: Original authors' names cannot be used for endorsement without permission

## Compliance Notes

- Font Awesome icons are used to represent generic functions, not specific brands
- Bootstrap and other MIT-licensed components include embedded copyright notices
- This project complies with all attribution requirements of the included dependencies
- All dependencies are used within the terms of their respective licenses