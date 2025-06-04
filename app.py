# app.py
import streamlit as st
import pandas as pd
from utils.data_manager import DataManager

# Initialize data manager in session_state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

def main():
    st.set_page_config(
        page_title="Logistics Cost Automation",
        page_icon="🚚",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Logistics Cost Estimation")
    st.markdown("---")

    # Sidebar navigation info - now extended for your new pages
    st.sidebar.title("Navigation")
    st.sidebar.markdown("""
    Use the pages on the left to navigate through the application:

    1. **Material Information** - Enter material details  
    2. **Supplier Information** - Vendor and location data  
    3. **KB/Bendix Location Info** - Plant, country, and distance  
    4. **Operations Information** - Incoterms, lead times, classifications  
    5. **Packaging Costs** - Standard & special packaging, loops  
    6. **Repacking Cost**  
    7. **Customs Cost**  
    8. **Transport Cost**  
    9. **Annual CO₂ Cost**  
    10. **Warehouse Cost**  
    11. **Inventory Cost**  
    12. **Inventory Interest**  
    13. **Additional Cost**  
    14. **Cost Calculation** - View final calculations and export  
    """)

    # Main dashboard: Show status of all major config types
    dashboard_columns = [
        ("Materials", st.session_state.data_manager.get_materials()),
        ("Suppliers", st.session_state.data_manager.get_suppliers()),
        ("Locations", getattr(st.session_state.data_manager, "get_locations", lambda: [])()),
        ("Operations", getattr(st.session_state.data_manager, "get_operations", lambda: [])()),
        ("Packaging", st.session_state.data_manager.get_packaging()),
        ("Repacking", getattr(st.session_state.data_manager, "get_repacking", lambda: [])()),
        ("Customs", getattr(st.session_state.data_manager, "get_customs", lambda: [])()),
        ("Transport", st.session_state.data_manager.get_transport()),
        ("CO₂", getattr(st.session_state.data_manager, "get_co2", lambda: [])()),
        ("Warehouse", st.session_state.data_manager.get_warehouse()),
        ("Inventory", getattr(st.session_state.data_manager, "get_inventory", lambda: [])()),
        ("Interest", getattr(st.session_state.data_manager, "get_interest", lambda: [])()),
        ("Additional Cost", getattr(st.session_state.data_manager, "get_additional_costs", lambda: [])()),
    ]

    st.subheader("📦 Configuration Status Overview")
    # Display metrics in 4 columns at a time for a nice grid
    n_cols = 4
    for i in range(0, len(dashboard_columns), n_cols):
        cols = st.columns(n_cols)
        for j, (label, entries) in enumerate(dashboard_columns[i:i+n_cols]):
            with cols[j]:
                st.metric(label, len(entries) if entries is not None else 0)

    st.markdown("---")
    st.header("Current Configuration Overview")

    # Display DataFrames for key configs
    config_sections = [
        ("Materials", st.session_state.data_manager.get_materials()),
        ("Suppliers", st.session_state.data_manager.get_suppliers()),
        ("Locations", getattr(st.session_state.data_manager, "get_locations", lambda: [])()),
        ("Operations", getattr(st.session_state.data_manager, "get_operations", lambda: [])()),
        ("Packaging", st.session_state.data_manager.get_packaging()),
        ("Repacking", getattr(st.session_state.data_manager, "get_repacking", lambda: [])()),
        ("Customs", getattr(st.session_state.data_manager, "get_customs", lambda: [])()),
        ("Transport", st.session_state.data_manager.get_transport()),
        ("Warehouse", st.session_state.data_manager.get_warehouse()),
        # Add more if you wish (CO2, inventory, interest, etc.)
    ]
    for name, data in config_sections:
        if data and len(data) > 0:
            st.subheader(name)
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info(f"No {name.lower()} configured yet. Please use the {name} page to add {name.lower()}.")

    st.markdown("---")
    st.header("Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Clear All Data", type="secondary"):
            if st.session_state.get('confirm_clear', False):
                st.session_state.data_manager.clear_all_data()
                st.success("All data cleared successfully!")
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm clearing all data")

    with col2:
        if st.button("Export Configuration", type="secondary"):
            config_data = st.session_state.data_manager.export_configuration()
            st.download_button(
                label="Download Configuration JSON",
                data=config_data,
                file_name="logistics_config.json",
                mime="application/json"
            )

    with col3:
        uploaded_file = st.file_uploader(
            "Import Configuration",
            type=['json'],
            help="Upload a previously exported configuration file"
        )
        if uploaded_file is not None:
            try:
                result = st.session_state.data_manager.import_configuration(uploaded_file.read())
                if result:
                    st.success("Configuration imported successfully!")
                    st.rerun()
                else:
                    st.error("Failed to import configuration. Please check the file format.")
            except Exception as e:
                st.error(f"Error importing configuration: {str(e)}")

if __name__ == "__main__":
    main()
