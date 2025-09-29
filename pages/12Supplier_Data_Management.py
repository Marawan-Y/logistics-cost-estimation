# pages/12Supplier_Data_Management.py
import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.supplier_database import SupplierDatabase
import json
from datetime import datetime

st.set_page_config(page_title="Supplier Data Management", page_icon="🏭", layout="wide")

# --- helper: normalize a supplier record to guarantee required keys exist ---
def normalize_supplier_record(s: dict) -> dict:
    s = dict(s or {})
    # support legacy alt key names (if any)
    if 'kb_country' in s and 'country' not in s:
        s['country'] = s.get('kb_country')

    # fill required keys with safe defaults
    defaults = {
        'vendor_id': '',
        'vendor_zip': '',
        'vendor_name': '',
        'vendor_country': '',
        'city_of_manufacture': '',
        'delivery_performance': 0.0,
        'deliveries_per_month': 0,
        'plant': '',        # <--- avoid KeyError
        'distance': 0.0,    # <--- avoid KeyError
        'country': '',      # <--- avoid KeyError
    }
    for k, v in defaults.items():
        if k not in s or s[k] is None:
            s[k] = v
    # coerce numerics
    try:
        s['delivery_performance'] = float(s.get('delivery_performance', 0.0) or 0.0)
    except Exception:
        s['delivery_performance'] = 0.0
    try:
        s['deliveries_per_month'] = int(s.get('deliveries_per_month', 0) or 0)
    except Exception:
        s['deliveries_per_month'] = 0
    try:
        s['distance'] = float(s.get('distance', 0.0) or 0.0)
    except Exception:
        s['distance'] = 0.0
    return s

def main():
    st.title("Supplier Data Management")
    st.markdown("Manage Supplier Historical Database")
    st.markdown("---")
    
    # Initialize
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    if 'supplier_db' not in st.session_state:
        st.session_state.supplier_db = SupplierDatabase()
        try:
            st.session_state.supplier_db.load_from_json('supplier_database.json')
        except:
            pass
    
    data_manager = st.session_state.data_manager
    supplier_db = st.session_state.supplier_db
    
    # Sync with current supplier configurations
    supplier_db.sync_with_configurations(data_manager.get_suppliers())
    supplier_db.save_to_json('supplier_database.json')
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 View Database", "➕ Add/Edit Supplier", "📁 Import/Export", "🔍 Search & Filter"])
    
    # Tab 1: View Database
    with tab1:
        st.subheader("Supplier Database")
        
        stats = supplier_db.get_statistics()
        if stats.get('total_suppliers', 0) > 0:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Suppliers", stats.get('total_suppliers', 0))
            col2.metric("Total Countries", stats.get('total_countries', 0))
            col3.metric("Synced with Configurations", "✅ Yes")
            
            display_data = []
            for idx, (vendor_id, supplier_data) in enumerate(supplier_db.database.items(), 1):
                s = normalize_supplier_record(supplier_data)
                display_data.append({
                    'Index': idx,
                    'Vendor ID': s.get('vendor_id', ''),
                    'Vendor ZIP': s.get('vendor_zip', ''),
                    'Vendor Name': s.get('vendor_name', ''),
                    'Vendor Country': s.get('vendor_country', ''),
                    'City of Manufacture': s.get('city_of_manufacture', ''),
                    'Delivery Performance (%)': f"{s.get('delivery_performance', 0.0):.1f}",
                    'Deliveries per Month': s.get('deliveries_per_month', 0),
                    'KB/Bendix Plant': s.get('plant', ''),
                    'Distance (km)': f"{s.get('distance', 0.0):.1f}",
                    'KB/Bendix Country': s.get('country', '')
                })
            
            if display_data:
                df_suppliers = pd.DataFrame(display_data)
                st.dataframe(df_suppliers, use_container_width=True, height=600, hide_index=True)
                st.info(f"📊 Showing {len(display_data)} supplier records")
            else:
                st.info("No supplier data in database.")
        else:
            st.warning("No supplier data loaded. Please add suppliers in Supplier Information page or import data.")
    
    # Tab 2: Add/Edit Supplier
    with tab2:
        st.subheader("Add or Edit Supplier")
        
        action = st.radio("Select Action", ["Add New Supplier", "Edit Existing Supplier"], horizontal=True)
        
        if action == "Add New Supplier":
            with st.form("add_supplier_form"):
                st.markdown("### Add New Supplier to Database")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Supplier Details")
                    vendor_id = st.text_input("Vendor ID *")
                    vendor_name = st.text_input("Vendor Name *")
                    vendor_country = st.text_input("Vendor Country *")
                    city_of_manufacture = st.text_input("City of Manufacture *")
                    vendor_zip = st.text_input("Vendor ZIP *")
                
                with col2:
                    st.markdown("#### Delivery & Location")
                    delivery_performance = st.number_input("Delivery Performance (%)*", min_value=0.0, max_value=100.0, step=0.1)
                    deliveries_per_month = st.number_input("Deliveries per Month *", min_value=0, step=1)
                    plant = st.text_input("KB/Bendix Plant *")
                    country = st.text_input("KB/Bendix Country *")
                    distance = st.number_input("Distance (km) *", min_value=0.0, step=0.1)
                
                submitted = st.form_submit_button("Add Supplier to Database", type="primary")
                if submitted:
                    if not vendor_id or not vendor_name:
                        st.error("Vendor ID and Vendor Name are required")
                    elif supplier_db.supplier_exists(vendor_id):
                        st.error(f"Supplier {vendor_id} already exists in database")
                    else:
                        supplier_data = normalize_supplier_record({
                            'vendor_id': vendor_id,
                            'vendor_name': vendor_name,
                            'vendor_country': vendor_country,
                            'city_of_manufacture': city_of_manufacture,
                            'vendor_zip': vendor_zip,
                            'delivery_performance': delivery_performance,
                            'deliveries_per_month': deliveries_per_month,
                            'plant': plant,
                            'country': country,
                            'distance': distance
                        })
                        supplier_db.add_supplier(vendor_id, supplier_data)
                        supplier_db.save_to_json('supplier_database.json')
                        st.success(f"Supplier {vendor_id} added successfully!")
                        st.rerun()
        else:
            existing_suppliers = list(supplier_db.database.keys())
            if not existing_suppliers:
                st.warning("No suppliers in database to edit.")
            else:
                selected_supplier_id = st.selectbox(
                    "Select Supplier to Edit",
                    existing_suppliers,
                    format_func=lambda x: f"{x} - {supplier_db.database[x].get('vendor_name', '')}"
                )
                
                supplier_data = normalize_supplier_record(supplier_db.database[selected_supplier_id])
                
                with st.form("edit_supplier_form"):
                    st.markdown(f"### Editing: {selected_supplier_id}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### Supplier Details")
                        vendor_name = st.text_input("Vendor Name", value=supplier_data.get('vendor_name', ''))
                        vendor_country = st.text_input("Vendor Country", value=supplier_data.get('vendor_country', ''))
                        city_of_manufacture = st.text_input("City of Manufacture", value=supplier_data.get('city_of_manufacture', ''))
                        vendor_zip = st.text_input("Vendor ZIP", value=supplier_data.get('vendor_zip', ''))
                    
                    with col2:
                        st.markdown("#### Delivery & Location")
                        delivery_performance = st.number_input(
                            "Delivery Performance (%)",
                            value=float(supplier_data.get('delivery_performance', 0.0)),
                            min_value=0.0, max_value=100.0, step=0.1
                        )
                        deliveries_per_month = st.number_input(
                            "Deliveries per Month",
                            value=int(supplier_data.get('deliveries_per_month', 0)),
                            min_value=0, step=1
                        )
                        plant_val = st.text_input("KB/Bendix Plant", value=supplier_data.get('plant', ''))
                        country_val = st.text_input("KB/Bendix Country", value=supplier_data.get('country', ''))
                        distance = st.number_input(
                            "Distance (km)",
                            value=float(supplier_data.get('distance', 0.0)),
                            min_value=0.0, step=0.1
                        )
                    
                    colA, colB = st.columns(2)
                    with colA:
                        if st.form_submit_button("Update Supplier", type="primary"):
                            updated_data = normalize_supplier_record({
                                'vendor_id': selected_supplier_id,
                                'vendor_name': vendor_name,
                                'vendor_country': vendor_country,
                                'city_of_manufacture': city_of_manufacture,
                                'vendor_zip': vendor_zip,
                                'delivery_performance': delivery_performance,
                                'deliveries_per_month': deliveries_per_month,
                                'plant': plant_val,
                                'country': country_val,
                                'distance': distance
                            })
                            supplier_db.update_supplier(selected_supplier_id, updated_data)
                            supplier_db.save_to_json('supplier_database.json')
                            st.success(f"Supplier {selected_supplier_id} updated successfully!")
                            st.rerun()
                    with colB:
                        if st.form_submit_button("Cancel"):
                            st.rerun()
    
    # Tab 3: Import/Export
    with tab3:
        st.subheader("Import/Export Supplier Data")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Import Data")
            upload_type = st.radio("Import format:", ["JSON (Database Format)", "CSV"])
            if upload_type == "JSON (Database Format)":
                uploaded_file = st.file_uploader("Choose JSON file", type=['json'])
                if uploaded_file is not None and st.button("Import JSON Data"):
                    try:
                        data = json.load(uploaded_file)
                        raw_db = data.get('database', {})
                        # normalize everything on import
                        supplier_db.database = {
                            vid: normalize_supplier_record(rec) for vid, rec in raw_db.items()
                        }
                        supplier_db.save_to_json('supplier_database.json')
                        st.success(f"Successfully imported {len(supplier_db.database)} suppliers!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error importing JSON: {str(e)}")
            else:
                uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
                if uploaded_file is not None and st.button("Import CSV Data"):
                    try:
                        df = pd.read_csv(uploaded_file)
                        supplier_db.load_from_csv_dataframe(df)
                        # normalize after loader
                        supplier_db.database = {
                            vid: normalize_supplier_record(rec) for vid, rec in supplier_db.database.items()
                        }
                        supplier_db.save_to_json('supplier_database.json')
                        st.success(f"Successfully imported {len(supplier_db.database)} suppliers!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error importing CSV: {str(e)}")
        
        with col2:
            st.markdown("### Export Data")
            if len(supplier_db.database) > 0:
                export_format = st.radio("Export format:", ["JSON", "CSV", "Excel"])
                if export_format == "JSON" and st.button("Export as JSON"):
                    data = {
                        'database': supplier_db.database,
                        'metadata': {
                            'export_date': datetime.now().isoformat(),
                            'total_suppliers': len(supplier_db.database)
                        }
                    }
                    json_str = json.dumps(data, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name="supplier_database.json",
                        mime="application/json"
                    )
                elif export_format == "CSV" and st.button("Export as CSV"):
                    df = supplier_db.to_dataframe()
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="supplier_database.csv",
                        mime="text/csv"
                    )
                elif export_format == "Excel" and st.button("Export as Excel"):
                    df = supplier_db.to_dataframe()
                    from io import BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Suppliers', index=False)
                    st.download_button(
                        label="Download Excel",
                        data=output.getvalue(),
                        file_name="supplier_database.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.info("No data to export. Please add suppliers first.")
    
    # Tab 4: Search & Filter
    with tab4:
        st.subheader("Search and Filter Suppliers")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_vendor_id = st.text_input("Vendor ID")
        with col2:
            search_country = st.text_input("Country")
        with col3:
            search_city = st.text_input("City")
        
        if st.button("Search"):
            results = supplier_db.filter_suppliers(
                vendor_id=search_vendor_id or None,
                country=search_country or None,
                city=search_city or None
            )
            if results:
                st.success(f"Found {len(results)} matching suppliers")
                rows = []
                for idx, rec in enumerate(results, 1):
                    s = normalize_supplier_record(rec)
                    rows.append({
                        'Index': idx,
                        'Vendor ID': s.get('vendor_id', ''),
                        'Vendor ZIP': s.get('vendor_zip', ''),
                        'Vendor Name': s.get('vendor_name', ''),
                        'Vendor Country': s.get('vendor_country', ''),
                        'City of Manufacture': s.get('city_of_manufacture', ''),
                        'Delivery Performance (%)': f"{s.get('delivery_performance', 0.0):.1f}",
                        'Deliveries per Month': s.get('deliveries_per_month', 0),
                        'KB/Bendix Plant': s.get('plant', ''),
                        'Distance (km)': f"{s.get('distance', 0.0):.1f}",
                        'KB/Bendix Country': s.get('country', '')
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.warning("No suppliers found matching the criteria")

if __name__ == "__main__":
    main()
