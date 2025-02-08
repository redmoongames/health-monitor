#!/bin/bash

# Check if the venv folder doesn't exist
if [ ! -d "venv" ]; then
    # Install python3-venv package with automatic "yes" confirmation
    sudo apt install -y python3-venv

    # Create a virtual environment
    python3 -m venv venv
fi

# Source the virtual environment activation script
source venv/bin/activate

# Install pip if not already installed
if ! command -v pip &> /dev/null; then
    python3 -m ensurepip
fi

# Install the requirements
pip install -r requirements.txt

# Run the Qt application
python app.py

# Deactivate the virtual environment after running the application
deactivate
