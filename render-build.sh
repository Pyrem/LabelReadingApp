#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "==> Installing Tesseract OCR..."
apt-get update
apt-get install -y tesseract-ocr

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Build complete!"
