import PyInstaller.__main__
import sys
import os
from pathlib import Path

def build_executable():
    """Build standalone executable"""
    
    project_root = Path(__file__).parent
    
    # PyInstaller arguments
    args = [
        'main.py',
        '--name=LogisticsCostCalculator',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',  # Add your icon file
        '--add-data=pages;pages',
        '--add-data=utils;utils',
        '--add-data=Overview.py;.',
        '--hidden-import=streamlit',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=xlsxwriter',
        '--collect-all=streamlit',
        '--collect-all=altair',
        '--collect-all=plotly',
        '--collect-all=pandas',
        '--noconsole'
    ]
    
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build_executable()