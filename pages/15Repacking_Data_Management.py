# pages/15Repacking_Data_Management.py
import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.repacking_database import RepackingDatabase
import json

st.set_page_config(page_title="Repacking Data Management", page_icon="🔄", layout="wide")

def main():
    st.title("Repacking Data Management")
    st.markdown("Manage Repacking Cost Database")
    st.markdown("---")
    
    # Initialize
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    if 'repacking_db' not in st.session_state:
        st.session_state.repacking_db = RepackingDatabase()
        try:
            st.session_state.repacking_db.load_from_json('repacking_database.json')
        except:
            pass
    
    repacking_db = st.session_state.repacking_db
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 View Database", "➕ Add/Edit/Delete Operation", "📁 Import/Export", "🔍 Search & Filter"])
    
    # Tab 1: View Database
    with tab1:
        st.subheader("Repacking Cost Database")
        
        stats = repacking_db.get_statistics()
        if stats['total_operations'] > 0:
            col1, col2, col3 = st.columns(3)
            col1.metric("Weight Categories", stats['weight_categories'])
            col2.metric("Total Operations", stats['total_operations'])
            
            # Display data by weight category
            for category in stats['categories']:
                st.markdown(f"### {category}")
                operations = repacking_db.get_operations_for_category(category)
                
                if operations:
                    df_operations = pd.DataFrame(operations)
                    st.dataframe(df_operations, use_container_width=True)
                else:
                    st.info(f"No operations defined for {category}")
        else:
            st.warning("No repacking data loaded. Please import data or add new operations.")
    
    # Tab 2: Add/Edit/Delete Operation
    with tab2:
        st.subheader("Add, Edit, or Delete Repacking Operation")
        
        # Action selector
        action = st.radio("Select Action", ["Add New Operation", "Edit Existing Operation", "Delete Operation"], horizontal=True)
        
        # Weight category selection
        existing_categories = repacking_db.get_weight_categories()
        
        if action == "Add New Operation":
            col1, col2 = st.columns([2, 1])
            with col1:
                category_option = st.radio(
                    "Weight Category",
                    ["Select existing", "Create new"]
                )
            
            if category_option == "Select existing":
                if existing_categories:
                    weight_category = st.selectbox("Select Weight Category", existing_categories)
                else:
                    st.warning("No existing categories. Please create a new one.")
                    weight_category = None
            else:
                weight_category = st.text_input("New Weight Category", 
                                              help="e.g., 'light (up to 0,050kg)'")
            
            if weight_category:
                with st.form("add_repacking_operation_form"):
                    st.markdown(f"### Adding operation for: **{weight_category}**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        supplier_packaging = st.selectbox(
                            "Supplier Packaging Type",
                            [
                                "N/A",
                                "one-way tray in cardboard/wooden box",
                                "Bulk (poss. in bag) in cardboard/wooden box",
                                "Einwegblister im Karton/Holzkiste"
                            ]
                        )
                        
                        operation_type = st.text_input(
                            "Operation Type",
                            help="e.g., 'each part individually', 'each tray individually'"
                        )
                    
                    with col2:
                        kb_packaging = st.selectbox(
                            "KB Packaging Type",
                            [
                                "N/A",
                                "returnable trays", 
                                "one-way tray in KLT",
                                "KLT"
                            ]
                        )
                        
                        col2a, col2b = st.columns(2)
                        with col2a:
                            cost = st.number_input("Cost", min_value=0.0, step=0.01)
                        with col2b:
                            unit = st.selectbox("Unit", ["per part", "per tray", "per bag/bulk transfer"])
                    
                    submitted = st.form_submit_button("Add Operation", type="primary")
                    
                    if submitted:
                        operation_data = {
                            "supplier_packaging": supplier_packaging,
                            "operation_type": operation_type,
                            "kb_packaging": kb_packaging,
                            "cost": cost,
                            "unit": unit
                        }
                        
                        repacking_db.add_operation_to_category(weight_category, operation_data)
                        repacking_db.save_to_json('repacking_database.json')
                        st.success(f"Operation added to '{weight_category}' successfully!")
                        st.rerun()
        
        elif action == "Edit Existing Operation":
            if not existing_categories:
                st.warning("No weight categories available to edit.")
            else:
                selected_category = st.selectbox("Select Weight Category", existing_categories, key="edit_category")
                operations = repacking_db.get_operations_for_category(selected_category)
                
                if not operations:
                    st.warning(f"No operations found in category '{selected_category}'")
                else:
                    # Create operation labels for selection
                    operation_labels = []
                    for i, op in enumerate(operations):
                        label = f"Op {i+1}: {op['supplier_packaging']} → {op['kb_packaging']} (€{op['cost']} {op['unit']})"
                        operation_labels.append(label)
                    
                    selected_op_label = st.selectbox("Select Operation to Edit", operation_labels, key="edit_operation")
                    selected_op_index = operation_labels.index(selected_op_label)
                    selected_operation = operations[selected_op_index]
                    
                    with st.form("edit_repacking_operation_form"):
                        st.markdown(f"### Editing Operation {selected_op_index + 1} in '{selected_category}'")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            supplier_packaging = st.selectbox(
                                "Supplier Packaging Type",
                                [
                                    "N/A",
                                    "one-way tray in cardboard/wooden box",
                                    "Bulk (poss. in bag) in cardboard/wooden box",
                                    "Einwegblister im Karton/Holzkiste"
                                ],
                                index=[
                                    "N/A",
                                    "one-way tray in cardboard/wooden box",
                                    "Bulk (poss. in bag) in cardboard/wooden box",
                                    "Einwegblister im Karton/Holzkiste"
                                ].index(selected_operation['supplier_packaging']) if selected_operation['supplier_packaging'] in [
                                    "N/A",
                                    "one-way tray in cardboard/wooden box",
                                    "Bulk (poss. in bag) in cardboard/wooden box",
                                    "Einwegblister im Karton/Holzkiste"
                                ] else 0
                            )
                            
                            operation_type = st.text_input(
                                "Operation Type",
                                value=selected_operation['operation_type']
                            )
                        
                        with col2:
                            kb_packaging = st.selectbox(
                                "KB Packaging Type",
                                [
                                    "N/A",
                                    "returnable trays", 
                                    "one-way tray in KLT",
                                    "KLT"
                                ],
                                index=[
                                    "N/A",
                                    "returnable trays", 
                                    "one-way tray in KLT",
                                    "KLT"
                                ].index(selected_operation['kb_packaging']) if selected_operation['kb_packaging'] in [
                                    "N/A",
                                    "returnable trays", 
                                    "one-way tray in KLT",
                                    "KLT"
                                ] else 0
                            )
                            
                            col2a, col2b = st.columns(2)
                            with col2a:
                                cost = st.number_input("Cost", value=float(selected_operation['cost']), min_value=0.0, step=0.01)
                            with col2b:
                                unit = st.selectbox(
                                    "Unit", 
                                    ["per part", "per tray", "per bag/bulk transfer"],
                                    index=["per part", "per tray", "per bag/bulk transfer"].index(selected_operation['unit']) if selected_operation['unit'] in ["per part", "per tray", "per bag/bulk transfer"] else 0
                                )
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("Update Operation", type="primary"):
                                updated_operation = {
                                    "supplier_packaging": supplier_packaging,
                                    "operation_type": operation_type,
                                    "kb_packaging": kb_packaging,
                                    "cost": cost,
                                    "unit": unit
                                }
                                
                                repacking_db.update_operation_in_category(selected_category, selected_op_index, updated_operation)
                                repacking_db.save_to_json('repacking_database.json')
                                st.success(f"Operation updated successfully!")
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.rerun()
        
        else:  # Delete Operation
            if not existing_categories:
                st.warning("No weight categories available.")
            else:
                selected_category = st.selectbox("Select Weight Category", existing_categories, key="delete_category")
                operations = repacking_db.get_operations_for_category(selected_category)
                
                if not operations:
                    st.warning(f"No operations found in category '{selected_category}'")
                else:
                    # Create operation labels for selection
                    operation_labels = []
                    for i, op in enumerate(operations):
                        label = f"Op {i+1}: {op['supplier_packaging']} → {op['kb_packaging']} (€{op['cost']} {op['unit']})"
                        operation_labels.append(label)
                    
                    selected_op_label = st.selectbox("Select Operation to Delete", operation_labels, key="delete_operation")
                    selected_op_index = operation_labels.index(selected_op_label)
                    
                    st.warning(f"⚠️ You are about to delete: **{selected_op_label}**")
                    st.info("This action cannot be undone. Make sure you have a backup if needed.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Confirm Delete", type="secondary", use_container_width=True):
                            repacking_db.remove_operation_from_category(selected_category, selected_op_index)
                            repacking_db.save_to_json('repacking_database.json')
                            st.success("Operation deleted successfully!")
                            st.rerun()
                    
                    with col2:
                        if st.button("Cancel", use_container_width=True):
                            st.rerun()
    
    # Tab 3: Import/Export
    with tab3:
        st.subheader("Import/Export Repacking Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Import Data")
            
            uploaded_file = st.file_uploader("Choose JSON file", type=['json'])
            if uploaded_file is not None:
                if st.button("Import JSON Data"):
                    try:
                        data = json.load(uploaded_file)
                        repacking_db.operation_costs = data.get('operation_costs', {})
                        repacking_db.save_to_json('repacking_database.json')
                        
                        st.success("Successfully imported repacking data!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error importing JSON: {str(e)}")
            
            if st.button("Reset to Defaults"):
                repacking_db.reset_to_defaults()
                repacking_db.save_to_json('repacking_database.json')
                st.success("Reset to default repacking data!")
                st.rerun()
        
        with col2:
            st.markdown("### Export Data")
            
            if st.button("Export as JSON"):
                data = {
                    'operation_costs': repacking_db.operation_costs
                }
                json_str = json.dumps(data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name="repacking_database.json",
                    mime="application/json"
                )
    
    # Tab 4: Search & Filter
    with tab4:
        st.subheader("Search Repacking Operations")
        
        search_term = st.text_input("Search by packaging type or operation")
        
        if st.button("Search") and search_term:
            results = repacking_db.search_operations(search_term)
            
            if results:
                for category, operations in results.items():
                    st.markdown(f"### {category}")
                    df_results = pd.DataFrame(operations)
                    st.dataframe(df_results, use_container_width=True)
            else:
                st.warning("No operations found matching the search criteria")

if __name__ == "__main__":
    main()