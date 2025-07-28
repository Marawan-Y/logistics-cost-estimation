# pages/9_Transport_Cost.py
import streamlit as st
from utils.validators import TransportValidator
from utils.data_manager import DataManager
from utils.transport_database import TransportDatabase, calculate_transport_cost_from_database
import uuid

st.set_page_config(page_title="Transport Cost", page_icon="🚚")

def main():
    st.title("Transport Cost")
    st.markdown("Configure transport mode and stackability - costs are calculated automatically from database")
    st.markdown("---")

    # Initialize DataManager, Validator & Database
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    if 'transport_db' not in st.session_state:
        st.session_state.transport_db = TransportDatabase()
        try:
            st.session_state.transport_db.load_from_json('transport_database.json')
        except:
            st.warning("Transport database not loaded. Please import data in Transport Data Management.")
    
    dm = st.session_state.data_manager
    val = TransportValidator()
    transport_db = st.session_state.transport_db

    transport_modes = ["Road", "Rail", "Sea"]
    stack_factors = ["1", "1.2", "1.25", "1.333333333", "1.166666667", "1.5", "2"]

    # Check if database is loaded
    if len(transport_db.database) == 0:
        st.error("⚠️ No transport database loaded. Please go to 'Transport Data Management' to import transport cost data.")
        if st.button("Go to Transport Data Management"):
            st.switch_page("pages/14Transport_Data_Management.py")
        return

    # Display database status
    stats = transport_db.get_statistics()
    st.success(f"✅ Transport database loaded: {stats['total_lanes']} lanes available")

    # ---------- Add New Transport Configuration ----------
    with st.form("transport_form"):
        st.subheader("Add New Transport Configuration")
        st.info("Transport costs will be calculated automatically based on the route and shipment details")

        col1, col2 = st.columns(2)
        with col1:
            mode1 = st.selectbox(
                "Transportation Mode *",
                transport_modes,
                help="Primary mode of transport"
            )
            
            # Show informational field about automatic calculation
            st.info("💡 Transport cost per LU will be calculated automatically based on:")
            st.caption("• Origin/destination from supplier")
            st.caption("• Shipment weight and volume")
            st.caption("• Selected transport mode")
            st.caption("• Current rates in database")
            
        with col2:
            stack_factor = st.selectbox(
                "Stackability Factor *",
                stack_factors,
                help="Factor by which items can be stacked (affects loading meters calculation)"
            )
            
            # Additional configuration options
            use_bonded_warehouse = st.checkbox(
                "Use Bonded Warehouse",
                help="Check if goods need bonded warehouse handling"
            )

        # Note about calculation
        st.markdown("---")
        st.markdown("### How Transport Cost Calculation Works:")
        st.markdown("""
        1. **Route Detection**: System finds the lane based on supplier and destination locations
        2. **Weight-based Pricing**: Determines price based on shipment weight clusters
        3. **Space-based Pricing**: Calculates based on loading meters if applicable
        4. **Mode Selection**: Uses higher of weight-based or space-based cost
        5. **Special Rules**: 
           - Full truck pricing for >34 pallets
           - International vs national rates
           - Fuel surcharges applied automatically
        """)

        submitted = st.form_submit_button("Add Transport Configuration", type="primary")
        if submitted:
            # Create configuration without manual cost entry
            obj = {
                "mode1": mode1,
                "cost_lu": 0.0,  # Will be calculated dynamically
                "cost_bonded": 0.0,  # Will be calculated if needed
                "stack_factor": stack_factor,
                "use_bonded_warehouse": use_bonded_warehouse,
                "auto_calculate": True,  # Flag to indicate automatic calculation
                "key": str(uuid.uuid4())
            }
            
            # Basic validation (mode and stack factor)
            if mode1 and stack_factor:
                dm.add_transport(obj)
                st.success("Transport configuration added! Costs will be calculated automatically during logistics calculation.")
                st.rerun()
            else:
                st.error("Please select transport mode and stackability factor")

    st.markdown("---")

    # ---------- Display Existing Transport Configurations ----------
    st.subheader("Existing Transport Configurations")
    transport_list = dm.get_transport()
    
    if not transport_list:
        st.info("No transport configurations yet. Add one above.")
    else:
        # Show configurations
        for i, tr in enumerate(transport_list):
            with st.expander(f"Configuration {i+1}: {tr.get('mode1', 'Unknown')}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Transport Mode:** {tr.get('mode1', 'N/A')}")
                    st.write(f"**Stackability Factor:** {tr.get('stack_factor', '1')}")
                    
                    if tr.get('auto_calculate', False):
                        st.write(f"**Cost Calculation:** Automatic (from database)")
                    else:
                        # Legacy manual cost display
                        st.write(f"**Cost per LU:** €{tr.get('cost_lu', 0):.2f}")
                        st.write(f"**Bonded Warehouse Cost:** €{tr.get('cost_bonded', 0):.2f}")
                    
                    if tr.get('use_bonded_warehouse', False):
                        st.write(f"**Bonded Warehouse:** Yes")
                    
                with col2:
                    if st.button("Edit", key=f"edit_btn_{i}"):
                        st.session_state[f"is_editing_tr_{i}"] = True
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"del_btn_{i}", type="secondary"):
                        dm.remove_transport(tr["key"])
                        st.success("Transport configuration deleted.")
                        st.rerun()

        # ---------- Edit Transport Configuration ----------
        for i, tr in enumerate(transport_list):
            if st.session_state.get(f"is_editing_tr_{i}", False):
                with st.form(f"edit_tr_form_{i}"):
                    st.subheader(f"Edit Transport Configuration")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_mode1 = st.selectbox(
                            "Transportation Mode",
                            transport_modes,
                            index=transport_modes.index(tr.get("mode1", "Road"))
                        )
                        
                        # Option to switch between auto and manual
                        calc_mode = st.radio(
                            "Cost Calculation Mode",
                            ["Automatic (Recommended)", "Manual Override"],
                            index=0 if tr.get('auto_calculate', True) else 1
                        )
                        
                        if calc_mode == "Manual Override":
                            new_cost_lu = st.number_input(
                                "Manual Cost per LU (€)",
                                value=tr.get("cost_lu", 0.0),
                                min_value=0.0,
                                step=0.01,
                                format="%.2f"
                            )
                            new_cost_bonded = st.number_input(
                                "Manual Bonded Warehouse Cost (€)",
                                value=tr.get("cost_bonded", 0.0),
                                min_value=0.0,
                                step=0.01,
                                format="%.2f"
                            )
                        else:
                            new_cost_lu = 0.0
                            new_cost_bonded = 0.0
                            st.info("Costs will be calculated automatically from database")
                    
                    with col2:
                        sf_index = stack_factors.index(tr.get("stack_factor", "1"))
                        new_stack_factor = st.selectbox(
                            "Stackability Factor",
                            stack_factors,
                            index=sf_index
                        )
                        
                        new_use_bonded = st.checkbox(
                            "Use Bonded Warehouse",
                            value=tr.get('use_bonded_warehouse', False)
                        )

                    col1b, col2b = st.columns(2)
                    with col1b:
                        if st.form_submit_button("Update Transport Configuration", type="primary"):
                            upd = {
                                "mode1": new_mode1,
                                "cost_lu": new_cost_lu,
                                "cost_bonded": new_cost_bonded,
                                "stack_factor": new_stack_factor,
                                "use_bonded_warehouse": new_use_bonded,
                                "auto_calculate": calc_mode == "Automatic (Recommended)",
                                "key": tr["key"]
                            }
                            
                            dm.update_transport(tr["key"], upd)
                            st.success("Transport configuration updated.")
                            st.session_state[f"is_editing_tr_{i}"] = False
                            st.rerun()
                    
                    with col2b:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f"is_editing_tr_{i}"] = False
                            st.rerun()

    # Show example calculation
    st.markdown("---")
    st.subheader("📊 Example Transport Cost Calculation")
    
    with st.expander("See how transport costs are calculated"):
        st.markdown("""
        **Example Shipment:**
        - Origin: Italy (IT) ZIP 23
        - Destination: Germany (DE) ZIP 94 (Aldersbach)
        - Weight: 978.32 kg
        - Pallets: 2
        - Mode: Road
        - Stackability: 2.0
        
        **Calculation Process:**
        1. **Loading Meters**: 0.40 m (based on pallet footprint / truck width)
        2. **Weight-based cost**: €290.71 (from 1000kg cluster)
        3. **Space-based cost**: €600 (0.40m × €1500/m for international)
        4. **Selected cost**: €600 (higher of the two)
        5. **Cost per pallet**: €300
        
        **Database lookup automatically handles:**
        - Finding correct lane (IT23 → DE94)
        - Applying weight cluster pricing
        - International vs national rates
        - Fuel surcharges
        """)

    # Test calculation section
    st.markdown("---")
    st.subheader("🧪 Test Transport Cost Calculation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_origin_country = st.text_input("Test Origin Country", value="IT")
        test_origin_zip = st.text_input("Test Origin ZIP", value="23")
        test_weight = st.number_input("Test Weight (kg)", value=1000.0, min_value=0.0)
        test_pallets = st.number_input("Test Pallets", value=2, min_value=1)
    
    with col2:
        test_dest_country = st.text_input("Test Destination Country", value="DE")
        test_dest_zip = st.text_input("Test Destination ZIP", value="94")
        test_loading_meters = st.number_input("Test Loading Meters", value=0.40, min_value=0.0)
        test_mode = st.selectbox("Test Mode", transport_modes)
    
    if st.button("Calculate Test Cost"):
        result = calculate_transport_cost_from_database(
            supplier_country=test_origin_country,
            supplier_zip=test_origin_zip,
            dest_country=test_dest_country,
            dest_zip=test_dest_zip,
            weight_kg=test_weight,
            num_pallets=test_pallets,
            loading_meters=test_loading_meters,
            transport_db=transport_db
        )
        
        if result:
            st.success("✅ Calculation successful!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Cost", f"€{result['total_cost']:.2f}")
            with col2:
                st.metric("Cost per Pallet", f"€{result['cost_per_pallet']:.2f}")
            with col3:
                st.metric("Cost Type", result['cost_type'].replace('_', ' ').title())
            
            # Show details
            with st.expander("Calculation Details"):
                st.write(f"**Weight-based cost**: €{result['weight_based_cost']:.2f}")
                if result.get('space_based_cost'):
                    st.write(f"**Space-based cost**: €{result['space_based_cost']:.2f}")
                if result.get('fuel_surcharge'):
                    st.write(f"**Fuel surcharge**: €{result['fuel_surcharge']:.2f}")
                st.write(f"**Weight cluster used**: ≤{result['weight_cluster_used']} kg")
        else:
            st.error(f"❌ No lane found for {test_origin_country}{test_origin_zip} → {test_dest_country}{test_dest_zip}")
            st.info("Please check if this lane exists in the transport database")

if __name__ == "__main__":
    main()