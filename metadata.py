# metadata.py
"""
Ekho Metadata - Entry Point
YouTube to MP3 Converter with Metadata Analysis

This is the main entry point for the metadata functionality.
Follows the same pattern as converter.py
"""
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import the main function from run_metadata
from run_metadata import main

if __name__ == "__main__":
    main()