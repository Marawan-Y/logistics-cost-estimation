# pages/6_Packaging_Cost.py
import streamlit as st
from utils.validators import PackagingValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Packaging Cost", page_icon="📦")

def main():
    st.title("Packaging Cost")
    st.markdown("Configure packaging-related cost parameters")
    st.markdown("---")

    # Initialize DataManager & Validator
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    dm = st.session_state.data_manager
    val = PackagingValidator()

    # ---------------- Add New Packaging Record ----------------
    with st.form("pkg_form"):
        st.subheader("Add New Packaging Record")

        # 6.1 Per‐Part Costs
        st.markdown("**6.1 ‒ Per Part (per piece)**")
        col1, col2 = st.columns(2)
        with col1:
            pack_maint = st.number_input(
                "Packaging maintenance (€ per pcs)",
                min_value=0.0, step=0.001, format="%.3f",
                help="Maintenance cost per piece"
            )
        with col2:
            empties_scrap = st.number_input(
                "Empties scrapping (€ per pcs)",
                min_value=0.0, step=0.001, format="%.3f",
                help="Scrapping cost per piece (cardboard/paper)"
            )

        st.markdown("---")
        # 6.2 Standard Packaging (Plant)
        st.markdown("**6.2 ‒ Standard Packaging (Plant)**")
        col1, col2 = st.columns(2)
        with col1:
            box_type = st.selectbox(
                "Packaging Type (box)",
                ["Cardboard", "Plastic", "Wooden", "Metal"],
                help="Select the type of box used"
            )
            fill_qty_box = st.number_input(
                "Filling Quantity (pcs/box)",
                min_value=0, step=1,
                help="Number of pieces per box"
            )
        with col2:
            pallet_type = st.selectbox(
                "LU Type (pallet)",
                ["EUR‐pallet", "Industrial", "Custom"],
                help="Select pallet type"
            )
            fill_qty_lu = st.number_input(
                "Filling Qty (pcs/LU) overseas",
                min_value=0, step=1,
                help="Number of pieces per load unit for overseas shipping"
            )
        add_pack_price = st.number_input(
            "Price additional packaging (inlays, etc.) €",
            min_value=0.0, step=0.01, format="%.2f",
            help="Extra packaging costs (e.g., inlays)"
        )

        st.markdown("---")
        # 6.3 Special Packaging (CoC)
        st.markdown("**6.3 ‒ Special Packaging (CoC)**")
        col1, col2 = st.columns(2)
        with col1:
            sp_needed = st.selectbox(
                "Special packaging needed?",
                ["Yes", "No"],
                help="Does this material require special packaging?"
            )
            sp_type = st.selectbox(
                "Special packaging type",
                ["Tray", "Blister", "Box", "Pallet Cover", "Other"],
                help="Select the special packaging type"
            )
            fill_qty_tray = st.number_input(
                "Filling Qty (pcs/tray)",
                min_value=0, step=1,
                help="Number of pieces per tray"
            )
            tooling_cost = st.number_input(
                "Tooling cost (€)",
                min_value=0.0, step=0.01, format="%.2f",
                help="One‐time tooling cost for special packaging"
            )
        with col2:
            add_sp_pack = st.selectbox(
                "Additional packaging needed (pallet, cover)?",
                ["Yes", "No"],
                help="Does special packaging require extra pallet or cover?"
            )
            trays_per_sp_pal = st.number_input(
                "No. of Trays per SP‐pallet",
                min_value=0, step=1,
                help="Trays per special‐packaging pallet"
            )
            sp_pallets_per_lu = st.number_input(
                "No. of SP‐pallets per LU",
                min_value=0, step=1,
                help="Special packaging pallets per load unit"
            )

        st.markdown("---")
        # 6.4 Total Packaging Loop (Qty of LUs at Each Stage)
        st.markdown("**6.4 ‒ Total Packaging Loop (Quantity of LUs)**")
        loop_fields = [
            "goods receipt", "stock raw materials", "production",
            "empties return", "cleaning", "dispatch",
            "empties transit (KB → Supplier)", "empties receipt (at Supplier)",
            "empties in stock (Supplier)", "production (contrary loop)",
            "stock finished parts", "dispatch (finished parts)",
            "transit (Supplier → KB)"
        ]
        loop_data = {}
        cols = st.columns(4)
        for idx, field in enumerate(loop_fields):
            loop_data[field] = cols[idx % 4].number_input(
                field.title(),
                min_value=0, step=1,
                help=f"Number of LUs for {field}"
            )

        submitted = st.form_submit_button("Add Packaging Cost", type="primary")
        if submitted:
            pkg = {
                "pack_maint": pack_maint,
                "empties_scrap": empties_scrap,
                "box_type": box_type,
                "fill_qty_box": fill_qty_box,
                "pallet_type": pallet_type,
                "fill_qty_lu": fill_qty_lu,
                "add_pack_price": add_pack_price,
                "sp_needed": sp_needed,
                "sp_type": sp_type,
                "fill_qty_tray": fill_qty_tray,
                "tooling_cost": tooling_cost,
                "add_sp_pack": add_sp_pack,
                "trays_per_sp_pal": trays_per_sp_pal,
                "sp_pallets_per_lu": sp_pallets_per_lu,
                "loop_data": loop_data
            }
            res = val.validate_packaging(pkg)
            if res["is_valid"]:
                dm.add_packaging(pkg)
                st.success("Packaging record added successfully!")
                st.rerun()
            else:
                for e in res["errors"]:
                    st.error(e)

    st.markdown("---")

    # ---------------- Display Existing Packaging Records ----------------
    st.subheader("Existing Packaging Records")
    packaging_list = dm.get_packaging()
    if not packaging_list:
        st.info("No packaging records configured yet.")
    for i, pkg in enumerate(packaging_list):
        header = f"{pkg['box_type']} | {pkg['pallet_type']} | Special: {pkg['sp_needed']}"
        with st.expander(header):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**Packaging maintenance:** €{pkg['pack_maint']:.3f} per pcs")
                st.write(f"**Empties scrapping:** €{pkg['empties_scrap']:.3f} per pcs")
                st.write(f"**Add. packaging price:** €{pkg['add_pack_price']:.2f}")
                st.write(f"**Special needed:** {pkg['sp_needed']}")
                st.write(f"**SP Type:** {pkg['sp_type']}")
                st.write(f"**Tooling cost:** €{pkg['tooling_cost']:.2f}")
                st.write(f"**Additional SP needed:** {pkg['add_sp_pack']}")
                st.write(f"**Trays/SP‐pallet:** {pkg['trays_per_sp_pal']}")
                st.write(f"**SP‐pallets/LU:** {pkg['sp_pallets_per_lu']}")
                st.write("**Loop Data (LUs):**")
                for stage, qty in pkg["loop_data"].items():
                    st.write(f"  • {stage.title()}: {qty}")
            with col2:
                if st.button("Edit", key=f"edit_pkg_{i}"):
                    st.session_state[f"edit_pkg_{i}"] = True
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"del_pkg_{i}", type="secondary"):
                    dm.remove_packaging(i)
                    st.success("Packaging record deleted")
                    st.rerun()

    # ---------------- Edit Packaging Record ----------------
    for i, pkg in enumerate(packaging_list):
        if st.session_state.get(f"edit_pkg_{i}", False):
            with st.form(f"edit_pkg_form_{i}"):
                st.subheader(f"Edit Packaging Record ({pkg['box_type']})")

                # 6.1 Per‐Part
                st.markdown("**6.1 ‒ Per Part (per piece)**")
                col1, col2 = st.columns(2)
                with col1:
                    new_pack_maint = st.number_input(
                        "Packaging maintenance (€ per pcs)",
                        value=pkg["pack_maint"], min_value=0.0, step=0.001, format="%.3f"
                    )
                with col2:
                    new_empties_scrap = st.number_input(
                        "Empties scrapping (€ per pcs)",
                        value=pkg["empties_scrap"], min_value=0.0, step=0.001, format="%.3f"
                    )

                st.markdown("---")
                # 6.2 Standard Packaging
                st.markdown("**6.2 ‒ Standard Packaging (Plant)**")
                col1, col2 = st.columns(2)
                with col1:
                    new_box_type = st.selectbox(
                        "Packaging Type (box)",
                        ["Cardboard", "Plastic", "Wooden", "Metal"],
                        index=["Cardboard", "Plastic", "Wooden", "Metal"].index(pkg["box_type"])
                    )
                    new_fill_qty_box = st.number_input(
                        "Filling Quantity (pcs/box)",
                        value=pkg["fill_qty_box"], min_value=0, step=1
                    )
                with col2:
                    new_pallet_type = st.selectbox(
                        "LU Type (pallet)",
                        ["EUR‐pallet", "Industrial", "Custom"],
                        index=["EUR‐pallet", "Industrial", "Custom"].index(pkg["pallet_type"])
                    )
                    new_fill_qty_lu = st.number_input(
                        "Filling Qty (pcs/LU) overseas",
                        value=pkg["fill_qty_lu"], min_value=0, step=1
                    )
                new_add_pack_price = st.number_input(
                    "Price additional packaging (inlays, etc.) €",
                    value=pkg["add_pack_price"], min_value=0.0, step=0.01, format="%.2f"
                )

                st.markdown("---")
                # 6.3 Special Packaging
                st.markdown("**6.3 ‒ Special Packaging (CoC)**")
                col1, col2 = st.columns(2)
                with col1:
                    new_sp_needed = st.selectbox(
                        "Special packaging needed?",
                        ["Yes", "No"],
                        index=["Yes", "No"].index(pkg["sp_needed"])
                    )
                    new_sp_type = st.selectbox(
                        "Special packaging type",
                        ["Tray", "Blister", "Box", "Pallet Cover", "Other"],
                        index=["Tray", "Blister", "Box", "Pallet Cover", "Other"].index(pkg["sp_type"])
                    )
                    new_fill_qty_tray = st.number_input(
                        "Filling Qty (pcs/tray)",
                        value=pkg["fill_qty_tray"], min_value=0, step=1
                    )
                    new_tooling_cost = st.number_input(
                        "Tooling cost (€)",
                        value=pkg["tooling_cost"], min_value=0.0, step=0.01, format="%.2f"
                    )
                with col2:
                    new_add_sp_pack = st.selectbox(
                        "Additional packaging needed (pallet, cover)?",
                        ["Yes", "No"],
                        index=["Yes", "No"].index(pkg["add_sp_pack"])
                    )
                    new_trays_per_sp_pal = st.number_input(
                        "No. of Trays per SP‐pallet",
                        value=pkg["trays_per_sp_pal"], min_value=0, step=1
                    )
                    new_sp_pallets_per_lu = st.number_input(
                        "No. of SP‐pallets per LU",
                        value=pkg["sp_pallets_per_lu"], min_value=0, step=1
                    )

                st.markdown("---")
                # 6.4 Total Packaging Loop
                st.markdown("**6.4 ‒ Total Packaging Loop (Quantity of LUs)**")
                cols = st.columns(4)
                new_loop_data = {}
                for idx, field in enumerate(loop_fields):
                    new_loop_data[field] = cols[idx % 4].number_input(
                        field.title(),
                        value=pkg["loop_data"][field],
                        min_value=0, step=1
                    )

                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update Packaging", type="primary"):
                        updated_pkg = {
                            "pack_maint": new_pack_maint,
                            "empties_scrap": new_empties_scrap,
                            "box_type": new_box_type,
                            "fill_qty_box": new_fill_qty_box,
                            "pallet_type": new_pallet_type,
                            "fill_qty_lu": new_fill_qty_lu,
                            "add_pack_price": new_add_pack_price,
                            "sp_needed": new_sp_needed,
                            "sp_type": new_sp_type,
                            "fill_qty_tray": new_fill_qty_tray,
                            "tooling_cost": new_tooling_cost,
                            "add_sp_pack": new_add_sp_pack,
                            "trays_per_sp_pal": new_trays_per_sp_pal,
                            "sp_pallets_per_lu": new_sp_pallets_per_lu,
                            "loop_data": new_loop_data
                        }
                        res = val.validate_packaging(updated_pkg)
                        if res["is_valid"]:
                            dm.update_packaging(i, updated_pkg)
                            st.success("Packaging record updated")
                            st.session_state[f"edit_pkg_{i}"] = False
                            st.rerun()
                        else:
                            for e in res["errors"]:
                                st.error(e)
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_pkg_{i}"] = False
                        st.rerun()

if __name__ == "__main__":
    main()
