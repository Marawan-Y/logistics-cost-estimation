"""
Data Manager for Logistics Cost Application

This module handles all data storage, retrieval, and management operations
for materials, suppliers, packaging, transport, warehouse, and all other configurations.
"""

import json
from typing import List, Dict, Any, Optional

class DataManager:
    """
    Manages all application data using session state storage.
    """
    
    def __init__(self):
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables if they don't exist."""
        import streamlit as st
        
        # Core data
        if 'materials' not in st.session_state:
            st.session_state.materials = []
        if 'suppliers' not in st.session_state:
            st.session_state.suppliers = []
        
        # Configuration data
        if 'locations' not in st.session_state:
            st.session_state.locations = []
        if 'operations' not in st.session_state:
            st.session_state.operations = []
        if 'packaging' not in st.session_state:
            st.session_state.packaging = []
        if 'repacking' not in st.session_state:
            st.session_state.repacking = []
        if 'customs' not in st.session_state:
            st.session_state.customs = []
        if 'transport' not in st.session_state:
            st.session_state.transport = []
        if 'co2' not in st.session_state:
            st.session_state.co2 = []
        if 'warehouse' not in st.session_state:
            st.session_state.warehouse = []
        if 'interest' not in st.session_state:
            st.session_state.interest = []
        if 'additional_costs' not in st.session_state:
            st.session_state.additional_costs = []
    
    # Material management
    def add_material(self, material_data: Dict[str, Any]) -> bool:
        """Add a new material to the database."""
        import streamlit as st
        try:
            st.session_state.materials.append(material_data)
            return True
        except Exception:
            return False
    
    def get_materials(self) -> List[Dict[str, Any]]:
        """Get all materials."""
        import streamlit as st
        return st.session_state.materials
    
    def get_material(self, material_no: str) -> Optional[Dict[str, Any]]:
        """Get a specific material by material number."""
        import streamlit as st
        for material in st.session_state.materials:
            if material['material_no'] == material_no:
                return material
        return None
    
    def material_exists(self, material_no: str) -> bool:
        """Check if a material exists."""
        return self.get_material(material_no) is not None
    
    def update_material(self, material_no: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing material."""
        import streamlit as st
        try:
            for i, material in enumerate(st.session_state.materials):
                if material['material_no'] == material_no:
                    st.session_state.materials[i] = updated_data
                    return True
            return False
        except Exception:
            return False
    
    def remove_material(self, material_no: str) -> bool:
        """Remove a material and all associated configurations."""
        import streamlit as st
        try:
            # Remove material
            st.session_state.materials = [
                m for m in st.session_state.materials 
                if m['material_no'] != material_no
            ]
            
            # Remove associated transport configs
            st.session_state.transport = [
                t for t in st.session_state.transport 
                if t.get('material_id') != material_no
            ]
            
            return True
        except Exception:
            return False
    
    # Supplier management
    def add_supplier(self, supplier_data: Dict[str, Any]) -> bool:
        """Add a new supplier to the database."""
        import streamlit as st
        try:
            st.session_state.suppliers.append(supplier_data)
            return True
        except Exception:
            return False
    
    def get_suppliers(self) -> List[Dict[str, Any]]:
        """Get all suppliers."""
        import streamlit as st
        return st.session_state.suppliers
    
    def get_supplier(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific supplier by vendor ID."""
        import streamlit as st
        for supplier in st.session_state.suppliers:
            if supplier['vendor_id'] == vendor_id:
                return supplier
        return None
    
    def supplier_exists(self, vendor_id: str) -> bool:
        """Check if a supplier exists."""
        return self.get_supplier(vendor_id) is not None
    
    def update_supplier(self, vendor_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing supplier."""
        import streamlit as st
        try:
            for i, supplier in enumerate(st.session_state.suppliers):
                if supplier['vendor_id'] == vendor_id:
                    st.session_state.suppliers[i] = updated_data
                    return True
            return False
        except Exception:
            return False
    
    def remove_supplier(self, vendor_id: str) -> bool:
        """Remove a supplier and all associated configurations."""
        import streamlit as st
        try:
            # Remove supplier
            st.session_state.suppliers = [
                s for s in st.session_state.suppliers 
                if s['vendor_id'] != vendor_id
            ]
            
            # Remove associated transport configs
            st.session_state.transport = [
                t for t in st.session_state.transport 
                if t.get('supplier_id') != vendor_id
            ]
            
            return True
        except Exception:
            return False
    
    # Location management
    def add_location(self, location_data: Dict[str, Any]) -> bool:
        """Add a new location."""
        import streamlit as st
        try:
            st.session_state.locations.append(location_data)
            return True
        except Exception:
            return False
    
    def get_locations(self) -> List[Dict[str, Any]]:
        """Get all locations."""
        import streamlit as st
        return st.session_state.locations
    
    def location_exists(self, plant: str) -> bool:
        """Check if a location exists."""
        import streamlit as st
        return any(loc['plant'] == plant for loc in st.session_state.locations)
    
    def update_location(self, plant: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing location."""
        import streamlit as st
        try:
            for i, loc in enumerate(st.session_state.locations):
                if loc['plant'] == plant:
                    st.session_state.locations[i] = updated_data
                    return True
            return False
        except Exception:
            return False
    
    def remove_location(self, plant: str) -> bool:
        """Remove a location."""
        import streamlit as st
        try:
            st.session_state.locations = [
                loc for loc in st.session_state.locations 
                if loc['plant'] != plant
            ]
            return True
        except Exception:
            return False
    
    # Operations management
    def add_operations(self, operations_data: Dict[str, Any]) -> bool:
        """Add new operations configuration."""
        import streamlit as st
        try:
            st.session_state.operations.append(operations_data)
            return True
        except Exception:
            return False
    
    def get_operations(self) -> List[Dict[str, Any]]:
        """Get all operations configurations."""
        import streamlit as st
        return st.session_state.operations
    
    def update_operations(self, index: int, updated_data: Dict[str, Any]) -> bool:
        """Update operations configuration by index."""
        import streamlit as st
        try:
            if 0 <= index < len(st.session_state.operations):
                st.session_state.operations[index] = updated_data
                return True
            return False
        except Exception:
            return False
    
    def remove_operations(self, index: int) -> bool:
        """Remove operations configuration by index."""
        import streamlit as st
        try:
            if 0 <= index < len(st.session_state.operations):
                st.session_state.operations.pop(index)
                return True
            return False
        except Exception:
            return False
    
    # Packaging management
    def add_packaging(self, packaging_data: Dict[str, Any]) -> bool:
        """Add new packaging configuration."""
        import streamlit as st
        try:
            st.session_state.packaging.append(packaging_data)
            return True
        except Exception:
            return False
    
    def get_packaging(self) -> List[Dict[str, Any]]:
        """Get all packaging configurations."""
        import streamlit as st
        return st.session_state.packaging
    
    def update_packaging(self, index: int, updated_data: Dict[str, Any]) -> bool:
        """Update packaging configuration by index."""
        import streamlit as st
        try:
            if 0 <= index < len(st.session_state.packaging):
                st.session_state.packaging[index] = updated_data
                return True
            return False
        except Exception:
            return False
    
    def remove_packaging(self, index: int) -> bool:
        """Remove packaging configuration by index."""
        import streamlit as st
        try:
            if 0 <= index < len(st.session_state.packaging):
                st.session_state.packaging.pop(index)
                return True
            return False
        except Exception:
            return False
    
    # Repacking management
    def add_repacking(self, repacking_data: Dict[str, Any]) -> bool:
        """Add new repacking configuration."""
        import streamlit as st
        try:
            st.session_state.repacking.append(repacking_data)
            return True
        except Exception:
            return False
    
    def get_repacking(self) -> List[Dict[str, Any]]:
        """Get all repacking configurations."""
        import streamlit as st
        return st.session_state.repacking
    
    def update_repacking(self, index: int, updated_data: Dict[str, Any]) -> bool:
        """Update repacking configuration by index."""
        import streamlit as st
        try:
            if 0 <= index < len(st.session_state.repacking):
                st.session_state.repacking[index] = updated_data
                return True
            return False
        except Exception:
            return False
    
    def remove_repacking(self, index: int) -> bool:
        """Remove repacking configuration by index."""
        import streamlit as st
        try:
            if 0 <= index < len(st.session_state.repacking):
                st.session_state.repacking.pop(index)
                return True
            return False
        except Exception:
            return False
    
    # Customs management
    def add_customs(self, customs_data: Dict[str, Any]) -> bool:
        """Add new customs configuration."""
        import streamlit as st
        try:
            st.session_state.customs.append(customs_data)
            return True
        except Exception:
            return False
    
    def get_customs(self) -> List[Dict[str, Any]]:
        """Get all customs configurations."""
        import streamlit as st
        return st.session_state.customs
    
    def customs_exists(self, hs_code: str) -> bool:
        """Check if customs configuration exists for HS code."""
        import streamlit as st
        return any(c['hs_code'] == hs_code for c in st.session_state.customs)
    
    def update_customs(self, hs_code: str, updated_data: Dict[str, Any]) -> bool:
        """Update customs configuration by HS code."""
        import streamlit as st
        try:
            for i, customs in enumerate(st.session_state.customs):
                if customs['hs_code'] == hs_code:
                    st.session_state.customs[i] = updated_data
                    return True
            return False
        except Exception:
            return False
    
    def remove_customs(self, hs_code: str) -> bool:
        """Remove customs configuration by HS code."""
        import streamlit as st
        try:
            st.session_state.customs = [
                c for c in st.session_state.customs 
                if c['hs_code'] != hs_code
            ]
            return True
        except Exception:
            return False
    
    # Transport management (updated for new structure)
    def add_transport(self, transport_data: Dict[str, Any]) -> bool:
        """Add new transport configuration."""
        import streamlit as st
        try:
            st.session_state.transport.append(transport_data)
            return True
        except Exception:
            return False
    
    def get_transport(self) -> List[Dict[str, Any]]:
        """Get all transport configurations."""
        import streamlit as st
        return st.session_state.transport
    
    def transport_exists(self, material_id: str, supplier_id: str) -> bool:
        """Check if transport configuration exists for material-supplier pair."""
        import streamlit as st
        return any(
            t.get('material_id') == material_id and t.get('supplier_id') == supplier_id 
            for t in st.session_state.transport
        )
    
    def remove_transport(self, material_id: str, supplier_id: str) -> bool:
        """Remove transport configuration for material-supplier pair."""
        import streamlit as st
        try:
            st.session_state.transport = [
                t for t in st.session_state.transport 
                if not (t.get('material_id') == material_id and t.get('supplier_id') == supplier_id)
            ]
            return True
        except Exception:
            return False
    
    # CO2 management
    def add_co2(self, co2_data: Dict[str, Any]) -> bool:
        """Add CO2 configuration."""
        import streamlit as st
        try:
            st.session_state.co2.append(co2_data)
            return True
        except Exception:
            return False
    
    def get_co2(self) -> List[Dict[str, Any]]:
        """Get all CO2 configurations."""
        import streamlit as st
        return st.session_state.co2
    
    def co2_exists(self) -> bool:
        """Check if CO2 configuration exists."""
        import streamlit as st
        return len(st.session_state.co2) > 0
    
    def update_co2(self, cost_per_ton: float, updated_data: Dict[str, Any]) -> bool:
        """Update CO2 configuration."""
        import streamlit as st
        try:
            for i, co2 in enumerate(st.session_state.co2):
                if co2['cost_per_ton'] == cost_per_ton:
                    st.session_state.co2[i] = updated_data
                    return True
            return False
        except Exception:
            return False
    
    def remove_co2(self, cost_per_ton: float) -> bool:
        """Remove CO2 configuration."""
        import streamlit as st
        try:
            st.session_state.co2 = [
                c for c in st.session_state.co2 
                if c['cost_per_ton'] != cost_per_ton
            ]
            return True
        except Exception:
            return False
    
    # Warehouse management
    def add_warehouse(self, warehouse_data: Dict[str, Any]) -> bool:
        """Add warehouse configuration."""
        import streamlit as st
        try:
            st.session_state.warehouse.append(warehouse_data)
            return True
        except Exception:
            return False
    
    def get_warehouse(self) -> List[Dict[str, Any]]:
        """Get all warehouse configurations."""
        import streamlit as st
        return st.session_state.warehouse
    
    def warehouse_exists(self) -> bool:
        """Check if warehouse configuration exists."""
        import streamlit as st
        return len(st.session_state.warehouse) > 0
    
    def update_warehouse(self, cost_per_loc: float, updated_data: Dict[str, Any]) -> bool:
        """Update warehouse configuration."""
        import streamlit as st
        try:
            for i, wh in enumerate(st.session_state.warehouse):
                if wh['cost_per_loc'] == cost_per_loc:
                    st.session_state.warehouse[i] = updated_data
                    return True
            return False
        except Exception:
            return False
    
    def remove_warehouse(self, cost_per_loc: float) -> bool:
        """Remove warehouse configuration."""
        import streamlit as st
        try:
            st.session_state.warehouse = [
                w for w in st.session_state.warehouse 
                if w['cost_per_loc'] != cost_per_loc
            ]
            return True
        except Exception:
            return False
    
    # Interest management
    def add_interest(self, interest_data: Dict[str, Any]) -> bool:
        """Add interest configuration."""
        import streamlit as st
        try:
            st.session_state.interest.append(interest_data)
            return True
        except Exception:
            return False
    
    def get_interest(self) -> List[Dict[str, Any]]:
        """Get all interest configurations."""
        import streamlit as st
        return st.session_state.interest
    
    def interest_exists(self) -> bool:
        """Check if interest configuration exists."""
        import streamlit as st
        return len(st.session_state.interest) > 0
    
    def update_interest(self, rate: float, updated_data: Dict[str, Any]) -> bool:
        """Update interest configuration."""
        import streamlit as st
        try:
            for i, intr in enumerate(st.session_state.interest):
                if intr['rate'] == rate:
                    st.session_state.interest[i] = updated_data
                    return True
            return False
        except Exception:
            return False
    
    def remove_interest(self, rate: float) -> bool:
        """Remove interest configuration."""
        import streamlit as st
        try:
            st.session_state.interest = [
                i for i in st.session_state.interest 
                if i['rate'] != rate
            ]
            return True
        except Exception:
            return False
    
    # Additional costs management
    def add_additional_cost(self, cost_data: Dict[str, Any]) -> bool:
        """Add additional cost item."""
        import streamlit as st
        try:
            st.session_state.additional_costs.append(cost_data)
            return True
        except Exception:
            return False
    
    def get_additional_costs(self) -> List[Dict[str, Any]]:
        """Get all additional cost items."""
        import streamlit as st
        return st.session_state.additional_costs
    
    def additional_cost_exists(self, cost_name: str) -> bool:
        """Check if additional cost exists."""
        import streamlit as st
        return any(c['cost_name'] == cost_name for c in st.session_state.additional_costs)
    
    def update_additional_cost(self, cost_name: str, updated_data: Dict[str, Any]) -> bool:
        """Update additional cost item."""
        import streamlit as st
        try:
            for i, cost in enumerate(st.session_state.additional_costs):
                if cost['cost_name'] == cost_name:
                    st.session_state.additional_costs[i] = updated_data
                    return True
            return False
        except Exception:
            return False
    
    def remove_additional_cost(self, cost_name: str) -> bool:
        """Remove additional cost item."""
        import streamlit as st
        try:
            st.session_state.additional_costs = [
                c for c in st.session_state.additional_costs 
                if c['cost_name'] != cost_name
            ]
            return True
        except Exception:
            return False
    
    # Utility methods
    def is_calculation_ready(self) -> bool:
        """Check if all required data is configured for calculations."""
        import streamlit as st
        
        materials = st.session_state.materials
        suppliers = st.session_state.suppliers
        
        # Need at least one material and supplier
        if not (materials and suppliers):
            return False
        
        # Need at least one transport configuration
        transport_configs = st.session_state.transport
        if not transport_configs:
            return False
        
        # Check if at least one complete configuration exists
        for transport in transport_configs:
            material_id = transport.get('material_id')
            supplier_id = transport.get('supplier_id')
            
            # Verify material and supplier exist
            material_exists = any(m['material_no'] == material_id for m in materials)
            supplier_exists = any(s['vendor_id'] == supplier_id for s in suppliers)
            
            if material_exists and supplier_exists:
                return True
        
        return False
    
    def clear_all_data(self) -> bool:
        """Clear all stored data."""
        import streamlit as st
        try:
            st.session_state.materials = []
            st.session_state.suppliers = []
            st.session_state.locations = []
            st.session_state.operations = []
            st.session_state.packaging = []
            st.session_state.repacking = []
            st.session_state.customs = []
            st.session_state.transport = []
            st.session_state.co2 = []
            st.session_state.warehouse = []
            st.session_state.interest = []
            st.session_state.additional_costs = []
            return True
        except Exception:
            return False
    
    def export_configuration(self) -> str:
        """Export all configuration data as JSON string."""
        import streamlit as st
        
        export_data = {
            'materials': st.session_state.materials,
            'suppliers': st.session_state.suppliers,
            'locations': st.session_state.locations,
            'operations': st.session_state.operations,
            'packaging': st.session_state.packaging,
            'repacking': st.session_state.repacking,
            'customs': st.session_state.customs,
            'transport': st.session_state.transport,
            'co2': st.session_state.co2,
            'warehouse': st.session_state.warehouse,
            'interest': st.session_state.interest,
            'additional_costs': st.session_state.additional_costs,
            'export_timestamp': str(__import__('datetime').datetime.now())
        }
        
        return json.dumps(export_data, indent=2, default=str)
    
    def import_configuration(self, json_data: bytes) -> bool:
        """Import configuration data from JSON."""
        import streamlit as st
        
        try:
            # Parse JSON data
            data = json.loads(json_data.decode('utf-8'))
            
            # Import all data types
            st.session_state.materials = data.get('materials', [])
            st.session_state.suppliers = data.get('suppliers', [])
            st.session_state.locations = data.get('locations', [])
            st.session_state.operations = data.get('operations', [])
            st.session_state.packaging = data.get('packaging', [])
            st.session_state.repacking = data.get('repacking', [])
            st.session_state.customs = data.get('customs', [])
            st.session_state.transport = data.get('transport', [])
            st.session_state.co2 = data.get('co2', [])
            st.session_state.warehouse = data.get('warehouse', [])
            st.session_state.interest = data.get('interest', [])
            st.session_state.additional_costs = data.get('additional_costs', [])
            
            return True
            
        except Exception:
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the current configuration."""
        import streamlit as st
        
        stats = {
            'total_materials': len(st.session_state.materials),
            'total_suppliers': len(st.session_state.suppliers),
            'total_locations': len(st.session_state.locations),
            'total_operations': len(st.session_state.operations),
            'total_packaging': len(st.session_state.packaging),
            'total_repacking': len(st.session_state.repacking),
            'total_customs': len(st.session_state.customs),
            'total_transport': len(st.session_state.transport),
            'total_co2': len(st.session_state.co2),
            'total_warehouse': len(st.session_state.warehouse),
            'total_interest': len(st.session_state.interest),
            'total_additional_costs': len(st.session_state.additional_costs),
            'calculation_ready': self.is_calculation_ready()
        }
        
        # Calculate complete configurations
        complete_configs = 0
        if st.session_state.transport:
            for transport in st.session_state.transport:
                material_id = transport.get('material_id')
                supplier_id = transport.get('supplier_id')
                
                material_exists = any(m['material_no'] == material_id for m in st.session_state.materials)
                supplier_exists = any(s['vendor_id'] == supplier_id for s in st.session_state.suppliers)
                
                if material_exists and supplier_exists:
                    complete_configs += 1
        
        stats['complete_configurations'] = complete_configs
        return stats