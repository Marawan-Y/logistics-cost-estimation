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
import math

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
                weight = float(str(value).replace("≤", "").strip())
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
            clean_value = str(value).replace(" ", "").replace(",", ".")
            return float(clean_value)
        except:
            return None
    
    def _parse_price(self, value) -> Optional[float]:
        """Parse price value from Excel cell"""
        if pd.isna(value):
            return None
        try:
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
            lane_key = f"{entry['origin']['country']}{entry['origin']['zip_code']}-{entry['destination']['country']}{entry['destination']['zip_code']}"
            self.lanes_index[lane_key] = entry
            if entry['lane_code']:
                self.lanes_index[entry['lane_code']] = entry
    
    def find_lane(self, origin_country: str, origin_zip: str, dest_country: str, dest_zip: str) -> Optional[Dict]:
        lane_key = f"{origin_country}{origin_zip}-{dest_country}{dest_zip}"
        if lane_key in self.lanes_index:
            return self.lanes_index[lane_key]
        
        origin_zip_2 = origin_zip[:2] if len(origin_zip) >= 2 else origin_zip
        dest_zip_2 = dest_zip[:2] if len(dest_zip) >= 2 else dest_zip
        lane_key_2 = f"{origin_country}{origin_zip_2}-{dest_country}{dest_zip_2}"
        
        if lane_key_2 in self.lanes_index:
            return self.lanes_index[lane_key_2]
        
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
        if num_pallets > 34:
            base_cost = self._parse_full_truck_price(lane_entry.get('full_truck_price', ''))
            extra_pallets = num_pallets - 34
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
        
        weight_based_cost = self._get_weight_based_price(weight_kg, lane_entry)
        space_based_cost = None
        if loading_meters is not None:
            if is_international:
                space_based_cost = loading_meters * 1500
            else:
                space_based_cost = loading_meters * 800
        if space_based_cost is not None and space_based_cost > weight_based_cost:
            total_cost = space_based_cost
            cost_type = 'space_based'
        else:
            total_cost = weight_based_cost
            cost_type = 'weight_based'
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
        # Ensure all keys are float for safe comparison!
        prices_by_weight = {float(k): v for k, v in lane_entry['prices_by_weight'].items()}
        weight_cluster = self._find_weight_cluster(weight_kg)
        if weight_cluster in prices_by_weight:
            return prices_by_weight[weight_cluster]
        available_clusters = sorted(prices_by_weight.keys())
        for cluster in available_clusters:
            if weight_kg <= cluster:
                return prices_by_weight[cluster]
        if available_clusters:
            return prices_by_weight[available_clusters[-1]]
        return 0.0

    def _find_weight_cluster(self, weight_kg: float) -> float:
        # Ensure all clusters are float
        sorted_clusters = sorted([float(w) for w in self.weight_clusters])
        for cluster in sorted_clusters:
            if weight_kg <= cluster:
                return cluster
        return sorted_clusters[-1] if sorted_clusters else 0

    def _parse_full_truck_price(self, price_str: str) -> float:
        if not price_str or price_str.lower() == 'gem. vereinbarung':
            return 0.0
        try:
            return self._parse_price(price_str) or 0.0
        except:
            return 0.0

    def save_to_json(self, file_path: str):
        data = {
            'weight_clusters': self.weight_clusters,
            'database': self.database
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_json(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Convert clusters to float
        self.weight_clusters = [float(w) for w in data['weight_clusters']]
        self.database = data['database']
        # Patch: fix all prices_by_weight keys to float
        for entry in self.database:
            entry['prices_by_weight'] = {float(k): v for k, v in entry['prices_by_weight'].items()}
        self._build_lane_index()
    
    def get_all_lanes(self) -> List[Dict]:
        return self.database
    
    def get_statistics(self) -> Dict:
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
        filtered = []
        for entry in self.database:
            if origin_country and entry['origin']['country'] != origin_country:
                continue
            if dest_country and entry['destination']['country'] != dest_country:
                continue
            if city:
                city_lower = city.lower()
                origin_city = entry['origin']['city'].lower()
                dest_city = entry['destination']['city'].lower()
                if city_lower not in origin_city and city_lower not in dest_city:
                    continue
            filtered.append(entry)
        return filtered

    def calculate_transport_cost_workflow(self,
        material_weight_per_piece: float,  # kg
        pieces_per_packaging: int,
        packaging_weight: float,  # kg
        daily_demand: int,
        deliveries_per_month: int,
        packaging_units_per_pallet: int,
        pallet_weight: float,  # kg (default 25)
        stackability_factor: float,
        supplier_country: str,
        supplier_zip: str,
        dest_country: str,
        dest_zip: str
    ) -> Dict:
        # STEP 1: Material and Packaging Calculations
        total_material_weight = material_weight_per_piece * pieces_per_packaging
        weight_per_packaging_unit = total_material_weight + packaging_weight
        monthly_demand_per_delivery = (daily_demand * 30) / deliveries_per_month
        packaging_units_per_delivery = monthly_demand_per_delivery / pieces_per_packaging

        # STEP 2: Logistics Unit (Pallet) Calculations
        pallets_needed = math.ceil(packaging_units_per_delivery / packaging_units_per_pallet)
        weight_per_pallet = (packaging_units_per_pallet * weight_per_packaging_unit) + pallet_weight
        total_shipment_weight = pallets_needed * weight_per_pallet
        pallet_footprint = 0.4  # meters
        loading_meters = (pallets_needed / stackability_factor) * pallet_footprint

        # STEP 3: Route Identification
        lane_code = f"{supplier_country}{supplier_zip}{dest_country}{dest_zip}"
        lane_entry = self.find_lane(supplier_country, supplier_zip, dest_country, dest_zip)
        if not lane_entry:
            return {
                'success': False,
                'error': f"No route found for {lane_code}",
                'calculation_details': {
                    'monthly_demand_per_delivery': monthly_demand_per_delivery,
                    'packaging_units_per_delivery': packaging_units_per_delivery,
                    'pallets_needed': pallets_needed,
                    'total_shipment_weight': total_shipment_weight
                }
            }
        is_international = supplier_country != dest_country
        cost_result = self.calculate_transport_cost(
            weight_kg=total_shipment_weight,
            lane_entry=lane_entry,
            loading_meters=loading_meters,
            is_international=is_international,
            num_pallets=pallets_needed
        )
        price_per_piece = cost_result['total_cost'] / monthly_demand_per_delivery if monthly_demand_per_delivery > 0 else 0
        return {
            'success': True,
            'lane_code': lane_code,
            'weight_bracket': cost_result.get('weight_cluster_used'),
            'price_per_delivery': cost_result['total_cost'],
            'price_per_pallet': cost_result['cost_per_pallet'],
            'price_per_piece': price_per_piece,
            'cost_type': cost_result['cost_type'],
            'fuel_surcharge': cost_result.get('fuel_surcharge', 0),
            'calculation_details': {
                # Step 1 results
                'material_weight_per_piece': material_weight_per_piece,
                'pieces_per_packaging': pieces_per_packaging,
                'weight_per_packaging_unit': weight_per_packaging_unit,
                'monthly_demand_per_delivery': monthly_demand_per_delivery,
                'packaging_units_per_delivery': packaging_units_per_delivery,
                # Step 2 results
                'pallets_needed': pallets_needed,
                'weight_per_pallet': weight_per_pallet,
                'total_shipment_weight': total_shipment_weight,
                'loading_meters': loading_meters,
                # Step 3 results
                'route': f"{supplier_country}{supplier_zip} → {dest_country}{dest_zip}",
                # Step 4 results
                'weight_bracket_used': cost_result.get('weight_cluster_used'),
                'base_price': cost_result['total_cost'] - cost_result.get('fuel_surcharge', 0),
                # Additional details from calculate_transport_cost
                'weight_based_cost': cost_result.get('weight_based_cost'),
                'space_based_cost': cost_result.get('space_based_cost')
            }
        }

    def calculate_transport_cost_from_database(
        self,
        supplier_country: str,
        supplier_zip: str,
        dest_country: str,
        dest_zip: str,
        weight_kg: float,
        num_pallets: int,
        loading_meters: float
    ) -> Optional[Dict]:
        lane = self.find_lane(supplier_country, supplier_zip, dest_country, dest_zip)
        if not lane:
            return None
        is_international = supplier_country != dest_country
        return self.calculate_transport_cost(
            weight_kg=weight_kg,
            lane_entry=lane,
            loading_meters=loading_meters,
            is_international=is_international,
            num_pallets=num_pallets
        )
