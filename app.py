import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.calculations import LogisticsCostCalculator

# Initialize data manager
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

def main():
    st.set_page_config(
        page_title="Logistics Cost Automation",
        page_icon="🚚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚚 Logistics Cost Automation Application")
    st.markdown("---")
    
    # Sidebar navigation info
    st.sidebar.title("Navigation")
    st.sidebar.markdown("""
    Use the pages on the left to navigate through the application:
    
    1. **Material Information** - Enter material details
    2. **Supplier Information** - Vendor and location data
    3. **Packaging Costs** - Packaging parameters
    4. **Transport Costs** - Transport mode and costs
    5. **Warehouse Costs** - Storage and inventory costs
    6. **Cost Calculation** - View final calculations and export
    """)
    
    # Main dashboard
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Materials Configured",
            value=len(st.session_state.data_manager.get_materials())
        )
    
    with col2:
        st.metric(
            label="Suppliers Configured", 
            value=len(st.session_state.data_manager.get_suppliers())
        )
    
    with col3:
        calculations_ready = st.session_state.data_manager.is_calculation_ready()
        st.metric(
            label="Calculation Status",
            value="Ready" if calculations_ready else "Pending"
        )
    
    st.markdown("---")
    
    # Overview of current data
    st.header("📊 Current Configuration Overview")
    
    # Material overview
    materials = st.session_state.data_manager.get_materials()
    if materials:
        st.subheader("Materials")
        df_materials = pd.DataFrame(materials)
        st.dataframe(df_materials, use_container_width=True)
    else:
        st.info("No materials configured yet. Please use the Material Information page to add materials.")
    
    # Supplier overview
    suppliers = st.session_state.data_manager.get_suppliers()
    if suppliers:
        st.subheader("Suppliers")
        df_suppliers = pd.DataFrame(suppliers)
        st.dataframe(df_suppliers, use_container_width=True)
    else:
        st.info("No suppliers configured yet. Please use the Supplier Information page to add suppliers.")
    
    # Quick actions
    st.markdown("---")
    st.header("🚀 Quick Actions")
    
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
