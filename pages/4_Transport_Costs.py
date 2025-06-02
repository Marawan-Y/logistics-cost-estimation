import streamlit as st
from utils.validators import TransportValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Transport Costs", page_icon="🚛")

def main():
    st.title("Transport Costs")
    st.markdown("Configure transport modes, distances, and cost calculations")
    st.markdown("---")
    
    # Initialize data manager
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    data_manager = st.session_state.data_manager
    validator = TransportValidator()
    
    # Get available materials and suppliers for selection
    materials = data_manager.get_materials()
    suppliers = data_manager.get_suppliers()
    
    if not materials:
        st.warning("⚠️ No materials configured. Please add materials in the Material Information page first.")
        return
    
    if not suppliers:
        st.warning("⚠️ No suppliers configured. Please add suppliers in the Supplier Information page first.")
        return
    
    # Transport mode options
    TRANSPORT_MODES = [
        "Road - Truck",
        "Rail - Train",
        "Sea - Ship",
        "Air - Airplane",
        "Multimodal - Combined",
        "Local Delivery"
    ]
    
    # Load unit types
    LOAD_UNIT_TYPES = [
        "Pallet - Standard",
        "Container 20ft",
        "Container 40ft",
        "Truck Load",
        "Parcel",
        "LTL - Less Than Truckload"
    ]
    
    # Transport form
    with st.form("transport_form"):
        st.subheader("Add New Transport Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Material selection
            material_options = [f"{m['material_no']} - {m['material_desc']}" for m in materials]
            selected_material = st.selectbox(
                "Material *",
                options=material_options,
                help="Select the material this transport configuration applies to"
            )
            
            # Supplier selection
            supplier_options = [f"{s['vendor_id']} - {s['vendor_name']}" for s in suppliers]
            selected_supplier = st.selectbox(
                "Supplier *",
                options=supplier_options,
                help="Select the supplier for this transport configuration"
            )
            
            transport_mode = st.selectbox(
                "Transport Mode *",
                options=TRANSPORT_MODES,
                help="Primary mode of transportation"
            )
            
            load_unit_type = st.selectbox(
                "Load Unit Type *",
                options=LOAD_UNIT_TYPES,
                help="Type of load unit used for transport"
            )
        
        with col2:
            distance_km = st.number_input(
                "Distance (km) *",
                min_value=0.0,
                step=0.1,
                format="%.1f",
                help="Total transport distance in kilometers"
            )
            
            transport_cost_per_lu = st.number_input(
                "Transport Cost per Load Unit (€) *",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Cost to transport one load unit"
            )
            
            lu_capacity = st.number_input(
                "Load Unit Capacity (pieces) *",
                min_value=1,
                step=1,
                help="Number of pieces that fit in one load unit"
            )
            
            transit_time_days = st.number_input(
                "Transit Time (days)",
                min_value=0.0,
                step=0.1,
                format="%.1f",
                help="Expected transit time in days"
            )
        
        # CO2 and environmental costs
        st.subheader("Environmental Impact")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            co2_emission_factor = st.number_input(
                "CO₂ Emission Factor (kg CO₂/ton-km)",
                min_value=0.0,
                value=0.06,  # Default for road transport
                step=0.001,
                format="%.3f",
                help="CO₂ emissions per ton-kilometer"
            )
            
            co2_cost_per_ton = st.number_input(
                "CO₂ Cost per Ton (€/ton CO₂)",
                min_value=0.0,
                value=25.0,  # EU ETS price approximation
                step=0.01,
                format="%.2f",
                help="Cost of CO₂ emissions per ton"
            )
        
        with col2:
            fuel_surcharge_rate = st.number_input(
                "Fuel Surcharge Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                format="%.1f",
                help="Fuel surcharge as percentage of base transport cost"
            )
            
            customs_handling = st.number_input(
                "Customs Handling Cost (€)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Additional cost for customs handling"
            )
        
        with col3:
            insurance_rate = st.number_input(
                "Insurance Rate (%)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.01,
                format="%.2f",
                help="Insurance cost as percentage of goods value"
            )
            
            handling_cost = st.number_input(
                "Handling Cost per LU (€)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Additional handling cost per load unit"
            )
        
        # Transport frequency and reliability
        st.subheader("Service Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            frequency_per_week = st.number_input(
                "Frequency (shipments per week)",
                min_value=0.1,
                value=1.0,
                step=0.1,
                format="%.1f",
                help="Number of shipments per week"
            )
            
            reliability_score = st.selectbox(
                "Reliability Score",
                options=["A - Excellent", "B - Good", "C - Average", "D - Below Average"],
                help="Reliability rating of the transport service"
            )
        
        with col2:
            min_shipment_size = st.number_input(
                "Minimum Shipment Size (pieces)",
                min_value=1,
                step=1,
                help="Minimum order size for this transport mode"
            )
            
            requires_special_handling = st.checkbox(
                "Requires Special Handling",
                help="Check if materials require special handling during transport"
            )
        
        transport_notes = st.text_area(
            "Notes",
            help="Additional notes about this transport configuration"
        )
        
        submitted = st.form_submit_button("Add Transport Configuration", type="primary")
        
        if submitted:
            # Extract material and supplier IDs
            material_id = selected_material.split(' - ')[0]
            supplier_id = selected_supplier.split(' - ')[0]
            
            # Validate input
            transport_data = {
                'material_id': material_id,
                'supplier_id': supplier_id,
                'transport_mode': transport_mode.split(' - ')[0] if ' - ' in transport_mode else transport_mode,
                'transport_mode_description': transport_mode,
                'load_unit_type': load_unit_type.split(' - ')[0] if ' - ' in load_unit_type else load_unit_type,
                'load_unit_description': load_unit_type,
                'distance_km': distance_km,
                'transport_cost_per_lu': transport_cost_per_lu,
                'lu_capacity': lu_capacity,
                'transit_time_days': transit_time_days,
                'co2_emission_factor': co2_emission_factor,
                'co2_cost_per_ton': co2_cost_per_ton,
                'fuel_surcharge_rate': fuel_surcharge_rate,
                'customs_handling': customs_handling,
                'insurance_rate': insurance_rate,
                'handling_cost': handling_cost,
                'frequency_per_week': frequency_per_week,
                'reliability_score': reliability_score.split(' - ')[0] if ' - ' in reliability_score else reliability_score,
                'min_shipment_size': min_shipment_size,
                'requires_special_handling': requires_special_handling,
                'notes': transport_notes
            }
            
            validation_result = validator.validate_transport(transport_data)
            
            if validation_result['is_valid']:
                # Check if transport configuration already exists for this material-supplier combination
                if data_manager.transport_exists(material_id, supplier_id):
                    st.error(f"Transport configuration for material {material_id} and supplier {supplier_id} already exists. Use the edit function to modify it.")
                else:
                    data_manager.add_transport(transport_data)
                    st.success(f"Transport configuration added successfully!")
                    st.rerun()
            else:
                for error in validation_result['errors']:
                    st.error(error)
    
    st.markdown("---")
    
    # Display existing transport configurations
    st.subheader("Existing Transport Configurations")
    transport_configs = data_manager.get_transport()
    
    if transport_configs:
        for i, config in enumerate(transport_configs):
            # Get material and supplier names for display
            material_name = "Unknown"
            supplier_name = "Unknown"
            
            for material in materials:
                if material['material_no'] == config['material_id']:
                    material_name = f"{material['material_no']} - {material['material_desc']}"
                    break
            
            for supplier in suppliers:
                if supplier['vendor_id'] == config['supplier_id']:
                    supplier_name = f"{supplier['vendor_id']} - {supplier['vendor_name']}"
                    break
            
            with st.expander(f"{material_name} | {supplier_name} | {config.get('transport_mode_description', config['transport_mode'])}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Transport Mode:** {config.get('transport_mode_description', config['transport_mode'])}")
                    st.write(f"**Load Unit:** {config.get('load_unit_description', config['load_unit_type'])}")
                    st.write(f"**Distance:** {config['distance_km']:.1f} km")
                    st.write(f"**Cost per LU:** €{config['transport_cost_per_lu']:.2f}")
                    st.write(f"**LU Capacity:** {config['lu_capacity']} pieces")
                    st.write(f"**Transit Time:** {config['transit_time_days']:.1f} days")
                    
                    # Environmental impact
                    st.write(f"**CO₂ Factor:** {config['co2_emission_factor']:.3f} kg CO₂/ton-km")
                    st.write(f"**CO₂ Cost:** €{config['co2_cost_per_ton']:.2f}/ton CO₂")
                    
                    # Additional costs
                    if config.get('fuel_surcharge_rate', 0) > 0:
                        st.write(f"**Fuel Surcharge:** {config['fuel_surcharge_rate']:.1f}%")
                    if config.get('customs_handling', 0) > 0:
                        st.write(f"**Customs Handling:** €{config['customs_handling']:.2f}")
                    if config.get('insurance_rate', 0) > 0:
                        st.write(f"**Insurance Rate:** {config['insurance_rate']:.2f}%")
                    if config.get('handling_cost', 0) > 0:
                        st.write(f"**Handling Cost:** €{config['handling_cost']:.2f}/LU")
                    
                    # Service parameters
                    st.write(f"**Frequency:** {config['frequency_per_week']:.1f} shipments/week")
                    st.write(f"**Reliability:** {config['reliability_score']}")
                    st.write(f"**Min Shipment Size:** {config['min_shipment_size']} pieces")
                    
                    if config.get('requires_special_handling', False):
                        st.write("**Special Handling:** Required")
                    
                    if config.get('notes'):
                        st.write(f"**Notes:** {config['notes']}")
                
                with col2:
                    if st.button("Edit", key=f"edit_transport_{i}"):
                        st.session_state[f'edit_transport_{i}'] = True
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"delete_transport_{i}", type="secondary"):
                        data_manager.remove_transport(config['material_id'], config['supplier_id'])
                        st.success("Transport configuration deleted successfully!")
                        st.rerun()
        
        # Calculate transport summary
        st.markdown("---")
        st.subheader("Transport Summary")
        
        total_configs = len(transport_configs)
        avg_distance = sum(config['distance_km'] for config in transport_configs) / total_configs if total_configs > 0 else 0
        avg_cost_per_lu = sum(config['transport_cost_per_lu'] for config in transport_configs) / total_configs if total_configs > 0 else 0
        total_co2_cost = sum(config['co2_cost_per_ton'] for config in transport_configs)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Configurations", total_configs)
        with col2:
            st.metric("Average Distance", f"{avg_distance:.0f} km")
        with col3:
            st.metric("Average Cost per LU", f"€{avg_cost_per_lu:.2f}")
        with col4:
            st.metric("Total CO₂ Cost", f"€{total_co2_cost:.2f}")
        
    else:
        st.info("No transport configurations yet. Add your first transport configuration using the form above.")

if __name__ == "__main__":
    main()
