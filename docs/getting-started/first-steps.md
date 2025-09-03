# First Steps

Welcome to DICOM Fabricator! This guide will help you create your first DICOM study and explore the basic features.

## Prerequisites

- DICOM Fabricator is installed and running (see [Installation Guide](installation.md))
- Web interface is accessible at `http://localhost:5001`

## Step 1: Access the Web Interface

1. Open your web browser
2. Navigate to `http://localhost:5001`
3. You should see the DICOM Fabricator dashboard

![Dashboard](images/dashboard.png)

## Step 2: Create Your First Patient

1. Click on **"Patient Management"** in the dashboard
2. Click **"Add New Patient"**
3. Fill in the patient information:
   - **Patient Name**: Enter a name (e.g., "DOE^JANE")
   - **Patient ID**: Leave blank for auto-generation
   - **Birth Date**: Select a date
   - **Sex**: Choose Male, Female, or Other
4. Click **"Save Patient"**

## Step 3: Generate Your First DICOM Study

1. Go back to the dashboard
2. Click **"DICOM Generator"**
3. In the **"Study Information"** section:
   - **Study Description**: Enter "Chest X-Ray"
   - **Accession Number**: Leave blank for auto-generation
   - **Patient**: Select the patient you just created
4. Click **"Generate DICOM"**

## Step 4: View Your Generated Study

1. After generation, you'll see the study in the list
2. Click **"View"** to see the DICOM metadata
3. Click **"Download"** to save the DICOM file

## Step 5: Explore the DICOM Viewer

1. Click **"DICOM Viewer"** in the dashboard
2. You'll see your generated study listed
3. Click on the study to view detailed metadata
4. Explore the different DICOM tags and values

## Step 6: Test PACS Integration (Optional)

If you have test PACS servers running:

1. Go to **"PACS Management"**
2. You should see your test PACS servers listed
3. Click **"Test Connection"** to verify connectivity
4. Go to **"Query PACS"** to search for studies
5. Try sending your generated study to a PACS server

## What You've Learned

- ✅ Created a synthetic patient record
- ✅ Generated a DICOM study with realistic metadata
- ✅ Viewed DICOM metadata and tags
- ✅ Explored the web interface
- ✅ Tested PACS connectivity (if available)

## Next Steps

- [Quick Tour](quick-tour.md) - Explore all features
- [Web Interface Guide](../user-guides/web-interface.md) - Detailed web interface usage
- [Command Line Guide](../user-guides/command-line.md) - Command-line tools
- [Authentication Setup](../configuration/authentication.md) - Configure user access

## Common Questions

**Q: Why is the patient data fictional?**
A: DICOM Fabricator generates synthetic data for testing purposes. This ensures no real patient information is used.

**Q: Can I use real patient data?**
A: No. DICOM Fabricator is designed for testing and development only. Never use real patient data.

**Q: What if I get an error?**
A: Check the [Common Issues](../troubleshooting/common-issues.md) guide or create a GitHub issue.

**Q: How do I delete a patient or study?**
A: Use the delete buttons in the respective management interfaces.

## Related Documents

- [Installation Guide](installation.md) - Setup instructions
- [Quick Tour](quick-tour.md) - Feature overview
- [Web Interface Guide](../user-guides/web-interface.md) - Detailed usage
- [Troubleshooting](../troubleshooting/common-issues.md) - Common problems
