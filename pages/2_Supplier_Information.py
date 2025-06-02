import streamlit as st
from utils.validators import SupplierValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Supplier Information", page_icon="🏭")

def main():
    st.title("Supplier Information")
    st.markdown("Configure supplier details and location information")
    st.markdown("---")
    
    # Initialize data manager
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    data_manager = st.session_state.data_manager
    validator = SupplierValidator()
    
    # Incoterm options
    INCOTERMS = [
        "EXW - Ex Works",
        "FCA - Free Carrier",
        "CPT - Carriage Paid To",
        "CIP - Carriage and Insurance Paid To",
        "DAP - Delivered At Place",
        "DPU - Delivered at Place Unloaded",
        "DDP - Delivered Duty Paid",
        "FAS - Free Alongside Ship",
        "FOB - Free On Board",
        "CFR - Cost and Freight",
        "CIF - Cost, Insurance and Freight"
    ]
    
    # Country codes (subset for common countries)
    COUNTRIES = [
        "DE - Germany", "FR - France", "IT - Italy", "ES - Spain", "NL - Netherlands",
        "BE - Belgium", "AT - Austria", "CH - Switzerland", "PL - Poland", "CZ - Czech Republic",
        "CN - China", "JP - Japan", "KR - South Korea", "IN - India", "TH - Thailand",
        "US - United States", "MX - Mexico", "BR - Brazil", "TR - Turkey", "RO - Romania"
    ]
    
    # Supplier form
    with st.form("supplier_form"):
        st.subheader("Add New Supplier")
        
        col1, col2 = st.columns(2)
        
        with col1:
            vendor_id = st.text_input(
                "Vendor ID *",
                help="Unique supplier code or identifier"
            )
            
            vendor_name = st.text_input(
                "Vendor Name *",
                help="Full name of the supplier company"
            )
            
            vendor_country = st.selectbox(
                "Vendor Country *",
                options=COUNTRIES,
                help="Country where the supplier is located"
            )
            
            city_manufacture = st.text_input(
                "City of Manufacture *",
                help="City where the material is manufactured"
            )
        
        with col2:
            vendor_zip = st.text_input(
                "Vendor ZIP Code",
                help="ZIP/Postal code of the manufacturing location"
            )
            
            incoterm = st.selectbox(
                "Incoterm *",
                options=INCOTERMS,
                help="International Commercial Terms for shipping responsibility"
            )
            
            contact_person = st.text_input(
                "Contact Person",
                help="Primary contact at the supplier"
            )
            
            contact_email = st.text_input(
                "Contact Email",
                help="Email address for communication"
            )
        
        # Additional supplier details
        st.subheader("Additional Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            payment_terms = st.text_input(
                "Payment Terms",
                placeholder="e.g., NET 30, 2/10 NET 30",
                help="Payment terms agreed with supplier"
            )
            
            currency = st.selectbox(
                "Currency",
                options=["EUR - Euro", "USD - US Dollar", "GBP - British Pound", "CNY - Chinese Yuan", "JPY - Japanese Yen"],
                help="Currency for transactions with this supplier"
            )
        
        with col2:
            lead_time_days = st.number_input(
                "Lead Time (days)",
                min_value=0,
                value=30,
                help="Standard lead time in days"
            )
            
            min_order_qty = st.number_input(
                "Minimum Order Quantity",
                min_value=0,
                step=1,
                help="Minimum order quantity required by supplier"
            )
        
        supplier_notes = st.text_area(
            "Notes",
            help="Additional notes about the supplier"
        )
        
        submitted = st.form_submit_button("Add Supplier", type="primary")
        
        if submitted:
            # Validate input
            supplier_data = {
                'vendor_id': vendor_id,
                'vendor_name': vendor_name,
                'vendor_country': vendor_country.split(' - ')[0] if ' - ' in vendor_country else vendor_country,
                'vendor_country_name': vendor_country.split(' - ')[1] if ' - ' in vendor_country else vendor_country,
                'city_manufacture': city_manufacture,
                'vendor_zip': vendor_zip,
                'incoterm': incoterm.split(' - ')[0] if ' - ' in incoterm else incoterm,
                'incoterm_description': incoterm,
                'contact_person': contact_person,
                'contact_email': contact_email,
                'payment_terms': payment_terms,
                'currency': currency.split(' - ')[0] if ' - ' in currency else currency,
                'lead_time_days': lead_time_days,
                'min_order_qty': min_order_qty,
                'notes': supplier_notes
            }
            
            validation_result = validator.validate_supplier(supplier_data)
            
            if validation_result['is_valid']:
                # Check if supplier already exists
                if data_manager.supplier_exists(vendor_id):
                    st.error(f"Supplier {vendor_id} already exists. Use the edit function to modify it.")
                else:
                    data_manager.add_supplier(supplier_data)
                    st.success(f"Supplier {vendor_id} added successfully!")
                    st.rerun()
            else:
                for error in validation_result['errors']:
                    st.error(error)
    
    st.markdown("---")
    
    # Display existing suppliers
    st.subheader("Existing Suppliers")
    suppliers = data_manager.get_suppliers()
    
    if suppliers:
        for i, supplier in enumerate(suppliers):
            with st.expander(f"{supplier['vendor_id']} - {supplier['vendor_name']}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Country:** {supplier.get('vendor_country_name', supplier['vendor_country'])}")
                    st.write(f"**City:** {supplier['city_manufacture']}")
                    if supplier.get('vendor_zip'):
                        st.write(f"**ZIP Code:** {supplier['vendor_zip']}")
                    st.write(f"**Incoterm:** {supplier.get('incoterm_description', supplier['incoterm'])}")
                    if supplier.get('contact_person'):
                        st.write(f"**Contact:** {supplier['contact_person']}")
                    if supplier.get('contact_email'):
                        st.write(f"**Email:** {supplier['contact_email']}")
                    if supplier.get('payment_terms'):
                        st.write(f"**Payment Terms:** {supplier['payment_terms']}")
                    if supplier.get('currency'):
                        st.write(f"**Currency:** {supplier['currency']}")
                    st.write(f"**Lead Time:** {supplier.get('lead_time_days', 'N/A')} days")
                    if supplier.get('min_order_qty'):
                        st.write(f"**Min Order Qty:** {supplier['min_order_qty']:,}")
                    if supplier.get('notes'):
                        st.write(f"**Notes:** {supplier['notes']}")
                
                with col2:
                    if st.button("Edit", key=f"edit_supplier_{i}"):
                        st.session_state[f'edit_supplier_{i}'] = True
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"delete_supplier_{i}", type="secondary"):
                        data_manager.remove_supplier(supplier['vendor_id'])
                        st.success("Supplier deleted successfully!")
                        st.rerun()
        
        # Edit supplier functionality
        for i, supplier in enumerate(suppliers):
            if st.session_state.get(f'edit_supplier_{i}', False):
                with st.form(f"edit_supplier_form_{i}"):
                    st.subheader(f"Edit Supplier: {supplier['vendor_id']}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input(
                            "Vendor Name",
                            value=supplier['vendor_name']
                        )
                        
                        current_country = supplier.get('vendor_country_name', supplier['vendor_country'])
                        country_index = 0
                        for idx, country in enumerate(COUNTRIES):
                            if current_country in country:
                                country_index = idx
                                break
                        
                        new_country = st.selectbox(
                            "Vendor Country",
                            options=COUNTRIES,
                            index=country_index
                        )
                        
                        new_city = st.text_input(
                            "City of Manufacture",
                            value=supplier['city_manufacture']
                        )
                        
                        new_zip = st.text_input(
                            "Vendor ZIP Code",
                            value=supplier.get('vendor_zip', '')
                        )
                    
                    with col2:
                        current_incoterm = supplier.get('incoterm_description', supplier['incoterm'])
                        incoterm_index = 0
                        for idx, incoterm in enumerate(INCOTERMS):
                            if current_incoterm in incoterm:
                                incoterm_index = idx
                                break
                        
                        new_incoterm = st.selectbox(
                            "Incoterm",
                            options=INCOTERMS,
                            index=incoterm_index
                        )
                        
                        new_contact_person = st.text_input(
                            "Contact Person",
                            value=supplier.get('contact_person', '')
                        )
                        
                        new_contact_email = st.text_input(
                            "Contact Email",
                            value=supplier.get('contact_email', '')
                        )
                        
                        new_payment_terms = st.text_input(
                            "Payment Terms",
                            value=supplier.get('payment_terms', '')
                        )
                    
                    new_lead_time = st.number_input(
                        "Lead Time (days)",
                        value=supplier.get('lead_time_days', 30),
                        min_value=0
                    )
                    
                    new_min_order_qty = st.number_input(
                        "Minimum Order Quantity",
                        value=supplier.get('min_order_qty', 0),
                        min_value=0,
                        step=1
                    )
                    
                    new_notes = st.text_area(
                        "Notes",
                        value=supplier.get('notes', '')
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update Supplier", type="primary"):
                            updated_supplier = {
                                'vendor_id': supplier['vendor_id'],
                                'vendor_name': new_name,
                                'vendor_country': new_country.split(' - ')[0] if ' - ' in new_country else new_country,
                                'vendor_country_name': new_country.split(' - ')[1] if ' - ' in new_country else new_country,
                                'city_manufacture': new_city,
                                'vendor_zip': new_zip,
                                'incoterm': new_incoterm.split(' - ')[0] if ' - ' in new_incoterm else new_incoterm,
                                'incoterm_description': new_incoterm,
                                'contact_person': new_contact_person,
                                'contact_email': new_contact_email,
                                'payment_terms': new_payment_terms,
                                'lead_time_days': new_lead_time,
                                'min_order_qty': new_min_order_qty,
                                'notes': new_notes
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
