import streamlit as st
from utils.validators import PackagingValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Packaging Costs", page_icon="📦")

def main():
    st.title("📦 Packaging Costs")
    st.markdown("Configure packaging parameters and cost calculations")
    st.markdown("---")
    
    # Initialize data manager
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    data_manager = st.session_state.data_manager
    validator = PackagingValidator()
    
    # Get available materials and suppliers for selection
    materials = data_manager.get_materials()
    suppliers = data_manager.get_suppliers()
    
    if not materials:
        st.warning("⚠️ No materials configured. Please add materials in the Material Information page first.")
        return
    
    if not suppliers:
        st.warning("⚠️ No suppliers configured. Please add suppliers in the Supplier Information page first.")
        return
    
    # Packaging type options
    PACKAGING_TYPES = [
        "KLT - Small Load Carrier",
        "GLT - Large Load Carrier", 
        "Cardboard Box",
        "Plastic Container",
        "Pallet",
        "Custom Packaging"
    ]
    
    # Packaging form
    with st.form("packaging_form"):
        st.subheader("Add New Packaging Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Material selection
            material_options = [f"{m['material_no']} - {m['material_desc']}" for m in materials]
            selected_material = st.selectbox(
                "Material *",
                options=material_options,
                help="Select the material this packaging configuration applies to"
            )
            
            # Supplier selection
            supplier_options = [f"{s['vendor_id']} - {s['vendor_name']}" for s in suppliers]
            selected_supplier = st.selectbox(
                "Supplier *",
                options=supplier_options,
                help="Select the supplier for this packaging configuration"
            )
            
            packaging_type = st.selectbox(
                "Packaging Type *",
                options=PACKAGING_TYPES,
                help="Type of packaging container used"
            )
            
            filling_degree = st.number_input(
                "Filling Degree (pieces per box) *",
                min_value=1,
                step=1,
                help="Number of pieces that fit in one packaging unit"
            )
        
        with col2:
            packaging_cost_per_part = st.number_input(
                "Packaging Cost per Part (€) *",
                min_value=0.0,
                step=0.001,
                format="%.3f",
                help="Cost of packaging material per individual part"
            )
            
            tooling_cost = st.number_input(
                "Tooling Cost (€)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="One-time cost for tooling/fixtures required for packaging"
            )
            
            loop_time_days = st.number_input(
                "Loop Time (days)",
                min_value=1,
                value=30,
                help="Time in days for packaging loop cycle"
            )
            
            scrap_rate = st.number_input(
                "Scrap Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=2.0,
                step=0.1,
                format="%.1f",
                help="Expected scrap rate as percentage"
            )
        
        # Advanced packaging parameters
        st.subheader("Advanced Parameters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            plant_cost = st.number_input(
                "Plant Cost (€)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Fixed plant costs associated with packaging"
            )
            
            coc_cost = st.number_input(
                "CoC Cost (€)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Certificate of Compliance costs"
            )
        
        with col2:
            maintenance_cost = st.number_input(
                "Maintenance Cost (€)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Ongoing maintenance costs for packaging equipment"
            )
            
            packaging_weight = st.number_input(
                "Packaging Weight (kg)",
                min_value=0.0,
                step=0.001,
                format="%.3f",
                help="Weight of empty packaging material"
            )
        
        with col3:
            reusable = st.checkbox(
                "Reusable Packaging",
                help="Check if packaging can be reused multiple times"
            )
            
            return_cost = st.number_input(
                "Return Cost per Unit (€)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Cost to return empty packaging (if reusable)"
            )
        
        packaging_notes = st.text_area(
            "Notes",
            help="Additional notes about this packaging configuration"
        )
        
        submitted = st.form_submit_button("Add Packaging Configuration", type="primary")
        
        if submitted:
            # Extract material and supplier IDs
            material_id = selected_material.split(' - ')[0]
            supplier_id = selected_supplier.split(' - ')[0]
            
            # Validate input
            packaging_data = {
                'material_id': material_id,
                'supplier_id': supplier_id,
                'packaging_type': packaging_type.split(' - ')[0] if ' - ' in packaging_type else packaging_type,
                'packaging_type_description': packaging_type,
                'filling_degree': filling_degree,
                'packaging_cost_per_part': packaging_cost_per_part,
                'tooling_cost': tooling_cost,
                'loop_time_days': loop_time_days,
                'scrap_rate': scrap_rate,
                'plant_cost': plant_cost,
                'coc_cost': coc_cost,
                'maintenance_cost': maintenance_cost,
                'packaging_weight': packaging_weight,
                'reusable': reusable,
                'return_cost': return_cost,
                'notes': packaging_notes
            }
            
            validation_result = validator.validate_packaging(packaging_data)
            
            if validation_result['is_valid']:
                # Check if packaging configuration already exists for this material-supplier combination
                if data_manager.packaging_exists(material_id, supplier_id):
                    st.error(f"Packaging configuration for material {material_id} and supplier {supplier_id} already exists. Use the edit function to modify it.")
                else:
                    data_manager.add_packaging(packaging_data)
                    st.success(f"Packaging configuration added successfully!")
                    st.rerun()
            else:
                for error in validation_result['errors']:
                    st.error(error)
    
    st.markdown("---")
    
    # Display existing packaging configurations
    st.subheader("Existing Packaging Configurations")
    packaging_configs = data_manager.get_packaging()
    
    if packaging_configs:
        for i, config in enumerate(packaging_configs):
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
            
            with st.expander(f"{material_name} | {supplier_name}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Packaging Type:** {config.get('packaging_type_description', config['packaging_type'])}")
                    st.write(f"**Filling Degree:** {config['filling_degree']} pieces per box")
                    st.write(f"**Cost per Part:** €{config['packaging_cost_per_part']:.3f}")
                    st.write(f"**Tooling Cost:** €{config['tooling_cost']:.2f}")
                    st.write(f"**Loop Time:** {config['loop_time_days']} days")
                    st.write(f"**Scrap Rate:** {config['scrap_rate']:.1f}%")
                    
                    if config.get('plant_cost', 0) > 0:
                        st.write(f"**Plant Cost:** €{config['plant_cost']:.2f}")
                    if config.get('coc_cost', 0) > 0:
                        st.write(f"**CoC Cost:** €{config['coc_cost']:.2f}")
                    if config.get('maintenance_cost', 0) > 0:
                        st.write(f"**Maintenance Cost:** €{config['maintenance_cost']:.2f}")
                    if config.get('packaging_weight', 0) > 0:
                        st.write(f"**Packaging Weight:** {config['packaging_weight']:.3f} kg")
                    
                    if config.get('reusable', False):
                        st.write(f"**Reusable:** Yes (Return cost: €{config.get('return_cost', 0):.2f})")
                    
                    if config.get('notes'):
                        st.write(f"**Notes:** {config['notes']}")
                
                with col2:
                    if st.button("Edit", key=f"edit_packaging_{i}"):
                        st.session_state[f'edit_packaging_{i}'] = True
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"delete_packaging_{i}", type="secondary"):
                        data_manager.remove_packaging(config['material_id'], config['supplier_id'])
                        st.success("Packaging configuration deleted successfully!")
                        st.rerun()
        
        # Calculate packaging summary
        st.markdown("---")
        st.subheader("Packaging Summary")
        
        total_configs = len(packaging_configs)
        avg_cost_per_part = sum(config['packaging_cost_per_part'] for config in packaging_configs) / total_configs if total_configs > 0 else 0
        total_tooling_cost = sum(config['tooling_cost'] for config in packaging_configs)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Configurations", total_configs)
        with col2:
            st.metric("Average Cost per Part", f"€{avg_cost_per_part:.3f}")
        with col3:
            st.metric("Total Tooling Cost", f"€{total_tooling_cost:.2f}")
        
    else:
        st.info("No packaging configurations yet. Add your first packaging configuration using the form above.")

if __name__ == "__main__":
    main()
