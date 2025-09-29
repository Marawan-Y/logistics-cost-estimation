# pages/2Supplier_Information.py
import streamlit as st
from utils.validators import SupplierValidator
import importlib, utils.validators as _valmod
importlib.reload(_valmod)
from utils.data_manager import DataManager

st.set_page_config(page_title="Supplier Information", page_icon="🏭")

def main():
    st.title("Supplier Information")
    st.markdown("Configure supplier details including location information for logistics cost calculation")
    st.markdown("---")
    
    # # Debug toggle
    # show_debug = st.toggle("Show debug details", value=False, help="Print submitted data when validation fails")

    # Initialize data manager
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    data_manager = st.session_state.data_manager
    validator = SupplierValidator()
    
    # -------------------------
    # Add New Supplier Form
    # -------------------------
    with st.form("supplier_form"):
        st.subheader("Add New Supplier")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Supplier Details")
            vendor_id = st.text_input(
                "Vendor ID *",
                help="Unique identifier for the supplier",
                key="supplier_add_vendor_id",
            )
            vendor_name = st.text_input(
                "Vendor Name *",
                help="Name of the supplier",
                key="supplier_add_vendor_name",
            )
            vendor_country = st.text_input(
                "Vendor Country *",
                help="Country where the supplier is located",
                key="supplier_add_vendor_country",
            )
            city_of_manufacture = st.text_input(
                "City of Manufacture *",
                help="City where the goods are manufactured",
                key="supplier_add_city_of_manufacture",
            )
            vendor_zip = st.text_input(
                "Vendor ZIP *",
                help="Postal code of the supplier's location",
                key="supplier_add_vendor_zip",
            )

        with col2:
            st.markdown("#### Delivery & Location Details")
            delivery_performance = st.number_input(
                "Delivery Performance (%) *",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.1f",
                help="On-time delivery performance as a percentage",
                key="supplier_add_delivery_performance",
            )
            deliveries_per_month = st.number_input(
                "Deliveries per Month *",
                min_value=0,
                step=1,
                help="Average number of deliveries per month",
                key="supplier_add_deliveries_per_month",
            )

            st.markdown("---")
            st.markdown("**KB/Bendix Plant Location**")
            # NOTE: Values are also re-read from session_state on submit (defensive)
            plant = st.text_input(
                "KB/Bendix Plant *",
                help="KB/Bendix plant name or identifier",
                key="supplier_add_plant",
            )
            country = st.text_input(
                "KB/Bendix Country *",
                help="Country where KB/Bendix plant is located",
                key="supplier_add_kb_country",
            )
            distance = st.number_input(
                "Distance (km) *",
                min_value=0.0,
                step=0.1,
                help="Distance from supplier to KB/Bendix plant",
                key="supplier_add_distance",
            )

        submitted = st.form_submit_button("Add Supplier", type="primary")
        if submitted:
            # DEFENSIVE: Re-read critical text inputs directly from session_state in case locals are empty
            plant_val = st.session_state.get("supplier_add_plant", "")
            country_val = st.session_state.get("supplier_add_kb_country", "")

            # Gather input into a dict
            supplier_data = {
                'vendor_id': vendor_id,
                'vendor_name': vendor_name,
                'vendor_country': vendor_country,
                'city_of_manufacture': city_of_manufacture,
                'vendor_zip': vendor_zip,
                'delivery_performance': delivery_performance,
                'deliveries_per_month': deliveries_per_month,
                'plant': plant_val,
                'country': country_val,
                'distance': distance,
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
                for error in validation_result['errors']:
                    st.error(error)
                # if show_debug:
                #     with st.expander("Debug: submitted supplier_data"):
                #         st.json(supplier_data)

    st.markdown("---")

    # -------------------------
    # Existing Suppliers
    # -------------------------
    st.subheader("Existing Suppliers")
    suppliers = data_manager.get_suppliers()

    if suppliers:
        # Expanders for current suppliers
        for i, supplier in enumerate(suppliers):
            header = f"{supplier.get('vendor_id', '')} - {supplier.get('vendor_name', '')}"
            with st.expander(header):
                col_info, col_edit, col_delete = st.columns([3, 1, 1])

                with col_info:
                    st.markdown("**Supplier Information:**")
                    st.write(f"**Vendor ID:** {supplier.get('vendor_id', 'N/A')}")
                    st.write(f"**Vendor Name:** {supplier.get('vendor_name', 'N/A')}")
                    st.write(f"**Country:** {supplier.get('vendor_country', 'N/A')}")
                    st.write(f"**City of Manufacture:** {supplier.get('city_of_manufacture', 'N/A')}")
                    st.write(f"**ZIP:** {supplier.get('vendor_zip', 'N/A')}")
                    st.write(f"**Delivery Performance:** {supplier.get('delivery_performance', 0.0):.1f}%")
                    st.write(f"**Deliveries/Month:** {supplier.get('deliveries_per_month', 0)}")

                    st.markdown("---")
                    st.markdown("**KB/Bendix Location:**")
                    st.write(f"**Plant:** {supplier.get('plant', 'N/A')}")
                    st.write(f"**Country:** {supplier.get('country', 'N/A')}")
                    st.write(f"**Distance:** {supplier.get('distance', 0):.1f} km")

                with col_edit:
                    if st.button("Edit", key=f"btn_edit_supplier_{i}"):
                        st.session_state[f'edit_supplier_{i}'] = True
                        st.rerun()

                with col_delete:
                    if st.button("Delete", key=f"delete_supplier_{i}", type="secondary"):
                        data_manager.remove_supplier(supplier.get('vendor_id', ''))
                        st.success("Supplier deleted successfully!")
                        st.rerun()

        # -------------------------
        # Edit Supplier Forms
        # -------------------------
        for i, supplier in enumerate(suppliers):
            if st.session_state.get(f'edit_supplier_{i}', False):
                with st.form(f"edit_supplier_form_{i}"):
                    st.subheader(f"Edit Supplier: {supplier.get('vendor_id', '')}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### Supplier Details")
                        new_vendor_name = st.text_input(
                            "Vendor Name",
                            value=supplier.get('vendor_name', ''),
                            key=f"supplier_edit_vendor_name_{i}",
                        )
                        new_vendor_country = st.text_input(
                            "Vendor Country",
                            value=supplier.get('vendor_country', ''),
                            key=f"supplier_edit_vendor_country_{i}",
                        )
                        new_city_of_manufacture = st.text_input(
                            "City of Manufacture",
                            value=supplier.get('city_of_manufacture', ''),
                            key=f"supplier_edit_city_of_manufacture_{i}",
                        )
                        new_vendor_zip = st.text_input(
                            "Vendor ZIP",
                            value=supplier.get('vendor_zip', ''),
                            key=f"supplier_edit_vendor_zip_{i}",
                        )

                    with col2:
                        st.markdown("#### Delivery & Location Details")
                        new_delivery_performance = st.number_input(
                            "Delivery Performance (%)",
                            value=float(supplier.get('delivery_performance', 0.0)),
                            min_value=0.0,
                            max_value=100.0,
                            step=0.1,
                            format="%.1f",
                            key=f"supplier_edit_delivery_performance_{i}",
                        )
                        new_deliveries_per_month = st.number_input(
                            "Deliveries per Month",
                            value=int(supplier.get('deliveries_per_month', 0)),
                            min_value=0,
                            step=1,
                            key=f"supplier_edit_deliveries_per_month_{i}",
                        )

                        st.markdown("---")
                        st.markdown("**KB/Bendix Plant Location**")
                        new_plant = st.text_input(
                            "KB/Bendix Plant",
                            value=supplier.get('plant', ''),
                            key=f"supplier_edit_plant_{i}",
                        )
                        new_country = st.text_input(
                            "KB/Bendix Country",
                            value=supplier.get('country', ''),
                            key=f"supplier_edit_kb_country_{i}",
                        )
                        new_distance = st.number_input(
                            "Distance (km)",
                            value=float(supplier.get('distance', 0.0)),
                            min_value=0.0,
                            step=0.1,
                            key=f"supplier_edit_distance_{i}",
                        )

                    col_left, col_right = st.columns(2)
                    with col_left:
                        if st.form_submit_button("Update Supplier", type="primary"):
                            updated_supplier = {
                                'vendor_id': supplier.get('vendor_id', ''),  # keep the same ID
                                'vendor_name': new_vendor_name,
                                'vendor_country': new_vendor_country,
                                'city_of_manufacture': new_city_of_manufacture,
                                'vendor_zip': new_vendor_zip,
                                'delivery_performance': new_delivery_performance,
                                'deliveries_per_month': new_deliveries_per_month,
                                'plant': new_plant,
                                'country': new_country,
                                'distance': new_distance,
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
                                # if show_debug:
                                #     with st.expander("Debug: submitted updated_supplier"):
                                #         st.json(updated_supplier)

                    with col_right:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f'edit_supplier_{i}'] = False
                            st.rerun()
    else:
        st.info("No suppliers configured yet. Add your first supplier using the form above.")

if __name__ == "__main__":
    main()