"""
Data Manager for Logistics Cost Application

This module handles all data storage, retrieval, and management operations
for materials, suppliers, packaging, transport, and warehouse configurations.
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
        
        if 'materials' not in st.session_state:
            st.session_state.materials = []
        if 'suppliers' not in st.session_state:
            st.session_state.suppliers = []
        if 'packaging_configs' not in st.session_state:
            st.session_state.packaging_configs = []
        if 'transport_configs' not in st.session_state:
            st.session_state.transport_configs = []
        if 'warehouse_configs' not in st.session_state:
            st.session_state.warehouse_configs = []
    
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
            
            # Remove associated configurations
            st.session_state.packaging_configs = [
                p for p in st.session_state.packaging_configs 
                if p['material_id'] != material_no
            ]
            st.session_state.transport_configs = [
                t for t in st.session_state.transport_configs 
                if t['material_id'] != material_no
            ]
            st.session_state.warehouse_configs = [
                w for w in st.session_state.warehouse_configs 
                if w['material_id'] != material_no
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
            
            # Remove associated configurations
            st.session_state.packaging_configs = [
                p for p in st.session_state.packaging_configs 
                if p['supplier_id'] != vendor_id
            ]
            st.session_state.transport_configs = [
                t for t in st.session_state.transport_configs 
                if t['supplier_id'] != vendor_id
            ]
            st.session_state.warehouse_configs = [
                w for w in st.session_state.warehouse_configs 
                if w['supplier_id'] != vendor_id
            ]
            
            return True
        except Exception:
            return False
    
    # Packaging configuration management
    def add_packaging(self, packaging_data: Dict[str, Any]) -> bool:
        """Add a new packaging configuration."""
        import streamlit as st
        try:
            st.session_state.packaging_configs.append(packaging_data)
            return True
        except Exception:
            return False
    
    def get_packaging(self) -> List[Dict[str, Any]]:
        """Get all packaging configurations."""
        import streamlit as st
        return st.session_state.packaging_configs
    
    def get_packaging_config(self, material_id: str, supplier_id: str) -> Optional[Dict[str, Any]]:
        """Get packaging configuration for a specific material-supplier combination."""
        import streamlit as st
        for config in st.session_state.packaging_configs:
            if config['material_id'] == material_id and config['supplier_id'] == supplier_id:
                return config
        return None
    
    def packaging_exists(self, material_id: str, supplier_id: str) -> bool:
        """Check if packaging configuration exists for a material-supplier combination."""
        return self.get_packaging_config(material_id, supplier_id) is not None
    
    def update_packaging(self, material_id: str, supplier_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing packaging configuration."""
        import streamlit as st
        try:
            for i, config in enumerate(st.session_state.packaging_configs):
                if config['material_id'] == material_id and config['supplier_id'] == supplier_id:
                    st.session_state.packaging_configs[i] = updated_data
                    return True
            return False
        except Exception:
            return False
    
    def remove_packaging(self, material_id: str, supplier_id: str) -> bool:
        """Remove a packaging configuration."""
        import streamlit as st
        try:
            st.session_state.packaging_configs = [
                p for p in st.session_state.packaging_configs 
                if not (p['material_id'] == material_id and p['supplier_id'] == supplier_id)
            ]
            return True
        except Exception:
            return False
    
    # Transport configuration management
    def add_transport(self, transport_data: Dict[str, Any]) -> bool:
        """Add a new transport configuration."""
        import streamlit as st
        try:
            st.session_state.transport_configs.append(transport_data)
            return True
        except Exception:
            return False
    
    def get_transport(self) -> List[Dict[str, Any]]:
        """Get all transport configurations."""
        import streamlit as st
        return st.session_state.transport_configs
    
    def get_transport_config(self, material_id: str, supplier_id: str) -> Optional[Dict[str, Any]]:
        """Get transport configuration for a specific material-supplier combination."""
        import streamlit as st
        for config in st.session_state.transport_configs:
            if config['material_id'] == material_id and config['supplier_id'] == supplier_id:
                return config
        return None
    
    def transport_exists(self, material_id: str, supplier_id: str) -> bool:
        """Check if transport configuration exists for a material-supplier combination."""
        return self.get_transport_config(material_id, supplier_id) is not None
    
    def update_transport(self, material_id: str, supplier_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing transport configuration."""
        import streamlit as st
        try:
            for i, config in enumerate(st.session_state.transport_configs):
                if config['material_id'] == material_id and config['supplier_id'] == supplier_id:
                    st.session_state.transport_configs[i] = updated_data
                    return True
            return False
        except Exception:
            return False
    
    def remove_transport(self, material_id: str, supplier_id: str) -> bool:
        """Remove a transport configuration."""
        import streamlit as st
        try:
            st.session_state.transport_configs = [
                t for t in st.session_state.transport_configs 
                if not (t['material_id'] == material_id and t['supplier_id'] == supplier_id)
            ]
            return True
        except Exception:
            return False
    
    # Warehouse configuration management
    def add_warehouse(self, warehouse_data: Dict[str, Any]) -> bool:
        """Add a new warehouse configuration."""
        import streamlit as st
        try:
            st.session_state.warehouse_configs.append(warehouse_data)
            return True
        except Exception:
            return False
    
    def get_warehouse(self) -> List[Dict[str, Any]]:
        """Get all warehouse configurations."""
        import streamlit as st
        return st.session_state.warehouse_configs
    
    def get_warehouse_config(self, material_id: str, supplier_id: str) -> Optional[Dict[str, Any]]:
        """Get warehouse configuration for a specific material-supplier combination."""
        import streamlit as st
        for config in st.session_state.warehouse_configs:
            if config['material_id'] == material_id and config['supplier_id'] == supplier_id:
                return config
        return None
    
    def warehouse_exists(self, material_id: str, supplier_id: str) -> bool:
        """Check if warehouse configuration exists for a material-supplier combination."""
        return self.get_warehouse_config(material_id, supplier_id) is not None
    
    def update_warehouse(self, material_id: str, supplier_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing warehouse configuration."""
        import streamlit as st
        try:
            for i, config in enumerate(st.session_state.warehouse_configs):
                if config['material_id'] == material_id and config['supplier_id'] == supplier_id:
                    st.session_state.warehouse_configs[i] = updated_data
                    return True
            return False
        except Exception:
            return False
    
    def remove_warehouse(self, material_id: str, supplier_id: str) -> bool:
        """Remove a warehouse configuration."""
        import streamlit as st
        try:
            st.session_state.warehouse_configs = [
                w for w in st.session_state.warehouse_configs 
                if not (w['material_id'] == material_id and w['supplier_id'] == supplier_id)
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
        packaging_configs = st.session_state.packaging_configs
        transport_configs = st.session_state.transport_configs
        warehouse_configs = st.session_state.warehouse_configs
        
        if not (materials and suppliers and packaging_configs and transport_configs and warehouse_configs):
            return False
        
        # Check if at least one complete configuration exists
        for material in materials:
            for supplier in suppliers:
                has_packaging = any(
                    p['material_id'] == material['material_no'] and p['supplier_id'] == supplier['vendor_id']
                    for p in packaging_configs
                )
                has_transport = any(
                    t['material_id'] == material['material_no'] and t['supplier_id'] == supplier['vendor_id']
                    for t in transport_configs
                )
                has_warehouse = any(
                    w['material_id'] == material['material_no'] and w['supplier_id'] == supplier['vendor_id']
                    for w in warehouse_configs
                )
                
                if has_packaging and has_transport and has_warehouse:
                    return True
        
        return False
    
    def clear_all_data(self) -> bool:
        """Clear all stored data."""
        import streamlit as st
        try:
            st.session_state.materials = []
            st.session_state.suppliers = []
            st.session_state.packaging_configs = []
            st.session_state.transport_configs = []
            st.session_state.warehouse_configs = []
            return True
        except Exception:
            return False
    
    def export_configuration(self) -> str:
        """Export all configuration data as JSON string."""
        import streamlit as st
        
        export_data = {
            'materials': st.session_state.materials,
            'suppliers': st.session_state.suppliers,
            'packaging_configs': st.session_state.packaging_configs,
            'transport_configs': st.session_state.transport_configs,
            'warehouse_configs': st.session_state.warehouse_configs,
            'export_timestamp': str(__import__('datetime').datetime.now())
        }
        
        return json.dumps(export_data, indent=2, default=str)
    
    def import_configuration(self, json_data: bytes) -> bool:
        """Import configuration data from JSON."""
        import streamlit as st
        
        try:
            # Parse JSON data
            data = json.loads(json_data.decode('utf-8'))
            
            # Validate required keys
            required_keys = ['materials', 'suppliers', 'packaging_configs', 'transport_configs', 'warehouse_configs']
            if not all(key in data for key in required_keys):
                return False
            
            # Import data
            st.session_state.materials = data['materials']
            st.session_state.suppliers = data['suppliers']
            st.session_state.packaging_configs = data['packaging_configs']
            st.session_state.transport_configs = data['transport_configs']
            st.session_state.warehouse_configs = data['warehouse_configs']
            
            return True
            
        except Exception:
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the current configuration."""
        import streamlit as st
        
        stats = {
            'total_materials': len(st.session_state.materials),
            'total_suppliers': len(st.session_state.suppliers),
            'total_packaging_configs': len(st.session_state.packaging_configs),
            'total_transport_configs': len(st.session_state.transport_configs),
            'total_warehouse_configs': len(st.session_state.warehouse_configs),
            'calculation_ready': self.is_calculation_ready()
        }
        
        # Calculate complete configurations
        complete_configs = 0
        for material in st.session_state.materials:
            for supplier in st.session_state.suppliers:
                has_packaging = any(
                    p['material_id'] == material['material_no'] and p['supplier_id'] == supplier['vendor_id']
                    for p in st.session_state.packaging_configs
                )
                has_transport = any(
                    t['material_id'] == material['material_no'] and t['supplier_id'] == supplier['vendor_id']
                    for t in st.session_state.transport_configs
                )
                has_warehouse = any(
                    w['material_id'] == material['material_no'] and w['supplier_id'] == supplier['vendor_id']
                    for w in st.session_state.warehouse_configs
                )
                
                if has_packaging and has_transport and has_warehouse:
                    complete_configs += 1
        
        stats['complete_configurations'] = complete_configs
        return stats
