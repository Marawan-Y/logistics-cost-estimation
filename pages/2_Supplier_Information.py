# ------2_Supplier_Information.py-------
import streamlit as st
from utils.validators import SupplierValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Supplier Information", page_icon="🏭")

def main():
    st.title("Supplier Information")
    st.markdown("Configure supplier details for logistics cost calculation")
    st.markdown("---")
    
    # Initialize data manager
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    data_manager = st.session_state.data_manager
    validator = SupplierValidator()
    
    # Supplier form
    with st.form("supplier_form"):
        st.subheader("Add New Supplier")
        
        col1, col2 = st.columns(2)
        
        with col1:
            vendor_id = st.text_input(
                "Vendor ID *",
                help="Unique identifier for the supplier"
            )
            
            vendor_name = st.text_input(
                "Vendor Name *",
                help="Name of the supplier"
            )
            
            vendor_country = st.text_input(
                "Vendor Country *",
                help="Country where the supplier is located"
            )
            
            city_of_manufacture = st.text_input(
                "City of Manufacture *",
                help="City where the goods are manufactured"
            )
        
        with col2:
            vendor_zip = st.text_input(
                "Vendor ZIP *",
                help="Postal code of the supplier's location"
            )
            
            delivery_performance = st.number_input(
                "Delivery Performance (%) *",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.1f",
                help="On‐time delivery performance as a percentage"
            )
            
            deliveries_per_month = st.number_input(
                "Deliveries per Month *",
                min_value=0,
                step=1,
                help="Average number of deliveries per month"
            )
        
        submitted = st.form_submit_button("Add Supplier", type="primary")
        
        if submitted:
            # Gather input into a dict
            supplier_data = {
                'vendor_id': vendor_id,
                'vendor_name': vendor_name,
                'vendor_country': vendor_country,
                'city_of_manufacture': city_of_manufacture,
                'vendor_zip': vendor_zip,
                'delivery_performance': delivery_performance,
                'deliveries_per_month': deliveries_per_month
            }
            
            # Validate
            validation_result = validator.validate_supplier(supplier_data)
            if validation_result['is_valid']:
                # Check for duplicates
                if data_manager.supplier_exists(vendor_id):
                    st.error(f"Supplier {vendor_id} already exists. Use the edit function to modify it.")
                else:
                    data_manager.add_supplier(supplier_data)
                    st.success(f"Supplier {vendor_id} added successfully!")
                    st.rerun()
            else:
                # Show validation errors
                for error in validation_result['errors']:
                    st.error(error)
    
    st.markdown("---")
    
    # Display existing suppliers
    st.subheader("Existing Suppliers")
    suppliers = data_manager.get_suppliers()
    
    if suppliers:
        for i, supplier in enumerate(suppliers):
            with st.expander(f"{supplier.get('vendor_id', '')} - {supplier.get('vendor_name', '')}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Vendor ID:** {supplier.get('vendor_id', 'N/A')}")
                    st.write(f"**Vendor Name:** {supplier.get('vendor_name', 'N/A')}")
                    st.write(f"**Country:** {supplier.get('vendor_country', 'N/A')}")
                    st.write(f"**City of Manufacture:** {supplier.get('city_of_manufacture', 'N/A')}")
                    st.write(f"**ZIP:** {supplier.get('vendor_zip', 'N/A')}")
                    st.write(f"**Delivery Performance:** {supplier.get('delivery_performance', 0.0):.1f}%")
                    st.write(f"**Deliveries/Month:** {supplier.get('deliveries_per_month', 0)}")
                
                with col2:
                    if st.button("Edit", key=f"edit_supplier_{i}"):
                        st.session_state[f'edit_supplier_{i}'] = True
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"delete_supplier_{i}", type="secondary"):
                        data_manager.remove_supplier(supplier.get('vendor_id', ''))
                        st.success("Supplier deleted successfully!")
                        st.rerun()
        
        # Edit supplier functionality
        for i, supplier in enumerate(suppliers):
            if st.session_state.get(f'edit_supplier_{i}', False):
                with st.form(f"edit_supplier_form_{i}"):
                    st.subheader(f"Edit Supplier: {supplier.get('vendor_id', '')}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_vendor_name = st.text_input(
                            "Vendor Name",
                            value=supplier.get('vendor_name', '')
                        )
                        new_vendor_country = st.text_input(
                            "Vendor Country",
                            value=supplier.get('vendor_country', '')
                        )
                        new_city_of_manufacture = st.text_input(
                            "City of Manufacture",
                            value=supplier.get('city_of_manufacture', '')
                        )
                    
                    with col2:
                        new_vendor_zip = st.text_input(
                            "Vendor ZIP",
                            value=supplier.get('vendor_zip', '')
                        )
                        new_delivery_performance = st.number_input(
                            "Delivery Performance (%)",
                            value=supplier.get('delivery_performance', 0.0),
                            min_value=0.0,
                            max_value=100.0,
                            step=0.1,
                            format="%.1f"
                        )
                        new_deliveries_per_month = st.number_input(
                            "Deliveries per Month",
                            value=supplier.get('deliveries_per_month', 0),
                            min_value=0,
                            step=1
                        )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update Supplier", type="primary"):
                            updated_supplier = {
                                'vendor_id': supplier['vendor_id'],  # Keep the same key
                                'vendor_name': new_vendor_name,
                                'vendor_country': new_vendor_country,
                                'city_of_manufacture': new_city_of_manufacture,
                                'vendor_zip': new_vendor_zip,
                                'delivery_performance': new_delivery_performance,
                                'deliveries_per_month': new_deliveries_per_month
                            }
                            validation_result = validator.validate_supplier(updated_supplier)
                            
                            if validation_result['is_valid']:
                                data_manager.update_supplier(supplier['vendor_id'], updated_supplier)
                                st.success("Supplier updated successfully!")
                                st.session_state[f'edit_supplier_{i}'] = False
                                st.rerun()
                            else:
                                for error in validation_result['errors']:
                                    st.error(error)
                    
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f'edit_supplier_{i}'] = False
                            st.rerun()
    else:
        st.info("No suppliers configured yet. Add your first supplier using the form above.")

if __name__ == "__main__":
    main()
