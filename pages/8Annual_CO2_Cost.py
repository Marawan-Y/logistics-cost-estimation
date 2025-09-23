# pages/9Annual_CO2_Cost.py
import streamlit as st
from utils.validators import CO2Validator
from utils.data_manager import DataManager

st.set_page_config(page_title="Annual CO2 Cost", page_icon="🌿")

def main():
    st.title("Annual CO₂ Cost")
    st.markdown("Configure annual CO₂ cost parameters - you can create multiple configurations for different scenarios")
    st.markdown("---")

    # Initialize DataManager & Validator
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    dm = st.session_state.data_manager
    val = CO2Validator()

    # ---------- Add New CO2 Cost ----------
    with st.form("co2_form"):
        st.subheader("Add New CO₂ Cost Configuration")

        cost_per_ton = st.number_input(
            "CO₂ Cost per Ton (€) *",
            min_value=0.0,
            step=0.10,
            format="%.2f",
            help="Cost of CO₂ emissions per metric ton"
        )

        co2_conversion_factor = st.selectbox(
            "CO₂ Conversion Factor *",
            ["2.65", "3.17", "3.31"],
            help="CO₂ conversion factor based on Transportation mode & location. Sea = 3.31, Road/Rail = 3.17/2.65"
        )

        # Optional description field for differentiating configurations
        description = st.text_input(
            "Configuration Description (Optional)",
            help="Optional description to help identify this configuration (e.g., 'High emission scenario', 'Standard rates 2024')"
        )

        submitted = st.form_submit_button("Add CO₂ Configuration", type="primary")
        if submitted:
            obj = {
                "cost_per_ton": cost_per_ton, 
                "co2_conversion_factor": co2_conversion_factor,
                "description": description.strip() if description else ""
            }
            res = val.validate_co2(obj)
            if res["is_valid"]:
                # Removed the single configuration check - now allows multiple
                dm.add_co2(obj)
                st.success("CO₂ cost configuration added successfully!")
                st.rerun()
            else:
                for e in res["errors"]:
                    st.error(e)

    st.markdown("---")

    # ---------- Display Existing CO2 Configurations ----------
    st.subheader("Existing CO₂ Cost Configurations")
    co2_list = dm.get_co2()
    
    if not co2_list:
        st.info("No CO₂ cost configurations yet. Add your first configuration above.")
    
    for i, co2 in enumerate(co2_list):
        # Create a more descriptive header
        header_parts = [f"€{co2['cost_per_ton']:.2f}/ton"]
        header_parts.append(f"Factor: {co2['co2_conversion_factor']}")
        
        if co2.get('description'):
            header_parts.append(f"({co2['description']})")
        
        header = " | ".join(header_parts)
        
        with st.expander(f"Configuration {i+1}: {header}"):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**Cost per Ton:** €{co2['cost_per_ton']:.2f}")
                st.write(f"**CO₂ Conversion Factor:** {co2['co2_conversion_factor']}")
                if co2.get('description'):
                    st.write(f"**Description:** {co2['description']}")
                
                # Show what transport modes this factor typically applies to
                factor_info = {
                    "2.65": "Typically for Road transport (Europe)",
                    "3.17": "Standard for Road/Rail transport",
                    "3.31": "Typically for Sea transport"
                }
                st.caption(f"ℹ️ {factor_info.get(co2['co2_conversion_factor'], 'Custom conversion factor')}")
                
            with col2:
                if st.button("Edit", key=f"btn_edit_co2_{i}"):
                    st.session_state[f"edit_co2_{i}"] = True
                    st.rerun()
            
            with col3:
                if st.button("Delete", key=f"del_co2_{i}", type="secondary"):
                    # Updated to use index-based removal instead of cost_per_ton
                    dm.remove_co2_by_index(i)
                    st.success("CO₂ cost configuration deleted.")
                    st.rerun()

    # ---------- Edit CO2 Cost ----------
    for i, co2 in enumerate(co2_list):
        if st.session_state.get(f"edit_co2_{i}", False):
            with st.form(f"edit_co2_form_{i}"):
                st.subheader(f"Edit CO₂ Configuration {i+1}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_cost = st.number_input(
                        "CO₂ Cost per Ton (€)",
                        value=co2["cost_per_ton"],
                        min_value=0.0,
                        step=0.10,
                        format="%.2f"
                    )
                    
                with col2:
                    current_factor_index = ["2.65", "3.17", "3.31"].index(co2["co2_conversion_factor"])
                    new_factor = st.selectbox(
                        "CO₂ Conversion Factor",
                        ["2.65", "3.17", "3.31"],
                        index=current_factor_index
                    )
                
                new_description = st.text_input(
                    "Configuration Description (Optional)",
                    value=co2.get("description", ""),
                    help="Optional description to help identify this configuration"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update CO₂ Configuration", type="primary"):
                        upd = {
                            "cost_per_ton": new_cost, 
                            "co2_conversion_factor": new_factor,
                            "description": new_description.strip() if new_description else ""
                        }
                        res = val.validate_co2(upd)
                        if res["is_valid"]:
                            # Updated to use index-based update
                            dm.update_co2_by_index(i, upd)
                            st.success("CO₂ cost configuration updated.")
                            st.session_state[f"edit_co2_{i}"] = False
                            st.rerun()
                        else:
                            for e in res["errors"]:
                                st.error(e)
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_co2_{i}"] = False
                        st.rerun()

    # ---------- Usage Guidelines ----------
    if co2_list:
        st.markdown("---")
        with st.expander("ℹ️ CO₂ Configuration Guidelines"):
            st.markdown("""
            ### 🌱 CO₂ Conversion Factors Guide
            
            **2.65**: Road transport (optimized European routes)
            **3.17**: Standard Road/Rail transport (most common)
            **3.31**: Sea transport (higher emissions per km)
            
            ### 💡 Usage Tips
            - Create different configurations for different transport scenarios
            - Use descriptions to identify specific use cases (e.g., "Standard 2024", "High carbon cost scenario")
            - Consider having configurations for different regulatory environments
            - The conversion factor should match your primary transport mode
            
            ### 🔄 How CO₂ Costs are Calculated
            ```
            CO₂ Cost per Piece = (Total Weight × Energy Consumption × Distance × Conversion Factor × Cost per Ton) / Annual Volume
            ```
            
            Where:
            - **Total Weight**: Shipment weight including packaging
            - **Energy Consumption**: Transport mode specific (Road: 0.04415, Rail: 0.0085, Sea: 0.006)
            - **Distance**: Route distance in kilometers
            - **Conversion Factor**: Selected factor above
            - **Cost per Ton**: Your specified cost per ton of CO₂
            """)

if __name__ == "__main__":
    main()