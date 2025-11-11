# utils/supplier_database.py
"""
Supplier Database Manager

This module handles the supplier historical database, providing functionality to:
1. Store all historical supplier configurations
2. Sync with current user configurations
3. Support import/export functionality

FIXED: Corrected key names for 'plant' and 'country' to match supplier data structure
"""

import json
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path

class SupplierDatabase:
    """
    Enhanced Supplier Database with Excel/JSON import capabilities
    """
    
    def __init__(self):
        self.database = {}  # vendor_id -> supplier data
    
    def add_supplier(self, vendor_id: str, supplier_data: Dict) -> None:
        """Add or update a supplier"""
        self.database[vendor_id] = supplier_data
    
    def update_supplier(self, vendor_id: str, supplier_data: Dict) -> None:
        """Update existing supplier"""
        if vendor_id in self.database:
            self.database[vendor_id].update(supplier_data)
    
    def remove_supplier(self, vendor_id: str) -> bool:
        """Remove a supplier"""
        if vendor_id in self.database:
            del self.database[vendor_id]
            return True
        return False
    
    def get_supplier(self, vendor_id: str) -> Optional[Dict]:
        """Get supplier by vendor ID"""
        return self.database.get(vendor_id)
    
    def supplier_exists(self, vendor_id: str) -> bool:
        """Check if supplier exists"""
        return vendor_id in self.database
    
    def filter_suppliers(self, vendor_id: str = None, country: str = None, 
                        city: str = None) -> List[Dict]:
        """Filter suppliers by criteria"""
        results = []
        
        for vid, data in self.database.items():
            match = True
            
            if vendor_id and vendor_id.lower() not in vid.lower():
                match = False
            
            if country and country.lower() not in data.get('vendor_country', '').lower():
                match = False
            
            if city and city.lower() not in data.get('city_of_manufacture', '').lower():
                match = False
            
            if match:
                results.append(data)
        
        return results
    
    def sync_with_configurations(self, current_suppliers: List[Dict]) -> None:
        """Sync database with current supplier configurations"""
        for supplier in current_suppliers:
            vendor_id = supplier.get('vendor_id', '')
            if vendor_id:
                self.add_supplier(vendor_id, supplier)
    
    def load_from_excel(self, file_path: str) -> None:
        """
        Load supplier data from Excel file
        Expected columns: Vendor ID, Vendor Name, Vendor Country, City of Manufacture,
                         Vendor ZIP, Delivery Performance, Deliveries per Month,
                         KB/Bendix Plant, KB/Bendix Country, Distance (km)
        """
        try:
            df = pd.read_excel(file_path)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Column mapping (Excel -> Database)
            column_mapping = {
                'Vendor ID': 'vendor_id',
                'Vendor Name': 'vendor_name',
                'Vendor Country': 'vendor_country',
                'City of Manufacture': 'city_of_manufacture',
                'Vendor ZIP': 'vendor_zip',
                'Delivery Performance': 'delivery_performance',
                'Delivery Performance (%)': 'delivery_performance',
                'Deliveries per Month': 'deliveries_per_month',
                'KB/Bendix Plant': 'plant',
                'Plant': 'plant',
                'KB/Bendix Country': 'country',
                'Country': 'country',
                'Distance (km)': 'distance',
                'Distance': 'distance'
            }
            
            # Process each row
            for _, row in df.iterrows():
                supplier_data = {}
                vendor_id = None
                
                for excel_col, db_col in column_mapping.items():
                    if excel_col in df.columns:
                        value = row[excel_col]
                        
                        # Handle NaN values
                        if pd.isna(value):
                            if db_col in ['delivery_performance', 'distance']:
                                value = 0.0
                            elif db_col == 'deliveries_per_month':
                                value = 0
                            else:
                                value = ""
                        
                        # Store vendor_id separately
                        if db_col == 'vendor_id':
                            vendor_id = str(value)
                        
                        supplier_data[db_col] = value
                
                # Add supplier if vendor_id exists
                if vendor_id:
                    self.add_supplier(vendor_id, supplier_data)
            
        except Exception as e:
            raise Exception(f"Error loading Excel file: {str(e)}")
    
    def load_from_csv(self, file_path: str) -> None:
        """Load supplier data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            column_mapping = {
                'Vendor ID': 'vendor_id',
                'Vendor Name': 'vendor_name',
                'Vendor Country': 'vendor_country',
                'City of Manufacture': 'city_of_manufacture',
                'Vendor ZIP': 'vendor_zip',
                'Delivery Performance': 'delivery_performance',
                'Delivery Performance (%)': 'delivery_performance',
                'Deliveries per Month': 'deliveries_per_month',
                'KB/Bendix Plant': 'plant',
                'Plant': 'plant',
                'KB/Bendix Country': 'country',
                'Country': 'country',
                'Distance (km)': 'distance',
                'Distance': 'distance'
            }
            
            for _, row in df.iterrows():
                supplier_data = {}
                vendor_id = None
                
                for excel_col, db_col in column_mapping.items():
                    if excel_col in df.columns:
                        value = row[excel_col]
                        
                        if pd.isna(value):
                            if db_col in ['delivery_performance', 'distance']:
                                value = 0.0
                            elif db_col == 'deliveries_per_month':
                                value = 0
                            else:
                                value = ""
                        
                        if db_col == 'vendor_id':
                            vendor_id = str(value)
                        
                        supplier_data[db_col] = value
                
                if vendor_id:
                    self.add_supplier(vendor_id, supplier_data)
                    
        except Exception as e:
            raise Exception(f"Error loading CSV file: {str(e)}")
    
    def load_from_csv_dataframe(self, df: pd.DataFrame) -> None:
        """Load supplier data from pandas DataFrame"""
        try:
            df.columns = df.columns.str.strip()
            
            column_mapping = {
                'Vendor ID': 'vendor_id',
                'Vendor Name': 'vendor_name',
                'Vendor Country': 'vendor_country',
                'City of Manufacture': 'city_of_manufacture',
                'Vendor ZIP': 'vendor_zip',
                'Delivery Performance': 'delivery_performance',
                'Delivery Performance (%)': 'delivery_performance',
                'Deliveries per Month': 'deliveries_per_month',
                'KB/Bendix Plant': 'plant',
                'Plant': 'plant',
                'KB/Bendix Country': 'country',
                'Country': 'country',
                'Distance (km)': 'distance',
                'Distance': 'distance'
            }
            
            for _, row in df.iterrows():
                supplier_data = {}
                vendor_id = None
                
                for excel_col, db_col in column_mapping.items():
                    if excel_col in df.columns:
                        value = row[excel_col]
                        
                        if pd.isna(value):
                            if db_col in ['delivery_performance', 'distance']:
                                value = 0.0
                            elif db_col == 'deliveries_per_month':
                                value = 0
                            else:
                                value = ""
                        
                        if db_col == 'vendor_id':
                            vendor_id = str(value)
                        
                        supplier_data[db_col] = value
                
                if vendor_id:
                    self.add_supplier(vendor_id, supplier_data)
                    
        except Exception as e:
            raise Exception(f"Error loading DataFrame: {str(e)}")
    
    def load_from_json(self, file_path: str) -> None:
        """Load supplier data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Support both direct database format and wrapped format
            if 'database' in data:
                self.database = data['database']
            else:
                self.database = data
            
        except FileNotFoundError:
            # Initialize with empty data if file doesn't exist
            pass
        except Exception as e:
            raise Exception(f"Error loading JSON file: {str(e)}")
    
    def save_to_json(self, file_path: str) -> None:
        """Save supplier data to JSON file"""
        data = {
            'database': self.database,
            'metadata': {
                'save_timestamp': pd.Timestamp.now().isoformat(),
                'version': '1.0.0',
                'total_suppliers': len(self.database)
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert supplier database to DataFrame for export"""
        if not self.database:
            return pd.DataFrame()
        
        # Convert to list of dicts
        data_list = []
        for vendor_id, supplier_data in self.database.items():
            row = {
                'Vendor ID': supplier_data.get('vendor_id', vendor_id),
                'Vendor Name': supplier_data.get('vendor_name', ''),
                'Vendor Country': supplier_data.get('vendor_country', ''),
                'City of Manufacture': supplier_data.get('city_of_manufacture', ''),
                'Vendor ZIP': supplier_data.get('vendor_zip', ''),
                'Delivery Performance (%)': supplier_data.get('delivery_performance', 0.0),
                'Deliveries per Month': supplier_data.get('deliveries_per_month', 0),
                'KB/Bendix Plant': supplier_data.get('plant', ''),
                'KB/Bendix Country': supplier_data.get('country', ''),
                'Distance (km)': supplier_data.get('distance', 0.0)
            }
            data_list.append(row)
        
        return pd.DataFrame(data_list)
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        countries = set()
        cities = set()
        
        for supplier_data in self.database.values():
            if supplier_data.get('vendor_country'):
                countries.add(supplier_data['vendor_country'])
            if supplier_data.get('city_of_manufacture'):
                cities.add(supplier_data['city_of_manufacture'])
        
        return {
            'total_suppliers': len(self.database),
            'total_countries': len(countries),
            'total_cities': len(cities),
            'countries': list(countries),
            'cities': list(cities)
        }