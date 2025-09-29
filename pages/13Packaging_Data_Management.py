# pages/13Packaging_Data_Management.py
import streamlit as st
import pandas as pd
import numpy as np
from utils.data_manager import DataManager
from utils.packaging_database import PackagingDatabase
import json
from io import BytesIO

st.set_page_config(page_title="Packaging Data Management", page_icon="📦", layout="wide")

def main():
    st.title("Packaging Data Management")
    st.markdown("Manage Packaging Database")
    st.markdown("---")
    
    # Initialize
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    if 'packaging_db' not in st.session_state:
        st.session_state.packaging_db = PackagingDatabase()
        try:
            st.session_state.packaging_db.load_from_json('packaging_database.json')
        except:
            pass
    
    packaging_db = st.session_state.packaging_db
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 View Database", "➕ Add/Edit/Delete Item", "📁 Import/Export", "🔍 Search & Filter"])
    
    # Tab 1: View Database
    with tab1:
        st.subheader("Packaging Database")
        
        stats = packaging_db.get_statistics()
        if stats['total_items'] > 0:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Standard Boxes", stats['standard_boxes_count'])
            col2.metric("Special Packaging", stats['special_packaging_count'])
            col3.metric("Additional Packaging", stats['additional_packaging_count'])
            col4.metric("Accessory Packaging", stats['accessory_packaging_count'])
            
            data_tabs = st.tabs(["Standard Boxes", "Special Packaging", "Additional Packaging", "Accessory Packaging"])
            
            with data_tabs[0]:
                if packaging_db.standard_boxes:
                    df_standard = pd.DataFrame.from_dict(packaging_db.standard_boxes, orient='index')
                    st.dataframe(df_standard, use_container_width=True)
                else:
                    st.info("No standard boxes configured.")
            
            with data_tabs[1]:
                if packaging_db.special_packaging:
                    df_special = pd.DataFrame.from_dict(packaging_db.special_packaging, orient='index')
                    st.dataframe(df_special, use_container_width=True)
                else:
                    st.info("No special packaging configured.")
            
            with data_tabs[2]:
                if packaging_db.additional_packaging:
                    df_additional = pd.DataFrame.from_dict(packaging_db.additional_packaging, orient='index')
                    st.dataframe(df_additional, use_container_width=True)
                else:
                    st.info("No additional packaging configured.")
                    
            with data_tabs[3]:
                if packaging_db.accessory_packaging:
                    df_accessory = pd.DataFrame.from_dict(packaging_db.accessory_packaging, orient='index')
                    st.dataframe(df_accessory, use_container_width=True)
                else:
                    st.info("No accessory packaging configured.")
        else:
            st.warning("No packaging data loaded. Please import data or add new items.")
    
    # Tab 2: Add/Edit/Delete Item
    with tab2:
        st.subheader("Add, Edit, or Delete Packaging Item")
        
        # Action selector
        action = st.radio("Select Action", ["Add New Item", "Edit Existing Item", "Delete Item"], horizontal=True)
        
        packaging_type = st.selectbox(
            "Packaging Type",
            ["Standard Boxes", "Special Packaging", "Additional Packaging", "Accessory Packaging"]
        )
        
        if action == "Add New Item":
            item_name = st.text_input("Item Name *", help="Name of the packaging item", key="add_item_name")
            
            if packaging_type == "Standard Boxes":
                with st.form("add_standard_box_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        characteristics = st.text_input("Packaging Characteristics", value="")
                        cost_per_pcs = st.number_input("Cost per Piece (€)", min_value=0.0, step=0.01)
                        length = st.number_input("Length (mm)", min_value=0, step=1)
                        width = st.number_input("Width (mm)", min_value=0, step=1)
                        height = st.number_input("Height (mm)", min_value=0, step=1)
                    
                    with col2:
                        weight_kg = st.number_input("Weight (kg)", min_value=0.0, step=0.01)
                        boxes_per_lu = st.number_input("Boxes per LU", min_value=0, step=1)
                        boxes_per_layer = st.number_input("Boxes per Layer", min_value=0, step=1)
                    
                    submitted = st.form_submit_button("Add Item", type="primary")
                    
                    if submitted and item_name:
                        item_data = {
                            "Packaging_Characteristics": characteristics,
                            "Cost_per_pcs": cost_per_pcs,
                            "L": length,
                            "W": width,
                            "H": height,
                            "MT_weight_kg": weight_kg,
                            "Pcs_Boxes_per_LU": boxes_per_lu,
                            "Boxes_per_layer": boxes_per_layer
                        }
                        
                        packaging_db.add_standard_box(item_name, item_data)
                        packaging_db.save_to_json('packaging_database.json')
                        st.success(f"Standard box '{item_name}' added successfully!")
                        st.rerun()
            
            elif packaging_type == "Special Packaging":
                with st.form("add_special_packaging_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        characteristics = st.text_input("Packaging Characteristics", value="")
                        cost_per_pcs = st.number_input("Cost per Piece (€)", min_value=0.0, step=0.01)
                        length = st.text_input("Length", value="")
                        width = st.text_input("Width", value="")
                    
                    with col2:
                        height = st.text_input("Height", value="")
                        weight_kg = st.number_input("Weight (kg)", min_value=0.0, step=0.01)
                        boxes_per_lu = st.text_input("Boxes per LU", value="")
                        boxes_per_layer = st.text_input("Boxes per Layer", value="")
                    
                    submitted = st.form_submit_button("Add Item", type="primary")
                    
                    if submitted and item_name:
                        item_data = {
                            "Packaging_Characteristics": characteristics,
                            "Cost_per_pcs": cost_per_pcs,
                            "L": length,
                            "W": width,
                            "H": height,
                            "MT_weight_kg": weight_kg,
                            "Pcs_Boxes_per_LU": boxes_per_lu,
                            "Boxes_per_layer": boxes_per_layer
                        }
                        
                        packaging_db.add_special_packaging(item_name, item_data)
                        packaging_db.save_to_json('packaging_database.json')
                        st.success(f"Special packaging '{item_name}' added successfully!")
                        st.rerun()
            
            elif packaging_type == "Additional Packaging":
                with st.form("add_additional_packaging_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        characteristics = st.text_input("Packaging Characteristics", value="")
                        cost_per_pcs = st.number_input("Cost per Piece (€)", min_value=0.0, step=0.01)
                        length = st.number_input("Length (mm)", min_value=0, step=1)
                        width = st.number_input("Width (mm)", min_value=0, step=1)
                    
                    with col2:
                        height = st.number_input("Height (mm)", min_value=0, step=1)
                        weight_kg = st.number_input("Weight (kg)", min_value=0.0, step=0.01)
                        boxes_per_lu = st.number_input("Boxes per LU", min_value=0, step=1)
                        boxes_per_layer = st.number_input("Boxes per Layer", min_value=0, step=1)
                    
                    submitted = st.form_submit_button("Add Item", type="primary")
                    
                    if submitted and item_name:
                        item_data = {
                            "Packaging_Characteristics": characteristics,
                            "Cost_per_pcs": cost_per_pcs,
                            "L": length,
                            "W": width,
                            "H": height,
                            "MT_weight_kg": weight_kg,
                            "Pcs_Boxes_per_LU": boxes_per_lu,
                            "Boxes_per_layer": boxes_per_layer
                        }
                        
                        packaging_db.add_additional_packaging(item_name, item_data)
                        packaging_db.save_to_json('packaging_database.json')
                        st.success(f"Additional packaging '{item_name}' added successfully!")
                        st.rerun()
            
            else:  # Accessory Packaging
                with st.form("add_accessory_packaging_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        no_per_pu = st.number_input("Number per PU", min_value=0, step=1)
                        ave_price = st.number_input("Average Price (€)", min_value=0.0, step=0.01)
                    
                    with col2:
                        ave_weight_kg = st.number_input("Average Weight (kg)", min_value=0.0, step=0.01)
                        characteristics = st.text_input("Packaging Characteristics", value="")
                    
                    submitted = st.form_submit_button("Add Item", type="primary")
                    
                    if submitted and item_name:
                        item_data = {
                            "No_per_PU": no_per_pu,
                            "Ave_Price": ave_price,
                            "Ave_Weight_kg": ave_weight_kg,
                            "Packaging_Characteristics": characteristics
                        }
                        
                        packaging_db.add_accessory_packaging(item_name, item_data)
                        packaging_db.save_to_json('packaging_database.json')
                        st.success(f"Accessory packaging '{item_name}' added successfully!")
                        st.rerun()
        
        elif action == "Edit Existing Item":
            # Get existing items for selected packaging type
            if packaging_type == "Standard Boxes":
                existing_items = list(packaging_db.standard_boxes.keys())
            elif packaging_type == "Special Packaging":
                existing_items = list(packaging_db.special_packaging.keys())
            elif packaging_type == "Additional Packaging":
                existing_items = list(packaging_db.additional_packaging.keys())
            else:
                existing_items = list(packaging_db.accessory_packaging.keys())
            
            if not existing_items:
                st.warning(f"No {packaging_type} items to edit.")
            else:
                selected_item = st.selectbox("Select Item to Edit", existing_items, key="edit_item_select")
                
                # Get current item data
                item_data = packaging_db.get_packaging_details(packaging_type, selected_item)
                
                if packaging_type == "Standard Boxes":
                    with st.form("edit_standard_box_form"):
                        st.markdown(f"### Editing: {selected_item}")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            characteristics = st.text_input("Packaging Characteristics", value=item_data.get("Packaging_Characteristics", ""))
                            cost_per_pcs = st.number_input("Cost per Piece (€)", value=float(item_data.get("Cost_per_pcs", 0)), min_value=0.0, step=0.01)
                            length = st.number_input("Length (mm)", value=int(item_data.get("L", 0)), min_value=0, step=1)
                            width = st.number_input("Width (mm)", value=int(item_data.get("W", 0)), min_value=0, step=1)
                            height = st.number_input("Height (mm)", value=int(item_data.get("H", 0)), min_value=0, step=1)
                        
                        with col2:
                            weight_kg = st.number_input("Weight (kg)", value=float(item_data.get("MT_weight_kg", 0)), min_value=0.0, step=0.01)
                            boxes_per_lu = st.number_input("Boxes per LU", value=int(item_data.get("Pcs_Boxes_per_LU", 0)), min_value=0, step=1)
                            boxes_per_layer = st.number_input("Boxes per Layer", value=int(item_data.get("Boxes_per_layer", 0)), min_value=0, step=1)
                        
                        submitted = st.form_submit_button("Update Item", type="primary")
                        
                        if submitted:
                            updated_data = {
                                "Packaging_Characteristics": characteristics,
                                "Cost_per_pcs": cost_per_pcs,
                                "L": length,
                                "W": width,
                                "H": height,
                                "MT_weight_kg": weight_kg,
                                "Pcs_Boxes_per_LU": boxes_per_lu,
                                "Boxes_per_layer": boxes_per_layer
                            }
                            
                            packaging_db.add_standard_box(selected_item, updated_data)
                            packaging_db.save_to_json('packaging_database.json')
                            st.success(f"Standard box '{selected_item}' updated successfully!")
                            st.rerun()
                
                elif packaging_type == "Special Packaging":
                    with st.form("edit_special_packaging_form"):
                        st.markdown(f"### Editing: {selected_item}")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            characteristics = st.text_input("Packaging Characteristics", value=item_data.get("Packaging_Characteristics", ""))
                            cost_per_pcs = st.number_input("Cost per Piece (€)", value=float(item_data.get("Cost_per_pcs", 0)), min_value=0.0, step=0.01)
                            length = st.text_input("Length", value=str(item_data.get("L", "")))
                            width = st.text_input("Width", value=str(item_data.get("W", "")))
                        
                        with col2:
                            height = st.text_input("Height", value=str(item_data.get("H", "")))
                            weight_kg = st.number_input("Weight (kg)", value=float(item_data.get("MT_weight_kg", 0)), min_value=0.0, step=0.01)
                            boxes_per_lu = st.text_input("Boxes per LU", value=str(item_data.get("Pcs_Boxes_per_LU", "")))
                            boxes_per_layer = st.text_input("Boxes per Layer", value=str(item_data.get("Boxes_per_layer", "")))
                        
                        submitted = st.form_submit_button("Update Item", type="primary")
                        
                        if submitted:
                            updated_data = {
                                "Packaging_Characteristics": characteristics,
                                "Cost_per_pcs": cost_per_pcs,
                                "L": length,
                                "W": width,
                                "H": height,
                                "MT_weight_kg": weight_kg,
                                "Pcs_Boxes_per_LU": boxes_per_lu,
                                "Boxes_per_layer": boxes_per_layer
                            }
                            
                            packaging_db.add_special_packaging(selected_item, updated_data)
                            packaging_db.save_to_json('packaging_database.json')
                            st.success(f"Special packaging '{selected_item}' updated successfully!")
                            st.rerun()
                
                elif packaging_type == "Additional Packaging":
                    with st.form("edit_additional_packaging_form"):
                        st.markdown(f"### Editing: {selected_item}")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            characteristics = st.text_input("Packaging Characteristics", value=item_data.get("Packaging_Characteristics", ""))
                            cost_per_pcs = st.number_input("Cost per Piece (€)", value=float(item_data.get("Cost_per_pcs", 0)), min_value=0.0, step=0.01)
                            length = st.number_input("Length (mm)", value=int(item_data.get("L", 0)), min_value=0, step=1)
                            width = st.number_input("Width (mm)", value=int(item_data.get("W", 0)), min_value=0, step=1)
                        
                        with col2:
                            height = st.number_input("Height (mm)", value=int(item_data.get("H", 0)), min_value=0, step=1)
                            weight_kg = st.number_input("Weight (kg)", value=float(item_data.get("MT_weight_kg", 0)), min_value=0.0, step=0.01)
                            boxes_per_lu = st.number_input("Boxes per LU", value=int(item_data.get("Pcs_Boxes_per_LU", 0)), min_value=0, step=1)
                            boxes_per_layer = st.number_input("Boxes per Layer", value=int(item_data.get("Boxes_per_layer", 0)), min_value=0, step=1)
                        
                        submitted = st.form_submit_button("Update Item", type="primary")
                        
                        if submitted:
                            updated_data = {
                                "Packaging_Characteristics": characteristics,
                                "Cost_per_pcs": cost_per_pcs,
                                "L": length,
                                "W": width,
                                "H": height,
                                "MT_weight_kg": weight_kg,
                                "Pcs_Boxes_per_LU": boxes_per_lu,
                                "Boxes_per_layer": boxes_per_layer
                            }
                            
                            packaging_db.add_additional_packaging(selected_item, updated_data)
                            packaging_db.save_to_json('packaging_database.json')
                            st.success(f"Additional packaging '{selected_item}' updated successfully!")
                            st.rerun()
                
                else:  # Accessory Packaging
                    with st.form("edit_accessory_packaging_form"):
                        st.markdown(f"### Editing: {selected_item}")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            no_per_pu = st.number_input("Number per PU", value=int(item_data.get("No_per_PU", 0)), min_value=0, step=1)
                            ave_price = st.number_input("Average Price (€)", value=float(item_data.get("Ave_Price", 0)), min_value=0.0, step=0.01)
                        
                        with col2:
                            ave_weight_kg = st.number_input("Average Weight (kg)", value=float(item_data.get("Ave_Weight_kg", 0)), min_value=0.0, step=0.01)
                            characteristics = st.text_input("Packaging Characteristics", value=item_data.get("Packaging_Characteristics", ""))
                        
                        submitted = st.form_submit_button("Update Item", type="primary")
                        
                        if submitted:
                            updated_data = {
                                "No_per_PU": no_per_pu,
                                "Ave_Price": ave_price,
                                "Ave_Weight_kg": ave_weight_kg,
                                "Packaging_Characteristics": characteristics
                            }
                            
                            packaging_db.add_accessory_packaging(selected_item, updated_data)
                            packaging_db.save_to_json('packaging_database.json')
                            st.success(f"Accessory packaging '{selected_item}' updated successfully!")
                            st.rerun()
        
        else:  # Delete Item
            # Get existing items for selected packaging type
            if packaging_type == "Standard Boxes":
                existing_items = list(packaging_db.standard_boxes.keys())
            elif packaging_type == "Special Packaging":
                existing_items = list(packaging_db.special_packaging.keys())
            elif packaging_type == "Additional Packaging":
                existing_items = list(packaging_db.additional_packaging.keys())
            else:
                existing_items = list(packaging_db.accessory_packaging.keys())
            
            if not existing_items:
                st.warning(f"No {packaging_type} items to delete.")
            else:
                selected_item = st.selectbox("Select Item to Delete", existing_items, key="delete_item_select")
                
                st.warning(f"⚠️ You are about to delete: **{selected_item}**")
                st.info("This action cannot be undone. Make sure you have a backup if needed.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Confirm Delete", type="secondary", use_container_width=True):
                        if packaging_type == "Standard Boxes":
                            packaging_db.remove_standard_box(selected_item)
                        elif packaging_type == "Special Packaging":
                            packaging_db.remove_special_packaging(selected_item)
                        elif packaging_type == "Additional Packaging":
                            packaging_db.remove_additional_packaging(selected_item)
                        else:
                            packaging_db.remove_accessory_packaging(selected_item)
                        
                        packaging_db.save_to_json('packaging_database.json')
                        st.success(f"Item '{selected_item}' deleted successfully!")
                        st.rerun()
                
                with col2:
                    if st.button("Cancel", use_container_width=True):
                        st.rerun()
    
    # Tab 3: Import/Export
    with tab3:
        st.subheader("Import/Export Packaging Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Import Data")
            
            uploaded_file = st.file_uploader("Choose JSON file", type=['json'])
            if uploaded_file is not None:
                if st.button("Import JSON Data"):
                    try:
                        data = json.load(uploaded_file)
                        packaging_db.standard_boxes = data.get('standard_boxes', {})
                        packaging_db.special_packaging = data.get('special_packaging', {})
                        packaging_db.additional_packaging = data.get('additional_packaging', {})
                        packaging_db.accessory_packaging = data.get('accessory_packaging', {})
                        packaging_db.save_to_json('packaging_database.json')
                        
                        st.success("Successfully imported packaging data!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error importing JSON: {str(e)}")
            
            if st.button("Reset to Defaults"):
                packaging_db.reset_to_defaults()
                packaging_db.save_to_json('packaging_database.json')
                st.success("Reset to default packaging data!")
                st.rerun()
        
        with col2:
            st.markdown("### Export Data")
            
            if st.button("Export as JSON"):
                data = {
                    'standard_boxes': packaging_db.standard_boxes,
                    'special_packaging': packaging_db.special_packaging,
                    'additional_packaging': packaging_db.additional_packaging,
                    'accessory_packaging': packaging_db.accessory_packaging
                }
                json_str = json.dumps(data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name="packaging_database.json",
                    mime="application/json"
                )
    
    # Tab 4: Search & Filter
    with tab4:
        st.subheader("Search Packaging Items")
        
        search_term = st.text_input("Search by name")
        
        if st.button("Search") and search_term:
            results = packaging_db.search_packaging(search_term)
            
            found_any = False
            for category, items in results.items():
                if items:
                    found_any = True
                    st.markdown(f"### {category}")
                    df_results = pd.DataFrame.from_dict(items, orient='index')
                    st.dataframe(df_results, use_container_width=True)
            
            if not found_any:
                st.warning("No items found matching the search criteria")

if __name__ == "__main__":
    main()