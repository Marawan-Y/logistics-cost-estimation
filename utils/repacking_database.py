# utils/repacking_database.py
"""
Repacking Database Manager

This module handles the repacking cost database, providing functionality to:
1. Load repacking cost data from static tables or JSON files
2. Manage CRUD operations for repacking cost configurations
3. Support import/export functionality
"""

import json
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
import streamlit as st
from .repacking_table import PACKAGING_OPERATION_COSTS


class RepackingDatabase:
    """
    Manages the repacking cost database and provides CRUD functionality.
    """

    def __init__(self):
        self.operation_costs = {}
        self._load_default_data()

    def _load_default_data(self):
        """Load default data from repacking_table.py"""
        self.operation_costs = PACKAGING_OPERATION_COSTS.copy()

    def load_from_json(self, file_path: str):
        """Load repacking data from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.operation_costs = data.get('operation_costs', {})
            
        except FileNotFoundError:
            # If file doesn't exist, use default data
            self._load_default_data()
        except Exception as e:
            st.error(f"Error loading repacking database: {e}")
            self._load_default_data()

    def save_to_json(self, file_path: str):
        """Save repacking data to JSON file."""
        data = {
            'operation_costs': self.operation_costs,
            'metadata': {
                'save_timestamp': pd.Timestamp.now().isoformat(),
                'version': '1.0.0'
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_weight_category(self, weight_category: str, operations_list: List[Dict]):
        """Add or update weight category with operations."""
        self.operation_costs[weight_category] = operations_list

    def remove_weight_category(self, weight_category: str):
        """Remove weight category."""
        if weight_category in self.operation_costs:
            del self.operation_costs[weight_category]

    def add_operation_to_category(self, weight_category: str, operation_data: Dict):
        """Add operation to existing weight category."""
        if weight_category not in self.operation_costs:
            self.operation_costs[weight_category] = []
        
        self.operation_costs[weight_category].append(operation_data)

    def remove_operation_from_category(self, weight_category: str, operation_index: int):
        """Remove specific operation from weight category."""
        if weight_category in self.operation_costs:
            if 0 <= operation_index < len(self.operation_costs[weight_category]):
                self.operation_costs[weight_category].pop(operation_index)

    def get_weight_categories(self):
        """Get all weight categories."""
        return list(self.operation_costs.keys())

    def get_operations_for_category(self, weight_category: str):
        """Get all operations for a weight category."""
        return self.operation_costs.get(weight_category, [])

    def get_statistics(self):
        """Get statistics about the repacking database."""
        total_operations = sum(len(ops) for ops in self.operation_costs.values())
        return {
            'weight_categories': len(self.operation_costs),
            'total_operations': total_operations,
            'categories': list(self.operation_costs.keys())
        }

    def search_operations(self, search_term: str):
        """Search for operations by packaging type or operation type."""
        results = {}
        search_term = search_term.lower()
        
        for weight_category, operations in self.operation_costs.items():
            matching_operations = []
            for op in operations:
                if (search_term in op.get('supplier_packaging', '').lower() or
                    search_term in op.get('kb_packaging', '').lower() or
                    search_term in op.get('operation_type', '').lower()):
                    matching_operations.append(op)
            
            if matching_operations:
                results[weight_category] = matching_operations
        
        return results

    def reset_to_defaults(self):
        """Reset database to default values."""
        self._load_default_data()

    def get_operation_cost(self, weight_category: str, supplier_packaging: str, kb_packaging: str):
        """Get operation cost for specific combination."""
        operations = self.get_operations_for_category(weight_category)
        
        for op in operations:
            if (op.get('supplier_packaging') == supplier_packaging and 
                op.get('kb_packaging') == kb_packaging):
                return op
        
        return None