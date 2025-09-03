# Quick Tour

Take a quick tour of DICOM Fabricator's main features and capabilities.

## Related Documents
- [First Steps](first-steps.md) - Step-by-step getting started
- [Installation Guide](installation.md) - Setup instructions
- [Web Interface Guide](../user-guides/web-interface.md) - Detailed interface guide
- [Glossary](../glossary.md) - Technical terms explained

## What is DICOM Fabricator?

DICOM Fabricator is a tool that helps you:
- **Generate synthetic DICOM studies** for testing
- **Manage patient records** with realistic data
- **Connect to image servers** (PACS) for testing
- **Transfer studies** between different servers
- **Test DICOM workflows** safely

## Key Features Overview

### 🏥 Patient Management
Create and manage synthetic patient records with realistic demographics.

**What you can do:**
- Add new patients with custom information
- Search and filter patient records
- Export patient data
- Generate realistic patient demographics

### 📋 DICOM Generation
Generate synthetic DICOM studies from HL7 messages or manual input.

**What you can do:**
- Create studies from HL7 ORM messages
- Generate studies manually with custom parameters
- Preview study metadata before saving
- Create multiple studies for the same patient

### 🖥️ DICOM Viewer
View and manage generated DICOM files with detailed metadata display.

**What you can do:**
- Browse through generated studies
- View detailed DICOM metadata
- Download DICOM files
- Send studies to image servers

### 🏥 PACS Integration
Connect to and manage image servers (PACS) for testing.

**What you can do:**
- Add and configure PACS servers
- Test server connectivity
- Query studies on servers
- Transfer studies between servers

### 🔐 User Management
Control access with role-based permissions.

**What you can do:**
- Create user accounts
- Assign roles and permissions
- Separate test and production access
- Integrate with enterprise systems

## User Roles Explained

| Role | What They Can Do | Best For |
|------|------------------|----------|
| **admin** | Everything - manage users, configure servers, access all features | System administrators |
| **test_write** | Work with test image servers - query, send, and move studies | Test environment users |
| **test_read** | View test image servers - can only look, not make changes | Test environment viewers |
| **prod_write** | Work with production image servers - query, send, and move studies | Production users |
| **prod_read** | View production image servers - can only look, not make changes | Production viewers |

## Typical Workflow

### 1. Setup
- Install DICOM Fabricator
- Configure authentication (optional)
- Set up test PACS servers (optional)

### 2. Create Test Data
- Add patient records
- Generate DICOM studies
- Review generated data

### 3. Test Integration
- Configure PACS servers
- Send studies to servers
- Query studies from servers
- Transfer studies between servers

### 4. Production Testing
- Configure production PACS
- Test with production users
- Validate workflows

## Environment Separation

DICOM Fabricator separates test and production environments:

### Test Environment
- Safe for testing and development
- Contains synthetic data only
- Accessible to test users
- No risk to real patient data

### Production Environment
- Real clinical data
- Restricted access
- Production users only
- Full security controls

## Security Features

### Data Protection
- **Synthetic Data Only**: All generated data is fictional
- **Local Storage**: No data transmitted to external services
- **Role-Based Access**: Granular permission control
- **Environment Separation**: Test and production isolation

### Enterprise Integration
- **Active Directory**: Connect to corporate user systems
- **SAML Support**: Single sign-on integration
- **Group Mapping**: Map corporate groups to roles
- **Audit Logging**: Track user activities

## Getting Started

### Quick Start (5 minutes)
1. **Install**: Follow the [Installation Guide](installation.md)
2. **Start**: Run `python app.py`
3. **Access**: Open `http://localhost:5001`
4. **Create**: Add a patient and generate a study
5. **Explore**: Use the DICOM viewer to see the results

### Next Steps
- [First Steps](first-steps.md) - Detailed getting started guide
- [Web Interface Guide](../user-guides/web-interface.md) - Learn the interface
- [Command Line Guide](../user-guides/command-line.md) - Command-line tools
- [PACS Setup](../configuration/pacs-setup.md) - Configure servers

## Common Use Cases

### Development Testing
- Generate test data for applications
- Test DICOM workflows
- Validate integration points
- Simulate real-world scenarios

### Training and Education
- Learn DICOM concepts
- Practice PACS operations
- Understand DICOM workflows
- Train new staff

### Quality Assurance
- Test system integrations
- Validate data formats
- Check error handling
- Performance testing

### Research and Development
- Prototype new features
- Test experimental workflows
- Validate new standards
- Research DICOM capabilities

## Tips for Success

### Start Simple
- Begin with basic patient and study generation
- Use the web interface first
- Explore features gradually
- Don't try to do everything at once

### Use Test Data
- Always use synthetic data
- Never use real patient information
- Test thoroughly before production
- Validate all workflows

### Plan Your Setup
- Decide on authentication early
- Plan PACS configuration
- Consider user roles and permissions
- Document your configuration

### Stay Organized
- Use consistent naming conventions
- Keep configurations backed up
- Document your workflows
- Regular cleanup of test data

## Support and Resources

### Documentation
- [Installation Guide](installation.md) - Setup instructions
- [User Guides](../user-guides/) - Detailed usage guides
- [Configuration](../configuration/) - Setup guides
- [Troubleshooting](../troubleshooting/) - Problem solving

### Getting Help
- Check the [Common Issues](../troubleshooting/common-issues.md) guide
- Review [GitHub Issues](https://github.com/flatmapit/dicom-fabricator/issues)
- Create a new issue with detailed information
- Join discussions in [GitHub Discussions](https://github.com/flatmapit/dicom-fabricator/discussions)

## Next Steps

- [First Steps](first-steps.md) - Start using DICOM Fabricator
- [Installation Guide](installation.md) - Set up the system
- [Web Interface Guide](../user-guides/web-interface.md) - Learn the interface
- [PACS Setup](../configuration/pacs-setup.md) - Configure servers
