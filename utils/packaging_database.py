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
from typing import Dict, List, Optional
from pathlib import Path

class PackagingDatabase:
    """
    Enhanced Packaging Database with p/n column support and Excel/JSON import
    """
    
    def __init__(self):
        # Updated schema with p/n as first field
        self.standard_boxes = {}
        self.special_packaging = {}
        self.additional_packaging = {}
        self.accessory_packaging = {}
    
    def add_standard_box(self, item_name: str, item_data: Dict) -> None:
        """Add or update a standard box with p/n support"""
        # Ensure p/n field exists
        if 'pn' not in item_data:
            item_data['pn'] = item_name  # Use name as p/n if not provided
        self.standard_boxes[item_name] = item_data
    
    def add_special_packaging(self, item_name: str, item_data: Dict) -> None:
        """Add or update special packaging with p/n support"""
        if 'pn' not in item_data:
            item_data['pn'] = item_name
        self.special_packaging[item_name] = item_data
    
    def add_additional_packaging(self, item_name: str, item_data: Dict) -> None:
        """Add or update additional packaging with p/n support"""
        if 'pn' not in item_data:
            item_data['pn'] = item_name
        self.additional_packaging[item_name] = item_data
    
    def add_accessory_packaging(self, item_name: str, item_data: Dict) -> None:
        """Add or update accessory packaging with p/n support"""
        if 'pn' not in item_data:
            item_data['pn'] = item_name
        self.accessory_packaging[item_name] = item_data
    
    def remove_standard_box(self, item_name: str) -> bool:
        """Remove a standard box"""
        if item_name in self.standard_boxes:
            del self.standard_boxes[item_name]
            return True
        return False
    
    def remove_special_packaging(self, item_name: str) -> bool:
        """Remove special packaging"""
        if item_name in self.special_packaging:
            del self.special_packaging[item_name]
            return True
        return False
    
    def remove_additional_packaging(self, item_name: str) -> bool:
        """Remove additional packaging"""
        if item_name in self.additional_packaging:
            del self.additional_packaging[item_name]
            return True
        return False
    
    def remove_accessory_packaging(self, item_name: str) -> bool:
        """Remove accessory packaging"""
        if item_name in self.accessory_packaging:
            del self.accessory_packaging[item_name]
            return True
        return False
    
    def get_packaging_details(self, packaging_type: str, item_name: str) -> Optional[Dict]:
        """Get details for a specific packaging item"""
        type_map = {
            "Standard Boxes": self.standard_boxes,
            "Special Packaging": self.special_packaging,
            "Additional Packaging": self.additional_packaging,
            "Accessory Packaging": self.accessory_packaging
        }
        
        packaging_dict = type_map.get(packaging_type, {})
        return packaging_dict.get(item_name)
    
    def search_packaging(self, search_term: str) -> Dict[str, Dict]:
        """Search for packaging items by name or p/n"""
        results = {
            "Standard Boxes": {},
            "Special Packaging": {},
            "Additional Packaging": {},
            "Accessory Packaging": {}
        }
        
        search_lower = search_term.lower()
        
        for name, data in self.standard_boxes.items():
            if (search_lower in name.lower() or 
                search_lower in data.get('pn', '').lower()):
                results["Standard Boxes"][name] = data
        
        for name, data in self.special_packaging.items():
            if (search_lower in name.lower() or 
                search_lower in data.get('pn', '').lower()):
                results["Special Packaging"][name] = data
        
        for name, data in self.additional_packaging.items():
            if (search_lower in name.lower() or 
                search_lower in data.get('pn', '').lower()):
                results["Additional Packaging"][name] = data
        
        for name, data in self.accessory_packaging.items():
            if (search_lower in name.lower() or 
                search_lower in data.get('pn', '').lower()):
                results["Accessory Packaging"][name] = data
        
        return results
    
    def load_from_excel(self, file_path: str) -> None:
        """
        Load packaging data from Excel file
        Expected columns: p/n, Name, Packaging Characteristics, Cost per pcs, L, W, H, 
                         MT weight kg, Pcs Boxes per LU, Boxes per Layer
        """
        try:
            df = pd.read_excel(file_path)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Expected columns mapping
            column_mapping = {
                'p/n': 'pn',
                'Name': 'name',
                'Packaging Characteristics': 'Packaging_Characteristics',
                'Cost per pcs': 'Cost_per_pcs',
                'L': 'L',
                'W': 'W',
                'H': 'H',
                'MT weight kg': 'MT_weight_kg',
                'Pcs Boxes per LU': 'Pcs_Boxes_per_LU',
                'Boxes per Layer': 'Boxes_per_layer'
            }
            
            # Process each row
            for _, row in df.iterrows():
                item_data = {}
                
                for excel_col, db_col in column_mapping.items():
                    if excel_col in df.columns:
                        value = row[excel_col]
                        # Handle NaN values
                        if pd.isna(value):
                            if db_col in ['Cost_per_pcs', 'L', 'W', 'H', 'MT_weight_kg']:
                                value = 0.0
                            elif db_col in ['Pcs_Boxes_per_LU', 'Boxes_per_layer']:
                                value = 0
                            else:
                                value = ""
                        item_data[db_col] = value
                
                # Use Name as key, fallback to p/n
                item_name = item_data.get('name', item_data.get('pn', f"Item_{len(self.standard_boxes)}"))
                
                # Determine packaging type based on characteristics
                characteristics = str(item_data.get('Packaging_Characteristics', '')).lower()
                
                if 'returnable' in characteristics:
                    self.add_standard_box(item_name, item_data)
                elif 'special' in characteristics or 'tray' in characteristics:
                    self.add_special_packaging(item_name, item_data)
                else:
                    self.add_additional_packaging(item_name, item_data)
            
        except Exception as e:
            raise Exception(f"Error loading Excel file: {str(e)}")
    
    def load_from_csv(self, file_path: str) -> None:
        """Load packaging data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            
            # Process similar to Excel
            df.columns = df.columns.str.strip()
            
            column_mapping = {
                'p/n': 'pn',
                'Name': 'name',
                'Packaging Characteristics': 'Packaging_Characteristics',
                'Cost per pcs': 'Cost_per_pcs',
                'L': 'L',
                'W': 'W',
                'H': 'H',
                'MT weight kg': 'MT_weight_kg',
                'Pcs Boxes per LU': 'Pcs_Boxes_per_LU',
                'Boxes per Layer': 'Boxes_per_layer'
            }
            
            for _, row in df.iterrows():
                item_data = {}
                
                for excel_col, db_col in column_mapping.items():
                    if excel_col in df.columns:
                        value = row[excel_col]
                        if pd.isna(value):
                            if db_col in ['Cost_per_pcs', 'L', 'W', 'H', 'MT_weight_kg']:
                                value = 0.0
                            elif db_col in ['Pcs_Boxes_per_LU', 'Boxes_per_layer']:
                                value = 0
                            else:
                                value = ""
                        item_data[db_col] = value
                
                item_name = item_data.get('name', item_data.get('pn', f"Item_{len(self.standard_boxes)}"))
                
                characteristics = str(item_data.get('Packaging_Characteristics', '')).lower()
                
                if 'returnable' in characteristics:
                    self.add_standard_box(item_name, item_data)
                elif 'special' in characteristics or 'tray' in characteristics:
                    self.add_special_packaging(item_name, item_data)
                else:
                    self.add_additional_packaging(item_name, item_data)
                    
        except Exception as e:
            raise Exception(f"Error loading CSV file: {str(e)}")
    
    def load_from_json(self, file_path: str) -> None:
        """Load packaging data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.standard_boxes = data.get('standard_boxes', {})
            self.special_packaging = data.get('special_packaging', {})
            self.additional_packaging = data.get('additional_packaging', {})
            self.accessory_packaging = data.get('accessory_packaging', {})
            
        except FileNotFoundError:
            # Initialize with empty data if file doesn't exist
            pass
        except Exception as e:
            raise Exception(f"Error loading JSON file: {str(e)}")
    
    def save_to_json(self, file_path: str) -> None:
        """Save packaging data to JSON file"""
        data = {
            'standard_boxes': self.standard_boxes,
            'special_packaging': self.special_packaging,
            'additional_packaging': self.additional_packaging,
            'accessory_packaging': self.accessory_packaging,
            'metadata': {
                'save_timestamp': pd.Timestamp.now().isoformat(),
                'version': '1.0.0',
                'total_items': (
                    len(self.standard_boxes) +
                    len(self.special_packaging) +
                    len(self.additional_packaging) +
                    len(self.accessory_packaging)
                )
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert all packaging data to DataFrame for export"""
        all_data = []
        
        # Standard boxes
        for name, data in self.standard_boxes.items():
            row = {'Type': 'Standard Box', 'Name': name}
            row.update(data)
            all_data.append(row)
        
        # Special packaging
        for name, data in self.special_packaging.items():
            row = {'Type': 'Special Packaging', 'Name': name}
            row.update(data)
            all_data.append(row)
        
        # Additional packaging
        for name, data in self.additional_packaging.items():
            row = {'Type': 'Additional Packaging', 'Name': name}
            row.update(data)
            all_data.append(row)
        
        # Accessory packaging
        for name, data in self.accessory_packaging.items():
            row = {'Type': 'Accessory Packaging', 'Name': name}
            row.update(data)
            all_data.append(row)
        
        if all_data:
            df = pd.DataFrame(all_data)
            # Reorder columns to put p/n first
            if 'pn' in df.columns:
                cols = ['pn'] + [col for col in df.columns if col != 'pn']
                df = df[cols]
            return df
        else:
            return pd.DataFrame()
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        return {
            'standard_boxes_count': len(self.standard_boxes),
            'special_packaging_count': len(self.special_packaging),
            'additional_packaging_count': len(self.additional_packaging),
            'accessory_packaging_count': len(self.accessory_packaging),
            'total_items': (
                len(self.standard_boxes) +
                len(self.special_packaging) +
                len(self.additional_packaging) +
                len(self.accessory_packaging)
            )
        }
    
    def reset_to_defaults(self) -> None:
        """Reset database to empty state"""
        self.standard_boxes = {}
        self.special_packaging = {}
        self.additional_packaging = {}
        self.accessory_packaging = {}