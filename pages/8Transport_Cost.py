# pages/9_Transport_Cost.py
import streamlit as st
from utils.validators import TransportValidator
from utils.data_manager import DataManager
from utils.transport_database import TransportDatabase
import uuid

st.set_page_config(page_title="Transport Cost", page_icon="🚚")

def main():
    st.title("Transport Cost")
    st.markdown("Configure transport mode and stackability - costs are calculated automatically from database or manually entered")
    st.markdown("---")

    # Initialize DataManager, Validator & Database
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    if 'transport_db' not in st.session_state:
        st.session_state.transport_db = TransportDatabase()
        try:
            st.session_state.transport_db.load_from_json('transport_database.json')
        except Exception:
            st.warning("Transport database not loaded. Please import data in Transport Data Management.")
    
    dm = st.session_state.data_manager
    val = TransportValidator()
    transport_db = st.session_state.transport_db

    transport_modes = ["Road", "Rail", "Sea"]
    stack_factors = ["1", "1.2", "1.25", "1.333333333", "1.166666667", "1.5", "2"]

    # Check if database is loaded - only show warning if automatic mode
    database_loaded = len(transport_db.database) > 0
    
    if not database_loaded:
        st.warning("⚠️ No transport database loaded. You can still use manual cost entry or go to 'Transport Data Management' to import transport cost data.")
        if st.button("Go to Transport Data Management"):
            st.switch_page("pages/14Transport_Data_Management.py")
    else:
        # Display database status
        stats = transport_db.get_statistics()
        st.success(f"✅ Transport database loaded: {stats['total_lanes']} lanes available")

    # ---------- Add New Transport Configuration ----------
    st.subheader("Add New Transport Configuration")

    # Choose calculation mode OUTSIDE the form so toggling triggers a rerun and re-renders inputs
    if 'calc_mode' not in st.session_state:
        st.session_state.calc_mode = "Automatic" if database_loaded else "Manual Override"
    st.session_state.calc_mode = st.radio(
        "Cost Calculation Mode",
        ["Automatic", "Manual Override"],
        index=0 if st.session_state.calc_mode == "Automatic" else 1,
        help="Choose whether to calculate costs automatically from database or enter manually",
        key="add_calc_mode_radio",
    )
    if st.session_state.calc_mode == "Automatic":
        st.info("Transport costs will be calculated automatically based on the route and shipment details")

    with st.form("transport_form"):
        calc_mode = st.session_state.calc_mode  # read chosen mode

        col1, col2 = st.columns(2)
        with col1:
            mode1 = st.selectbox(
                "Transportation Mode *",
                transport_modes,
                help="Primary mode of transport"
            )

            if calc_mode == "Automatic":
                # Show informational field about automatic calculation
                st.info("💡 Transport cost per LU will be calculated automatically based on:")
                st.caption("• Origin/destination from supplier")
                st.caption("• Shipment weight and volume")
                st.caption("• Selected transport mode")
                st.caption("• Current rates in database")
                cost_lu = 0.0
                cost_bonded = 0.0
            else:
                # Manual entry fields (render immediately when user switches to Manual Override)
                cost_lu = st.number_input(
                    "Transport Cost per LU (€) *",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="Manual cost per Loading Unit"
                )
                cost_bonded = st.number_input(
                    "Bonded Warehouse Cost per LU (€)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    value=0.0,
                    help="Additional cost for bonded warehouse if applicable"
                )
            
        with col2:
            stack_factor = st.selectbox(
                "Stackability Factor *",
                stack_factors,
                help="Factor by which items can be stacked (affects loading meters calculation)"
            )
            use_bonded_warehouse = st.checkbox(
                "Use Bonded Warehouse",
                help="Check if goods need bonded warehouse handling"
            )

        # Notes about calculation based on mode
        st.markdown("---")
        if calc_mode == "Automatic":
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
        else:
            st.markdown("### Manual Cost Entry:")
            st.markdown("""
            - Enter the transport cost per Loading Unit (LU) directly  
            - Add bonded warehouse cost if applicable  
            - Costs will be used as-is without automatic calculation  
            - Useful when you have negotiated rates or when database data is not available
            """)

        submitted = st.form_submit_button("Add Transport Configuration", type="primary")
        if submitted:
            # Basic validation then add
            if not mode1 or not stack_factor:
                st.error("Please select transport mode and stackability factor")
            elif calc_mode == "Manual Override" and cost_lu <= 0:
                st.error("Please enter a valid Transport Cost per LU greater than 0")
            else:
                obj = {
                    "mode1": mode1,
                    "cost_lu": float(cost_lu),
                    "cost_bonded": float(cost_bonded),
                    "stack_factor": stack_factor,
                    "use_bonded_warehouse": use_bonded_warehouse,
                    "auto_calculate": (calc_mode == "Automatic"),
                    "key": str(uuid.uuid4())
                }
                dm.add_transport(obj)
                if calc_mode == "Automatic":
                    st.success("Transport configuration added! Costs will be calculated automatically during logistics calculation.")
                else:
                    st.success(f"Transport configuration added with manual cost: €{cost_lu:.2f} per LU")
                st.rerun()

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
                        st.write("**Cost Calculation:** Automatic (from database)")
                    else:
                        # Manual cost display (ensure floats for formatting)
                        st.write("**Cost Calculation:** Manual")
                        st.write(f"**Cost per LU:** €{float(tr.get('cost_lu', 0)):.2f}")
                        if float(tr.get('cost_bonded', 0)) > 0:
                            st.write(f"**Bonded Warehouse Cost:** €{float(tr.get('cost_bonded', 0)):.2f}")
                    
                    if tr.get('use_bonded_warehouse', False):
                        st.write("**Bonded Warehouse:** Yes")
                    
                with col2:
                    if st.button("Edit", key=f"edit_btn_{i}"):
                        st.session_state[f"is_editing_tr_{i}"] = True
                        # initialize edit calc mode session key for immediate toggling
                        st.session_state[f"edit_calc_mode_{tr['key']}"] = "Automatic" if tr.get('auto_calculate', True) else "Manual Override"
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"del_btn_{i}", type="secondary"):
                        dm.remove_transport(tr["key"])
                        st.success("Transport configuration deleted.")
                        st.rerun()

        # ---------- Edit Transport Configuration ----------
        for i, tr in enumerate(transport_list):
            if st.session_state.get(f"is_editing_tr_{i}", False):
                # Put the mode toggle OUTSIDE the form for instant re-render
                edit_mode_key = f"edit_calc_mode_{tr['key']}"
                if edit_mode_key not in st.session_state:
                    st.session_state[edit_mode_key] = "Automatic" if tr.get('auto_calculate', True) else "Manual Override"

                st.markdown("---")
                st.subheader("Edit Transport Configuration")
                st.session_state[edit_mode_key] = st.radio(
                    "Cost Calculation Mode",
                    ["Automatic", "Manual Override"],
                    index=0 if st.session_state[edit_mode_key] == "Automatic" else 1,
                    help="Choose whether to calculate costs automatically from database or enter manually",
                    key=f"{edit_mode_key}_radio"
                )
                if st.session_state[edit_mode_key] == "Automatic":
                    st.info("Costs will be calculated automatically from database")

                with st.form(f"edit_tr_form_{i}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_mode1 = st.selectbox(
                            "Transportation Mode",
                            transport_modes,
                            index=transport_modes.index(tr.get("mode1", "Road"))
                        )

                        # Manual inputs only when manual mode is selected (reflects radio outside form)
                        if st.session_state[edit_mode_key] == "Manual Override":
                            new_cost_lu = st.number_input(
                                "Manual Cost per LU (€)",
                                value=float(tr.get("cost_lu", 0.0)),
                                min_value=0.0,
                                step=0.01,
                                format="%.2f",
                                key=f"edit_cost_lu_{i}"
                            )
                            new_cost_bonded = st.number_input(
                                "Manual Bonded Warehouse Cost (€)",
                                value=float(tr.get("cost_bonded", 0.0)),
                                min_value=0.0,
                                step=0.01,
                                format="%.2f",
                                key=f"edit_cost_bonded_{i}"
                            )
                        else:
                            new_cost_lu = 0.0
                            new_cost_bonded = 0.0
                            st.caption("Cost fields disabled: Automatic calculation enabled.")

                    with col2:
                        existing_sf = tr.get("stack_factor", "1")
                        sf_index = stack_factors.index(existing_sf) if existing_sf in stack_factors else 0
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
                            if st.session_state[edit_mode_key] == "Manual Override" and new_cost_lu <= 0:
                                st.error("Please enter a valid Transport Cost per LU greater than 0")
                            else:
                                upd = {
                                    "mode1": new_mode1,
                                    "cost_lu": float(new_cost_lu),
                                    "cost_bonded": float(new_cost_bonded),
                                    "stack_factor": new_stack_factor,
                                    "use_bonded_warehouse": new_use_bonded,
                                    "auto_calculate": (st.session_state[edit_mode_key] == "Automatic"),
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

    # Show example calculation or test section only if database is loaded
    if database_loaded:
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

        # Test calculation section - only show if database is loaded
        st.markdown("---")
        st.subheader("🧪 Test Transport Cost Calculation")

        with st.form("transport_test_form"):
            st.markdown("### Material and Packaging")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                test_material_weight = st.number_input("Material weight/piece (kg)", min_value=0.0, value=0.08, step=0.001, format="%.3f", key="material_weight_piece")
                test_pieces_per_pkg = st.number_input("Pieces per packaging", value=100, step=1)
                test_pkg_weight = st.number_input("Packaging weight (kg)", value=1.67, step=0.01)
            
            with col2:
                test_daily_demand = st.number_input("Daily demand", value=800, step=10)
                test_deliveries = st.number_input("Deliveries/month", value=2, min_value=1)
            
            with col3:
                test_units_per_pallet = st.number_input("Units per pallet", value=48, step=1)
                test_pallet_weight = st.number_input("Pallet weight (kg)", value=25.0, step=0.1)
                test_stackability = st.number_input("Stackability factor", value=2.0, min_value=1.0, step=0.1)
            
            st.markdown("### Route Information")
            col1, col2 = st.columns(2)
            
            with col1:
                test_origin_country = st.text_input("Origin Country", value="IT")
                test_origin_zip = st.text_input("Origin ZIP (2 digits)", value="23", max_chars=2)
            
            with col2:
                test_dest_country = st.text_input("Destination Country", value="DE")
                test_dest_zip = st.text_input("Destination ZIP (2 digits)", value="94", max_chars=2)
            
            calculate_button = st.form_submit_button("Calculate Transport Cost", type="primary")
            
            if calculate_button:
                # Run the calculation
                fill_qty_lu = max(test_pieces_per_pkg, 1) * max(test_units_per_pallet, 1)
                result = transport_db.calculate_transport_cost_workflow(
                    material_weight_per_piece=test_material_weight,
                    pieces_per_packaging=test_pieces_per_pkg,
                    packaging_weight=test_pkg_weight,
                    daily_demand=test_daily_demand,
                    deliveries_per_month=test_deliveries,
                    packaging_units_per_pallet=test_units_per_pallet,
                    pallet_weight=test_pallet_weight,
                    stackability_factor=test_stackability,
                    supplier_country=test_origin_country,
                    supplier_zip=test_origin_zip,
                    dest_country=test_dest_country,
                    dest_zip=test_dest_zip,
                    fill_qty_lu=fill_qty_lu
                )
                
                if result.get('success'):
                    st.success("✅ Calculation completed successfully!")
                    
                    # Display results matching PDF format
                    st.markdown("### 📊 Results")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Price per Delivery", f"€{result['price_per_delivery']:.2f}")
                    with col2:
                        st.metric("Price per Pallet", f"€{result['price_per_pallet']:.2f}")
                    with col3:
                        st.metric("Price per Piece", f"€{result['price_per_piece']:.3f}")
                    
                    # Detailed breakdown
                    with st.expander("📋 Detailed Calculation Breakdown"):
                        details = result['calculation_details']
                        
                        st.markdown("**Step 1: Material and Packaging Calculations**")
                        st.write(f"- Weight per packaging unit: {details['weight_per_packaging_unit']:.2f} kg")
                        st.write(f"- Monthly demand per delivery: {details['monthly_demand_per_delivery']:,.0f} pieces")
                        st.write(f"- Packaging units per delivery: {details['packaging_units_per_delivery']:.0f}")
                        
                        st.markdown("**Step 2: Logistics Unit Calculations**")
                        st.write(f"- Pallets needed: {details['pallets_needed']}")
                        st.write(f"- Weight per pallet: {details['weight_per_pallet']:.2f} kg")
                        st.write(f"- Total shipment weight: {details['total_shipment_weight']:.2f} kg")
                        st.write(f"- Loading meters: {details['loading_meters']:.2f} m")
                        
                        st.markdown("**Step 3: Route Identification**")
                        st.write(f"- Lane code: {result['lane_code']}")
                        st.write(f"- Route: {details['route']}")
                        
                        st.markdown("**Step 4: Price Lookup**")
                        st.write(f"- Weight bracket used: ≤{details['weight_bracket_used']} kg")
                        st.write(f"- Base price: €{details['base_price']:.2f}")
                        if result.get('fuel_surcharge', 0) > 0:
                            st.write(f"- Fuel surcharge: €{result['fuel_surcharge']:.2f}")
                        
                        st.markdown("**Step 5: Final Calculations**")
                        st.write(f"- Cost type: {result['cost_type']}")
                else:
                    st.error(f"❌ {result.get('error', 'Calculation failed')}")

if __name__ == "__main__":
    main()
