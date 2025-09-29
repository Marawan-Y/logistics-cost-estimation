"""
Data Manager for Logistics Cost Application

This module handles all data storage, retrieval, and management operations
for materials, suppliers, packaging, transport, warehouse, and all other configurations.
Now includes persistent storage using JSON files.
Location data is now part of supplier information.
"""
import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class DataManager:
    """
    Manages all application data using session state storage with JSON file persistence.
    """
    
    def __init__(self):
        self.data_file = Path("logistics_data.json")
        self.backup_dir = Path("backups")
        self.auto_save = True
        self._initialize_session_state()
        self._load_data_on_startup()
    
    def _initialize_session_state(self):
        """Initialize session state variables if they don't exist."""
        
        # Core data
        if 'materials' not in st.session_state:
            st.session_state.materials = []
        if 'suppliers' not in st.session_state:
            st.session_state.suppliers = []
        
        # Configuration data (locations removed - now in supplier)
        if 'operations' not in st.session_state:
            st.session_state.operations = []
        if 'packaging' not in st.session_state:
            st.session_state.packaging = []
        if 'repacking' not in st.session_state:
            st.session_state.repacking = []
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
        
        # Settings
        if 'auto_save' not in st.session_state:
            st.session_state.auto_save = True
        if 'last_save_time' not in st.session_state:
            st.session_state.last_save_time = None
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
    
    def _load_data_on_startup(self):
        """Load data from file on application startup"""
        if not st.session_state.data_loaded and self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._populate_session_state(data)
                st.session_state.data_loaded = True
                st.session_state.last_save_time = datetime.fromtimestamp(
                    os.path.getmtime(self.data_file)
                )
            except Exception as e:
                st.error(f"Error loading saved data: {e}")
                self._backup_corrupted_file()
    
    def _populate_session_state(self, data: Dict[str, Any]):
        """Populate session state with loaded data"""
        st.session_state.materials = data.get('materials', [])
        st.session_state.suppliers = data.get('suppliers', [])
        # locations removed - now in supplier
        st.session_state.operations = data.get('operations', [])
        st.session_state.packaging = data.get('packaging', [])
        st.session_state.repacking = data.get('repacking', [])
        st.session_state.transport = data.get('transport', [])
        st.session_state.co2 = data.get('co2', [])
        st.session_state.warehouse = data.get('warehouse', [])
        st.session_state.interest = data.get('interest', [])
        st.session_state.additional_costs = data.get('additional_costs', [])
        
        # Load settings if available
        if 'settings' in data:
            settings = data['settings']
            st.session_state.auto_save = settings.get('auto_save', True)
    
    def _get_all_data(self) -> Dict[str, Any]:
        """Get all session state data for saving"""
        return {
            'materials': st.session_state.materials,
            'suppliers': st.session_state.suppliers,
            # locations removed
            'operations': st.session_state.operations,
            'packaging': st.session_state.packaging,
            'repacking': st.session_state.repacking,
            'transport': st.session_state.transport,
            'co2': st.session_state.co2,
            'warehouse': st.session_state.warehouse,
            'interest': st.session_state.interest,
            'additional_costs': st.session_state.additional_costs,
            'settings': {
                'auto_save': st.session_state.auto_save,
            },
            'metadata': {
                'save_timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            }
        }
    
    def _save_data_automatically(self):
        """Save data to file automatically after changes"""
        if not st.session_state.get('auto_save', True):
            return
        
        try:
            # Create backup directory if it doesn't exist
            self.backup_dir.mkdir(exist_ok=True)
            
            # Create backup of current file if it exists
            if self.data_file.exists():
                backup_file = self.backup_dir / f"logistics_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                import shutil
                shutil.copy2(self.data_file, backup_file)
                
                # Keep only last 10 backups
                self._cleanup_old_backups()
            
            # Save current data
            export_data = self._get_all_data()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
            
            st.session_state.last_save_time = datetime.now()
            
        except Exception as e:
            st.error(f"Error saving data: {e}")
    
    def _cleanup_old_backups(self):
        """Keep only the last 10 backup files"""
        try:
            backup_files = list(self.backup_dir.glob("logistics_data_backup_*.json"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups (keep last 10)
            for old_backup in backup_files[10:]:
                old_backup.unlink()
        except Exception:
            pass  # Ignore cleanup errors
    
    def _backup_corrupted_file(self):
        """Create backup of corrupted file"""
        try:
            self.backup_dir.mkdir(exist_ok=True)
            corrupted_backup = self.backup_dir / f"corrupted_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import shutil
            shutil.copy2(self.data_file, corrupted_backup)
        except Exception:
            pass
    
    def manual_save(self) -> bool:
        """Manually save data - always saves regardless of auto_save setting"""
        try:
            original_auto_save = st.session_state.auto_save
            st.session_state.auto_save = True
            self._save_data_automatically()
            st.session_state.auto_save = original_auto_save
            return True
        except Exception:
            return False
    
    def get_save_status(self) -> Dict[str, Any]:
        """Get information about save status"""
        return {
            'file_exists': self.data_file.exists(),
            'last_save_time': st.session_state.last_save_time,
            'auto_save_enabled': st.session_state.auto_save,
            'file_size': self.data_file.stat().st_size if self.data_file.exists() else 0,
            'backup_count': len(list(self.backup_dir.glob("*.json"))) if self.backup_dir.exists() else 0
        }
    
    # Material management
    def add_material(self, material_data: Dict[str, Any]) -> bool:
        """Add a new material to the database."""
        try:
            st.session_state.materials.append(material_data)
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    def get_materials(self) -> List[Dict[str, Any]]:
        """Get all materials."""
        return st.session_state.materials
    
    def get_material(self, material_no: str) -> Optional[Dict[str, Any]]:
        """Get a specific material by material number."""
        for material in st.session_state.materials:
            if material['material_no'] == material_no:
                return material
        return None
    
    def material_exists(self, material_no: str) -> bool:
        """Check if a material exists."""
        return self.get_material(material_no) is not None
    
    def update_material(self, material_no: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing material."""
        try:
            for i, material in enumerate(st.session_state.materials):
                if material['material_no'] == material_no:
                    st.session_state.materials[i] = updated_data
                    self._save_data_automatically()
                    return True
            return False
        except Exception:
            return False
    
    def remove_material(self, material_no: str) -> bool:
        """Remove a material and all associated configurations."""
        try:
            st.session_state.materials = [
                m for m in st.session_state.materials 
                if m['material_no'] != material_no
            ]
            
            st.session_state.packaging = [
                p for p in st.session_state.packaging 
                if p.get('material_id') != material_no
            ]
            st.session_state.transport = [
                t for t in st.session_state.transport 
                if t.get('material_id') != material_no
            ]
            
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    # Supplier management (now includes location data)
    def add_supplier(self, supplier_data: Dict[str, Any]) -> bool:
        """Add a new supplier to the database."""
        try:
            st.session_state.suppliers.append(supplier_data)
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    def get_suppliers(self) -> List[Dict[str, Any]]:
        """Get all suppliers."""
        return st.session_state.suppliers
    
    def get_supplier(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific supplier by vendor ID."""
        for supplier in st.session_state.suppliers:
            if supplier['vendor_id'] == vendor_id:
                return supplier
        return None
    
    def supplier_exists(self, vendor_id: str) -> bool:
        """Check if a supplier exists."""
        return self.get_supplier(vendor_id) is not None
    
    def update_supplier(self, vendor_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing supplier."""
        try:
            for i, supplier in enumerate(st.session_state.suppliers):
                if supplier['vendor_id'] == vendor_id:
                    st.session_state.suppliers[i] = updated_data
                    self._save_data_automatically()
                    return True
            return False
        except Exception:
            return False
    
    def remove_supplier(self, vendor_id: str) -> bool:
        """Remove a supplier and all associated configurations."""
        try:
            st.session_state.suppliers = [
                s for s in st.session_state.suppliers 
                if s['vendor_id'] != vendor_id
            ]
            
            st.session_state.packaging = [
                p for p in st.session_state.packaging 
                if p.get('supplier_id') != vendor_id
            ]
            st.session_state.transport = [
                t for t in st.session_state.transport 
                if t.get('supplier_id') != vendor_id
            ]
            
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    # Operations management
    def add_operations(self, operations_data: Dict[str, Any]) -> bool:
        """Add new operations configuration."""
        try:
            st.session_state.operations.append(operations_data)
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    def get_operations(self) -> List[Dict[str, Any]]:
        """Get all operations configurations."""
        return st.session_state.operations
    
    def update_operations(self, index: int, updated_data: Dict[str, Any]) -> bool:
        """Update operations configuration by index."""
        try:
            if 0 <= index < len(st.session_state.operations):
                st.session_state.operations[index] = updated_data
                self._save_data_automatically()
                return True
            return False
        except Exception:
            return False
    
    def remove_operations(self, index: int) -> bool:
        """Remove operations configuration by index."""
        try:
            if 0 <= index < len(st.session_state.operations):
                st.session_state.operations.pop(index)
                self._save_data_automatically()
                return True
            return False
        except Exception:
            return False
    
    # Packaging management
    def add_packaging(self, packaging_data: Dict[str, Any]) -> bool:
        """Add new packaging configuration."""
        try:
            st.session_state.packaging.append(packaging_data)
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    def get_packaging(self) -> List[Dict[str, Any]]:
        """Get all packaging configurations."""
        return st.session_state.packaging
    
    def update_packaging(self, index: int, updated_data: Dict[str, Any]) -> bool:
        """Update packaging configuration by index."""
        try:
            if 0 <= index < len(st.session_state.packaging):
                st.session_state.packaging[index] = updated_data
                self._save_data_automatically()
                return True
            return False
        except Exception:
            return False
    
    def remove_packaging(self, index: int) -> bool:
        """Remove packaging configuration by index."""
        try:
            if 0 <= index < len(st.session_state.packaging):
                st.session_state.packaging.pop(index)
                self._save_data_automatically()
                return True
            return False
        except Exception:
            return False
    
    # Repacking management
    def add_repacking(self, repacking_data: Dict[str, Any]) -> bool:
        """Add new repacking configuration."""
        try:
            st.session_state.repacking.append(repacking_data)
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    def get_repacking(self) -> List[Dict[str, Any]]:
        """Get all repacking configurations."""
        return st.session_state.repacking
    
    def update_repacking(self, index: int, updated_data: Dict[str, Any]) -> bool:
        """Update repacking configuration by index."""
        try:
            if 0 <= index < len(st.session_state.repacking):
                st.session_state.repacking[index] = updated_data
                self._save_data_automatically()
                return True
            return False
        except Exception:
            return False
    
    def remove_repacking(self, index: int) -> bool:
        """Remove repacking configuration by index."""
        try:
            if 0 <= index < len(st.session_state.repacking):
                st.session_state.repacking.pop(index)
                self._save_data_automatically()
                return True
            return False
        except Exception:
            return False
    
    # Transport management
    def add_transport(self, transport_data: Dict[str, Any]) -> bool:
        """Add new transport configuration."""
        try:
            st.session_state.transport.append(transport_data)
            self._save_data_automatically()
            return True
        except Exception:
            return False

    def get_transport(self) -> List[Dict[str, Any]]:
        """Get all transport configurations."""
        return st.session_state.transport

    def transport_exists(self, key: str) -> bool:
        """Check if transport configuration exists by its unique key."""
        return any(t.get('key') == key for t in st.session_state.transport)

    def update_transport(self, old_key: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing transport configuration identified by old_key."""
        try:
            for i, t in enumerate(st.session_state.transport):
                if t.get('key') == old_key:
                    st.session_state.transport[i] = updated_data
                    self._save_data_automatically()
                    return True
            return False
        except Exception:
            return False

    def remove_transport(self, key: str) -> bool:
        """Remove transport configuration by its unique key."""
        try:
            st.session_state.transport = [
                t for t in st.session_state.transport 
                if t.get('key') != key
            ]
            self._save_data_automatically()
            return True
        except Exception:
            return False

    def get_transport_database_path(self) -> Path:
        """Get the path for transport database file"""
        return Path("transport_database.json")

    def has_transport_database(self) -> bool:
        """Check if transport database exists"""
        return self.get_transport_database_path().exists()

    def get_transport_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the transport database"""
        try:
            from utils.transport_database import TransportDatabase
            db = TransportDatabase()
            db.load_from_json(str(self.get_transport_database_path()))
            return db.get_statistics()
        except Exception:
            return {
                'total_lanes': 0,
                'weight_clusters': 0,
                'countries': [],
                'exists': False
            }

    def backup_transport_database(self) -> bool:
        """Create backup of transport database"""
        try:
            db_path = self.get_transport_database_path()
            if db_path.exists():
                backup_file = self.backup_dir / f"transport_database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                import shutil
                shutil.copy2(db_path, backup_file)
                return True
        except Exception:
            return False

    # CO2 management
    def add_co2(self, co2_data: Dict[str, Any]) -> bool:
        """Add CO2 configuration - now supports multiple configurations."""
        try:
            st.session_state.co2.append(co2_data)
            self._save_data_automatically()
            return True
        except Exception:
            return False
        
    def get_co2(self) -> List[Dict[str, Any]]:
        """Get all CO2 configurations."""
        return st.session_state.co2

    def co2_exists(self) -> bool:
        """Check if CO2 configuration exists - now checks if any exist."""
        return len(st.session_state.co2) > 0

    def update_co2_by_index(self, index: int, updated_data: Dict[str, Any]) -> bool:
        """Update CO2 configuration by index."""
        try:
            if 0 <= index < len(st.session_state.co2):
                st.session_state.co2[index] = updated_data
                self._save_data_automatically()
                return True
            return False
        except Exception:
            return False

    def remove_co2_by_index(self, index: int) -> bool:
        """Remove CO2 configuration by index."""
        try:
            if 0 <= index < len(st.session_state.co2):
                st.session_state.co2.pop(index)
                self._save_data_automatically()
                return True
            return False
        except Exception:
            return False

    # Backward compatibility methods
    def update_co2(self, cost_per_ton: float, updated_data: Dict[str, Any]) -> bool:
        """Update CO2 configuration by cost_per_ton - kept for backward compatibility."""
        try:
            for i, co2 in enumerate(st.session_state.co2):
                if co2['cost_per_ton'] == cost_per_ton:
                    st.session_state.co2[i] = updated_data
                    self._save_data_automatically()
                    return True
            return False
        except Exception:
            return False

    def remove_co2(self, cost_per_ton: float) -> bool:
        """Remove CO2 configuration by cost_per_ton - kept for backward compatibility."""
        try:
            st.session_state.co2 = [
                c for c in st.session_state.co2 
                if c['cost_per_ton'] != cost_per_ton
            ]
            self._save_data_automatically()
            return True
        except Exception:
            return False

    # Warehouse management
    def add_warehouse(self, warehouse_data: Dict[str, Any]) -> bool:
        """Add warehouse configuration."""
        try:
            st.session_state.warehouse.append(warehouse_data)
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    def get_warehouse(self) -> List[Dict[str, Any]]:
        """Get all warehouse configurations."""
        return st.session_state.warehouse
    
    def warehouse_exists(self) -> bool:
        """Check if warehouse configuration exists."""
        return len(st.session_state.warehouse) > 0
    
    def update_warehouse(self, cost_per_loc: float, updated_data: Dict[str, Any]) -> bool:
        """Update warehouse configuration."""
        try:
            for i, wh in enumerate(st.session_state.warehouse):
                if wh['cost_per_loc'] == cost_per_loc:
                    st.session_state.warehouse[i] = updated_data
                    self._save_data_automatically()
                    return True
            return False
        except Exception:
            return False
    
    def remove_warehouse(self, cost_per_loc: float) -> bool:
        """Remove warehouse configuration."""
        try:
            st.session_state.warehouse = [
                w for w in st.session_state.warehouse 
                if w['cost_per_loc'] != cost_per_loc
            ]
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    # Interest management
    def add_interest(self, interest_data: Dict[str, Any]) -> bool:
        """Add interest configuration."""
        try:
            st.session_state.interest.append(interest_data)
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    def get_interest(self) -> List[Dict[str, Any]]:
        """Get all interest configurations."""
        return st.session_state.interest
    
    def interest_exists(self) -> bool:
        """Check if interest configuration exists."""
        return len(st.session_state.interest) > 0
    
    def update_interest(self, rate: float, updated_data: Dict[str, Any]) -> bool:
        """Update interest configuration."""
        try:
            for i, intr in enumerate(st.session_state.interest):
                if intr['rate'] == rate:
                    st.session_state.interest[i] = updated_data
                    self._save_data_automatically()
                    return True
            return False
        except Exception:
            return False
    
    def remove_interest(self, rate: float) -> bool:
        """Remove interest configuration."""
        try:
            st.session_state.interest = [
                i for i in st.session_state.interest 
                if i['rate'] != rate
            ]
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    # Additional costs management
    def add_additional_cost(self, cost_data: Dict[str, Any]) -> bool:
        """Add additional cost item."""
        try:
            st.session_state.additional_costs.append(cost_data)
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    def get_additional_costs(self) -> List[Dict[str, Any]]:
        """Get all additional cost items."""
        return st.session_state.additional_costs
    
    def additional_cost_exists(self, cost_name: str) -> bool:
        """Check if additional cost exists."""
        return any(c['cost_name'] == cost_name for c in st.session_state.additional_costs)
    
    def update_additional_cost(self, cost_name: str, updated_data: Dict[str, Any]) -> bool:
        """Update additional cost item."""
        try:
            for i, cost in enumerate(st.session_state.additional_costs):
                if cost['cost_name'] == cost_name:
                    st.session_state.additional_costs[i] = updated_data
                    self._save_data_automatically()
                    return True
            return False
        except Exception:
            return False
    
    def remove_additional_cost(self, cost_name: str) -> bool:
        """Remove additional cost item."""
        try:
            st.session_state.additional_costs = [
                c for c in st.session_state.additional_costs 
                if c['cost_name'] != cost_name
            ]
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    # Database management methods
    def get_packaging_database_path(self) -> Path:
        """Get the path for packaging database file"""
        return Path("packaging_database.json")

    def has_packaging_database(self) -> bool:
        """Check if packaging database exists"""
        return self.get_packaging_database_path().exists()

    def get_repacking_database_path(self) -> Path:
        """Get the path for repacking database file"""
        return Path("repacking_database.json")

    def has_repacking_database(self) -> bool:
        """Check if repacking database exists"""
        return self.get_repacking_database_path().exists()
    
    def get_supplier_database_path(self) -> Path:
        """Get the path for supplier database file"""
        return Path("supplier_database.json")

    def has_supplier_database(self) -> bool:
        """Check if supplier database exists"""
        return self.get_supplier_database_path().exists()
    
    # Utility methods
    def is_calculation_ready(self) -> bool:
        """Check if all required data is configured for calculations."""
        materials = st.session_state.materials
        suppliers = st.session_state.suppliers
        
        # Need at least one material and supplier
        if not (materials and suppliers):
            return False
        
        # Need at least basic configurations
        packaging_configs = st.session_state.packaging
        transport_configs = st.session_state.transport
        warehouse_configs = st.session_state.warehouse
        co2_configs = st.session_state.co2
        
        # Check if minimum required configs exist
        if not (packaging_configs and transport_configs and warehouse_configs and co2_configs):
            return False
        
        return True
    
    def get_material_supplier_pairs(self) -> List[Dict[str, Any]]:
        """Get all possible material-supplier pairs with their configurations."""
        pairs = []
        
        for material in st.session_state.materials:
            for supplier in st.session_state.suppliers:
                pair = {
                    'material': material,
                    'supplier': supplier,
                    'pair_id': f"{material['material_no']}_{supplier['vendor_id']}",
                    'display_name': f"{material['material_no']} - {material['material_desc']} | {supplier['vendor_id']} - {supplier['vendor_name']}"
                }
                pairs.append(pair)
        
        return pairs
    
    def clear_all_data(self) -> bool:
        """Clear all stored data."""
        try:
            st.session_state.materials = []
            st.session_state.suppliers = []
            # locations removed
            st.session_state.operations = []
            st.session_state.packaging = []
            st.session_state.repacking = []
            st.session_state.transport = []
            st.session_state.co2 = []
            st.session_state.warehouse = []
            st.session_state.interest = []
            st.session_state.additional_costs = []
            self._save_data_automatically()
            return True
        except Exception:
            return False
    
    def export_configuration(self) -> str:
        """Export all configuration data as JSON string."""
        export_data = self._get_all_data()
        return json.dumps(export_data, indent=2, default=str)
    
    def import_configuration(self, json_data: bytes) -> bool:
        """Import configuration data from JSON."""
        try:
            # Parse JSON data
            data = json.loads(json_data.decode('utf-8'))
            
            # Import all data types
            self._populate_session_state(data)
            self._save_data_automatically()
            return True
            
        except Exception:
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the current configuration."""
        stats = {
            'total_materials': len(st.session_state.materials),
            'total_suppliers': len(st.session_state.suppliers),
            # locations removed
            'total_operations': len(st.session_state.operations),
            'total_packaging': len(st.session_state.packaging),
            'total_repacking': len(st.session_state.repacking),
            'total_transport': len(st.session_state.transport),
            'total_co2': len(st.session_state.co2),
            'total_warehouse': len(st.session_state.warehouse),
            'total_interest': len(st.session_state.interest),
            'total_additional_costs': len(st.session_state.additional_costs),
            'calculation_ready': self.is_calculation_ready(),
            'save_status': self.get_save_status()
        }
        
        return stats