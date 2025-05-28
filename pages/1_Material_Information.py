import streamlit as st
from utils.validators import MaterialValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Material Information", page_icon="📦")

def main():
    st.title("📦 Material Information")
    st.markdown("Configure material details for logistics cost calculation")
    st.markdown("---")
    
    # Initialize data manager
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    data_manager = st.session_state.data_manager
    validator = MaterialValidator()
    
    # Material form
    with st.form("material_form"):
        st.subheader("Add New Material")
        
        col1, col2 = st.columns(2)
        
        with col1:
            material_no = st.text_input(
                "Material Number *",
                help="Unique identifier for the material"
            )
            
            material_desc = st.text_input(
                "Material Description *",
                help="Name or description of the material"
            )
            
            weight_per_pcs = st.number_input(
                "Weight per piece (kg) *",
                min_value=0.0,
                step=0.001,
                format="%.3f",
                help="Weight of each individual piece"
            )
            
            annual_volume = st.number_input(
                "Annual Volume (average) *",
                min_value=0,
                step=1,
                help="Average annual demand in pieces"
            )
        
        with col2:
            lifetime_volume = st.number_input(
                "Lifetime Volume",
                min_value=0,
                step=1,
                help="Total volume over the material's lifetime"
            )
            
            sop_year = st.number_input(
                "Start of Production (SOP) Year",
                min_value=2020,
                max_value=2050,
                value=2024,
                help="Year when production starts"
            )
            
            material_value = st.number_input(
                "Material Value per piece (€)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Value of each piece for inventory calculations"
            )
            
            hs_code = st.text_input(
                "HS Code",
                help="Harmonized System code for customs classification"
            )
        
        submitted = st.form_submit_button("Add Material", type="primary")
        
        if submitted:
            # Validate input
            material_data = {
                'material_no': material_no,
                'material_desc': material_desc,
                'weight_per_pcs': weight_per_pcs,
                'annual_volume': annual_volume,
                'lifetime_volume': lifetime_volume,
                'sop_year': sop_year,
                'material_value': material_value,
                'hs_code': hs_code
            }
            
            validation_result = validator.validate_material(material_data)
            
            if validation_result['is_valid']:
                # Check if material already exists
                if data_manager.material_exists(material_no):
                    st.error(f"Material {material_no} already exists. Use the edit function to modify it.")
                else:
                    data_manager.add_material(material_data)
                    st.success(f"Material {material_no} added successfully!")
                    st.rerun()
            else:
                for error in validation_result['errors']:
                    st.error(error)
    
    st.markdown("---")
    
    # Display existing materials
    st.subheader("Existing Materials")
    materials = data_manager.get_materials()
    
    if materials:
        for i, material in enumerate(materials):
            with st.expander(f"{material['material_no']} - {material['material_desc']}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Weight per piece:** {material['weight_per_pcs']:.3f} kg")
                    st.write(f"**Annual Volume:** {material['annual_volume']:,} pieces")
                    st.write(f"**Lifetime Volume:** {material.get('lifetime_volume', 'N/A'):,} pieces" if material.get('lifetime_volume') else "**Lifetime Volume:** Not specified")
                    st.write(f"**SOP Year:** {material.get('sop_year', 'N/A')}")
                    st.write(f"**Material Value:** €{material.get('material_value', 0):.2f}")
                    if material.get('hs_code'):
                        st.write(f"**HS Code:** {material['hs_code']}")
                
                with col2:
                    if st.button("Edit", key=f"edit_{i}"):
                        st.session_state[f'edit_material_{i}'] = True
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"delete_{i}", type="secondary"):
                        data_manager.remove_material(material['material_no'])
                        st.success("Material deleted successfully!")
                        st.rerun()
        
        # Edit material functionality
        for i, material in enumerate(materials):
            if st.session_state.get(f'edit_material_{i}', False):
                with st.form(f"edit_form_{i}"):
                    st.subheader(f"Edit Material: {material['material_no']}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_desc = st.text_input(
                            "Material Description",
                            value=material['material_desc']
                        )
                        
                        new_weight = st.number_input(
                            "Weight per piece (kg)",
                            value=material['weight_per_pcs'],
                            min_value=0.0,
                            step=0.001,
                            format="%.3f"
                        )
                        
                        new_annual_volume = st.number_input(
                            "Annual Volume",
                            value=material['annual_volume'],
                            min_value=0,
                            step=1
                        )
                    
                    with col2:
                        new_lifetime_volume = st.number_input(
                            "Lifetime Volume",
                            value=material.get('lifetime_volume', 0),
                            min_value=0,
                            step=1
                        )
                        
                        new_sop_year = st.number_input(
                            "SOP Year",
                            value=material.get('sop_year', 2024),
                            min_value=2020,
                            max_value=2050
                        )
                        
                        new_material_value = st.number_input(
                            "Material Value per piece (€)",
                            value=material.get('material_value', 0.0),
                            min_value=0.0,
                            step=0.01,
                            format="%.2f"
                        )
                        
                        new_hs_code = st.text_input(
                            "HS Code",
                            value=material.get('hs_code', '')
                        )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update Material", type="primary"):
                            updated_material = {
                                'material_no': material['material_no'],
                                'material_desc': new_desc,
                                'weight_per_pcs': new_weight,
                                'annual_volume': new_annual_volume,
                                'lifetime_volume': new_lifetime_volume,
                                'sop_year': new_sop_year,
                                'material_value': new_material_value,
                                'hs_code': new_hs_code
                            }
                            
                            validation_result = validator.validate_material(updated_material)
                            
                            if validation_result['is_valid']:
                                data_manager.update_material(material['material_no'], updated_material)
                                st.success("Material updated successfully!")
                                st.session_state[f'edit_material_{i}'] = False
                                st.rerun()
                            else:
                                for error in validation_result['errors']:
                                    st.error(error)
                    
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f'edit_material_{i}'] = False
                            st.rerun()
    else:
        st.info("No materials configured yet. Add your first material using the form above.")

if __name__ == "__main__":
    main()
