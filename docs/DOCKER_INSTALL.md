# Docker Desktop Installation Guide for Mac

## Option 1: Install via Homebrew (Recommended)

Run this command in your terminal:
```bash
brew install --cask docker
```

If prompted for your password, enter your Mac login password.

## Option 2: Download from Docker Website

1. Visit: https://www.docker.com/products/docker-desktop/
2. Click "Download for Mac" (choose Apple Silicon for M1/M2/M3 Macs)
3. Open the downloaded Docker.dmg file
4. Drag Docker.app to Applications folder
5. Open Docker from Applications

## After Installation

1. **Start Docker Desktop**
   - Open Docker from Applications folder
   - You'll see the Docker icon in your menu bar when it's running

2. **Verify Installation**
   ```bash
   docker --version
   docker compose version
   ```

3. **Start the Orthanc PACS**
   ```bash
   cd /Users/christophergentle/2025-development/hl7-tester
   docker compose up -d
   ```

4. **Access Orthanc Web Interface**
   - URL: http://localhost:8042
   - Username: test
   - Password: test123

## Troubleshooting

### If Docker commands not found after installation:
1. Restart your terminal
2. Make sure Docker Desktop is running (check menu bar)

### If ports are already in use:
Edit `docker-compose.yml` and change the port numbers

## Next Steps
Once Docker is installed and running, return to this project directory and run:
```bash
docker compose up -d
```

This will start the Orthanc PACS server for testing.