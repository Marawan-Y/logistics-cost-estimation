import streamlit as st
import pandas as pd
from utils.calculations import LogisticsCostCalculator
from utils.data_manager import DataManager
import json

st.set_page_config(page_title="Cost Calculation", page_icon="💰")

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
    materials         = data_manager.get_materials()
    suppliers         = data_manager.get_suppliers()
    locations         = data_manager.get_locations() if hasattr(data_manager, 'get_locations') else []
    operations        = data_manager.get_operations() if hasattr(data_manager, 'get_operations') else []
    pcs_prices        = data_manager.get_pcs_prices() if hasattr(data_manager, 'get_pcs_prices') else []
    packaging_configs = data_manager.get_packaging()
    repacking_configs = data_manager.get_repacking() if hasattr(data_manager, 'get_repacking') else []
    customs_configs   = data_manager.get_customs() if hasattr(data_manager, 'get_customs') else []
    transport_configs = data_manager.get_transport()
    co2_configs       = data_manager.get_co2() if hasattr(data_manager, 'get_co2') else []
    warehouse_configs = data_manager.get_warehouse()
    inventory_configs = data_manager.get_inventory() if hasattr(data_manager, 'get_inventory') else []
    interest_configs  = data_manager.get_interest() if hasattr(data_manager, 'get_interest') else []
    additional_costs  = data_manager.get_additional_costs() if hasattr(data_manager, 'get_additional_costs') else []

    # --- Check Required Data ---
    missing_configs = []
    if not materials:          missing_configs.append("Materials")
    if not suppliers:          missing_configs.append("Suppliers")
    if not packaging_configs:  missing_configs.append("Packaging")
    if not transport_configs:  missing_configs.append("Transport")
    if not warehouse_configs:  missing_configs.append("Warehouse")
    # (optionally add more if you want to require others before calculating)

    if missing_configs:
        st.error(f"⚠️ Missing configurations: {', '.join(missing_configs)}")
        st.info("Please configure all required data before performing calculations.")
        return

    # --- Metrics Overview ---
    st.subheader("📊 Configuration Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Materials", len(materials))
    col2.metric("Suppliers", len(suppliers))
    col3.metric("Packaging", len(packaging_configs))
    col4.metric("Transport", len(transport_configs))
    col5.metric("Warehouse", len(warehouse_configs))

    st.markdown("---")

    # --- Calculation Controls ---
    st.subheader("🔧 Calculation Settings")
    col1, col2 = st.columns(2)
    with col1:
        calculation_mode = st.selectbox(
            "Calculation Mode",
            options=["All Configurations", "Selected Material-Supplier Pairs"]
        )
        include_co2_costs = st.checkbox("Include CO₂ Costs", value=True)
    with col2:
        export_format = st.selectbox(
            "Export Format", options=["CSV", "Excel", "JSON"]
        )
        show_detailed_breakdown = st.checkbox("Show Detailed Breakdown", value=True)

    # --- Select pairs if needed ---
    if calculation_mode == "Selected Material-Supplier Pairs":
        st.subheader("Select Material-Supplier Pairs")
        available_pairs = []
        for material in materials:
            for supplier in suppliers:
                # Check all required configs for this pair (add your own logic for new configs)
                has_packaging = any(p['material_id'] == material['material_no'] and p['supplier_id'] == supplier['vendor_id'] for p in packaging_configs)
                has_transport = any(t['material_id'] == material['material_no'] and t['supplier_id'] == supplier['vendor_id'] for t in transport_configs)
                has_warehouse = any(w['material_id'] == material['material_no'] and w['supplier_id'] == supplier['vendor_id'] for w in warehouse_configs)
                if has_packaging and has_transport and has_warehouse:
                    available_pairs.append({
                        'material': material,
                        'supplier': supplier,
                        'pair_id': f"{material['material_no']}_{supplier['vendor_id']}",
                        'display_name': f"{material['material_no']} - {material['material_desc']} | {supplier['vendor_id']} - {supplier['vendor_name']}"
                    })
        if not available_pairs:
            st.warning("No complete material-supplier pairs found.")
            return
        selected_pairs = st.multiselect(
            "Select Material-Supplier Pairs for Calculation",
            options=[pair['pair_id'] for pair in available_pairs],
            default=[pair['pair_id'] for pair in available_pairs],
            format_func=lambda x: next(pair['display_name'] for pair in available_pairs if pair['pair_id'] == x)
        )
        if not selected_pairs:
            st.warning("Please select at least one pair.")
            return

    # --- Run Calculation ---
    if st.button("🚀 Calculate Logistics Costs", type="primary"):
        with st.spinner("Calculating logistics costs..."):
            try:
                # Adapt calculation to include all config data (expand this as your backend calculation grows)
                if calculation_mode == "All Configurations":
                    results = calculator.calculate_all_costs(
                        materials, suppliers, packaging_configs,
                        transport_configs, warehouse_configs,
                        include_co2_costs
                        # Optionally pass new configs here
                    )
                else:
                    # Only selected pairs
                    selected_materials = []
                    selected_suppliers = []
                    selected_packaging = []
                    selected_transport = []
                    selected_warehouse = []
                    for pair_id in selected_pairs:
                        material_id, supplier_id = pair_id.split('_')
                        material  = next(m for m in materials if m['material_no'] == material_id)
                        supplier  = next(s for s in suppliers if s['vendor_id'] == supplier_id)
                        packaging = next(p for p in packaging_configs if p['material_id'] == material_id and p['supplier_id'] == supplier_id)
                        transport = next(t for t in transport_configs if t['material_id'] == material_id and t['supplier_id'] == supplier_id)
                        warehouse = next(w for w in warehouse_configs if w['material_id'] == material_id and w['supplier_id'] == supplier_id)
                        selected_materials.append(material)
                        selected_suppliers.append(supplier)
                        selected_packaging.append(packaging)
                        selected_transport.append(transport)
                        selected_warehouse.append(warehouse)
                    results = calculator.calculate_all_costs(
                        selected_materials, selected_suppliers, selected_packaging,
                        selected_transport, selected_warehouse, include_co2_costs
                        # Optionally pass new configs here
                    )
                if results:
                    st.session_state.calculation_results = results
                    st.success(f"✅ Calculation completed! {len(results)} configs processed.")
                else:
                    st.error("❌ Calculation failed. Please check your configurations.")
                    return
            except Exception as e:
                st.error(f"❌ Error during calculation: {str(e)}")
                return

    # --- Display Results ---
    if 'calculation_results' in st.session_state and st.session_state.calculation_results:
        results = st.session_state.calculation_results
        st.markdown("---")
        st.subheader("📈 Calculation Results")

        # Summary metrics (extend as needed)
        total_configurations = len(results)
        avg_total_cost = sum(r['total_cost_per_piece'] for r in results) / total_configurations
        min_cost = min(r['total_cost_per_piece'] for r in results)
        max_cost = max(r['total_cost_per_piece'] for r in results)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Configurations", total_configurations)
        col2.metric("Average Cost/Piece", f"€{avg_total_cost:.3f}")
        col3.metric("Min Cost/Piece", f"€{min_cost:.3f}")
        col4.metric("Max Cost/Piece", f"€{max_cost:.3f}")

        # --- Results Table (add new columns as you extend the calculation model) ---
        st.subheader("Detailed Results")
        df_results = pd.DataFrame(results)
        column_order = [
            'material_id', 'material_desc', 'supplier_id', 'supplier_name',
            'total_cost_per_piece', 'packaging_cost_per_piece', 'transport_cost_per_piece',
            'warehouse_cost_per_piece', 'co2_cost_per_piece', 'total_annual_cost'
            # Add new cost fields here as needed!
        ]
        display_columns = [col for col in column_order if col in df_results.columns]
        df_display = df_results[display_columns].copy()
        for col in ['total_cost_per_piece', 'packaging_cost_per_piece', 'transport_cost_per_piece', 'warehouse_cost_per_piece', 'co2_cost_per_piece', 'total_annual_cost']:
            if col in df_display.columns:
                if col == 'total_annual_cost':
                    df_display[col] = df_display[col].apply(lambda x: f"€{x:,.0f}")
                else:
                    df_display[col] = df_display[col].apply(lambda x: f"€{x:.3f}")
        column_names = {
            'material_id': 'Material ID',
            'material_desc': 'Material Description',
            'supplier_id': 'Supplier ID',
            'supplier_name': 'Supplier Name',
            'total_cost_per_piece': 'Total Cost/Piece',
            'packaging_cost_per_piece': 'Packaging Cost/Piece',
            'transport_cost_per_piece': 'Transport Cost/Piece',
            'warehouse_cost_per_piece': 'Warehouse Cost/Piece',
            'co2_cost_per_piece': 'CO₂ Cost/Piece',
            'total_annual_cost': 'Total Annual Cost'
            # Add new columns names here as needed!
        }
        df_display = df_display.rename(columns=column_names)
        st.dataframe(df_display, use_container_width=True)

        # --- Detailed Breakdown ---
        if show_detailed_breakdown:
            st.subheader("Detailed Cost Breakdown")
            for i, result in enumerate(results):
                with st.expander(f"{result['material_id']} - {result['material_desc']} | {result['supplier_id']} - {result['supplier_name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Cost Components:**")
                        st.write(f"• Packaging: €{result.get('packaging_cost_per_piece', 0):.3f}")
                        st.write(f"• Transport: €{result.get('transport_cost_per_piece', 0):.3f}")
                        st.write(f"• Warehouse: €{result.get('warehouse_cost_per_piece', 0):.3f}")
                        if include_co2_costs and 'co2_cost_per_piece' in result:
                            st.write(f"• CO₂ Emissions: €{result['co2_cost_per_piece']:.3f}")
                        # Add more breakdowns here as you extend!
                        st.write(f"**Total per Piece: €{result['total_cost_per_piece']:.3f}**")
                    with col2:
                        st.write("**Annual Calculations:**")
                        annual_volume = next((m['annual_volume'] for m in materials if m['material_no'] == result['material_id']), 0)
                        st.write(f"• Annual Volume: {annual_volume:,} pieces")
                        st.write(f"• Total Annual Cost: €{result['total_annual_cost']:,.0f}")
                        total_cost = result['total_cost_per_piece']
                        if total_cost > 0:
                            st.write("**Cost Distribution:**")
                            st.write(f"• Packaging: {(result.get('packaging_cost_per_piece',0)/total_cost)*100:.1f}%")
                            st.write(f"• Transport: {(result.get('transport_cost_per_piece',0)/total_cost)*100:.1f}%")
                            st.write(f"• Warehouse: {(result.get('warehouse_cost_per_piece',0)/total_cost)*100:.1f}%")
                            if include_co2_costs and 'co2_cost_per_piece' in result:
                                st.write(f"• CO₂: {(result['co2_cost_per_piece']/total_cost)*100:.1f}%")

        # --- Export Functionality ---
        st.markdown("---")
        st.subheader("📁 Export Results")
        col1, col2, col3 = st.columns(3)
        if export_format == "CSV":
            csv_data = df_results.to_csv(index=False)
            col1.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"logistics_costs_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        if export_format == "JSON":
            json_data = json.dumps(results, indent=2, default=str)
            col2.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"logistics_costs_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        # Add Excel export if needed

        # --- Comparison Analysis ---
        if len(results) > 1:
            st.markdown("---")
            st.subheader("📊 Comparison Analysis")
            best_config = min(results, key=lambda x: x['total_cost_per_piece'])
            worst_config = max(results, key=lambda x: x['total_cost_per_piece'])
            col1, col2 = st.columns(2)
            with col1:
                st.success("**Best Configuration (Lowest Cost)**")
                st.write(f"Material: {best_config['material_id']} - {best_config['material_desc']}")
                st.write(f"Supplier: {best_config['supplier_id']} - {best_config['supplier_name']}")
                st.write(f"Total Cost: €{best_config['total_cost_per_piece']:.3f}/piece")
                st.write(f"Annual Cost: €{best_config['total_annual_cost']:,.0f}")
            with col2:
                st.error("**Worst Configuration (Highest Cost)**")
                st.write(f"Material: {worst_config['material_id']} - {worst_config['material_desc']}")
                st.write(f"Supplier: {worst_config['supplier_id']} - {worst_config['supplier_name']}")
                st.write(f"Total Cost: €{worst_config['total_cost_per_piece']:.3f}/piece")
                st.write(f"Annual Cost: €{worst_config['total_annual_cost']:,.0f}")
            cost_difference = worst_config['total_cost_per_piece'] - best_config['total_cost_per_piece']
            cost_difference_pct = (cost_difference / best_config['total_cost_per_piece']) * 100 if best_config['total_cost_per_piece'] > 0 else 0
            st.info(f"**Cost Difference:** €{cost_difference:.3f}/piece ({cost_difference_pct:.1f}% higher)")
    else:
        st.info("No calculation results available. Please run the calculation first.")

if __name__ == "__main__":
    main()
