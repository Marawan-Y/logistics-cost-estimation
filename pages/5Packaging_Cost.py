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

    # Pre-define loop_fields for reuse
    loop_fields = [
        "goods receipt", "stock raw materials", "production",
        "empties return", "cleaning", "dispatch",
        "empties transit (KB → Supplier)", "empties receipt (at Supplier)",
        "empties in stock (Supplier)", "production (contrary loop)",
        "stock finished parts", "dispatch (finished parts)",
        "transit (Supplier → KB)"
    ]

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
                [
                    "None", "Cardboard S", "Cardboard M", "Cardboard L", "Cardboard XL",
                    "Cardboard LU (ISO)", "KLT3214 / LID", "KLT4314 / LID",
                    "KLT4328 / LID", "KLT6414 / LID", "KLT6417 / LID", "KLT6422 / LID",
                    "KLT6428 / LID", "R-KLT6429 / LID", "ESD KLT3115 / LID",
                    "ESD KLT4115 / LID", "ESD KLT4129 / LID", "ESD KLT 6115 / LID",
                    "ESD KLT 6122 / LID", "ESD KLT 6129 / LID", "Green Basket / LID",
                    "Magnum OPT", "Wooden Box", "Gitterbox (rental)", "Gitterbox", "EURO LU / LID"
                ],
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
                ["EURO Pallet Price", "ISO Pallet Price"],
                help="Select pallet type"
            )
            fill_qty_lu_oversea = st.number_input(
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
                ["Inlay Tray", "Inlay tray pallet size", "Standalone tray"],
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
                "fill_qty_lu_oversea": fill_qty_lu_oversea,
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

    # Callbacks to manage edit flags
    def enter_edit_pkg(idx):
        st.session_state[f"edit_pkg_flag_{idx}"] = True

    def exit_edit_pkg(idx):
        st.session_state[f"edit_pkg_flag_{idx}"] = False

    for i, pkg in enumerate(packaging_list):
        # Initialize flag if missing
        flag_key = f"edit_pkg_flag_{i}"
        if flag_key not in st.session_state:
            st.session_state[flag_key] = False

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
                st.button(
                    "Edit",
                    key=f"edit_pkg_btn_{i}",
                    on_click=enter_edit_pkg,
                    args=(i,)
                )
            with col3:
                if st.button("Delete", key=f"del_pkg_{i}", type="secondary"):
                    dm.remove_packaging(i)
                    st.success("Packaging record deleted")
                    st.rerun()

    # ---------------- Edit Packaging Record ----------------
    for i, pkg in enumerate(packaging_list):
        if st.session_state.get(f"edit_pkg_flag_{i}", False):
            with st.form(f"edit_pkg_form_{i}"):
                st.subheader(f"Edit Packaging Record ({pkg['box_type']})")

                # 6.1 Per‐Part
                st.markdown("**6.1 ‒ Per Part (per piece)**")
                col1, col2 = st.columns(2)
                with col1:
                    new_pack_maint = st.number_input(
                        "Packaging maintenance (€ per pcs)",
                        value=pkg["pack_maint"], min_value=0.0, step=0.001, format="%.3f",
                        key=f"new_pack_maint_{i}"
                    )
                with col2:
                    new_empties_scrap = st.number_input(
                        "Empties scrapping (€ per pcs)",
                        value=pkg["empties_scrap"], min_value=0.0, step=0.001, format="%.3f",
                        key=f"new_empties_scrap_{i}"
                    )

                st.markdown("---")
                # 6.2 Standard Packaging
                st.markdown("**6.2 ‒ Standard Packaging (Plant)**")
                col1, col2 = st.columns(2)
                with col1:
                    box_options = [
                        "None", "Cardboard S", "Cardboard M", "Cardboard L", "Cardboard XL",
                        "Cardboard LU (ISO)", "KLT3214 / LID", "KLT4314 / LID",
                        "KLT4328 / LID", "KLT6414 / LID", "KLT6417 / LID", "KLT6422 / LID",
                        "KLT6428 / LID", "R-KLT6429 / LID", "ESD KLT3115 / LID",
                        "ESD KLT4115 / LID", "ESD KLT4129 / LID", "ESD KLT 6115 / LID",
                        "ESD KLT 6122 / LID", "ESD KLT 6129 / LID", "Green Basket / LID",
                        "Magnum OPT", "Wooden Box", "Gitterbox (rental)", "Gitterbox", "EURO LU / LID"
                    ]
                    try:
                        default_idx = box_options.index(pkg["box_type"])
                    except ValueError:
                        default_idx = 0
                    new_box_type = st.selectbox(
                        "Packaging Type (box)",
                        box_options,
                        index=default_idx,
                        key=f"new_box_type_{i}"
                    )
                    new_fill_qty_box = st.number_input(
                        "Filling Quantity (pcs/box)",
                        value=pkg["fill_qty_box"], min_value=0, step=1,
                        key=f"new_fill_qty_box_{i}"
                    )
                with col2:
                    pallet_options = ["EURO Pallet Price", "ISO Pallet Price"]
                    try:
                        pal_idx = pallet_options.index(pkg["pallet_type"])
                    except ValueError:
                        pal_idx = 0
                    new_pallet_type = st.selectbox(
                        "LU Type (pallet)",
                        pallet_options,
                        index=pal_idx,
                        key=f"new_pallet_type_{i}"
                    )
                    new_fill_qty_lu_oversea = st.number_input(
                        "Filling Qty (pcs/LU) overseas",
                        value=pkg["fill_qty_lu_oversea"], min_value=0, step=1,
                        key=f"new_fill_qty_lu_oversea_{i}"
                    )
                new_add_pack_price = st.number_input(
                    "Price additional packaging (inlays, etc.) €",
                    value=pkg["add_pack_price"], min_value=0.0, step=0.01, format="%.2f",
                    key=f"new_add_pack_price_{i}"
                )

                st.markdown("---")
                # 6.3 Special Packaging
                st.markdown("**6.3 ‒ Special Packaging (CoC)**")
                col1, col2 = st.columns(2)
                with col1:
                    sp_needed_options = ["Yes", "No"]
                    try:
                        spn_idx = sp_needed_options.index(pkg["sp_needed"])
                    except ValueError:
                        spn_idx = 0
                    new_sp_needed = st.selectbox(
                        "Special packaging needed?",
                        sp_needed_options,
                        index=spn_idx,
                        key=f"new_sp_needed_{i}"
                    )
                    sp_type_options = ["Inlay Tray", "Inlay tray pallet size", "Standalone tray"]
                    try:
                        spt_idx = sp_type_options.index(pkg["sp_type"])
                    except ValueError:
                        spt_idx = 0
                    new_sp_type = st.selectbox(
                        "Special packaging type",
                        sp_type_options,
                        index=spt_idx,
                        key=f"new_sp_type_{i}"
                    )
                    new_fill_qty_tray = st.number_input(
                        "Filling Qty (pcs/tray)",
                        value=pkg["fill_qty_tray"], min_value=0, step=1,
                        key=f"new_fill_qty_tray_{i}"
                    )
                    new_tooling_cost = st.number_input(
                        "Tooling cost (€)",
                        value=pkg["tooling_cost"], min_value=0.0, step=0.01, format="%.2f",
                        key=f"new_tooling_cost_{i}"
                    )
                with col2:
                    add_sp_pack_options = ["Yes", "No"]
                    try:
                        asp_idx = add_sp_pack_options.index(pkg["add_sp_pack"])
                    except ValueError:
                        asp_idx = 0
                    new_add_sp_pack = st.selectbox(
                        "Additional packaging needed (pallet, cover)?",
                        add_sp_pack_options,
                        index=asp_idx,
                        key=f"new_add_sp_pack_{i}"
                    )
                    new_trays_per_sp_pal = st.number_input(
                        "No. of Trays per SP‐pallet",
                        value=pkg["trays_per_sp_pal"], min_value=0, step=1,
                        key=f"new_trays_per_sp_pal_{i}"
                    )
                    new_sp_pallets_per_lu = st.number_input(
                        "No. of SP‐pallets per LU",
                        value=pkg["sp_pallets_per_lu"], min_value=0, step=1,
                        key=f"new_sp_pallets_per_lu_{i}"
                    )

                st.markdown("---")
                # 6.4 Total Packaging Loop
                st.markdown("**6.4 ‒ Total Packaging Loop (Quantity of LUs)**")
                cols = st.columns(4)
                new_loop_data = {}
                for idx_field, field in enumerate(loop_fields):
                    new_loop_data[field] = cols[idx_field % 4].number_input(
                        field.title(),
                        value=pkg["loop_data"].get(field, 0),
                        min_value=0, step=1,
                        key=f"new_loop_{i}_{idx_field}"
                    )

                # Action buttons
                col_upd, col_cancel = st.columns(2)
                with col_upd:
                    if st.form_submit_button("Update Packaging", type="primary"):
                        updated_pkg = {
                            "pack_maint": new_pack_maint,
                            "empties_scrap": new_empties_scrap,
                            "box_type": new_box_type,
                            "fill_qty_box": new_fill_qty_box,
                            "pallet_type": new_pallet_type,
                            "fill_qty_lu_oversea": new_fill_qty_lu_oversea,
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
                            exit_edit_pkg(i)
                            st.rerun()
                        else:
                            for e in res["errors"]:
                                st.error(e)
                with col_cancel:
                    if st.form_submit_button("Cancel"):
                        exit_edit_pkg(i)
                        st.rerun()

if __name__ == "__main__":
    main()
