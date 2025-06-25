# app.py
import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
import base64
import os

# Initialize data manager in session_state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

def load_svg_logo():
    """Load and return the SVG logo as base64 encoded string"""
    try:
        # Try different possible logo file names
        logo_files = ['logo.svg', 'company_logo.svg', 'Logo.svg']
        
        for logo_file in logo_files:
            if os.path.exists(logo_file):
                with open(logo_file, "r", encoding="utf-8") as f:
                    svg_content = f.read()
                return svg_content
        
        # If no logo file found
        return None
    except Exception as e:
        st.error(f"Error loading logo: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Logistics Cost Automation",
        page_icon="🚚",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Create centered header with logo above title
    _, center_col, _ = st.columns([1, 4, 1])
    
    with center_col:
        svg_logo = load_svg_logo()
        if svg_logo:
            # Display SVG logo centered above the title
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                    <div style="width: 80%; max-width: 600px;">
                        {svg_logo}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Fallback if no logo found
            st.info("Add logo.svg to project directory")
        
        # Title and subtitle centered below the logo
        st.markdown(
            """
            <h1 style='text-align: center; margin-top: 0;'>
                 Logistics Cost Estimation
            </h1>
            <p style='text-align: center; font-size: 1.2em; color: #666;'>
                Comprehensive logistics cost calculation and analysis platform
            </p>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("---")

    # Sidebar navigation info
    st.sidebar.title("📋 Navigation Guide")
    st.sidebar.markdown("""
    ### Configuration Pages:
    
    **Basic Setup:**
    1. **Material Information** - Product specifications
    2. **Supplier Information** - Vendor details
    3. **KB/Bendix Location** - Plant locations
    4. **Operations Information** - Business parameters
    
    **Cost Components:**
    5. **Packaging Cost** - Container & packaging setup
    6. **Repacking Cost** - Material handling costs
    7. **Customs Cost** - Import/export duties
    8. **Transport Cost** - Shipping & logistics
    9. **Annual CO₂ Cost** - Environmental costs
    10. **Warehouse Cost** - Storage expenses
    11. **Inventory Cost** - Interest rates
    12. **Additional Cost** - Other expenses
    
    **Analysis:**
    13. **Cost Calculation** - Run calculations & export
    """)

    # Main dashboard
    data_manager = st.session_state.data_manager
    
    # Get configuration counts
    config_counts = {
        "Materials": len(data_manager.get_materials()),
        "Suppliers": len(data_manager.get_suppliers()),
        "Locations": len(data_manager.get_locations()),
        "Operations": len(data_manager.get_operations()),
        "Packaging": len(data_manager.get_packaging()),
        "Repacking": len(data_manager.get_repacking()),
        "Customs": len(data_manager.get_customs()),
        "Transport": len(data_manager.get_transport()),
        "CO₂": len(data_manager.get_co2()),
        "Warehouse": len(data_manager.get_warehouse()),
        "Interest": len(data_manager.get_interest()),
        "Additional": len(data_manager.get_additional_costs()),
    }

    # Status Overview
    st.subheader("📊 System Status Overview")
    
    # Create status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    # Core configurations
    with col1:
        st.markdown("### 🏢 Core Setup")
        for key in ["Materials", "Suppliers", "Locations", "Operations"]:
            count = config_counts[key]
            status = "✅" if count > 0 else "❌"
            st.metric(f"{status} {key}", count)
    
    # Packaging configurations
    with col2:
        st.markdown("### 📦 Packaging")
        for key in ["Packaging", "Repacking", "Customs"]:
            count = config_counts[key]
            status = "✅" if count > 0 else "❌"
            st.metric(f"{status} {key}", count)
    
    # Transport & Environment
    with col3:
        st.markdown("### 🚛 Transport & Environment")
        for key in ["Transport", "CO₂", "Warehouse"]:
            count = config_counts[key]
            status = "✅" if count > 0 else "❌"
            st.metric(f"{status} {key}", count)
    
    # Financial
    with col4:
        st.markdown("### 💰 Financial")
        for key in ["Interest", "Additional"]:
            count = config_counts[key]
            status = "✅" if count > 0 else "❌"
            st.metric(f"{status} {key}", count)
        
        # Calculation readiness
        ready = data_manager.is_calculation_ready()
        status = "✅" if ready else "❌"
        st.metric(f"{status} Ready to Calculate", "Yes" if ready else "No")

    st.markdown("---")

    # Quick Stats
    st.subheader("📈 Quick Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_configs = sum(config_counts.values())
        st.metric("Total Configurations", total_configs)
    
    with col2:
        material_supplier_pairs = len(data_manager.get_material_supplier_pairs())
        st.metric("Material-Supplier Pairs", material_supplier_pairs)
    
    with col3:
        completeness = sum(1 for v in config_counts.values() if v > 0) / len(config_counts) * 100
        st.metric("Configuration Completeness", f"{completeness:.0f}%")

    # Configuration Details
    st.markdown("---")
    st.subheader("🔍 Configuration Details")
    
    # Use tabs for different configuration types
    tabs = st.tabs(["Materials & Suppliers", "Operations & Locations", "Cost Components", "All Configurations"])
    
    with tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Materials")
            materials = data_manager.get_materials()
            if materials:
                df_materials = pd.DataFrame(materials)[['material_no', 'material_desc', 'annual_volume', 'weight_per_pcs']]
                st.dataframe(df_materials, use_container_width=True, height=300)
            else:
                st.info("No materials configured yet.")
        
        with col2:
            st.markdown("### Suppliers")
            suppliers = data_manager.get_suppliers()
            if suppliers:
                df_suppliers = pd.DataFrame(suppliers)[['vendor_id', 'vendor_name', 'vendor_country', 'city_of_manufacture']]
                st.dataframe(df_suppliers, use_container_width=True, height=300)
            else:
                st.info("No suppliers configured yet.")
    
    with tabs[1]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Operations")
            operations = data_manager.get_operations()
            if operations:
                df_ops = pd.DataFrame(operations)
                display_cols = ['incoterm_code', 'lead_time', 'currency', 'responsible']
                available_cols = [col for col in display_cols if col in df_ops.columns]
                if available_cols:
                    st.dataframe(df_ops[available_cols], use_container_width=True, height=200)
            else:
                st.info("No operations configured yet.")
        
        with col2:
            st.markdown("### Locations")
            locations = data_manager.get_locations()
            if locations:
                df_locations = pd.DataFrame(locations)
                st.dataframe(df_locations, use_container_width=True, height=200)
            else:
                st.info("No locations configured yet.")
    
    with tabs[2]:
        # Cost components overview
        cost_configs = {
            "Packaging": data_manager.get_packaging(),
            "Transport": data_manager.get_transport(),
            "Warehouse": data_manager.get_warehouse(),
            "CO₂": data_manager.get_co2()
        }
        
        for name, configs in cost_configs.items():
            if configs:
                st.markdown(f"### {name}")
                df = pd.DataFrame(configs)
                # Show only first few columns to avoid clutter
                display_cols = list(df.columns)[:5]
                st.dataframe(df[display_cols], use_container_width=True, height=150)
            else:
                st.info(f"No {name.lower()} configurations yet.")
    
    with tabs[3]:
        # Export all configurations for review
        all_configs = {
            "Materials": data_manager.get_materials(),
            "Suppliers": data_manager.get_suppliers(),
            "Locations": data_manager.get_locations(),
            "Operations": data_manager.get_operations(),
            "Packaging": data_manager.get_packaging(),
            "Repacking": data_manager.get_repacking(),
            "Customs": data_manager.get_customs(),
            "Transport": data_manager.get_transport(),
            "CO2": data_manager.get_co2(),
            "Warehouse": data_manager.get_warehouse(),
            "Interest": data_manager.get_interest(),
            "Additional_Costs": data_manager.get_additional_costs()
        }
        
        for config_name, config_data in all_configs.items():
            if config_data:
                st.markdown(f"### {config_name}")
                st.json(config_data, expanded=False)

    st.markdown("---")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
            if st.session_state.get('confirm_clear', False):
                data_manager.clear_all_data()
                st.success("✅ All data cleared successfully!")
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ Click again to confirm clearing all data")
    
    with col2:
        if st.button("💾 Export Configuration", type="primary", use_container_width=True):
            config_data = data_manager.export_configuration()
            st.download_button(
                label="📥 Download Configuration JSON",
                data=config_data,
                file_name=f"logistics_config_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col3:
        st.markdown("### Import Configuration")
        uploaded_file = st.file_uploader(
            "Choose file",
            type=['json'],
            help="Upload a previously exported configuration file",
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            try:
                result = data_manager.import_configuration(uploaded_file.read())
                if result:
                    st.success("✅ Configuration imported successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to import configuration")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col4:
        ready = data_manager.is_calculation_ready()
        if ready:
            st.success("✅ Ready to calculate!")
            st.markdown("[Go to Calculation →](/Cost_Calculation)")
        else:
            st.warning("⚠️ Missing required configs")
            missing = []
            if config_counts["Materials"] == 0:
                missing.append("Materials")
            if config_counts["Suppliers"] == 0:
                missing.append("Suppliers")
            if config_counts["Packaging"] == 0:
                missing.append("Packaging")
            if config_counts["Transport"] == 0:
                missing.append("Transport")
            if config_counts["Warehouse"] == 0:
                missing.append("Warehouse")
            if config_counts["CO₂"] == 0:
                missing.append("CO₂")
            if missing:
                st.caption(f"Required: {', '.join(missing)}")

    # Help Section
    st.markdown("---")
    with st.expander("ℹ️ Getting Started Guide"):
        st.markdown("""
        ### 🚀 Quick Start Guide
        
        1. **Configure Materials**: Start by adding your materials with specifications
        2. **Add Suppliers**: Enter vendor information and locations
        3. **Set Operations**: Configure lead times, incoterms, and currencies
        4. **Define Costs**: Add packaging, transport, warehouse, and other cost parameters
        5. **Calculate**: Run the cost calculation engine to get detailed results
        6. **Export Results**: Download your analysis in CSV, Excel, or JSON format
        
        ### 💡 Tips:
        - Use the sidebar to navigate between pages
        - Each configuration can be edited or deleted after creation
        - Import/Export functionality allows you to save and share configurations
        - The calculation page provides detailed breakdowns and comparisons
        
        ### 📊 Understanding Results:
        - **Cost per Piece**: Individual component costs broken down
        - **Annual Costs**: Projected yearly expenses based on volumes
        - **Comparison Analysis**: Identifies best and worst configurations
        - **Export Options**: Multiple formats for different use cases
        """)

    # Footer
    st.markdown("---")
    st.caption("Logistics Cost Automation Software v1.0")

if __name__ == "__main__":
    main()