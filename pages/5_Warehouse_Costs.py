import streamlit as st
from utils.validators import WarehouseValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Warehouse Costs", page_icon="🏪")

def main():
    st.title("🏪 Warehouse Costs")
    st.markdown("Configure warehouse storage, inventory, and handling costs")
    st.markdown("---")
    
    # Initialize data manager
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    data_manager = st.session_state.data_manager
    validator = WarehouseValidator()
    
    # Get available materials and suppliers for selection
    materials = data_manager.get_materials()
    suppliers = data_manager.get_suppliers()
    
    if not materials:
        st.warning("⚠️ No materials configured. Please add materials in the Material Information page first.")
        return
    
    if not suppliers:
        st.warning("⚠️ No suppliers configured. Please add suppliers in the Supplier Information page first.")
        return
    
    # Storage types
    STORAGE_TYPES = [
        "Standard Rack",
        "High Bay Storage",
        "Floor Storage",
        "Climate Controlled",
        "Hazardous Material Storage",
        "Automated Storage"
    ]
    
    # Warehouse form
    with st.form("warehouse_form"):
        st.subheader("Add New Warehouse Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Material selection
            material_options = [f"{m['material_no']} - {m['material_desc']}" for m in materials]
            selected_material = st.selectbox(
                "Material *",
                options=material_options,
                help="Select the material this warehouse configuration applies to"
            )
            
            # Supplier selection
            supplier_options = [f"{s['vendor_id']} - {s['vendor_name']}" for s in suppliers]
            selected_supplier = st.selectbox(
                "Supplier *",
                options=supplier_options,
                help="Select the supplier for this warehouse configuration"
            )
            
            storage_type = st.selectbox(
                "Storage Type *",
                options=STORAGE_TYPES,
                help="Type of storage used for this material"
            )
            
            storage_locations = st.number_input(
                "Number of Storage Locations *",
                min_value=1,
                value=1,
                step=1,
                help="Number of storage locations/bins required"
            )
        
        with col2:
            safety_stock_pallets = st.number_input(
                "Safety Stock (pallets) *",
                min_value=0,
                step=1,
                help="Number of pallets required for safety stock"
            )
            
            warehouse_cost_per_piece = st.number_input(
                "Warehouse Cost per Piece (€) *",
                min_value=0.0,
                step=0.001,
                format="%.3f",
                help="Storage cost per piece per year"
            )
            
            pieces_per_pallet = st.number_input(
                "Pieces per Pallet",
                min_value=1,
                value=100,
                step=1,
                help="Number of pieces that fit on one pallet"
            )
            
            storage_days = st.number_input(
                "Average Storage Days",
                min_value=1,
                value=30,
                step=1,
                help="Average number of days material is stored"
            )
        
        # Inventory and financial parameters
        st.subheader("Inventory & Financial Parameters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            inventory_interest_rate = st.number_input(
                "Inventory Interest Rate (%/year)",
                min_value=0.0,
                max_value=50.0,
                value=5.0,
                step=0.1,
                format="%.1f",
                help="Annual interest rate for inventory holding costs"
            )
            
            handling_cost_in = st.number_input(
                "Handling Cost In (€/pallet)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Cost to handle material into warehouse per pallet"
            )
        
        with col2:
            handling_cost_out = st.number_input(
                "Handling Cost Out (€/pallet)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Cost to handle material out of warehouse per pallet"
            )
            
            storage_cost_per_pallet_day = st.number_input(
                "Storage Cost per Pallet per Day (€)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Daily storage cost per pallet"
            )
        
        with col3:
            obsolescence_rate = st.number_input(
                "Obsolescence Rate (%/year)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                format="%.1f",
                help="Annual rate of material obsolescence"
            )
            
            damage_rate = st.number_input(
                "Damage Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                format="%.1f",
                help="Percentage of material damaged during storage"
            )
        
        # Warehouse facility parameters
        st.subheader("Facility Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            temperature_controlled = st.checkbox(
                "Temperature Controlled",
                help="Check if materials require temperature-controlled storage"
            )
            
            humidity_controlled = st.checkbox(
                "Humidity Controlled",
                help="Check if materials require humidity-controlled storage"
            )
            
            security_level = st.selectbox(
                "Security Level",
                options=["Standard", "High", "Maximum"],
                help="Required security level for stored materials"
            )
        
        with col2:
            hazmat_classification = st.text_input(
                "Hazmat Classification",
                help="Hazardous material classification if applicable"
            )
            
            special_equipment = st.text_input(
                "Special Equipment Required",
                help="Any special equipment needed for handling"
            )
            
            certification_required = st.text_input(
                "Certifications Required",
                help="Any certifications required for storage facility"
            )
        
        warehouse_notes = st.text_area(
            "Notes",
            help="Additional notes about this warehouse configuration"
        )
        
        submitted = st.form_submit_button("Add Warehouse Configuration", type="primary")
        
        if submitted:
            # Extract material and supplier IDs
            material_id = selected_material.split(' - ')[0]
            supplier_id = selected_supplier.split(' - ')[0]
            
            # Validate input
            warehouse_data = {
                'material_id': material_id,
                'supplier_id': supplier_id,
                'storage_type': storage_type,
                'storage_locations': storage_locations,
                'safety_stock_pallets': safety_stock_pallets,
                'warehouse_cost_per_piece': warehouse_cost_per_piece,
                'pieces_per_pallet': pieces_per_pallet,
                'storage_days': storage_days,
                'inventory_interest_rate': inventory_interest_rate,
                'handling_cost_in': handling_cost_in,
                'handling_cost_out': handling_cost_out,
                'storage_cost_per_pallet_day': storage_cost_per_pallet_day,
                'obsolescence_rate': obsolescence_rate,
                'damage_rate': damage_rate,
                'temperature_controlled': temperature_controlled,
                'humidity_controlled': humidity_controlled,
                'security_level': security_level,
                'hazmat_classification': hazmat_classification,
                'special_equipment': special_equipment,
                'certification_required': certification_required,
                'notes': warehouse_notes
            }
            
            validation_result = validator.validate_warehouse(warehouse_data)
            
            if validation_result['is_valid']:
                # Check if warehouse configuration already exists for this material-supplier combination
                if data_manager.warehouse_exists(material_id, supplier_id):
                    st.error(f"Warehouse configuration for material {material_id} and supplier {supplier_id} already exists. Use the edit function to modify it.")
                else:
                    data_manager.add_warehouse(warehouse_data)
                    st.success(f"Warehouse configuration added successfully!")
                    st.rerun()
            else:
                for error in validation_result['errors']:
                    st.error(error)
    
    st.markdown("---")
    
    # Display existing warehouse configurations
    st.subheader("Existing Warehouse Configurations")
    warehouse_configs = data_manager.get_warehouse()
    
    if warehouse_configs:
        for i, config in enumerate(warehouse_configs):
            # Get material and supplier names for display
            material_name = "Unknown"
            supplier_name = "Unknown"
            
            for material in materials:
                if material['material_no'] == config['material_id']:
                    material_name = f"{material['material_no']} - {material['material_desc']}"
                    break
            
            for supplier in suppliers:
                if supplier['vendor_id'] == config['supplier_id']:
                    supplier_name = f"{supplier['vendor_id']} - {supplier['vendor_name']}"
                    break
            
            with st.expander(f"{material_name} | {supplier_name} | {config['storage_type']}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Storage Type:** {config['storage_type']}")
                    st.write(f"**Storage Locations:** {config['storage_locations']}")
                    st.write(f"**Safety Stock:** {config['safety_stock_pallets']} pallets")
                    st.write(f"**Cost per Piece:** €{config['warehouse_cost_per_piece']:.3f}")
                    st.write(f"**Pieces per Pallet:** {config['pieces_per_pallet']}")
                    st.write(f"**Storage Days:** {config['storage_days']}")
                    
                    # Financial parameters
                    st.write(f"**Interest Rate:** {config['inventory_interest_rate']:.1f}%/year")
                    if config.get('handling_cost_in', 0) > 0:
                        st.write(f"**Handling Cost In:** €{config['handling_cost_in']:.2f}/pallet")
                    if config.get('handling_cost_out', 0) > 0:
                        st.write(f"**Handling Cost Out:** €{config['handling_cost_out']:.2f}/pallet")
                    if config.get('storage_cost_per_pallet_day', 0) > 0:
                        st.write(f"**Storage Cost:** €{config['storage_cost_per_pallet_day']:.2f}/pallet/day")
                    
                    # Risk factors
                    if config.get('obsolescence_rate', 0) > 0:
                        st.write(f"**Obsolescence Rate:** {config['obsolescence_rate']:.1f}%/year")
                    if config.get('damage_rate', 0) > 0:
                        st.write(f"**Damage Rate:** {config['damage_rate']:.1f}%")
                    
                    # Special requirements
                    special_reqs = []
                    if config.get('temperature_controlled', False):
                        special_reqs.append("Temperature Controlled")
                    if config.get('humidity_controlled', False):
                        special_reqs.append("Humidity Controlled")
                    if special_reqs:
                        st.write(f"**Special Requirements:** {', '.join(special_reqs)}")
                    
                    st.write(f"**Security Level:** {config['security_level']}")
                    
                    if config.get('hazmat_classification'):
                        st.write(f"**Hazmat Classification:** {config['hazmat_classification']}")
                    if config.get('special_equipment'):
                        st.write(f"**Special Equipment:** {config['special_equipment']}")
                    if config.get('certification_required'):
                        st.write(f"**Certifications:** {config['certification_required']}")
                    
                    if config.get('notes'):
                        st.write(f"**Notes:** {config['notes']}")
                
                with col2:
                    if st.button("Edit", key=f"edit_warehouse_{i}"):
                        st.session_state[f'edit_warehouse_{i}'] = True
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"delete_warehouse_{i}", type="secondary"):
                        data_manager.remove_warehouse(config['material_id'], config['supplier_id'])
                        st.success("Warehouse configuration deleted successfully!")
                        st.rerun()
        
        # Calculate warehouse summary
        st.markdown("---")
        st.subheader("Warehouse Summary")
        
        total_configs = len(warehouse_configs)
        total_storage_locations = sum(config['storage_locations'] for config in warehouse_configs)
        total_safety_stock = sum(config['safety_stock_pallets'] for config in warehouse_configs)
        avg_cost_per_piece = sum(config['warehouse_cost_per_piece'] for config in warehouse_configs) / total_configs if total_configs > 0 else 0
        avg_interest_rate = sum(config['inventory_interest_rate'] for config in warehouse_configs) / total_configs if total_configs > 0 else 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Configurations", total_configs)
        with col2:
            st.metric("Total Storage Locations", total_storage_locations)
        with col3:
            st.metric("Total Safety Stock", f"{total_safety_stock} pallets")
        with col4:
            st.metric("Average Cost per Piece", f"€{avg_cost_per_piece:.3f}")
        with col5:
            st.metric("Average Interest Rate", f"{avg_interest_rate:.1f}%")
        
    else:
        st.info("No warehouse configurations yet. Add your first warehouse configuration using the form above.")

if __name__ == "__main__":
    main()
