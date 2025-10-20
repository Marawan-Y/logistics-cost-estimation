# pages/14Transport_Data_Management.py
import streamlit as st
import pandas as pd
import numpy as np
from utils.data_manager import DataManager
from utils.transport_database import TransportDatabase
import json
from io import BytesIO

st.set_page_config(page_title="Transport Data Management", page_icon="🚛", layout="wide")

def main():
    st.title("Transport Data Management")
    st.markdown("Manage Transport Cost Database")
    st.markdown("---")
    
    # Initialize
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    if 'transport_db' not in st.session_state:
        st.session_state.transport_db = TransportDatabase()
        try:
            st.session_state.transport_db.load_from_json('transport_database.json')
        except:
            pass
    
    transport_db = st.session_state.transport_db
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 View Database", "➕ Add/Edit/Delete Lane", "📁 Import/Export", "🔍 Search & Filter"])
    
    # Tab 1: View Database
    with tab1:
        st.subheader("Transport Cost Database")
        
        if len(transport_db.database) > 0:
            # Convert to DataFrame for display - COMPLETE DATA
            display_data = []
            for entry in transport_db.database:
                row = {
                    'Lane ID': entry['lane_id'],
                    'Origin Country': entry['origin']['country'],
                    'Origin Zip': entry['origin']['zip_code'],
                    'Origin City': entry['origin']['city'],
                    'Dest Country': entry['destination']['country'],
                    'Dest Zip': entry['destination']['zip_code'],
                    'Dest City': entry['destination']['city'],
                    'Lane Code': entry['lane_code'],
                    'Shipments/Year': entry['statistics']['shipments_per_year'],
                    'Weight/Year': entry['statistics']['weight_per_year'],
                    'Avg Shipment': entry['statistics']['avg_shipment_size'],
                    'Lead Time Groupage': entry['lead_time']['groupage'],
                    'Lead Time LTL': entry['lead_time']['ltl'],
                    'Lead Time FTL': entry['lead_time']['ftl']
                }
                
                # Add ALL weight cluster prices
                for weight in sorted(entry['prices_by_weight'].keys()):
                    row[f'≤{weight}kg'] = f"€{entry['prices_by_weight'][weight]:.2f}"
                
                # Add full truck and fuel surcharge
                row['Full Truck'] = entry.get('full_truck_price', 'N/A')
                row['Fuel Surcharge'] = f"{entry.get('fuel_surcharge', 0)}%"
                
                display_data.append(row)
            
            df_display = pd.DataFrame(display_data)
            
            # Add horizontal scrolling for the complete table
            st.dataframe(
                df_display,
                use_container_width=False,
                height=600,
                hide_index=True
            )
            
            # Add filtering options
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_origin = st.selectbox(
                    "Filter by Origin Country",
                    ["All"] + sorted(set(df_display['Origin Country'].unique()))
                )
            with col2:
                filter_dest = st.selectbox(
                    "Filter by Destination Country",
                    ["All"] + sorted(set(df_display['Dest Country'].unique()))
                )
            with col3:
                search_text = st.text_input("Search City", "")
            
            st.info(f"📊 Showing {len(display_data)} transport lanes")
        else:
            st.warning("No transport data loaded. Please import data in the Import/Export tab.")
    
    # Tab 2: Add/Edit/Delete Lane (MATCHING PACKAGING STYLE)
    with tab2:
        st.subheader("Add, Edit, or Delete Transport Lane")
        
        # Action selector
        action = st.radio("Select Action", ["Add New Lane", "Edit Existing Lane", "Delete Lane"], horizontal=True)
        
        if action == "Add New Lane":
            lane_name = st.text_input("Lane Identifier *", help="Unique identifier for this lane", key="add_lane_name")
            
            with st.form("add_lane_form"):
                st.markdown("### Add New Transport Lane")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Origin Information")
                    origin_country = st.text_input("Origin Country Code *", max_chars=2, key="add_origin_country")
                    origin_zip = st.text_input("Origin Zip Code (2-digit) *", max_chars=5, key="add_origin_zip")
                    origin_city = st.text_input("Origin City", key="add_origin_city")
                
                with col2:
                    st.markdown("#### Destination Information")
                    dest_country = st.text_input("Destination Country Code *", max_chars=2, key="add_dest_country")
                    dest_zip = st.text_input("Destination Zip Code (2-digit) *", max_chars=5, key="add_dest_zip")
                    dest_city = st.text_input("Destination City", key="add_dest_city")
                
                st.markdown("---")
                st.markdown("### Lead Times")
                col1, col2, col3 = st.columns(3)
                with col1:
                    lead_groupage = st.text_input("Lead Time Groupage", value="2-5", key="add_lead_groupage")
                with col2:
                    lead_ltl = st.text_input("Lead Time LTL", value="2-5", key="add_lead_ltl")
                with col3:
                    lead_ftl = st.text_input("Lead Time FTL", value="1-3", key="add_lead_ftl")
                
                st.markdown("---")
                st.markdown("### Pricing by Weight Cluster")
                
                # Create input fields for common weight clusters
                price_inputs = {}
                clusters = [50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000, 7500, 10000, 15000, 20000]
                
                # Display in rows of 4
                for i in range(0, len(clusters), 4):
                    cols = st.columns(4)
                    for j, col in enumerate(cols):
                        if i + j < len(clusters):
                            weight = clusters[i + j]
                            with col:
                                price_inputs[weight] = st.number_input(
                                    f"≤ {weight} kg (€)",
                                    min_value=0.0,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"add_price_{weight}"
                                )
                
                st.markdown("---")
                st.markdown("### Special Pricing")
                col1, col2 = st.columns(2)
                with col1:
                    full_truck_price = st.text_input("Full Truck Price", value="Contact for price", key="add_ftl_price")
                with col2:
                    fuel_surcharge = st.number_input("Fuel Surcharge (%)", min_value=0.0, max_value=100.0, step=0.01, key="add_fuel")
                
                submitted = st.form_submit_button("Add Lane", type="primary")
                
                if submitted:
                    if origin_country and origin_zip and dest_country and dest_zip and lane_name:
                        # Create new entry
                        new_entry = {
                            "lane_id": lane_name,
                            "origin": {
                                "country": origin_country.upper(),
                                "zip_code": origin_zip,
                                "city": origin_city
                            },
                            "destination": {
                                "country": dest_country.upper(),
                                "zip_code": dest_zip,
                                "city": dest_city
                            },
                            "lane_code": f"{origin_country.upper()}{origin_zip}{dest_country.upper()}{dest_zip}",
                            "statistics": {
                                "shipments_per_year": 0,
                                "weight_per_year": 0,
                                "avg_shipment_size": 0
                            },
                            "lead_time": {
                                "groupage": lead_groupage,
                                "ltl": lead_ltl,
                                "ftl": lead_ftl
                            },
                            "prices_by_weight": {k: v for k, v in price_inputs.items() if v > 0},
                            "full_truck_price": full_truck_price,
                            "fuel_surcharge": fuel_surcharge
                        }
                        
                        # Check if lane exists
                        existing = transport_db.find_lane(origin_country, origin_zip, dest_country, dest_zip)
                        if existing:
                            st.error(f"Lane already exists: {existing['lane_code']}")
                        else:
                            # Add new
                            transport_db.database.append(new_entry)
                            transport_db._build_lane_index()
                            transport_db.save_to_json('transport_database.json')
                            st.success("New lane added successfully!")
                            st.rerun()
                    else:
                        st.error("Please fill in all required fields marked with *")
        
        elif action == "Edit Existing Lane":
            # Get existing lanes
            existing_lanes = transport_db.database
            
            if not existing_lanes:
                st.warning("No lanes available to edit.")
            else:
                # Create lane labels for selection
                lane_labels = []
                for entry in existing_lanes:
                    label = f"{entry['lane_id']}: {entry['origin']['country']}{entry['origin']['zip_code']} → {entry['destination']['country']}{entry['destination']['zip_code']}"
                    lane_labels.append(label)
                
                selected_lane_label = st.selectbox("Select Lane to Edit", lane_labels, key="edit_lane_select")
                selected_lane_index = lane_labels.index(selected_lane_label)
                selected_lane = existing_lanes[selected_lane_index]
                
                with st.form("edit_lane_form"):
                    st.markdown(f"### Editing Lane: {selected_lane['lane_id']}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Origin Information")
                        new_origin_country = st.text_input("Origin Country Code", value=selected_lane['origin']['country'], max_chars=2, key="edit_origin_country")
                        new_origin_zip = st.text_input("Origin Zip Code", value=selected_lane['origin']['zip_code'], max_chars=5, key="edit_origin_zip")
                        new_origin_city = st.text_input("Origin City", value=selected_lane['origin']['city'], key="edit_origin_city")
                    
                    with col2:
                        st.markdown("#### Destination Information")
                        new_dest_country = st.text_input("Destination Country Code", value=selected_lane['destination']['country'], max_chars=2, key="edit_dest_country")
                        new_dest_zip = st.text_input("Destination Zip Code", value=selected_lane['destination']['zip_code'], max_chars=5, key="edit_dest_zip")
                        new_dest_city = st.text_input("Destination City", value=selected_lane['destination']['city'], key="edit_dest_city")
                    
                    st.markdown("---")
                    st.markdown("### Lead Times")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_lead_groupage = st.text_input("Lead Time Groupage", value=selected_lane['lead_time']['groupage'], key="edit_lead_groupage")
                    with col2:
                        new_lead_ltl = st.text_input("Lead Time LTL", value=selected_lane['lead_time']['ltl'], key="edit_lead_ltl")
                    with col3:
                        new_lead_ftl = st.text_input("Lead Time FTL", value=selected_lane['lead_time']['ftl'], key="edit_lead_ftl")
                    
                    st.markdown("---")
                    st.markdown("### Pricing by Weight Cluster")
                    
                    # Create input fields for weight clusters
                    new_price_inputs = {}
                    clusters = [50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000, 7500, 10000, 15000, 20000]
                    
                    for i in range(0, len(clusters), 4):
                        cols = st.columns(4)
                        for j, col in enumerate(cols):
                            if i + j < len(clusters):
                                weight = clusters[i + j]
                                current_price = selected_lane['prices_by_weight'].get(float(weight), 0.0)
                                with col:
                                    new_price_inputs[weight] = st.number_input(
                                        f"≤ {weight} kg (€)",
                                        value=float(current_price),
                                        min_value=0.0,
                                        step=0.01,
                                        format="%.2f",
                                        key=f"edit_price_{weight}"
                                    )
                    
                    st.markdown("---")
                    st.markdown("### Special Pricing")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_full_truck_price = st.text_input("Full Truck Price", value=str(selected_lane.get('full_truck_price', '')), key="edit_ftl_price")
                    with col2:
                        # FIX: Handle None values properly
                        fuel_surcharge_value = selected_lane.get('fuel_surcharge', 0)
                        if fuel_surcharge_value is None:
                            fuel_surcharge_value = 0.0
                        new_fuel_surcharge = st.number_input("Fuel Surcharge (%)", value=float(fuel_surcharge_value), min_value=0.0, max_value=100.0, step=0.01, key="edit_fuel")
                    
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        submit_update = st.form_submit_button("Update Lane", type="primary")
                    
                    with col2:
                        cancel_update = st.form_submit_button("Cancel")
                    
                    # Handle form submission
                    if submit_update:
                        updated_entry = {
                            "lane_id": selected_lane['lane_id'],
                            "origin": {
                                "country": new_origin_country.upper(),
                                "zip_code": new_origin_zip,
                                "city": new_origin_city
                            },
                            "destination": {
                                "country": new_dest_country.upper(),
                                "zip_code": new_dest_zip,
                                "city": new_dest_city
                            },
                            "lane_code": f"{new_origin_country.upper()}{new_origin_zip}{new_dest_country.upper()}{new_dest_zip}",
                            "statistics": selected_lane.get('statistics', {"shipments_per_year": 0, "weight_per_year": 0, "avg_shipment_size": 0}),
                            "lead_time": {
                                "groupage": new_lead_groupage,
                                "ltl": new_lead_ltl,
                                "ftl": new_lead_ftl
                            },
                            "prices_by_weight": {k: v for k, v in new_price_inputs.items() if v > 0},
                            "full_truck_price": new_full_truck_price,
                            "fuel_surcharge": new_fuel_surcharge
                        }
                        
                        transport_db.database[selected_lane_index] = updated_entry
                        transport_db._build_lane_index()
                        transport_db.save_to_json('transport_database.json')
                        st.success("Lane updated successfully!")
                        st.rerun()
                    
                    if cancel_update:
                        st.rerun()
        
        else:  # Delete Lane
            existing_lanes = transport_db.database
            
            if not existing_lanes:
                st.warning("No lanes available to delete.")
            else:
                # Create lane labels for selection
                lane_labels = []
                for entry in existing_lanes:
                    label = f"{entry['lane_id']}: {entry['origin']['country']}{entry['origin']['zip_code']} → {entry['destination']['country']}{entry['destination']['zip_code']}"
                    lane_labels.append(label)
                
                selected_lane_label = st.selectbox("Select Lane to Delete", lane_labels, key="delete_lane_select")
                selected_lane_index = lane_labels.index(selected_lane_label)
                selected_lane = existing_lanes[selected_lane_index]
                
                st.warning(f"⚠️ You are about to delete: **{selected_lane_label}**")
                st.info("This action cannot be undone. Make sure you have a backup if needed.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Confirm Delete", type="secondary", use_container_width=True):
                        transport_db.database.pop(selected_lane_index)
                        transport_db._build_lane_index()
                        transport_db.save_to_json('transport_database.json')
                        st.success("Lane deleted successfully!")
                        st.rerun()
                
                with col2:
                    if st.button("Cancel", use_container_width=True):
                        st.rerun()
    
    # Tab 3: Import/Export
    with tab3:
        st.subheader("Import/Export Transport Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Import Data")
            
            upload_type = st.radio("Import format:", ["Excel (Original Format)", "JSON (Database Format)"])
            
            if upload_type == "Excel (Original Format)":
                uploaded_file = st.file_uploader("Choose Excel file", type=['xlsx', 'xls'])
                if uploaded_file is not None:
                    if st.button("Import Excel Data"):
                        try:
                            temp_path = "temp_transport.xlsx"
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            transport_db.load_from_excel(temp_path)
                            transport_db.save_to_json('transport_database.json')
                            
                            st.success(f"Successfully imported {len(transport_db.database)} transport lanes!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error importing Excel: {str(e)}")
            
            else:
                uploaded_file = st.file_uploader("Choose JSON file", type=['json'])
                if uploaded_file is not None:
                    if st.button("Import JSON Data"):
                        try:
                            data = json.load(uploaded_file)
                            transport_db.weight_clusters = data['weight_clusters']
                            transport_db.database = data['database']
                            transport_db._build_lane_index()
                            transport_db.save_to_json('transport_database.json')
                            
                            st.success(f"Successfully imported {len(transport_db.database)} transport lanes!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error importing JSON: {str(e)}")
        
        with col2:
            st.markdown("### Export Data")
            
            if len(transport_db.database) > 0:
                export_format = st.radio("Export format:", ["JSON", "CSV", "Excel"])
                
                if export_format == "JSON":
                    if st.button("Export as JSON"):
                        data = {
                            'weight_clusters': transport_db.weight_clusters,
                            'database': transport_db.database
                        }
                        json_str = json.dumps(data, indent=2)
                        st.download_button(
                            label="Download JSON",
                            data=json_str,
                            file_name="transport_database.json",
                            mime="application/json"
                        )
                
                elif export_format == "CSV":
                    if st.button("Export as CSV"):
                        rows = []
                        for entry in transport_db.database:
                            row = {
                                'lane_id': entry['lane_id'],
                                'origin_country': entry['origin']['country'],
                                'origin_zip': entry['origin']['zip_code'],
                                'origin_city': entry['origin']['city'],
                                'dest_country': entry['destination']['country'],
                                'dest_zip': entry['destination']['zip_code'],
                                'dest_city': entry['destination']['city'],
                                'lead_time_groupage': entry['lead_time']['groupage'],
                                'fuel_surcharge': entry.get('fuel_surcharge', 0)
                            }
                            for weight, price in entry['prices_by_weight'].items():
                                row[f'price_{weight}kg'] = price
                            rows.append(row)
                        
                        df = pd.DataFrame(rows)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="transport_database.csv",
                            mime="text/csv"
                        )
                
                else:
                    if st.button("Export as Excel"):
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            rows = []
                            for entry in transport_db.database:
                                row = {
                                    'Lane ID': entry['lane_id'],
                                    'Origin Country': entry['origin']['country'],
                                    'Origin Zip': entry['origin']['zip_code'],
                                    'Origin City': entry['origin']['city'],
                                    'Destination Country': entry['destination']['country'],
                                    'Destination Zip': entry['destination']['zip_code'],
                                    'Destination City': entry['destination']['city'],
                                    'Lane Code': entry['lane_code'],
                                    'Lead Time Groupage': entry['lead_time']['groupage'],
                                    'Lead Time LTL': entry['lead_time']['ltl'],
                                    'Lead Time FTL': entry['lead_time']['ftl'],
                                    'Fuel Surcharge %': entry.get('fuel_surcharge', 0),
                                    'Full Truck Price': entry.get('full_truck_price', '')
                                }
                                for weight in transport_db.weight_clusters:
                                    if weight in entry['prices_by_weight']:
                                        row[f'≤ {weight} kg'] = entry['prices_by_weight'][weight]
                                rows.append(row)
                            
                            df = pd.DataFrame(rows)
                            df.to_excel(writer, sheet_name='Transport Costs', index=False)
                            
                            stats = transport_db.get_statistics()
                            df_stats = pd.DataFrame([
                                {'Metric': 'Total Lanes', 'Value': stats['total_lanes']},
                                {'Metric': 'Weight Clusters', 'Value': stats['weight_clusters']},
                                {'Metric': 'Countries', 'Value': ', '.join(stats['countries'])},
                                {'Metric': 'Min Weight', 'Value': stats['min_weight']},
                                {'Metric': 'Max Weight', 'Value': stats['max_weight']}
                            ])
                            df_stats.to_excel(writer, sheet_name='Statistics', index=False)
                        
                        st.download_button(
                            label="Download Excel",
                            data=output.getvalue(),
                            file_name="transport_database.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.info("No data to export. Please import data first.")
    
    # Tab 4: Search & Filter
    with tab4:
        st.subheader("Search and Filter Lanes")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_origin_country = st.text_input("Origin Country")
        with col2:
            search_dest_country = st.text_input("Destination Country")
        with col3:
            search_city = st.text_input("City (Origin or Destination)")
        
        weight_range = st.slider(
            "Weight Range (kg)",
            min_value=0,
            max_value=25000,
            value=(0, 25000),
            step=100
        )
        
        if st.button("Search"):
            filtered = transport_db.filter_lanes(
                origin_country=search_origin_country.upper() if search_origin_country else None,
                dest_country=search_dest_country.upper() if search_dest_country else None,
                city=search_city if search_city else None
            )
            
            if filtered:
                st.success(f"Found {len(filtered)} matching lanes")
                
                display_data = []
                for entry in filtered:
                    row = {
                        'Lane': f"{entry['origin']['country']}{entry['origin']['zip_code']} → {entry['destination']['country']}{entry['destination']['zip_code']}",
                        'Cities': f"{entry['origin']['city']} → {entry['destination']['city']}",
                        'Lead Time': entry['lead_time']['groupage'],
                    }
                    # Show all cluster prices within the selected range, sorted numerically
                    for weight in sorted(entry['prices_by_weight'].keys(), key=float):
                        w = float(weight)
                        if weight_range[0] <= w <= weight_range[1]:
                            label = f'≤ {int(w)} kg'
                            row[label] = f"€{entry['prices_by_weight'][weight]:.2f}"
                    display_data.append(row)
                
                st.dataframe(pd.DataFrame(display_data), use_container_width=True)
            else:
                st.warning("No lanes found matching the criteria")

if __name__ == "__main__":
    main()
