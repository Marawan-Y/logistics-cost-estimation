# pages/13Cost_Calculation.py
import streamlit as st
import pandas as pd
from utils.calculations import LogisticsCostCalculator
from utils.data_manager import DataManager
from utils.excel_exporter import LogisticsExcelExporter
import json

st.set_page_config(page_title="Cost Calculation", page_icon="💰", layout="wide")

def main():
    st.title("Cost Calculation & Results")
    st.markdown("Calculate total logistics costs with precise configuration selection")
    st.markdown("---")

    # --- Data Initialization ---
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()

    data_manager = st.session_state.data_manager
    calculator = LogisticsCostCalculator()
    excel_exporter = LogisticsExcelExporter()

    # Load All Configurations
    materials = data_manager.get_materials()
    suppliers = data_manager.get_suppliers()
    locations = data_manager.get_locations()
    operations = data_manager.get_operations()
    packaging_configs = data_manager.get_packaging()
    repacking_configs = data_manager.get_repacking()
    # REMOVED: customs_configs = data_manager.get_customs()
    transport_configs = data_manager.get_transport()
    co2_configs = data_manager.get_co2()
    warehouse_configs = data_manager.get_warehouse()
    interest_configs = data_manager.get_interest()
    additional_costs = data_manager.get_additional_costs()

    # Check Required Data
    missing_configs = []
    if not materials:          missing_configs.append("Materials")
    if not suppliers:          missing_configs.append("Suppliers")
    if not packaging_configs:  missing_configs.append("Packaging")
    if not transport_configs:  missing_configs.append("Transport")
    if not warehouse_configs:  missing_configs.append("Warehouse")
    if not co2_configs:        missing_configs.append("CO₂")

    if missing_configs:
        st.error(f"⚠️ Missing configurations: {', '.join(missing_configs)}")
        st.info("Please configure all required data before performing calculations.")
        return

    # Configuration Overview
    st.subheader("📊 Available Configurations")
    
    # Show configuration counts
    config_counts = {
        "Materials": len(materials),
        "Suppliers": len(suppliers),
        "Locations": len(locations),
        "Operations": len(operations),
        "Packaging": len(packaging_configs),
        "Repacking": len(repacking_configs),
        # REMOVED: "Customs": len(customs_configs),
        "Transport": len(transport_configs),
        "CO₂": len(co2_configs),
        "Warehouse": len(warehouse_configs),
        "Interest": len(interest_configs),
        "Additional": len(additional_costs)
    }
    
    # Display counts in columns
    col1, col2, col3, col4 = st.columns(4)
    config_items = list(config_counts.items())
    
    for i, col in enumerate([col1, col2, col3, col4]):
        with col:
            for j in range(3):  # 3 items per column
                idx = i * 3 + j
                if idx < len(config_items):
                    name, count = config_items[idx]
                    status = "✅" if count > 0 else "❌"
                    col.metric(f"{status} {name}", count)

    st.markdown("---")

    # Configuration Selection Mode
    st.subheader("🔧 Calculation Configuration")
    
    calculation_mode = st.radio(
        "**Configuration Selection Mode**",
        options=[
            "Quick Mode (Use First Available Configs)", 
            "Precise Mode (Select Specific Configs)"
        ],
        help="Quick Mode uses the first configuration of each type. Precise Mode allows you to select specific configurations."
    )

    # Initialize session state for selected configurations
    if 'selected_configs' not in st.session_state:
        st.session_state.selected_configs = {}

    selected_material_supplier_pairs = []
    selected_configs = {}

    if calculation_mode == "Quick Mode (Use First Available Configs)":
        # Quick mode - show what will be used
        st.info("📋 **Quick Mode**: Using first available configuration for each component")
        
        with st.expander("🔍 View Configurations to be Used"):
            col1, col2 = st.columns(2)
            
            with col1:
                if locations: 
                    st.write(f"**Location:** {locations[0]['plant']} - {locations[0]['country']}")
                if operations: 
                    st.write(f"**Operations:** {operations[0]['incoterm_code']} @ {operations[0]['incoterm_place']}")
                if packaging_configs: 
                    st.write(f"**Packaging:** {packaging_configs[0]['box_type']} | {packaging_configs[0]['pallet_type']}")
                if repacking_configs: 
                    st.write(f"**Repacking:** {repacking_configs[0]['pcs_weight']}")
                # REMOVED: customs display
                if transport_configs: 
                    st.write(f"**Transport:** {transport_configs[0]['mode1']}")
            
            with col2:
                if co2_configs: 
                    st.write(f"**CO₂:** €{co2_configs[0]['cost_per_ton']}/ton")
                if warehouse_configs: 
                    st.write(f"**Warehouse:** €{warehouse_configs[0]['cost_per_loc']}/location")
                if interest_configs: 
                    st.write(f"**Interest:** {interest_configs[0]['rate']}%")
                if additional_costs: 
                    total_additional = sum(c['cost_value'] for c in additional_costs)
                    st.write(f"**Additional Costs:** €{total_additional:.2f} total")
                else:
                    st.write("**Additional Costs:** None")
                st.write("**Duty Rate:** Will be entered during calculation")

        # Material-Supplier selection for quick mode
        st.subheader("📦 Select Material-Supplier Pairs")
        available_pairs = data_manager.get_material_supplier_pairs()
        
        if not available_pairs:
            st.warning("No material-supplier pairs found.")
            return
            
        selected_pair_ids = st.multiselect(
            "Choose Material-Supplier pairs for calculation:",
            options=[pair['pair_id'] for pair in available_pairs],
            default=[pair['pair_id'] for pair in available_pairs[:5]],
            format_func=lambda x: next(pair['display_name'] for pair in available_pairs if pair['pair_id'] == x)
        )
        
        if not selected_pair_ids:
            st.warning("Please select at least one Material-Supplier pair.")
            return
        
        selected_material_supplier_pairs = [pair for pair in available_pairs if pair['pair_id'] in selected_pair_ids]

        # Set default configs for quick mode
        selected_configs = {
            'location': locations[0] if locations else None,
            'operations': operations[0] if operations else None,
            'packaging': packaging_configs[0] if packaging_configs else None,
            'repacking': repacking_configs[0] if repacking_configs else None,
            # REMOVED: 'customs': customs_configs[0] if customs_configs else None,
            'transport': transport_configs[0] if transport_configs else None,
            'co2': co2_configs[0] if co2_configs else None,
            'warehouse': warehouse_configs[0] if warehouse_configs else None,
            'interest': interest_configs[0] if interest_configs else None,
            'additional_costs': additional_costs,
            'duty_rate_percent': 0  # Will be set below
        }

        # Add duty rate input for quick mode
        st.subheader("🛃 Customs Duty Rate")
        duty_rate_input = st.number_input(
            "Duty Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            help="Enter the customs duty rate as a percentage"
        )
        selected_configs['duty_rate_percent'] = duty_rate_input

    else:  # Precise Mode
        st.info("🎯 **Precise Mode**: Select specific configurations for accurate calculations")
        
        # Configuration Selection Interface
        st.subheader("📋 Configuration Selection")
        
        # Create tabs for different configuration types
        config_tabs = st.tabs([
            "Material & Supplier", "Locations & Operations", 
            "Packaging & Repacking", "Transport & CO₂", 
            "Warehouse & Costs"
        ])

        # Tab 1: Material & Supplier
        with config_tabs[0]:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📦 Materials Selection")
                if materials:
                    selected_material_ids = st.multiselect(
                        "Select Materials:",
                        options=[m['material_no'] for m in materials],
                        default=[m['material_no'] for m in materials[:3]],
                        format_func=lambda x: f"{x} - {next(m['material_desc'] for m in materials if m['material_no'] == x)}"
                    )
                else:
                    selected_material_ids = []
                    st.warning("No materials available")
            
            with col2:
                st.markdown("### 🏭 Suppliers Selection")
                if suppliers:
                    selected_supplier_ids = st.multiselect(
                        "Select Suppliers:",
                        options=[s['vendor_id'] for s in suppliers],
                        default=[s['vendor_id'] for s in suppliers[:3]],
                        format_func=lambda x: f"{x} - {next(s['vendor_name'] for s in suppliers if s['vendor_id'] == x)}"
                    )
                else:
                    selected_supplier_ids = []
                    st.warning("No suppliers available")

            # Generate Material-Supplier pairs
            if selected_material_ids and selected_supplier_ids:
                selected_materials = [m for m in materials if m['material_no'] in selected_material_ids]
                selected_suppliers = [s for s in suppliers if s['vendor_id'] in selected_supplier_ids]
                
                for material in selected_materials:
                    for supplier in selected_suppliers:
                        pair = {
                            'material': material,
                            'supplier': supplier,
                            'pair_id': f"{material['material_no']}_{supplier['vendor_id']}",
                            'display_name': f"{material['material_no']} - {material['material_desc']} | {supplier['vendor_id']} - {supplier['vendor_name']}"
                        }
                        selected_material_supplier_pairs.append(pair)
                
                st.success(f"✅ Generated {len(selected_material_supplier_pairs)} Material-Supplier combinations")

        # Tab 2: Locations & Operations
        with config_tabs[1]:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📍 Location Configuration")
                if locations:
                    location_options = [f"{loc['plant']} - {loc['country']} ({loc['distance']} km)" 
                                     for loc in locations]
                    selected_location_idx = st.selectbox(
                        "Select Location:",
                        range(len(locations)),
                        format_func=lambda x: location_options[x]
                    )
                    selected_configs['location'] = locations[selected_location_idx]
                else:
                    st.warning("No locations configured")
                    selected_configs['location'] = None
            
            with col2:
                st.markdown("### ⚙️ Operations Configuration")
                if operations:
                    ops_options = [f"{op['incoterm_code']} @ {op['incoterm_place']} | {op['currency']} | {op['lead_time']}d lead time" 
                                 for op in operations]
                    selected_ops_idx = st.selectbox(
                        "Select Operations:",
                        range(len(operations)),
                        format_func=lambda x: ops_options[x]
                    )
                    selected_configs['operations'] = operations[selected_ops_idx]
                else:
                    st.warning("No operations configured")
                    selected_configs['operations'] = None

        # Tab 3: Packaging & Repacking
        with config_tabs[2]:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📦 Packaging Configuration")
                if packaging_configs:
                    pkg_options = [f"{pkg['box_type']} | {pkg['pallet_type']} | SP: {pkg['sp_needed']}" 
                                 for pkg in packaging_configs]
                    selected_pkg_idx = st.selectbox(
                        "Select Packaging:",
                        range(len(packaging_configs)),
                        format_func=lambda x: pkg_options[x]
                    )
                    selected_configs['packaging'] = packaging_configs[selected_pkg_idx]
                    
                    # Show packaging details
                    pkg = selected_configs['packaging']
                    st.caption(f"Fill/Box: {pkg['fill_qty_box']} | Tooling: €{pkg['tooling_cost']}")
                else:
                    st.error("No packaging configurations available")
                    selected_configs['packaging'] = None
            
            with col2:
                st.markdown("### 🔄 Repacking Configuration")
                if repacking_configs:
                    rep_options = [f"{rep['pcs_weight']} | {rep['packaging_one_way']}" 
                                 for rep in repacking_configs]
                    selected_rep_idx = st.selectbox(
                        "Select Repacking:",
                        range(len(repacking_configs)),
                        format_func=lambda x: rep_options[x]
                    )
                    selected_configs['repacking'] = repacking_configs[selected_rep_idx]
                else:
                    st.info("No repacking configurations (costs will be zero)")
                    selected_configs['repacking'] = None

        # Tab 4: Transport & CO₂
        with config_tabs[3]:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🚚 Transport Configuration")
                if transport_configs:
                    trans_options = []
                    for trans in transport_configs:
                        if trans.get('auto_calculate', False):
                            trans_options.append(f"{trans['mode1']} | Auto-calculated | SF: {trans['stack_factor']}")
                        else:
                            trans_options.append(f"{trans['mode1']} | €{trans['cost_lu']:.2f}/LU | SF: {trans['stack_factor']}")
                    
                    selected_trans_idx = st.selectbox(
                        "Select Transport:",
                        range(len(transport_configs)),
                        format_func=lambda x: trans_options[x]
                    )
                    selected_configs['transport'] = transport_configs[selected_trans_idx]
                else:
                    st.error("No transport configurations available")
                    selected_configs['transport'] = None
            
            with col2:
                st.markdown("### 🌱 CO₂ Configuration")
                if co2_configs:
                    co2_options = [f"€{co2['cost_per_ton']:.0f}/ton | Factor: {co2['co2_conversion_factor']}" 
                                 for co2 in co2_configs]
                    selected_co2_idx = st.selectbox(
                        "Select CO₂ Config:",
                        range(len(co2_configs)),
                        format_func=lambda x: co2_options[x]
                    )
                    selected_configs['co2'] = co2_configs[selected_co2_idx]
                else:
                    st.error("No CO₂ configurations available")
                    selected_configs['co2'] = None
            
            with col3:
                st.markdown("### 🛃 Customs Configuration")
                # Direct duty rate input instead of customs config selection
                duty_rate_input = st.number_input(
                    "Duty Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=0.1,
                    help="Enter the customs duty rate as a percentage"
                )
                selected_configs['duty_rate_percent'] = duty_rate_input

        # Tab 5: Warehouse & Additional Costs
        with config_tabs[4]:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🏗️ Warehouse Configuration")
                if warehouse_configs:
                    wh_options = [f"€{wh['cost_per_loc']:.2f}/location/month" for wh in warehouse_configs]
                    selected_wh_idx = st.selectbox(
                        "Select Warehouse:",
                        range(len(warehouse_configs)),
                        format_func=lambda x: wh_options[x]
                    )
                    selected_configs['warehouse'] = warehouse_configs[selected_wh_idx]
                else:
                    st.error("No warehouse configurations available")
                    selected_configs['warehouse'] = None
            
            with col2:
                st.markdown("### 💰 Interest Configuration")
                if interest_configs:
                    int_options = [f"{intr['rate']:.2f}% annual" for intr in interest_configs]
                    selected_int_idx = st.selectbox(
                        "Select Interest:",
                        range(len(interest_configs)),
                        format_func=lambda x: int_options[x]
                    )
                    selected_configs['interest'] = interest_configs[selected_int_idx]
                else:
                    st.info("No interest configurations")
                    selected_configs['interest'] = None
            
            with col3:
                st.markdown("### ➕ Additional Costs")
                if additional_costs:
                    selected_additional_indices = st.multiselect(
                        "Select Additional Costs:",
                        range(len(additional_costs)),
                        default=list(range(len(additional_costs))),
                        format_func=lambda x: f"{additional_costs[x]['cost_name']}: €{additional_costs[x]['cost_value']:.2f}"
                    )
                    selected_configs['additional_costs'] = [additional_costs[i] for i in selected_additional_indices]
                else:
                    st.info("No additional costs configured")
                    selected_configs['additional_costs'] = []

    # Configuration Summary
    if selected_material_supplier_pairs:
        st.markdown("---")
        st.subheader("📊 Selected Configuration Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Material-Supplier Pairs:** {len(selected_material_supplier_pairs)}")
            location_name = selected_configs.get('location', {}).get('plant', 'Not selected') if selected_configs.get('location') else 'Not selected'
            st.write(f"**Location:** {location_name}")
            operations_name = selected_configs.get('operations', {}).get('incoterm_code', 'Not selected') if selected_configs.get('operations') else 'Not selected'
            st.write(f"**Operations:** {operations_name}")
            packaging_name = selected_configs.get('packaging', {}).get('box_type', 'Not selected') if selected_configs.get('packaging') else 'Not selected'
            st.write(f"**Packaging:** {packaging_name}")
        
        with col2:
            transport_name = selected_configs.get('transport', {}).get('mode1', 'Not selected') if selected_configs.get('transport') else 'Not selected'
            st.write(f"**Transport:** {transport_name}")
            co2_cost = selected_configs.get('co2', {}).get('cost_per_ton', 0) if selected_configs.get('co2') else 0
            st.write(f"**CO₂:** €{co2_cost}/ton")
            warehouse_cost = selected_configs.get('warehouse', {}).get('cost_per_loc', 0) if selected_configs.get('warehouse') else 0
            st.write(f"**Warehouse:** €{warehouse_cost}/loc")
            duty_rate = selected_configs.get('duty_rate_percent', 0)
            st.write(f"**Duty Rate:** {duty_rate}%")
        
        with col3:
            repacking_name = selected_configs.get('repacking', {}).get('pcs_weight', 'Not selected') if selected_configs.get('repacking') else 'Not selected'
            st.write(f"**Repacking:** {repacking_name}")
            interest_rate = selected_configs.get('interest', {}).get('rate', 0) if selected_configs.get('interest') else 0
            st.write(f"**Interest:** {interest_rate}%")
            additional_total = sum(c['cost_value'] for c in selected_configs.get('additional_costs', []))
            st.write(f"**Additional Costs:** €{additional_total:.2f}")

        # Validation
        required_configs = ['packaging', 'transport', 'warehouse', 'co2']
        missing_required = [cfg for cfg in required_configs if not selected_configs.get(cfg)]
        
        if missing_required:
            st.error(f"❌ Missing required configurations: {', '.join(missing_required)}")
            return
        else:
            st.success("✅ All required configurations selected")

    # Export Format Selection
    st.markdown("---")
    st.subheader("📁 Export Settings")
    export_format = st.selectbox(
        "Export Format", options=["Formatted Excel", "CSV", "JSON"]
    )
    show_detailed_breakdown = st.checkbox("Show Detailed Breakdown", value=True)

    # Run Calculation
    if st.button("🚀 Calculate Logistics Costs", type="primary", use_container_width=True):
        if not selected_material_supplier_pairs:
            st.error("Please select at least one Material-Supplier pair")
            return
            
        with st.spinner("Calculating logistics costs..."):
            try:
                results = []
                
                # Calculate for each selected pair with selected configurations
                for pair in selected_material_supplier_pairs:
                    material = pair['material']
                    supplier = pair['supplier']
                    
                    # Calculate costs using selected configurations and duty rate
                    result = calculator.calculate_total_logistics_cost(
                        material=material,
                        supplier=supplier,
                        packaging_config=selected_configs['packaging'],
                        transport_config=selected_configs['transport'],
                        warehouse_config=selected_configs['warehouse'],
                        repacking_config=selected_configs['repacking'],
                        duty_rate_percent=selected_configs.get('duty_rate_percent', 0),  # Use duty rate directly
                        co2_config=selected_configs['co2'],
                        additional_costs=selected_configs['additional_costs'],
                        operations_config=selected_configs['operations'],
                        location_config=selected_configs['location'],
                        inventory_config=selected_configs['interest']
                    )
                    
                    if result:
                        results.append(result)
                
                if results:
                    st.session_state.calculation_results = results
                    st.success(f"✅ Calculation completed! {len(results)} configurations processed.")
                    
                    errors = calculator.get_calculation_errors()
                    if errors:
                        with st.expander("⚠️ Calculation Warnings"):
                            for error in errors:
                                st.warning(error)
                else:
                    st.error("❌ No valid calculations could be performed. Please check your configurations.")
                    errors = calculator.get_calculation_errors()
                    if errors:
                        st.error("Calculation errors:")
                        for error in errors:
                            st.error(f"• {error}")
                    
            except Exception as e:
                st.error(f"❌ Error during calculation: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
                return

    # Display Results (rest of the code remains the same)
    if 'calculation_results' in st.session_state and st.session_state.calculation_results:
        results = st.session_state.calculation_results
        st.markdown("---")
        st.subheader("📈 Calculation Results")

        # Summary metrics
        total_configurations = len(results)
        total_costs = [r['total_cost_per_piece'] for r in results if r.get('total_cost_per_piece') is not None]
        
        if total_costs:
            avg_total_cost = sum(total_costs) / len(total_costs)
            min_cost = min(total_costs)
            max_cost = max(total_costs)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Configurations", total_configurations)
            col2.metric("Average Cost/Piece", f"€{avg_total_cost:.3f}")
            col3.metric("Min Cost/Piece", f"€{min_cost:.3f}")
            col4.metric("Max Cost/Piece", f"€{max_cost:.3f}")

        # Results Table
        st.subheader("Summary Results")
        
        # Create summary dataframe
        summary_data = []
        for r in results:
            summary_data.append({
                'Material ID': r.get('material_id', ''),
                'Material Description': r.get('material_desc', ''),
                'Supplier ID': r.get('supplier_id', ''),
                'Supplier Name': r.get('supplier_name', ''),
                'Total Cost/Piece': f"€{r.get('total_cost_per_piece', 0):.3f}",
                'Packaging Cost': f"€{r.get('packaging_cost_per_piece', 0):.3f}",
                'Transport Cost': f"€{r.get('transport_cost_per_piece', 0):.3f}",
                'Warehouse Cost': f"€{r.get('warehouse_cost_per_piece', 0):.3f}",
                'CO₂ Cost': f"€{r.get('co2_cost_per_piece', 0):.3f}",
                'Logistics cost supplier (pcs)': f"€{r.get('total_cost_per_piece', 0):.3f}",
                'Logistics cost supplier (year)': f"€{r.get('total_annual_cost', 0):,.0f}"
            })
        
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True)

        # Export functionality and comparison analysis remain the same as before...
        # (The rest of the code for export and detailed breakdown remains unchanged)
        
        # Export functionality (keep existing export logic)
        st.markdown("---")
        st.subheader("📁 Export Results")
        
        # Create export options based on selected format
        if export_format == "Formatted Excel":
            st.info("📋 **Formatted Excel Export** - Creates a professional report matching the logistics cost calculation template with proper formatting, colors, and structure.")
            
            # Allow user to select which result to export (if multiple)
            if len(results) > 1:
                result_options = []
                for i, r in enumerate(results):
                    material_desc = f"{r.get('material_id', '')} - {r.get('material_desc', '')}"
                    supplier_desc = f"{r.get('supplier_id', '')} - {r.get('supplier_name', '')}"
                    result_options.append(f"{material_desc} | {supplier_desc}")
                
                selected_result_idx = st.selectbox(
                    "Select configuration to export:",
                    range(len(results)),
                    format_func=lambda x: result_options[x]
                )
                selected_result = results[selected_result_idx]
            else:
                selected_result = results[0]
            
            # Export settings
            col1, col2, col3 = st.columns(3)
            with col1:
                plant_id = st.text_input("Plant ID", value="1051")
            with col2:
                version = st.text_input("Version", value="1.5.5")
            with col3:
                created_by = st.text_input("Created by", value="System")
            
            if st.button("📊 Generate Formatted Excel Report", type="primary"):
                try:
                    excel_buffer = excel_exporter.create_logistics_report(
                        selected_result, 
                        plant_id=plant_id, 
                        version=version, 
                        created_by=created_by
                    )
                    
                    # Create filename
                    material_id = selected_result.get('material_id', 'Material')
                    supplier_id = selected_result.get('supplier_id', 'Supplier')
                    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"Logistics_Cost_Report_{material_id}_{supplier_id}_{timestamp}.xlsx"
                    
                    st.download_button(
                        label="📥 Download Formatted Excel Report",
                        data=excel_buffer,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success("✅ Formatted Excel report generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating formatted Excel: {str(e)}")
        
        elif export_format == "CSV":
            df_export = pd.DataFrame(results)
            csv_data = df_export.to_csv(index=False)
            st.download_button(
                label="📄 Download Full Results CSV",
                data=csv_data,
                file_name=f"logistics_costs_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        elif export_format == "JSON":
            json_data = json.dumps(results, indent=2, default=str)
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"logistics_costs_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

        # Rest of the detailed breakdown and comparison code remains the same...
    else:
        st.info("No calculation results available. Please run the calculation first.")

if __name__ == "__main__":
    main()