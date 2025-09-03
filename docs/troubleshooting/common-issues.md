# Common Issues and Solutions

This guide helps you resolve common problems with DICOM Fabricator.

## Related Documents
- [Installation Guide](../getting-started/installation.md) - Setup instructions
- [Authentication Setup](../configuration/authentication.md) - User access
- [PACS Setup](../configuration/pacs-setup.md) - Server configuration
- [C-MOVE Troubleshooting](cmove-troubleshooting.md) - Transfer issues

## Installation Issues

### "Command not found: findscu"
**Problem:** DCMTK tools are not installed or not in your system PATH.

**Solution:**
```bash
# macOS
brew install dcmtk

# Ubuntu/Debian
sudo apt-get install dcmtk

# Windows
# Download from https://dcmtk.org/en/dcmtk/dcmtk-downloads/
```

### "Module not found" errors
**Problem:** Python dependencies are not installed or virtual environment is not activated.

**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r config/requirements.txt
```

### "Port already in use" errors
**Problem:** Another application is using port 5001.

**Solution:**
```bash
# Find what's using the port
lsof -i :5001

# Kill the process (replace PID with actual process ID)
kill PID

# Or change the port in app.py
```

## Application Issues

### "Page not loading" errors
**Problem:** Web interface is not accessible.

**Solutions:**
1. **Check if application is running:**
   ```bash
   ps aux | grep python
   ```

2. **Verify the correct URL:**
   - Use `http://localhost:5001` (not https)
   - Check for typos in the URL

3. **Check browser console:**
   - Press F12 to open developer tools
   - Look for error messages in the Console tab

### "Authentication failed" errors
**Problem:** Cannot log in to the application.

**Solutions:**
1. **Check username and password:**
   - Verify credentials are correct
   - Check for typos or case sensitivity

2. **Verify authentication is enabled:**
   - Check `config/auth_config.json`
   - Ensure `auth_enabled` is set correctly

3. **Reset admin password:**
   ```bash
   python3 -c "
   from src.auth import AuthManager
   auth = AuthManager()
   auth.create_user('admin', 'newpassword', 'admin@example.com', 'admin')
   print('Admin password reset')
   "
   ```

### "Permission denied" errors
**Problem:** User doesn't have permission for an action.

**Solutions:**
1. **Check user role:**
   - Verify user has appropriate role
   - Check role permissions in user management

2. **Verify environment access:**
   - Test users can only access test PACS
   - Production users can only access production PACS

3. **Contact administrator:**
   - Request role changes
   - Verify group mappings (for enterprise auth)

## PACS Connection Issues

### "Connection failed" errors
**Problem:** Cannot connect to PACS server.

**Solutions:**
1. **Check server information:**
   - Verify host address and port
   - Test network connectivity: `ping server-address`
   - Check if server is running

2. **Verify DICOM settings:**
   - Check AE Title (AEC) is correct
   - Ensure port number is right (usually 104)
   - Verify firewall allows DICOM traffic

3. **Test with DCMTK tools:**
   ```bash
   # Test connectivity
   echoscu -aec DICOMFAB server-address 104
   ```

### "AE Title not recognized" errors
**Problem:** PACS server doesn't recognize your application's connection name.

**Solutions:**
1. **Check AE Title configuration:**
   - Verify your application's AE Titles
   - Check server's expected AE Titles
   - Ensure both sides use the same names

2. **Contact PACS administrator:**
   - Request proper AE Title configuration
   - Verify your application is authorized

### "C-MOVE failed" errors
**Problem:** Cannot transfer studies between PACS servers.

**Solutions:**
1. **Check C-MOVE routing:**
   - Verify Move AE titles are configured
   - Check routing table in PACS management
   - Ensure both PACS support C-MOVE

2. **Test connectivity:**
   - Verify both PACS servers are reachable
   - Check network connectivity between servers
   - Test with DCMTK tools

3. **Check study existence:**
   - Verify study exists on source PACS
   - Check study is accessible
   - Ensure proper permissions

## Data Issues

### "Patient not found" warnings
**Problem:** System cannot find patient record.

**Solutions:**
1. **Check patient registry:**
   ```bash
   python3 patient_manager.py list
   ```

2. **Create missing patient:**
   - System will auto-generate if ID doesn't exist
   - Or create patient manually in web interface

3. **Verify patient ID format:**
   - Check ID matches expected pattern
   - Review patient configuration

### "Invalid VR AS" warnings
**Problem:** pydicom warning about age formatting.

**Solutions:**
1. **This is usually safe to ignore:**
   - Ages are calculated correctly from birth dates
   - Warning doesn't affect functionality

2. **If problematic:**
   - Check patient birth date format
   - Verify age calculation logic

### "Permission errors" when saving files
**Problem:** Cannot write to output directory.

**Solutions:**
1. **Check directory permissions:**
   ```bash
   ls -la dicom_output/
   chmod 755 dicom_output/
   ```

2. **Verify write access:**
   - Ensure user has write permissions
   - Check disk space availability
   - Create directory if missing

## Performance Issues

### Slow application startup
**Problem:** Application takes a long time to start.

**Solutions:**
1. **Check system resources:**
   - Monitor CPU and memory usage
   - Close unnecessary applications
   - Restart system if needed

2. **Optimize configuration:**
   - Reduce number of PACS servers
   - Simplify patient configuration
   - Check for large data files

### Slow PACS operations
**Problem:** PACS queries and transfers are slow.

**Solutions:**
1. **Check network connectivity:**
   - Test network speed
   - Check for network congestion
   - Verify server performance

2. **Optimize queries:**
   - Use specific date ranges
   - Limit result counts
   - Use appropriate search criteria

## Browser Issues

### "Mixed content" errors
**Problem:** Browser blocks HTTP content on HTTPS pages.

**Solutions:**
1. **Use HTTP consistently:**
   - Access application via `http://localhost:5001`
   - Don't use HTTPS for local development

2. **Configure browser:**
   - Allow mixed content for localhost
   - Disable security warnings for development

### JavaScript errors
**Problem:** Web interface doesn't work properly.

**Solutions:**
1. **Check browser console:**
   - Press F12 to open developer tools
   - Look for error messages
   - Check for JavaScript errors

2. **Try different browser:**
   - Test with Chrome, Firefox, or Safari
   - Clear browser cache
   - Disable browser extensions

## Getting Help

### Before Asking for Help
1. **Check this guide** for your specific error
2. **Review application logs** for detailed error messages
3. **Test with minimal configuration** to isolate the issue
4. **Document the exact steps** that cause the problem

### When Creating an Issue
Include the following information:
- **Error message** (exact text)
- **Steps to reproduce** the problem
- **System information** (OS, Python version, browser)
- **Configuration files** (sanitized of sensitive data)
- **Application logs** (relevant error messages)

### Useful Commands for Debugging
```bash
# Check application status
ps aux | grep python

# Check port usage
lsof -i :5001

# Check DCMTK tools
findscu --version

# Check Python environment
python --version
pip list

# Check file permissions
ls -la config/
ls -la data/
```

## Next Steps

- [C-MOVE Troubleshooting](cmove-troubleshooting.md) - Transfer-specific issues
- [PACS Setup](../configuration/pacs-setup.md) - Server configuration
- [Authentication Setup](../configuration/authentication.md) - User access
