"""
Run script for the Lora Model Manager Flask backend.
Execute this file directly: python run.py
"""
import sys
import os

# Add the parent directory to the Python path so the backend package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import main

if __name__ == '__main__':
    main()
