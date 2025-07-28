# transport_database.py
"""
Transport Database Manager

This module handles the transport cost database, providing functionality to:
1. Load transport cost data from Excel/JSON
2. Query costs based on lane and weight
3. Calculate transport costs automatically based on shipment parameters
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import streamlit as st

class TransportDatabase:
    """
    Manages the transport cost database and provides cost lookup functionality.
    """
    
    def __init__(self):
        self.database = []
        self.weight_clusters = []
        self.lanes_index = {}
        
    def load_from_excel(self, file_path: str):
        """
        Load transport cost data from Excel file.
        """
        df = pd.read_excel(file_path, sheet_name=0)
        
        # Find the header row containing weight clusters
        header_row = None
        for idx, row in df.iterrows():
            if pd.notna(row.iloc[14]) and str(row.iloc[14]).startswith("≤"):
                header_row = idx
                break
        
        if header_row is None:
            raise ValueError("Could not find header row with weight clusters")
        
        # Extract weight clusters
        self.weight_clusters = []
        for col in range(14, len(df.columns)):
            value = df.iloc[header_row, col]
            if pd.notna(value) and str(value).startswith("≤"):
                weight = int(str(value).replace("≤", "").strip())
                self.weight_clusters.append(weight)
            elif self.weight_clusters:  # Stop when we've found all weight clusters
                break
        
        # Process data rows
        self.database = []
        for idx in range(header_row + 1, len(df)):
            row = df.iloc[idx]
            
            # Skip empty rows
            if pd.isna(row.iloc[0]):
                continue
            
            entry = {
                "lane_id": str(row.iloc[0]),
                "origin": {
                    "country": str(row.iloc[1]) if pd.notna(row.iloc[1]) else "",
                    "zip_code": str(row.iloc[2]) if pd.notna(row.iloc[2]) else "",
                    "city": str(row.iloc[3]) if pd.notna(row.iloc[3]) else ""
                },
                "destination": {
                    "country": str(row.iloc[4]) if pd.notna(row.iloc[4]) else "",
                    "zip_code": str(row.iloc[5]) if pd.notna(row.iloc[5]) else "",
                    "city": str(row.iloc[6]) if pd.notna(row.iloc[6]) else ""
                },
                "lane_code": str(row.iloc[7]) if pd.notna(row.iloc[7]) else "",
                "statistics": {
                    "shipments_per_year": self._parse_number(row.iloc[8]),
                    "weight_per_year": self._parse_number(row.iloc[9]),
                    "avg_shipment_size": self._parse_number(row.iloc[10])
                },
                "lead_time": {
                    "groupage": str(row.iloc[11]) if pd.notna(row.iloc[11]) else "",
                    "ltl": str(row.iloc[12]) if pd.notna(row.iloc[12]) else "",
                    "ftl": str(row.iloc[13]) if pd.notna(row.iloc[13]) else ""
                },
                "prices_by_weight": {}
            }
            
            # Add prices for each weight cluster
            for i, weight in enumerate(self.weight_clusters):
                price_value = row.iloc[14 + i]
                if pd.notna(price_value):
                    price = self._parse_price(price_value)
                    if price is not None:
                        entry["prices_by_weight"][weight] = price
            
            # Add full truck price
            ftl_index = 14 + len(self.weight_clusters)
            if ftl_index < len(row) and pd.notna(row.iloc[ftl_index]):
                entry["full_truck_price"] = str(row.iloc[ftl_index])
            
            # Add fuel surcharge
            if ftl_index + 1 < len(row) and pd.notna(row.iloc[ftl_index + 1]):
                entry["fuel_surcharge"] = self._parse_percentage(row.iloc[ftl_index + 1])
            
            self.database.append(entry)
        
        # Build lane index for faster lookup
        self._build_lane_index()
    
    def _parse_number(self, value) -> Optional[float]:
        """Parse numeric value from Excel cell"""
        if pd.isna(value):
            return None
        try:
            # Remove spaces and convert
            clean_value = str(value).replace(" ", "").replace(",", ".")
            return float(clean_value)
        except:
            return None
    
    def _parse_price(self, value) -> Optional[float]:
        """Parse price value from Excel cell"""
        if pd.isna(value):
            return None
        try:
            # Remove currency symbol, spaces, and convert
            clean_value = str(value).replace("€", "").replace(" ", "").replace(",", ".")
            return float(clean_value)
        except:
            return None
    
    def _parse_percentage(self, value) -> Optional[float]:
        """Parse percentage value from Excel cell"""
        if pd.isna(value):
            return None
        try:
            clean_value = str(value).replace("%", "").replace(" ", "").replace(",", ".")
            return float(clean_value)
        except:
            return None
    
    def _build_lane_index(self):
        """Build index for faster lane lookup"""
        self.lanes_index = {}
        for entry in self.database:
            # Create lookup keys
            lane_key = f"{entry['origin']['country']}{entry['origin']['zip_code']}-{entry['destination']['country']}{entry['destination']['zip_code']}"
            self.lanes_index[lane_key] = entry
            
            # Also index by lane code
            if entry['lane_code']:
                self.lanes_index[entry['lane_code']] = entry
    
    def find_lane(self, origin_country: str, origin_zip: str, dest_country: str, dest_zip: str) -> Optional[Dict]:
        """
        Find lane entry based on origin and destination.
        First tries exact match, then tries with 2-digit zip codes.
        """
        # Try exact match
        lane_key = f"{origin_country}{origin_zip}-{dest_country}{dest_zip}"
        if lane_key in self.lanes_index:
            return self.lanes_index[lane_key]
        
        # Try with 2-digit zip codes
        origin_zip_2 = origin_zip[:2] if len(origin_zip) >= 2 else origin_zip
        dest_zip_2 = dest_zip[:2] if len(dest_zip) >= 2 else dest_zip
        lane_key_2 = f"{origin_country}{origin_zip_2}-{dest_country}{dest_zip_2}"
        
        if lane_key_2 in self.lanes_index:
            return self.lanes_index[lane_key_2]
        
        # Search through all entries for partial match
        for entry in self.database:
            if (entry['origin']['country'] == origin_country and 
                entry['origin']['zip_code'][:2] == origin_zip_2 and
                entry['destination']['country'] == dest_country and
                entry['destination']['zip_code'][:2] == dest_zip_2):
                return entry
        
        return None
    
    def calculate_transport_cost(self, weight_kg: float, lane_entry: Dict, 
                               loading_meters: float = None, is_international: bool = False,
                               num_pallets: int = 1) -> Dict:
        """
        Calculate transport cost based on carrier pricing rules.
        
        Args:
            weight_kg: Total weight in kg
            lane_entry: Lane database entry
            loading_meters: Loading meters (for space-based pricing)
            is_international: Whether shipment is international
            num_pallets: Number of pallets
            
        Returns:
            Dictionary with cost details
        """
        # Determine if full truck is needed (>34 pallets)
        if num_pallets > 34:
            base_cost = self._parse_full_truck_price(lane_entry.get('full_truck_price', ''))
            extra_pallets = num_pallets - 34
            
            # Calculate cost for extra pallets
            extra_weight = weight_kg * (extra_pallets / num_pallets)
            extra_cost = self._get_weight_based_price(extra_weight, lane_entry)
            
            total_cost = base_cost + extra_cost if base_cost else extra_cost
            cost_per_pallet = total_cost / num_pallets if num_pallets > 0 else 0
            
            return {
                'total_cost': total_cost,
                'cost_per_pallet': cost_per_pallet,
                'cost_type': 'full_truck_plus',
                'base_truck_cost': base_cost,
                'extra_pallets_cost': extra_cost
            }
        
        # Standard calculation - compare weight-based vs space-based
        weight_based_cost = self._get_weight_based_price(weight_kg, lane_entry)
        
        # Space-based cost calculation
        space_based_cost = None
        if loading_meters is not None:
            if is_international:
                # International: 1500 €/loading meter
                space_based_cost = loading_meters * 1500
            else:
                # National: 800 €/loading meter
                space_based_cost = loading_meters * 800
        
        # Use the higher cost
        if space_based_cost is not None and space_based_cost > weight_based_cost:
            total_cost = space_based_cost
            cost_type = 'space_based'
        else:
            total_cost = weight_based_cost
            cost_type = 'weight_based'
        
        # Apply fuel surcharge if available
        if 'fuel_surcharge' in lane_entry and lane_entry['fuel_surcharge']:
            surcharge = total_cost * (lane_entry['fuel_surcharge'] / 100)
            total_cost += surcharge
        else:
            surcharge = 0
        
        cost_per_pallet = total_cost / num_pallets if num_pallets > 0 else total_cost
        
        return {
            'total_cost': total_cost,
            'cost_per_pallet': cost_per_pallet,
            'cost_type': cost_type,
            'weight_based_cost': weight_based_cost,
            'space_based_cost': space_based_cost,
            'fuel_surcharge': surcharge,
            'weight_cluster_used': self._find_weight_cluster(weight_kg)
        }
    
    def _get_weight_based_price(self, weight_kg: float, lane_entry: Dict) -> float:
        """Get price based on weight cluster"""
        weight_cluster = self._find_weight_cluster(weight_kg)
        
        if weight_cluster in lane_entry['prices_by_weight']:
            return lane_entry['prices_by_weight'][weight_cluster]
        
        # If exact cluster not found, use the highest available
        available_clusters = sorted(lane_entry['prices_by_weight'].keys())
        if available_clusters:
            return lane_entry['prices_by_weight'][available_clusters[-1]]
        
        return 0.0
    
    def _find_weight_cluster(self, weight_kg: float) -> int:
        """Find appropriate weight cluster for given weight"""
        for cluster in self.weight_clusters:
            if weight_kg <= cluster:
                return cluster
        # If weight exceeds all clusters, return the highest
        return self.weight_clusters[-1] if self.weight_clusters else 0
    
    def _parse_full_truck_price(self, price_str: str) -> float:
        """Parse full truck price from string"""
        if not price_str or price_str.lower() == 'gem. vereinbarung':
            return 0.0
        try:
            return self._parse_price(price_str) or 0.0
        except:
            return 0.0
    
    def save_to_json(self, file_path: str):
        """Save database to JSON file"""
        data = {
            'weight_clusters': self.weight_clusters,
            'database': self.database
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_json(self, file_path: str):
        """Load database from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.weight_clusters = data['weight_clusters']
        self.database = data['database']
        self._build_lane_index()
    
    def get_all_lanes(self) -> List[Dict]:
        """Get all lanes in the database"""
        return self.database
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        total_lanes = len(self.database)
        countries = set()
        
        for entry in self.database:
            countries.add(entry['origin']['country'])
            countries.add(entry['destination']['country'])
        
        return {
            'total_lanes': total_lanes,
            'weight_clusters': len(self.weight_clusters),
            'countries': sorted(list(countries)),
            'min_weight': min(self.weight_clusters) if self.weight_clusters else 0,
            'max_weight': max(self.weight_clusters) if self.weight_clusters else 0
        }
    
    def filter_lanes(self, origin_country: str = None, dest_country: str = None, 
                     city: str = None) -> List[Dict]:
        """Filter lanes based on criteria"""
        filtered = []
        
        for entry in self.database:
            # Check origin country
            if origin_country and entry['origin']['country'] != origin_country:
                continue
            
            # Check destination country
            if dest_country and entry['destination']['country'] != dest_country:
                continue
            
            # Check city (in either origin or destination)
            if city:
                city_lower = city.lower()
                origin_city = entry['origin']['city'].lower()
                dest_city = entry['destination']['city'].lower()
                if city_lower not in origin_city and city_lower not in dest_city:
                    continue
            
            filtered.append(entry)
        
        return filtered


# Helper function to integrate with existing transport cost calculation
def calculate_transport_cost_from_database(
    supplier_country: str,
    supplier_zip: str,
    dest_country: str,
    dest_zip: str,
    weight_kg: float,
    num_pallets: int,
    loading_meters: float,
    transport_db: TransportDatabase
) -> Optional[Dict]:
    """
    Calculate transport cost using the database.
    
    Returns:
        Dictionary with cost details or None if lane not found
    """
    # Find the lane
    lane = transport_db.find_lane(supplier_country, supplier_zip, dest_country, dest_zip)
    
    if not lane:
        return None
    
    # Determine if international
    is_international = supplier_country != dest_country
    
    # Calculate cost
    return transport_db.calculate_transport_cost(
        weight_kg=weight_kg,
        lane_entry=lane,
        loading_meters=loading_meters,
        is_international=is_international,
        num_pallets=num_pallets
    )