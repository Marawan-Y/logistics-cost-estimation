import streamlit as st
from utils.validators import MaterialValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Material Information", page_icon="📦")

def main():
    st.title("Material Information")
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
            project_name = st.text_input(
                "Project Name *",
                help="Name of the overall project this material belongs to"
            )
            
            material_no = st.text_input(
                "Material Number *",
                help="Unique identifier for the material"
            )
            
            material_desc = st.text_input(
                "Material Description *",
                help="Name or description of the material"
            )

            weight_per_pcs = st.number_input(
                "Weight per pcs (kg) *",
                min_value=0.0,
                step=0.001,
                format="%.3f",
                help="Weight of each individual piece"
            )

            usage = st.text_input(
                "Usage",
                help="Describe the intended usage for this material"
            )

            daily_demand = st.number_input(
                "Daily demand (average)",
                min_value=0.0,
                step=0.01,
                help="Average daily demand (pcs)"
            )

            annual_volume = st.number_input(
                "Annual volume (average) *",
                min_value=0,
                step=1,
                help="Average annual demand in pieces"
            )

        with col2:
            lifetime_volume = st.number_input(
                "Lifetime (volume)",
                min_value=0.0,
                step=0.1,
                help="Expected lifetime of the material"
            )

            peak_year = st.text_input(
                "Peak year",
                help="Indicate the year with the highest demand/volume"
            )

            peak_year_volume = st.number_input(
                "Peak year volume",
                min_value=0,
                step=1,
                help="Volume for the peak year (pcs)"
            )

            working_days = st.number_input(
                "Working Days per year",
                min_value=0,
                step=1,
                help="Number of working days per year"
            )

            sop = st.text_input(
                "SOP",
                help="Start of Production (date or code)"
            )

            Pcs_Price = st.number_input(
                "Pcs_Price",
                min_value=0.0,
                step=0.01,
                help="Material Price / Piece"
            )

        submitted = st.form_submit_button("Add Material", type="primary")
        
        if submitted:
            # Validate input
            material_data = {
                'project_name': project_name,
                'material_no': material_no,
                'material_desc': material_desc,
                'weight_per_pcs': weight_per_pcs,
                'usage': usage,
                'daily_demand': daily_demand,
                'annual_volume': annual_volume,
                'lifetime_volume': lifetime_volume,
                'peak_year': peak_year,
                'peak_year_volume': peak_year_volume,
                'working_days': working_days,
                'sop': sop,
                'Pcs_Price': Pcs_Price
            }
            
            validation_result = validator.validate_material(material_data)
            
            if validation_result['is_valid']:
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
            with st.expander(f"{material.get('material_no', '')} - {material.get('material_desc', '')}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Project Name:** {material.get('project_name', 'N/A')}")
                    st.write(f"**Weight per pcs:** {material.get('weight_per_pcs', 0):.3f} kg")
                    st.write(f"**Annual volume:** {material.get('annual_volume', 0):,} pcs")
                    st.write(f"**Lifetime (years):** {material.get('lifetime_volume', 'N/A')}")
                    st.write(f"**Peak year:** {material.get('peak_year', 'N/A')}")
                    st.write(f"**Peak year volume:** {material.get('peak_year_volume', 'N/A')}")
                    st.write(f"**Working Days/year:** {material.get('working_days', 'N/A')}")
                    st.write(f"**SOP:** {material.get('sop', 'N/A')}")
                    st.write(f"**Usage:** {material.get('usage', 'N/A')}")
                    st.write(f"**Daily demand:** {material.get('daily_demand', 'N/A')} pcs")
                    st.write(f"**Pcs_Price:** {material.get('Pcs_Price', 'N/A')} €")               
                with col2:
                    if st.button("Edit", key=f"edit_{i}"):
                        st.session_state[f'edit_material_{i}'] = True
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"delete_{i}", type="secondary"):
                        data_manager.remove_material(material.get('material_no', ''))
                        st.success("Material deleted successfully!")
                        st.rerun()
        
        # Edit material functionality
        for i, material in enumerate(materials):
            if st.session_state.get(f'edit_material_{i}', False):
                with st.form(f"edit_form_{i}"):
                    st.subheader(f"Edit Material: {material.get('material_no', '')}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_project_name = st.text_input(
                            "Project Name",
                            value=material.get('project_name', '')
                        )
                        new_desc = st.text_input(
                            "Material Description",
                            value=material.get('material_desc', '')
                        )
                        new_weight = st.number_input(
                            "Weight per pcs (kg)",
                            value=material.get('weight_per_pcs', 0.0),
                            min_value=0.0,
                            step=0.001,
                            format="%.3f"
                        )
                        new_usage = st.text_input(
                            "Usage",
                            value=material.get('usage', '')
                        )
                        new_daily_demand = st.number_input(
                            "Daily demand (average)",
                            value=material.get('daily_demand', 0.0),
                            min_value=0.0,
                            step=0.01
                        )
                        new_annual_volume = st.number_input(
                            "Annual volume (average)",
                            value=material.get('annual_volume', 0),
                            min_value=0,
                            step=1
                        )
                    
                    with col2:
                        new_lifetime_volume = st.number_input(
                            "Lifetime (volume)",
                            value=material.get('lifetime_volume', 0.0),
                            min_value=0.0,
                            step=0.1
                        )
                        new_peak_year = st.text_input(
                            "Peak year",
                            value=material.get('peak_year', '')
                        )
                        new_peak_year_volume = st.number_input(
                            "Peak year volume",
                            value=material.get('peak_year_volume', 0),
                            min_value=0,
                            step=1
                        )
                        new_working_days = st.number_input(
                            "Working Days per year",
                            value=material.get('working_days', 0),
                            min_value=0,
                            step=1
                        )
                        new_sop = st.text_input(
                            "SOP",
                            value=material.get('sop', '')
                        )

                        new_Pcs_Price = st.number_input(
                            "Pcs_Price",
                            value=material.get('Pcs_Price', 0.0),
                            min_value=0.0,
                            step=0.01
                        )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update Material", type="primary"):
                            updated_material = {
                                'project_name': new_project_name,
                                'material_no': material['material_no'],
                                'material_desc': new_desc,
                                'weight_per_pcs': new_weight,
                                'usage': new_usage,
                                'daily_demand': new_daily_demand,
                                'annual_volume': new_annual_volume,
                                'lifetime_volume': new_lifetime_volume,
                                'peak_year': new_peak_year,
                                'peak_year_volume': new_peak_year_volume,
                                'working_days': new_working_days,
                                'sop': new_sop,
                                'Pcs_Price': new_Pcs_Price
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
