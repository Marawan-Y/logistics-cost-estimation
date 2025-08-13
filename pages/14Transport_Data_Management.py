# pages/15_Transport_Data_Management.py
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
        # Try to load existing database
        try:
            st.session_state.transport_db.load_from_json('transport_database.json')
        except:
            pass
    
    transport_db = st.session_state.transport_db
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 View Database", "➕ Add/Edit Lane", "📁 Import/Export", "🔍 Search & Filter"])
    
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
                use_container_width=False,  # Allow horizontal scrolling
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
            
            # Apply filters
            if filter_origin != "All":
                df_display = df_display[df_display['Origin Country'] == filter_origin]
            if filter_dest != "All":
                df_display = df_display[df_display['Dest Country'] == filter_dest]
            if search_text:
                mask = (df_display['Origin City'].str.contains(search_text, case=False, na=False) | 
                       df_display['Dest City'].str.contains(search_text, case=False, na=False))
                df_display = df_display[mask]
            
            # Display with pagination
            rows_per_page = st.number_input("Rows per page", min_value=10, max_value=100, value=20)
            total_pages = len(df_display) // rows_per_page + (1 if len(df_display) % rows_per_page > 0 else 0)
            
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 0
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("⬅️ Previous", disabled=st.session_state.current_page == 0):
                    st.session_state.current_page -= 1
            with col2:
                st.write(f"Page {st.session_state.current_page + 1} of {max(1, total_pages)}")
            with col3:
                if st.button("Next ➡️", disabled=st.session_state.current_page >= total_pages - 1):
                    st.session_state.current_page += 1
            
            # Display current page
            start_idx = st.session_state.current_page * rows_per_page
            end_idx = min(start_idx + rows_per_page, len(df_display))
            
            st.dataframe(
                df_display.iloc[start_idx:end_idx],
                use_container_width=True,
                height=600
            )
            
            st.info(f"Showing {end_idx - start_idx} of {len(df_display)} total lanes")
        else:
            st.warning("No transport data loaded. Please import data in the Import/Export tab.")
    
    # Tab 2: Add/Edit Lane
    with tab2:
        st.subheader("Add or Edit Transport Lane")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Origin Information")
            origin_country = st.text_input("Origin Country Code *", max_chars=2)
            origin_zip = st.text_input("Origin Zip Code (2-digit) *", max_chars=5)
            origin_city = st.text_input("Origin City")
        
        with col2:
            st.markdown("### Destination Information")
            dest_country = st.text_input("Destination Country Code *", max_chars=2)
            dest_zip = st.text_input("Destination Zip Code (2-digit) *", max_chars=5)
            dest_city = st.text_input("Destination City")
        
        st.markdown("### Lead Times")
        col1, col2, col3 = st.columns(3)
        with col1:
            lead_groupage = st.text_input("Lead Time Groupage", value="2-5")
        with col2:
            lead_ltl = st.text_input("Lead Time LTL", value="2-5")
        with col3:
            lead_ftl = st.text_input("Lead Time FTL", value="1-3")
        
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
                            key=f"price_{weight}"
                        )
        
        # Full truck price
        st.markdown("### Special Pricing")
        col1, col2 = st.columns(2)
        with col1:
            full_truck_price = st.text_input("Full Truck Price", value="Contact for price")
        with col2:
            fuel_surcharge = st.number_input("Fuel Surcharge (%)", min_value=0.0, max_value=100.0, step=0.01)
        
        if st.button("Add/Update Lane", type="primary"):
            if origin_country and origin_zip and dest_country and dest_zip:
                # Create new entry
                new_entry = {
                    "lane_id": f"{len(transport_db.database) + 1}",
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
                    # Update existing
                    for i, entry in enumerate(transport_db.database):
                        if entry['lane_id'] == existing['lane_id']:
                            transport_db.database[i] = new_entry
                            new_entry['lane_id'] = existing['lane_id']
                            break
                    st.success("Lane updated successfully!")
                else:
                    # Add new
                    transport_db.database.append(new_entry)
                    transport_db._build_lane_index()
                    st.success("New lane added successfully!")
                
                # Save database
                transport_db.save_to_json('transport_database.json')
                st.rerun()
            else:
                st.error("Please fill in all required fields marked with *")
    
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
                            # Save temporary file
                            temp_path = "temp_transport.xlsx"
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Load into database
                            transport_db.load_from_excel(temp_path)
                            transport_db.save_to_json('transport_database.json')
                            
                            st.success(f"Successfully imported {len(transport_db.database)} transport lanes!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error importing Excel: {str(e)}")
            
            else:  # JSON format
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
                        # Convert to flat structure for CSV
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
                            # Add all price points
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
                
                else:  # Excel
                    if st.button("Export as Excel"):
                        # Create Excel file with multiple sheets
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            # Main data sheet
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
                                # Add weight-based prices
                                for weight in transport_db.weight_clusters:
                                    if weight in entry['prices_by_weight']:
                                        row[f'≤ {weight} kg'] = entry['prices_by_weight'][weight]
                                rows.append(row)
                            
                            df = pd.DataFrame(rows)
                            df.to_excel(writer, sheet_name='Transport Costs', index=False)
                            
                            # Statistics sheet
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
            # Filter results
            filtered = transport_db.filter_lanes(
                origin_country=search_origin_country.upper() if search_origin_country else None,
                dest_country=search_dest_country.upper() if search_dest_country else None,
                city=search_city if search_city else None
            )
            
            if filtered:
                st.success(f"Found {len(filtered)} matching lanes")
                
                # Display results
                display_data = []
                for entry in filtered:
                    # Find price for the weight range
                    avg_weight = (weight_range[0] + weight_range[1]) / 2
                    price = "N/A"
                    for weight in sorted(entry['prices_by_weight'].keys()):
                        if avg_weight <= weight:
                            price = f"€{entry['prices_by_weight'][weight]:.2f}"
                            break
                    
                    display_data.append({
                        'Lane': f"{entry['origin']['country']}{entry['origin']['zip_code']} → {entry['destination']['country']}{entry['destination']['zip_code']}",
                        'Cities': f"{entry['origin']['city']} → {entry['destination']['city']}",
                        'Lead Time': entry['lead_time']['groupage'],
                        f'Price (~{int(avg_weight)}kg)': price
                    })
                
                st.dataframe(pd.DataFrame(display_data), use_container_width=True)
            else:
                st.warning("No lanes found matching the criteria")
    
    # # Tab 5: Statistics
    # with tab5:
    #     st.subheader("Database Statistics -- Soon!")
        
        # if len(transport_db.database) > 0:
        #     stats = transport_db.get_statistics()
            
        #     col1, col2, col3 = st.columns(3)
            
        #     with col1:
        #         st.metric("Total Lanes", stats['total_lanes'])
        #         st.metric("Weight Clusters", stats['weight_clusters'])
            
        #     with col2:
        #         st.metric("Countries", len(stats['countries']))
        #         st.metric("Min Weight Cluster", f"{stats['min_weight']} kg")
            
        #     with col3:
        #         st.metric("Max Weight Cluster", f"{stats['max_weight']:,} kg")
        #         st.metric("Avg Lanes per Country", f"{stats['total_lanes'] / max(1, len(stats['countries'])):.1f}")
            
        #     # Country distribution
        #     st.markdown("### Country Coverage")
        #     country_counts = {}
        #     for entry in transport_db.database:
        #         orig = entry['origin']['country']
        #         dest = entry['destination']['country']
        #         country_counts[orig] = country_counts.get(orig, 0) + 1
        #         country_counts[dest] = country_counts.get(dest, 0) + 1
            
        #     df_countries = pd.DataFrame(
        #         [(k, v) for k, v in country_counts.items()],
        #         columns=['Country', 'Lane Count']
        #     ).sort_values('Lane Count', ascending=False)
            
        #     st.bar_chart(df_countries.set_index('Country'))
            
        #     # Price analysis
        #     st.markdown("### Price Analysis")
            
        #     # Collect all prices for analysis
        #     all_prices = []
        #     for entry in transport_db.database:
        #         for weight, price in entry['prices_by_weight'].items():
        #             all_prices.append({
        #                 'weight': weight,
        #                 'price': price,
        #                 'route': f"{entry['origin']['country']} → {entry['destination']['country']}"
        #             })
            
        #     if all_prices:
        #         df_prices = pd.DataFrame(all_prices)
                
        #         # Average price by weight cluster
        #         avg_prices = df_prices.groupby('weight')['price'].agg(['mean', 'min', 'max', 'count'])
        #         st.dataframe(avg_prices, use_container_width=True)
                
        #         # Price distribution chart
        #         st.line_chart(avg_prices['mean'])
        # else:
        #     st.info("No data loaded. Please import transport data to view statistics.")

if __name__ == "__main__":
    main()