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
    customs_configs = data_manager.get_customs()
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
        "Customs": len(customs_configs),
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
                if customs_configs: 
                    st.write(f"**Customs:** Preference {customs_configs[0]['pref_usage']}")
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
            'customs': customs_configs[0] if customs_configs else None,
            'transport': transport_configs[0] if transport_configs else None,
            'co2': co2_configs[0] if co2_configs else None,
            'warehouse': warehouse_configs[0] if warehouse_configs else None,
            'interest': interest_configs[0] if interest_configs else None,
            'additional_costs': additional_costs
        }

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
                if customs_configs:
                    customs_options = [f"Preference: {cust['pref_usage']} | Duty: {cust['duty_rate']}%" 
                                     for cust in customs_configs]
                    selected_customs_idx = st.selectbox(
                        "Select Customs:",
                        range(len(customs_configs)),
                        format_func=lambda x: customs_options[x]
                    )
                    selected_configs['customs'] = customs_configs[selected_customs_idx]
                else:
                    st.info("No customs configurations (costs will be zero)")
                    selected_configs['customs'] = None

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
            st.write(f"**Location:** {selected_configs.get('location', {}).get('plant', 'Not selected')}")
            st.write(f"**Operations:** {selected_configs.get('operations', {}).get('incoterm_code', 'Not selected')}")
            st.write(f"**Packaging:** {selected_configs.get('packaging', {}).get('box_type', 'Not selected')}")
        
        with col2:
            st.write(f"**Transport:** {selected_configs.get('transport', {}).get('mode1', 'Not selected')}")
            st.write(f"**CO₂:** €{selected_configs.get('co2', {}).get('cost_per_ton', 0)}/ton")
            st.write(f"**Warehouse:** €{selected_configs.get('warehouse', {}).get('cost_per_loc', 0)}/loc")
            st.write(f"**Customs:** {selected_configs.get('customs', {}).get('pref_usage', 'Not selected')}")
        
        with col3:
            st.write(f"**Repacking:** {selected_configs.get('repacking', {}).get('pcs_weight', 'Not selected')}")
            st.write(f"**Interest:** {selected_configs.get('interest', {}).get('rate', 0)}%")
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
                    
                    # Calculate costs using selected configurations
                    result = calculator.calculate_total_logistics_cost(
                        material=material,
                        supplier=supplier,
                        packaging_config=selected_configs['packaging'],
                        transport_config=selected_configs['transport'],
                        warehouse_config=selected_configs['warehouse'],
                        repacking_config=selected_configs['repacking'],
                        customs_config=selected_configs['customs'],
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

    # Display Results (keep existing results display logic)
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

        # Comparison Analysis (keep existing comparison logic if multiple results)
        if len(results) > 1:
            st.markdown("---")
            st.subheader("📊 Comparison Analysis")
            
            valid_results = [r for r in results if r.get('total_cost_per_piece') is not None]
            if valid_results:
                best_config = min(valid_results, key=lambda x: x['total_cost_per_piece'])
                worst_config = max(valid_results, key=lambda x: x['total_cost_per_piece'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.success("**🏆 Best Configuration (Lowest Cost)**")
                    st.write(f"Material: {best_config['material_id']} - {best_config['material_desc']}")
                    st.write(f"Supplier: {best_config['supplier_id']} - {best_config['supplier_name']}")
                    st.write(f"Total Cost: €{best_config['total_cost_per_piece']:.3f}/piece")
                    st.write(f"Annual Cost: €{best_config['total_annual_cost']:,.0f}")
                
                with col2:
                    st.error("**📈 Highest Cost Configuration**")
                    st.write(f"Material: {worst_config['material_id']} - {worst_config['material_desc']}")
                    st.write(f"Supplier: {worst_config['supplier_id']} - {worst_config['supplier_name']}")
                    st.write(f"Total Cost: €{worst_config['total_cost_per_piece']:.3f}/piece")
                    st.write(f"Annual Cost: €{worst_config['total_annual_cost']:,.0f}")
                
                # Cost difference analysis
                cost_difference = worst_config['total_cost_per_piece'] - best_config['total_cost_per_piece']
                cost_difference_pct = (cost_difference / best_config['total_cost_per_piece']) * 100 if best_config['total_cost_per_piece'] > 0 else 0
                
                st.info(f"**💡 Cost Difference:** €{cost_difference:.3f}/piece ({cost_difference_pct:.1f}% higher)")
                
                # Component comparison
                st.subheader("Component Cost Comparison")
                components = ['packaging_cost_per_piece', 'transport_cost_per_piece', 'warehouse_cost_per_piece', 
                             'co2_cost_per_piece', 'customs_cost_per_piece', 'repacking_cost_per_piece']
                
                comparison_data = []
                for comp in components:
                    comp_name = comp.replace('_cost_per_piece', '').replace('_', ' ').title()
                    comparison_data.append({
                        'Component': comp_name,
                        'Best Config': f"€{best_config.get(comp, 0):.3f}",
                        'Worst Config': f"€{worst_config.get(comp, 0):.3f}",
                        'Difference': f"€{worst_config.get(comp, 0) - best_config.get(comp, 0):.3f}"
                    })
                
                df_comparison = pd.DataFrame(comparison_data)
                st.dataframe(df_comparison, use_container_width=True)

        # Detailed breakdown display (keep existing detailed breakdown logic if enabled)
        if show_detailed_breakdown:
            st.subheader("Detailed Cost Breakdown")
            
            for i, result in enumerate(results):
                material_desc = f"{result.get('material_id', '')} - {result.get('material_desc', '')}"
                supplier_desc = f"{result.get('supplier_id', '')} - {result.get('supplier_name', '')}"
                
                with st.expander(f"📦 {material_desc} | 🏭 {supplier_desc}"):
                    # Create tabs for different sections
                    tab1, tab2, tab3, tab4 = st.tabs(["Cost Components", "Material Details", "Supply Chain", "Packaging Details"])
                    
                    with tab1:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**💰 Cost Breakdown per Piece:**")
                            st.write(f"• Packaging: €{result.get('packaging_cost_per_piece', 0):.3f}")
                            st.write(f"• Repacking: €{result.get('repacking_cost_per_piece', 0):.3f}")
                            st.write(f"• Transport: €{result.get('transport_cost_per_piece', 0):.3f}")
                            st.write(f"• Warehouse: €{result.get('warehouse_cost_per_piece', 0):.3f}")
                            st.write(f"• Customs: €{result.get('customs_cost_per_piece', 0):.3f}")
                            st.write(f"• CO₂: €{result.get('co2_cost_per_piece', 0):.3f}")
                            st.write(f"• Additional: €{result.get('additional_cost_per_piece', 0):.3f}")
                            st.write(f"**🎯 Total per Piece: €{result.get('total_cost_per_piece', 0):.3f}**")
                        
                        with col2:
                            st.write("**📊 Annual Calculations:**")
                            st.write(f"• Annual Volume: {result.get('Annual Volume', 0):,} pieces")
                            st.write(f"• Total Annual Cost: €{result.get('total_annual_cost', 0):,.0f}")
                            
                            # Cost distribution
                            total_cost = result.get('total_cost_per_piece', 0)
                            if total_cost > 0:
                                st.write("**📈 Cost Distribution:**")
                                costs = {
                                    'Packaging': result.get('packaging_cost_per_piece', 0),
                                    'Transport': result.get('transport_cost_per_piece', 0),
                                    'Warehouse': result.get('warehouse_cost_per_piece', 0),
                                    'CO₂': result.get('co2_cost_per_piece', 0),
                                    'Customs': result.get('customs_cost_per_piece', 0),
                                    'Repacking': result.get('repacking_cost_per_piece', 0),
                                    'Additional': result.get('additional_cost_per_piece', 0)
                                }
                                for component, cost in costs.items():
                                    if cost > 0:
                                        percentage = (cost / total_cost) * 100
                                        st.write(f"• {component}: {percentage:.1f}%")
                    
                    with tab2:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**📦 Material Information:**")
                            st.write(f"• Project: {result.get('Project Name', 'N/A')}")
                            st.write(f"• Material ID: {result.get('material_id', 'N/A')}")
                            st.write(f"• Description: {result.get('material_desc', 'N/A')}")
                            st.write(f"• Annual Volume: {result.get('Annual Volume', 0):,}")
                            st.write(f"• Price per Piece: €{result.get('Price (Pcs)', 0):.2f}")
                            st.write(f"• SOP: {result.get('SOP', 'N/A')}")
                        
                        with col2:
                            st.write("**🏭 Supplier Information:**")
                            st.write(f"• Supplier ID: {result.get('supplier_id', 'N/A')}")
                            st.write(f"• Name: {result.get('supplier_name', 'N/A')}")
                            st.write(f"• City: {result.get('City of Manufacture', 'N/A')}")
                            st.write(f"• ZIP: {result.get('Vendor ZIP', 'N/A')}")
                            st.write(f"• Deliveries/Month: {result.get('Deliveries per Month', 0)}")
                    
                    with tab3:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**🚚 Transport & Operations:**")
                            st.write(f"• Transport Mode: {result.get('Transport type', 'N/A')}")
                            st.write(f"• Transport Cost/LU: €{result.get('Transport cost per LU', 0):.2f}")
                            st.write(f"• Incoterm: {result.get('Incoterm code', 'N/A')}")
                            st.write(f"• Incoterm Place: {result.get('Incoterm Named Place', 'N/A')}")
                            st.write(f"• Lead Time: {result.get('Lead time (d)', 0)} days")
                        
                        with col2:
                            st.write("**🏬 Warehouse & Inventory:**")
                            st.write(f"• Safety Stock (pallets): {result.get('safety_stock_no_pal', 0):.1f}")
                            st.write(f"• Call-off Type: {result.get('Call-off transfer type', 'N/A')}")
                            st.write(f"• Sub-supplier Used: {result.get('Sub-Supplier Used', 'N/A')}")
                            st.write(f"• Duty Rate: {result.get('Duty Rate (% Of pcs price)', 0):.1f}%")
                    
                    with tab4:
                        st.write("**📦 Packaging Configuration:**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"• Packaging Type: {result.get('packaging_type', 'N/A')}")
                            st.write(f"• Filling/Box: {result.get('Filling degree per box', 0)} pcs")
                            st.write(f"• Filling/Pallet: {result.get('Filling degree per pallet', 0)} pcs")
                            st.write(f"• Special Packaging: {result.get('Special packaging required', 'N/A')}")
                            st.write(f"• Packaging Loop: {result.get('Packaging Loop', 0)} days")
                        
                        with col2:
                            st.write("**🔄 Packaging Loop Details:**")
                            loop_stages = [
                                ('Goods Receipt', 'goods_receipt'),
                                ('Stock Raw Materials', 'stock_raw_materials'),
                                ('Production', 'production'),
                                ('Empties Return', 'empties_return'),
                                ('Cleaning', 'cleaning'),
                                ('Dispatch', 'dispatch')
                            ]
                            for label, key in loop_stages:
                                value = result.get(key, 0)
                                if value > 0:
                                    st.write(f"• {label}: {value} days")
                
    else:
        st.info("No calculation results available. Please run the calculation first.")

if __name__ == "__main__":
    main()