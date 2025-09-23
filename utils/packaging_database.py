# utils/packaging_database.py
"""
Packaging Database Manager

This module handles the packaging data database, providing functionality to:
1. Load packaging data from the static tables or JSON files
2. Manage CRUD operations for packaging configurations
3. Support import/export functionality
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
import streamlit as st
from .packaging_tables import STANDARD_BOXES, SPECIAL_PACKAGING, ADDITIONAL_PACKAGING, ACCESSORY_PACKAGING


class PackagingDatabase:
    """
    Manages the packaging database and provides CRUD functionality.
    """

    def __init__(self):
        self.standard_boxes = {}
        self.special_packaging = {}
        self.additional_packaging = {}
        self.accessory_packaging = {}
        self._load_default_data()

    def _load_default_data(self):
        """Load default data from packaging_tables.py"""
        self.standard_boxes = STANDARD_BOXES.copy()
        self.special_packaging = SPECIAL_PACKAGING.copy()
        self.additional_packaging = ADDITIONAL_PACKAGING.copy()
        self.accessory_packaging = ACCESSORY_PACKAGING.copy()

    def load_from_json(self, file_path: str):
        """Load packaging data from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.standard_boxes = data.get('standard_boxes', {})
            self.special_packaging = data.get('special_packaging', {})
            self.additional_packaging = data.get('additional_packaging', {})
            self.accessory_packaging = data.get('accessory_packaging', {})
            
        except FileNotFoundError:
            # If file doesn't exist, use default data
            self._load_default_data()
        except Exception as e:
            st.error(f"Error loading packaging database: {e}")
            self._load_default_data()

    def save_to_json(self, file_path: str):
        """Save packaging data to JSON file."""
        data = {
            'standard_boxes': self.standard_boxes,
            'special_packaging': self.special_packaging,
            'additional_packaging': self.additional_packaging,
            'accessory_packaging': self.accessory_packaging,
            'metadata': {
                'save_timestamp': pd.Timestamp.now().isoformat(),
                'version': '1.0.0'
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_standard_box(self, box_name: str, box_data: Dict):
        """Add or update standard box configuration."""
        self.standard_boxes[box_name] = box_data

    def remove_standard_box(self, box_name: str):
        """Remove standard box configuration."""
        if box_name in self.standard_boxes:
            del self.standard_boxes[box_name]

    def add_special_packaging(self, package_name: str, package_data: Dict):
        """Add or update special packaging configuration."""
        self.special_packaging[package_name] = package_data

    def remove_special_packaging(self, package_name: str):
        """Remove special packaging configuration."""
        if package_name in self.special_packaging:
            del self.special_packaging[package_name]

    def add_additional_packaging(self, package_name: str, package_data: Dict):
        """Add or update additional packaging configuration."""
        self.additional_packaging[package_name] = package_data

    def remove_additional_packaging(self, package_name: str):
        """Remove additional packaging configuration."""
        if package_name in self.additional_packaging:
            del self.additional_packaging[package_name]

    def add_accessory_packaging(self, accessory_name: str, accessory_data: Dict):
        """Add or update accessory packaging configuration."""
        self.accessory_packaging[accessory_name] = accessory_data

    def remove_accessory_packaging(self, accessory_name: str):
        """Remove accessory packaging configuration."""
        if accessory_name in self.accessory_packaging:
            del self.accessory_packaging[accessory_name]

    def get_all_packaging_types(self):
        """Get all packaging types for dropdowns."""
        types = {
            'Standard Boxes': list(self.standard_boxes.keys()),
            'Special Packaging': list(self.special_packaging.keys()),
            'Additional Packaging': list(self.additional_packaging.keys()),
            'Accessory Packaging': list(self.accessory_packaging.keys())
        }
        return types

    def get_packaging_details(self, package_type: str, package_name: str):
        """Get details for a specific packaging item."""
        if package_type == 'Standard Boxes':
            return self.standard_boxes.get(package_name, {})
        elif package_type == 'Special Packaging':
            return self.special_packaging.get(package_name, {})
        elif package_type == 'Additional Packaging':
            return self.additional_packaging.get(package_name, {})
        elif package_type == 'Accessory Packaging':
            return self.accessory_packaging.get(package_name, {})
        return {}

    def get_statistics(self):
        """Get statistics about the packaging database."""
        return {
            'standard_boxes_count': len(self.standard_boxes),
            'special_packaging_count': len(self.special_packaging),
            'additional_packaging_count': len(self.additional_packaging),
            'accessory_packaging_count': len(self.accessory_packaging),
            'total_items': len(self.standard_boxes) + len(self.special_packaging) + 
                          len(self.additional_packaging) + len(self.accessory_packaging)
        }

    def reset_to_defaults(self):
        """Reset database to default values."""
        self._load_default_data()

    def search_packaging(self, search_term: str):
        """Search for packaging items by name."""
        results = {
            'Standard Boxes': {},
            'Special Packaging': {},
            'Additional Packaging': {},
            'Accessory Packaging': {}
        }
        
        search_term = search_term.lower()
        
        for name, data in self.standard_boxes.items():
            if search_term in name.lower():
                results['Standard Boxes'][name] = data
                
        for name, data in self.special_packaging.items():
            if search_term in name.lower():
                results['Special Packaging'][name] = data
                
        for name, data in self.additional_packaging.items():
            if search_term in name.lower():
                results['Additional Packaging'][name] = data
                
        for name, data in self.accessory_packaging.items():
            if search_term in name.lower():
                results['Accessory Packaging'][name] = data
        
        return results