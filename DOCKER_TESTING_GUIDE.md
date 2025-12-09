# Docker Testing Guide

Quick guide for testing the Docker deployment locally on your Linux system.

---

## Prerequisites

Install Docker if not already installed:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, to avoid sudo)
sudo usermod -aG docker $USER
# Log out and back in for group change to take effect
```

Verify Docker installation:
```bash
docker --version
```

---

## Build and Run

### Step 1: Navigate to Project Directory

```bash
cd /path/to/LabelReadingApp
```

### Step 2: Build the Docker Image

```bash
docker build -t label-verification-app .
```

**What happens during build:**
- Base image: Python 3.11-slim (lightweight)
- Installs: `tesseract-ocr` via apt-get (this is why Docker works!)
- Installs: All Python dependencies from requirements.txt
- Copies: Application code (backend/ and frontend/)

**Expected output:**
```
[+] Building 45.2s (12/12) FINISHED
 => [1/7] FROM docker.io/library/python:3.11-slim
 => [2/7] WORKDIR /app
 => [3/7] RUN apt-get update && apt-get install -y tesseract-ocr
 => [4/7] COPY requirements.txt .
 => [5/7] RUN pip install --no-cache-dir -r requirements.txt
 => [6/7] COPY backend/ ./backend/
 => [7/7] COPY frontend/ ./frontend/
 => exporting to image
Successfully tagged label-verification-app:latest
```

### Step 3: Run the Container

```bash
docker run -p 5000:10000 label-verification-app
```

**Port mapping explained:**
- `-p 5000:10000` means:
  - `5000` = port on your Linux machine (what you access in browser)
  - `10000` = port inside the container (where Flask/Gunicorn runs)

**Run in background (detached mode):**
```bash
docker run -d -p 5000:10000 --name label-app label-verification-app
```

**Expected output:**
```
[2025-12-09 19:26:46 +0000] [1] [INFO] Starting gunicorn 22.0.0
[2025-12-09 19:26:46 +0000] [1] [INFO] Listening at: http://0.0.0.0:10000 (1)
[2025-12-09 19:26:46 +0000] [1] [INFO] Using worker: sync
[2025-12-09 19:26:46 +0000] [2] [INFO] Booting worker with pid: 2
```

### Step 4: Test the Application

Open your browser:
```
http://localhost:5000
```

You should see the "TTB Label Application Form" interface.

---

## Testing Steps

### Test 1: Basic Functionality

1. Fill out the form:
   - Brand Name: "Test Distillery"
   - Product Type: "Bourbon Whiskey"
   - ABV: "45"
   - Net Contents: "750 mL"

2. Upload any image with text

3. Click "Verify Label"

4. Verify you get results (not an error about Tesseract)

### Test 2: OCR Verification

Create a simple test image with text:
```bash
# Quick way to create test image (if you have ImageMagick):
convert -size 800x600 xc:white \
  -gravity center \
  -pointsize 48 \
  -annotate +0-200 "TEST DISTILLERY" \
  -annotate +0-100 "BOURBON WHISKEY" \
  -annotate +0+0 "45% ALC/VOL" \
  -annotate +0+100 "750 mL" \
  -annotate +0+200 "GOVERNMENT WARNING" \
  test_label.png
```

Then upload this image and verify:
- Brand Name matches
- Product Type matches
- ABV matches
- Net Contents matches
- Government Warning detected

---

## Docker Commands Reference

### View Running Containers
```bash
docker ps
```

### View All Containers (including stopped)
```bash
docker ps -a
```

### View Container Logs
```bash
docker logs label-app
# Or if you didn't use --name:
docker logs <container-id>
```

### Follow Logs in Real-time
```bash
docker logs -f label-app
```

### Stop Container
```bash
docker stop label-app
```

### Start Stopped Container
```bash
docker start label-app
```

### Remove Container
```bash
docker rm label-app
```

### Remove Image
```bash
docker rmi label-verification-app
```

### Access Container Shell (for debugging)
```bash
docker exec -it label-app /bin/bash

# Inside container, you can:
tesseract --version  # Verify Tesseract is installed
python --version     # Check Python version
ls /app/backend      # View application files
```

---

## Troubleshooting

### Issue: "docker: command not found"
**Solution:** Install Docker:
```bash
sudo apt-get install docker.io
```

### Issue: "permission denied while trying to connect to Docker daemon"
**Solution:** Either:
1. Use sudo: `sudo docker build ...`
2. Add user to docker group:
   ```bash
   sudo usermod -aG docker $USER
   # Log out and log back in
   ```

### Issue: Port 5000 already in use
**Solution:** Use a different port:
```bash
docker run -p 8080:10000 label-verification-app
# Access at http://localhost:8080
```

### Issue: Build fails with network errors
**Solution:** Check internet connection. Docker needs to download base images and packages.

### Issue: Container exits immediately
**Check logs:**
```bash
docker logs <container-id>
```
Look for Python errors or missing files.

### Issue: Application returns 500 error when uploading images
**Check logs in real-time:**
```bash
docker logs -f label-app
```
Upload an image and watch for errors. Most likely cause: Tesseract not installed (shouldn't happen with Docker, but check the Dockerfile if it does).

---

## Rebuilding After Code Changes

If you modify the code, rebuild the image:

```bash
# Stop and remove old container
docker stop label-app
docker rm label-app

# Rebuild image (Docker will cache unchanged layers)
docker build -t label-verification-app .

# Run new container
docker run -d -p 5000:10000 --name label-app label-verification-app
```

**Pro tip:** Use `docker-compose` for easier rebuilds (optional):

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:10000"
    image: label-verification-app
```

Then just:
```bash
docker-compose up --build
```

---

## Comparing to Local Setup

| Aspect | Docker | Local Python |
|--------|--------|--------------|
| Tesseract Install | ✅ Automatic | ❌ Manual (apt-get) |
| Python Deps | ✅ Automatic | ❌ Manual (pip) |
| Isolation | ✅ Fully isolated | ⚠️ System-wide |
| Startup Time | ⚠️ ~30s first run | ✅ Instant |
| Development | ⚠️ Need rebuild | ✅ Auto-reload |
| Production Match | ✅ Identical | ⚠️ May differ |

**Recommendation:**
- **Development:** Local Python (faster iteration)
- **Testing/Production:** Docker (consistency, easier deployment)

---

## Success Criteria

✅ Docker builds without errors
✅ Container starts and stays running
✅ Application accessible at http://localhost:5000
✅ Form loads correctly
✅ Image upload works
✅ OCR processing succeeds (no Tesseract errors)
✅ Verification results display properly
✅ Government warning detection works

If all of these pass, your Docker setup is working perfectly! 🎉
