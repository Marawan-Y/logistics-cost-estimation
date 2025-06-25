"""
Data Manager for Logistics Cost Application

Stores all configurations in Streamlit session_state.
"""

import json
from typing import List, Dict, Any, Optional

class DataManager:
    """
    Manages application data via streamlit.session_state.
    """

    def __init__(self):
        self._initialize_session_state()

    def _initialize_session_state(self):
        import streamlit as st
        defaults = {
            'materials': [],
            'suppliers': [],
            'locations': [],
            'operations': [],
            'packaging': [],
            'repacking': [],
            'customs': [],
            'transport': [],
            'co2': [],
            'warehouse': [],
            'interest': [],
            'additional_costs': []
        }
        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val

    # --- Material ----------------------------------------------------------------

    def add_material(self, material_data: Dict[str, Any]) -> bool:
        import streamlit as st
        st.session_state.materials.append(material_data)
        return True

    def get_materials(self) -> List[Dict[str, Any]]:
        import streamlit as st
        return st.session_state.materials

    def get_material(self, material_no: str) -> Optional[Dict[str, Any]]:
        return next((m for m in self.get_materials() if m['material_no'] == material_no), None)

    def material_exists(self, material_no: str) -> bool:
        return self.get_material(material_no) is not None

    def update_material(self, material_no: str, updated: Dict[str, Any]) -> bool:
        import streamlit as st
        for i, m in enumerate(st.session_state.materials):
            if m['material_no'] == material_no:
                st.session_state.materials[i] = updated
                return True
        return False

    def remove_material(self, material_no: str) -> bool:
        import streamlit as st
        st.session_state.materials = [m for m in st.session_state.materials if m['material_no'] != material_no]
        # also remove dependent configs
        keys = ['packaging', 'transport', 'warehouse']
        for k in keys:
            st.session_state[k] = [
                cfg for cfg in st.session_state[k]
                if cfg.get('material_id') != material_no
            ]
        return True

    # --- Supplier ----------------------------------------------------------------

    def add_supplier(self, supplier_data: Dict[str, Any]) -> bool:
        import streamlit as st
        st.session_state.suppliers.append(supplier_data)
        return True

    def get_suppliers(self) -> List[Dict[str, Any]]:
        import streamlit as st
        return st.session_state.suppliers

    def get_supplier(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        return next((s for s in self.get_suppliers() if s['vendor_id'] == vendor_id), None)

    def supplier_exists(self, vendor_id: str) -> bool:
        return self.get_supplier(vendor_id) is not None

    def update_supplier(self, vendor_id: str, updated: Dict[str, Any]) -> bool:
        import streamlit as st
        for i, s in enumerate(st.session_state.suppliers):
            if s['vendor_id'] == vendor_id:
                st.session_state.suppliers[i] = updated
                return True
        return False

    def remove_supplier(self, vendor_id: str) -> bool:
        import streamlit as st
        st.session_state.suppliers = [s for s in st.session_state.suppliers if s['vendor_id'] != vendor_id]
        keys = ['packaging', 'transport', 'warehouse']
        for k in keys:
            st.session_state[k] = [
                cfg for cfg in st.session_state[k]
                if cfg.get('supplier_id') != vendor_id
            ]
        return True

    # --- Generic add/get/remove for configs that must include material_id & supplier_id ---

    def add_packaging(self, packaging_data: Dict[str, Any]) -> bool:
        """
        packaging_data must include:
          - material_id
          - supplier_id
          plus all user inputs and sheet placeholders
        """
        import streamlit as st
        st.session_state.packaging.append(packaging_data)
        return True

    def get_packaging(self) -> List[Dict[str, Any]]:
        import streamlit as st
        return st.session_state.packaging

    def update_packaging(self, index: int, updated: Dict[str, Any]) -> bool:
        import streamlit as st
        if 0 <= index < len(st.session_state.packaging):
            st.session_state.packaging[index] = updated
            return True
        return False

    def remove_packaging(self, index: int) -> bool:
        import streamlit as st
        if 0 <= index < len(st.session_state.packaging):
            st.session_state.packaging.pop(index)
            return True
        return False

    def add_transport(self, transport_data: Dict[str, Any]) -> bool:
        import streamlit as st
        st.session_state.transport.append(transport_data)
        return True

    def get_transport(self) -> List[Dict[str, Any]]:
        import streamlit as st
        return st.session_state.transport

    def update_transport(self, index: int, updated: Dict[str, Any]) -> bool:
        import streamlit as st
        if 0 <= index < len(st.session_state.transport):
            st.session_state.transport[index] = updated
            return True
        return False

    def remove_transport(self, index: int) -> bool:
        import streamlit as st
        if 0 <= index < len(st.session_state.transport):
            st.session_state.transport.pop(index)
            return True
        return False

    def add_warehouse(self, warehouse_data: Dict[str, Any]) -> bool:
        import streamlit as st
        st.session_state.warehouse.append(warehouse_data)
        return True

    def get_warehouse(self) -> List[Dict[str, Any]]:
        import streamlit as st
        return st.session_state.warehouse

    def update_warehouse(self, index: int, updated: Dict[str, Any]) -> bool:
        import streamlit as st
        if 0 <= index < len(st.session_state.warehouse):
            st.session_state.warehouse[index] = updated
            return True
        return False

    def remove_warehouse(self, index: int) -> bool:
        import streamlit as st
        if 0 <= index < len(st.session_state.warehouse):
            st.session_state.warehouse.pop(index)
            return True
        return False

    # --- Other config managers (unchanged) --------------------------------------

    def add_repacking(self, data): ...
    def get_repacking(self): ...
    def update_repacking(self, idx, data): ...
    def remove_repacking(self, idx): ...

    def add_customs(self, data): ...
    def get_customs(self): ...
    def update_customs(self, idx, data): ...
    def remove_customs(self, idx): ...

    def add_co2(self, data): ...
    def get_co2(self): ...
    def update_co2(self, idx, data): ...
    def remove_co2(self, idx): ...

    def add_interest(self, data): ...
    def get_interest(self): ...
    def update_interest(self, idx, data): ...
    def remove_interest(self, idx): ...

    def add_additional_cost(self, data): ...
    def get_additional_costs(self): ...
    def update_additional_cost(self, idx, data): ...
    def remove_additional_cost(self, idx): ...

    # --- Export / import -------------------------------------------------------

    def export_configuration(self) -> str:
        import streamlit as st
        cfg = {k: st.session_state[k] for k in st.session_state.keys()}
        return json.dumps(cfg, default=str, indent=2)

    def import_configuration(self, raw: bytes) -> bool:
        import streamlit as st
        data = json.loads(raw.decode())
        for k, v in data.items():
            st.session_state[k] = v
        return True
