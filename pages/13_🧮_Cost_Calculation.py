import streamlit as st
import pandas as pd
from utils.calculations import LogisticsCostCalculator
from utils.data_manager import DataManager
import json

st.set_page_config(page_title="Cost Calculation", page_icon="💰", layout="wide")

def main():
    st.title("Cost Calculation & Results")
    st.markdown("Calculate total logistics costs and export results")
    st.markdown("---")

    # --- Data Initialization ---
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()

    data_manager = st.session_state.data_manager
    calculator = LogisticsCostCalculator()

    # --- Load All Configurations ---
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

    # --- Check Required Data ---
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

    # --- Metrics Overview ---
    st.subheader("📊 Configuration Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Materials", len(materials))
        st.metric("Suppliers", len(suppliers))
        st.metric("Locations", len(locations))
    with col2:
        st.metric("Operations", len(operations))
        st.metric("Packaging", len(packaging_configs))
        st.metric("Repacking", len(repacking_configs))
    with col3:
        st.metric("Customs", len(customs_configs))
        st.metric("Transport", len(transport_configs))
        st.metric("CO₂", len(co2_configs))
    with col4:
        st.metric("Warehouse", len(warehouse_configs))
        st.metric("Interest", len(interest_configs))
        st.metric("Additional", len(additional_costs))

    st.markdown("---")

    # --- Calculation Controls ---
    st.subheader("🔧 Calculation Settings")
    col1, col2 = st.columns(2)
    with col1:
        calculation_mode = st.selectbox(
            "Calculation Mode",
            options=["All Material-Supplier Pairs", "Selected Material-Supplier Pairs"]
        )
    with col2:
        export_format = st.selectbox(
            "Export Format", options=["CSV", "Excel", "JSON"]
        )
        show_detailed_breakdown = st.checkbox("Show Detailed Breakdown", value=True)

    # --- Select pairs if needed ---
    selected_pairs = []
    if calculation_mode == "Selected Material-Supplier Pairs":
        st.subheader("Select Material-Supplier Pairs")
        available_pairs = data_manager.get_material_supplier_pairs()
        
        if not available_pairs:
            st.warning("No material-supplier pairs found.")
            return
            
        selected_pair_ids = st.multiselect(
            "Select Material-Supplier Pairs for Calculation",
            options=[pair['pair_id'] for pair in available_pairs],
            default=[pair['pair_id'] for pair in available_pairs[:5]],  # Default to first 5
            format_func=lambda x: next(pair['display_name'] for pair in available_pairs if pair['pair_id'] == x)
        )
        
        if not selected_pair_ids:
            st.warning("Please select at least one pair.")
            return
        
        selected_pairs = [pair for pair in available_pairs if pair['pair_id'] in selected_pair_ids]

    # --- Run Calculation ---
    if st.button("🚀 Calculate Logistics Costs", type="primary"):
        with st.spinner("Calculating logistics costs..."):
            try:
                results = []
                
                # Prepare pairs for calculation
                if calculation_mode == "All Material-Supplier Pairs":
                    pairs_to_calculate = data_manager.get_material_supplier_pairs()
                else:
                    pairs_to_calculate = selected_pairs
                
                # Get singleton configs (first one if exists)
                operations_config = operations[0] if operations else None
                location_config = locations[0] if locations else None
                repacking_config = repacking_configs[0] if repacking_configs else None
                customs_config = customs_configs[0] if customs_configs else None
                co2_config = co2_configs[0] if co2_configs else None
                
                # Calculate for each pair
                for pair in pairs_to_calculate:
                    material = pair['material']
                    supplier = pair['supplier']
                    
                    # Get configs for this pair (using first available for now)
                    packaging_config = packaging_configs[0] if packaging_configs else None
                    transport_config = transport_configs[0] if transport_configs else None
                    warehouse_config = warehouse_configs[0] if warehouse_configs else None
                    
                    if not all([packaging_config, transport_config, warehouse_config]):
                        st.warning(f"Skipping {material['material_no']} - {supplier['vendor_id']}: Missing required configurations")
                        continue
                    
                    # Calculate costs
                    result = calculator.calculate_total_logistics_cost(
                        material=material,
                        supplier=supplier,
                        packaging_config=packaging_config,
                        transport_config=transport_config,
                        warehouse_config=warehouse_config,
                        repacking_config=repacking_config,
                        customs_config=customs_config,
                        co2_config=co2_config,
                        additional_costs=additional_costs,
                        operations_config=operations_config,
                        location_config=location_config,
                        inventory_config=interest_configs[0] if interest_configs else None
                    )
                    
                    if result:
                        results.append(result)
                
                if results:
                    st.session_state.calculation_results = results
                    st.success(f"✅ Calculation completed! {len(results)} configurations processed.")
                    
                    # Show any calculation errors
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

    # --- Display Results ---
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

        # --- Results Table ---
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

        # --- Detailed Breakdown ---
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
                            
                            # Cost distribution pie chart
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

        # --- Export Functionality ---
        st.markdown("---")
        st.subheader("📁 Export Results")
        
        if export_format == "CSV":
            # Create full results dataframe
            df_export = pd.DataFrame(results)
            csv_data = df_export.to_csv(index=False)
            st.download_button(
                label="📄 Download Full Results CSV",
                data=csv_data,
                file_name=f"logistics_costs_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        elif export_format == "Excel":
            # Create Excel file with multiple sheets
            output = pd.ExcelWriter('temp.xlsx', engine='xlsxwriter')
            
            # Summary sheet
            df_summary.to_excel(output, sheet_name='Summary', index=False)
            
            # Detailed results sheet
            df_detailed = pd.DataFrame(results)
            df_detailed.to_excel(output, sheet_name='Detailed Results', index=False)
            
            # Cost breakdown sheet
            cost_breakdown = []
            for r in results:
                cost_breakdown.append({
                    'Material': f"{r.get('material_id')} - {r.get('material_desc')}",
                    'Supplier': f"{r.get('supplier_id')} - {r.get('supplier_name')}",
                    'Packaging Cost': r.get('packaging_cost_per_piece', 0),
                    'Transport Cost': r.get('transport_cost_per_piece', 0),
                    'Warehouse Cost': r.get('warehouse_cost_per_piece', 0),
                    'CO₂ Cost': r.get('co2_cost_per_piece', 0),
                    'Customs Cost': r.get('customs_cost_per_piece', 0),
                    'Repacking Cost': r.get('repacking_cost_per_piece', 0),
                    'Additional Cost': r.get('additional_cost_per_piece', 0),
                    'Total Cost': r.get('total_cost_per_piece', 0)
                })
            df_breakdown = pd.DataFrame(cost_breakdown)
            df_breakdown.to_excel(output, sheet_name='Cost Breakdown', index=False)
            
            output.close()
            
            with open('temp.xlsx', 'rb') as f:
                excel_data = f.read()
            
            st.download_button(
                label="📊 Download Excel Report",
                data=excel_data,
                file_name=f"logistics_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        elif export_format == "JSON":
            json_data = json.dumps(results, indent=2, default=str)
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"logistics_costs_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

        # --- Comparison Analysis ---
        if len(results) > 1:
            st.markdown("---")
            st.subheader("📊 Comparison Analysis")
            
            # Find best and worst configs
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
                
    else:
        st.info("No calculation results available. Please run the calculation first.")

if __name__ == "__main__":
    main()