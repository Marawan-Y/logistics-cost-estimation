# pages/13Packaging_Data_Management.py - UPDATED WITH EXCEL/CSV/JSON IMPORT & p/n ACROSS ALL TYPES
import streamlit as st
import pandas as pd
import numpy as np
from utils.data_manager import DataManager
from utils.packaging_database import PackagingDatabase
import json
from io import BytesIO
from pathlib import Path

DB_DIR = Path("DB")
PACKAGING_JSON_CACHE = Path("packaging_database.json")  # legacy local cache for UI saves

st.set_page_config(page_title="Packaging Data Management", page_icon="📦", layout="wide")

def _df_put_pn_first(df: pd.DataFrame) -> pd.DataFrame:
    if 'pn' in df.columns:
        cols = ['pn'] + [c for c in df.columns if c != 'pn']
        return df[cols]
    return df

def _autoload_packaging_once():
    """
    Load Packaging DB from DB/Excel/Packaging.xlsx, else DB/JSON/packaging_database.json,
    else legacy local JSON cache. Run once per session.
    """
    if st.session_state.get("_packaging_autoloaded"):
        return

    packaging_db = st.session_state.packaging_db
    excel_path = DB_DIR / "Excel" / "Packaging.xlsx"
    json_path  = DB_DIR / "JSON"  / "packaging_database.json"

    loaded_from = None
    try:
        if excel_path.exists():
            packaging_db.reset_to_defaults()
            packaging_db.load_from_excel(str(excel_path))
            loaded_from = str(excel_path)
        elif json_path.exists():
            packaging_db.reset_to_defaults()
            packaging_db.load_from_json(str(json_path))
            loaded_from = str(json_path)
        elif PACKAGING_JSON_CACHE.exists():
            # last resort: local cache
            packaging_db.reset_to_defaults()
            packaging_db.load_from_json(str(PACKAGING_JSON_CACHE))
            loaded_from = str(PACKAGING_JSON_CACHE)
    except Exception as e:
        st.warning(f"Packaging autoload warning: {e}")

    if loaded_from:
        st.info(f"📥 Packaging DB auto-loaded from: `{loaded_from}`")
    else:
        st.info("📥 Packaging DB: no file found in /DB (Excel/JSON). Starting empty/default.")

    st.session_state["_packaging_autoloaded"] = True

def main():
    st.title("Packaging Data Management")
    st.markdown("Manage Packaging Database with Excel/CSV/JSON Import")
    st.markdown("---")
    
    # Initialize
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    if 'packaging_db' not in st.session_state:
        st.session_state.packaging_db = PackagingDatabase()
        try:
            st.session_state.packaging_db.load_from_json('packaging_database.json')
        except Exception:
            pass
    
    # 🔄 AUTOLOAD from /DB once per session
    _autoload_packaging_once()

    packaging_db = st.session_state.packaging_db
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 View Database", "➕ Add/Edit/Delete Item", "📁 Import/Export", "🔍 Search & Filter"])
    
    # ------------------------------ TAB 1: VIEW ------------------------------
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
                    st.dataframe(_df_put_pn_first(df_standard), use_container_width=True, hide_index=True)
                else:
                    st.info("No standard boxes configured.")
            
            with data_tabs[1]:
                if packaging_db.special_packaging:
                    df_special = pd.DataFrame.from_dict(packaging_db.special_packaging, orient='index')
                    st.dataframe(_df_put_pn_first(df_special), use_container_width=True)
                else:
                    st.info("No special packaging configured.")
            
            with data_tabs[2]:
                if packaging_db.additional_packaging:
                    df_additional = pd.DataFrame.from_dict(packaging_db.additional_packaging, orient='index')
                    st.dataframe(_df_put_pn_first(df_additional), use_container_width=True)
                else:
                    st.info("No additional packaging configured.")
                    
            with data_tabs[3]:
                if packaging_db.accessory_packaging:
                    df_accessory = pd.DataFrame.from_dict(packaging_db.accessory_packaging, orient='index')
                    st.dataframe(_df_put_pn_first(df_accessory), use_container_width=True)
                else:
                    st.info("No accessory packaging configured.")
        else:
            st.warning("No packaging data loaded. Please import data or add new items.")
    
    # --------------- TAB 2: ADD / EDIT / DELETE (with pn across all types) ---------------
    with tab2:
        st.subheader("Add, Edit, or Delete Packaging Item")

        action = st.radio("Select Action", ["Add New Item", "Edit Existing Item", "Delete Item"], horizontal=True)

        packaging_type = st.selectbox(
            "Packaging Type",
            ["Standard Boxes", "Special Packaging", "Additional Packaging", "Accessory Packaging"]
        )

        # ---------------- ADD ----------------
        if action == "Add New Item":
            item_name = st.text_input("Item Name *", help="Name of the packaging item", key="add_item_name")
            pn = st.text_input("P/N (Part Number)", help="Part number identifier", key="add_pn")

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
                            "pn": pn or item_name,
                            "name": item_name,
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
                            "pn": pn or item_name,
                            "name": item_name,
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
                            "pn": pn or item_name,
                            "name": item_name,
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
                            "pn": pn or item_name,
                            "name": item_name,
                            "No_per_PU": no_per_pu,
                            "Ave_Price": ave_price,
                            "Ave_Weight_kg": ave_weight_kg,
                            "Packaging_Characteristics": characteristics
                        }
                        packaging_db.add_accessory_packaging(item_name, item_data)
                        packaging_db.save_to_json('packaging_database.json')
                        st.success(f"Accessory packaging '{item_name}' added successfully!")
                        st.rerun()

        # ---------------- EDIT ----------------
        elif action == "Edit Existing Item":
            if packaging_type == "Standard Boxes":
                items = list(packaging_db.standard_boxes.keys())
            elif packaging_type == "Special Packaging":
                items = list(packaging_db.special_packaging.keys())
            elif packaging_type == "Additional Packaging":
                items = list(packaging_db.additional_packaging.keys())
            else:
                items = list(packaging_db.accessory_packaging.keys())

            if not items:
                st.warning(f"No {packaging_type} items to edit.")
            else:
                selected = st.selectbox("Select Item to Edit", items, key="edit_item_select")
                item_data = packaging_db.get_packaging_details(packaging_type, selected)
                pn_val = item_data.get("pn", selected)

                if packaging_type == "Standard Boxes":
                    with st.form("edit_standard_box_form"):
                        st.markdown(f"### Editing: {selected}")
                        pn_new = st.text_input("P/N (Part Number)", value=pn_val)
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
                            updated = {
                                "pn": pn_new or selected,
                                "name": selected,
                                "Packaging_Characteristics": characteristics,
                                "Cost_per_pcs": cost_per_pcs,
                                "L": length, "W": width, "H": height,
                                "MT_weight_kg": weight_kg,
                                "Pcs_Boxes_per_LU": boxes_per_lu,
                                "Boxes_per_layer": boxes_per_layer
                            }
                            packaging_db.add_standard_box(selected, updated)
                            packaging_db.save_to_json('packaging_database.json')
                            st.success(f"Standard box '{selected}' updated.")
                            st.rerun()

                elif packaging_type == "Special Packaging":
                    with st.form("edit_special_packaging_form"):
                        st.markdown(f"### Editing: {selected}")
                        pn_new = st.text_input("P/N (Part Number)", value=pn_val)
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
                            updated = {
                                "pn": pn_new or selected,
                                "name": selected,
                                "Packaging_Characteristics": characteristics,
                                "Cost_per_pcs": cost_per_pcs,
                                "L": length, "W": width, "H": height,
                                "MT_weight_kg": weight_kg,
                                "Pcs_Boxes_per_LU": boxes_per_lu,
                                "Boxes_per_layer": boxes_per_layer
                            }
                            packaging_db.add_special_packaging(selected, updated)
                            packaging_db.save_to_json('packaging_database.json')
                            st.success(f"Special packaging '{selected}' updated.")
                            st.rerun()

                elif packaging_type == "Additional Packaging":
                    with st.form("edit_additional_packaging_form"):
                        st.markdown(f"### Editing: {selected}")
                        pn_new = st.text_input("P/N (Part Number)", value=pn_val)
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
                            updated = {
                                "pn": pn_new or selected,
                                "name": selected,
                                "Packaging_Characteristics": characteristics,
                                "Cost_per_pcs": cost_per_pcs,
                                "L": length, "W": width, "H": height,
                                "MT_weight_kg": weight_kg,
                                "Pcs_Boxes_per_LU": boxes_per_lu,
                                "Boxes_per_layer": boxes_per_layer
                            }
                            packaging_db.add_additional_packaging(selected, updated)
                            packaging_db.save_to_json('packaging_database.json')
                            st.success(f"Additional packaging '{selected}' updated.")
                            st.rerun()

                else:  # Accessory
                    with st.form("edit_accessory_packaging_form"):
                        st.markdown(f"### Editing: {selected}")
                        pn_new = st.text_input("P/N (Part Number)", value=pn_val)
                        col1, col2 = st.columns(2)
                        with col1:
                            no_per_pu = st.number_input("Number per PU", value=int(item_data.get("No_per_PU", 0)), min_value=0, step=1)
                            ave_price = st.number_input("Average Price (€)", value=float(item_data.get("Ave_Price", 0)), min_value=0.0, step=0.01)
                        with col2:
                            ave_weight_kg = st.number_input("Average Weight (kg)", value=float(item_data.get("Ave_Weight_kg", 0)), min_value=0.0, step=0.01)
                            characteristics = st.text_input("Packaging Characteristics", value=item_data.get("Packaging_Characteristics", ""))
                        submitted = st.form_submit_button("Update Item", type="primary")
                        if submitted:
                            updated = {
                                "pn": pn_new or selected,
                                "name": selected,
                                "No_per_PU": no_per_pu,
                                "Ave_Price": ave_price,
                                "Ave_Weight_kg": ave_weight_kg,
                                "Packaging_Characteristics": characteristics
                            }
                            packaging_db.add_accessory_packaging(selected, updated)
                            packaging_db.save_to_json('packaging_database.json')
                            st.success(f"Accessory packaging '{selected}' updated.")
                            st.rerun()

        # ---------------- DELETE ----------------
        else:  # Delete Item
            if packaging_type == "Standard Boxes":
                items = list(packaging_db.standard_boxes.keys())
            elif packaging_type == "Special Packaging":
                items = list(packaging_db.special_packaging.keys())
            elif packaging_type == "Additional Packaging":
                items = list(packaging_db.additional_packaging.keys())
            else:
                items = list(packaging_db.accessory_packaging.keys())

            if not items:
                st.warning(f"No {packaging_type} items to delete.")
            else:
                selected = st.selectbox("Select Item to Delete", items, key="delete_item_select")
                st.warning(f"⚠️ You are about to delete: **{selected}**")
                st.info("This action cannot be undone. Make sure you have a backup if needed.")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Confirm Delete", type="secondary", use_container_width=True):
                        if packaging_type == "Standard Boxes":
                            packaging_db.remove_standard_box(selected)
                        elif packaging_type == "Special Packaging":
                            packaging_db.remove_special_packaging(selected)
                        elif packaging_type == "Additional Packaging":
                            packaging_db.remove_additional_packaging(selected)
                        else:
                            packaging_db.remove_accessory_packaging(selected)
                        packaging_db.save_to_json('packaging_database.json')
                        st.success(f"Item '{selected}' deleted successfully!")
                        st.rerun()
                with col2:
                    if st.button("Cancel", use_container_width=True):
                        st.rerun()
    
    # ------------------------------ TAB 3: IMPORT / EXPORT ------------------------------
    with tab3:
        st.subheader("Import/Export Packaging Data")
        col1, col2 = st.columns(2)
        
        # IMPORT
        with col1:
            st.markdown("### Import Data")
            upload_type = st.radio("Import format:", ["Excel", "CSV", "JSON"])
            
            if upload_type == "Excel":
                st.info("📋 **Expected Excel format:**\nColumns: p/n, Name, Packaging Characteristics, Cost per pcs, L, W, H, MT weight kg, Pcs Boxes per LU, Boxes per Layer")
                uploaded_file = st.file_uploader("Choose Excel file", type=['xlsx', 'xls'])
                if uploaded_file is not None:
                    if st.button("Import Excel Data"):
                        try:
                            temp_path = "temp_packaging.xlsx"
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            packaging_db.load_from_excel(temp_path)
                            packaging_db.save_to_json('packaging_database.json')
                            st.success(f"Successfully imported {packaging_db.get_statistics()['total_items']} packaging items!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error importing Excel: {str(e)}")
            
            elif upload_type == "CSV":
                st.info("📋 **Expected CSV format:**\nColumns: p/n, Name, Packaging Characteristics, Cost per pcs, L, W, H, MT weight kg, Pcs Boxes per LU, Boxes per Layer")
                uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
                if uploaded_file is not None:
                    if st.button("Import CSV Data"):
                        try:
                            temp_path = "temp_packaging.csv"
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            packaging_db.load_from_csv(temp_path)
                            packaging_db.save_to_json('packaging_database.json')
                            st.success(f"Successfully imported {packaging_db.get_statistics()['total_items']} packaging items!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error importing CSV: {str(e)}")
            
            else:  # JSON
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
        
        # EXPORT
        with col2:
            st.markdown("### Export Data")
            if packaging_db.get_statistics()['total_items'] > 0:
                export_format = st.radio("Export format:", ["JSON", "CSV", "Excel"])
                
                if export_format == "JSON":
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
                
                elif export_format == "CSV":
                    if st.button("Export as CSV"):
                        df = packaging_db.to_dataframe()
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="packaging_database.csv",
                            mime="text/csv"
                        )
                
                else:  # Excel
                    if st.button("Export as Excel"):
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df = packaging_db.to_dataframe()
                            df.to_excel(writer, sheet_name='Packaging', index=False)
                        st.download_button(
                            label="Download Excel",
                            data=output.getvalue(),
                            file_name="packaging_database.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.info("No data to export. Please add packaging items or import data first.")
    
    # ------------------------------ TAB 4: SEARCH ------------------------------
    with tab4:
        st.subheader("Search Packaging Items")
        search_term = st.text_input("Search by name or p/n")
        if st.button("Search") and search_term:
            results = packaging_db.search_packaging(search_term)
            found_any = False
            for category, items in results.items():
                if items:
                    found_any = True
                    st.markdown(f"### {category}")
                    df_results = pd.DataFrame.from_dict(items, orient='index')
                    st.dataframe(_df_put_pn_first(df_results), use_container_width=True)
            if not found_any:
                st.warning("No items found matching the search criteria")

if __name__ == "__main__":
    main()
