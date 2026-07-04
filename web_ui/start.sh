#!/bin/bash

# Face Liveness Detection - Web UI Launcher
# Linux/macOS shell script

echo ""
echo "========================================"
echo "Face Liveness Detection - Web UI"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python not found. Please install Python 3.8+"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $python_version"

# Install dependencies if needed
echo ""
echo "Checking dependencies..."
if ! pip3 list | grep -q flask; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

# Start backend
echo ""
echo "Starting Face Liveness Detection server..."
echo ""
echo "OPEN THIS URL IN YOUR BROWSER:"
echo "========================================"
echo "http://localhost:5000"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 backend.py
