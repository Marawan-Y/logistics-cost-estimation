# utils/supplier_database.py
"""
Supplier Database Manager

This module handles the supplier historical database, providing functionality to:
1. Store all historical supplier configurations
2. Sync with current user configurations
3. Support import/export functionality
"""

import json
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
import streamlit as st


class SupplierDatabase:
    """
    Manages the supplier historical database and provides CRUD functionality.
    """

    def __init__(self):
        self.database = {}  # Dict with vendor_id as key

    def load_from_json(self, file_path: str):
        """Load supplier data from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.database = data.get('database', {})
            
        except FileNotFoundError:
            self.database = {}
        except Exception as e:
            st.error(f"Error loading supplier database: {e}")
            self.database = {}

    def save_to_json(self, file_path: str):
        """Save supplier data to JSON file."""
        data = {
            'database': self.database,
            'metadata': {
                'save_timestamp': pd.Timestamp.now().isoformat(),
                'version': '1.0.0',
                'total_suppliers': len(self.database)
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def sync_with_configurations(self, supplier_configs: List[Dict]):
        """Sync database with current supplier configurations."""
        for supplier in supplier_configs:
            vendor_id = supplier.get('vendor_id')
            if vendor_id:
                # Update or add supplier to database
                self.database[vendor_id] = {
                    'vendor_id': supplier.get('vendor_id', ''),
                    'vendor_name': supplier.get('vendor_name', ''),
                    'vendor_country': supplier.get('vendor_country', ''),
                    'city_of_manufacture': supplier.get('city_of_manufacture', ''),
                    'vendor_zip': supplier.get('vendor_zip', ''),
                    'delivery_performance': supplier.get('delivery_performance', 0.0),
                    'deliveries_per_month': supplier.get('deliveries_per_month', 0),
                    'kb_plant': supplier.get('kb_plant', ''),
                    'kb_country': supplier.get('kb_country', ''),
                    'distance': supplier.get('distance', 0.0)
                }

    def add_supplier(self, vendor_id: str, supplier_data: Dict):
        """Add or update supplier in database."""
        self.database[vendor_id] = supplier_data

    def remove_supplier(self, vendor_id: str):
        """Remove supplier from database."""
        if vendor_id in self.database:
            del self.database[vendor_id]

    def update_supplier(self, vendor_id: str, supplier_data: Dict):
        """Update existing supplier."""
        if vendor_id in self.database:
            self.database[vendor_id] = supplier_data

    def supplier_exists(self, vendor_id: str) -> bool:
        """Check if supplier exists in database."""
        return vendor_id in self.database

    def get_supplier(self, vendor_id: str) -> Optional[Dict]:
        """Get supplier data by vendor ID."""
        return self.database.get(vendor_id, None)

    def get_all_suppliers(self) -> List[Dict]:
        """Get all suppliers as a list."""
        return list(self.database.values())

    def to_dataframe(self) -> pd.DataFrame:
        """Convert database to pandas DataFrame with proper column order."""
        if not self.database:
            return pd.DataFrame()
        
        data_list = []
        for idx, (vendor_id, supplier_data) in enumerate(self.database.items(), 1):
            row = {
                'Index': idx,
                'Vendor ID': supplier_data['vendor_id'],
                'Vendor ZIP': supplier_data['vendor_zip'],
                'Vendor Name': supplier_data['vendor_name'],
                'Vendor Country': supplier_data['vendor_country'],
                'City of Manufacture': supplier_data['city_of_manufacture'],
                'Delivery Performance (%)': supplier_data['delivery_performance'],
                'Deliveries per Month': supplier_data['deliveries_per_month'],
                'KB/Bendix Plant': supplier_data['kb_plant'],
                'Distance (km)': supplier_data['distance'],
                'KB/Bendix Country': supplier_data['kb_country']
            }
            data_list.append(row)
        
        return pd.DataFrame(data_list)

    def load_from_csv_dataframe(self, df: pd.DataFrame):
        """Load suppliers from CSV DataFrame."""
        self.database = {}
        
        for _, row in df.iterrows():
            vendor_id = str(row.get('Vendor ID', ''))
            if vendor_id:
                self.database[vendor_id] = {
                    'vendor_id': vendor_id,
                    'vendor_zip': str(row.get('Vendor ZIP', '')),
                    'vendor_name': str(row.get('Vendor Name', '')),
                    'vendor_country': str(row.get('Vendor Country', '')),
                    'city_of_manufacture': str(row.get('City of Manufacture', '')),
                    'delivery_performance': float(row.get('Delivery Performance (%)', 0.0)),
                    'deliveries_per_month': int(row.get('Deliveries per Month', 0)),
                    'kb_plant': str(row.get('KB/Bendix Plant', '')),
                    'distance': float(row.get('Distance (km)', 0.0)),
                    'kb_country': str(row.get('KB/Bendix Country', ''))
                }

    def filter_suppliers(self, vendor_id: str = None, country: str = None, city: str = None) -> List[Dict]:
        """Filter suppliers based on criteria."""
        filtered = []
        
        for supplier_data in self.database.values():
            if vendor_id and vendor_id.lower() not in supplier_data['vendor_id'].lower():
                continue
            if country and country.lower() not in supplier_data['vendor_country'].lower():
                continue
            if city and city.lower() not in supplier_data['city_of_manufacture'].lower():
                continue
            filtered.append(supplier_data)
        
        return filtered

    def get_statistics(self) -> Dict:
        """Get statistics about the supplier database."""
        countries = set()
        for supplier_data in self.database.values():
            countries.add(supplier_data['vendor_country'])
        
        return {
            'total_suppliers': len(self.database),
            'total_countries': len(countries),
            'countries': sorted(list(countries))
        }