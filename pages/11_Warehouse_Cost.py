# pages/11_Warehouse_Cost.py
import streamlit as st
from utils.validators import WarehouseValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Warehouse Cost", page_icon="🏬")

def main():
    st.title("Warehouse Cost")
    st.markdown("Configure warehouse-related cost parameters")
    st.markdown("---")

    # Initialize DataManager & Validator
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    dm = st.session_state.data_manager
    val = WarehouseValidator()

    # ---------- Add New Warehouse Cost ----------
    with st.form("warehouse_form"):
        st.subheader("Add New Warehouse Cost")

        cost_per_loc = st.number_input(
            "Cost per Storage Location (monthly) (€) *",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            help="Monthly cost for one storage location"
        )

        submitted = st.form_submit_button("Add Warehouse Cost", type="primary")
        if submitted:
            obj = {"cost_per_loc": cost_per_loc}
            res = val.validate_warehouse(obj)
            if res["is_valid"]:
                if dm.warehouse_exists():
                    st.error("Warehouse cost already defined. Edit the existing entry instead.")
                else:
                    dm.add_warehouse(obj)
                    st.success("Warehouse cost added successfully!")
                    st.rerun()
            else:
                for e in res["errors"]:
                    st.error(e)

    st.markdown("---")

    # ---------- Display Existing Warehouse Cost ----------
    st.subheader("Existing Warehouse Cost")
    wh_list = dm.get_warehouse()
    if not wh_list:
        st.info("No warehouse cost configured yet.")
    for i, wh in enumerate(wh_list):
        with st.expander(f"Cost per Location: €{wh['cost_per_loc']:.2f}/month"):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**Cost per Location:** €{wh['cost_per_loc']:.2f}")
            with col2:
                if st.button("Edit", key=f"edit_wh_{i}"):
                    st.session_state[f"edit_wh_{i}"] = True
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"del_wh_{i}", type="secondary"):
                    dm.remove_warehouse(wh["cost_per_loc"])
                    st.success("Warehouse cost deleted.")
                    st.rerun()

    # ---------- Edit Warehouse Cost ----------
    for i, wh in enumerate(wh_list):
        if st.session_state.get(f"edit_wh_{i}", False):
            with st.form(f"edit_wh_form_{i}"):
                st.subheader(f"Edit Warehouse Cost: €{wh['cost_per_loc']:.2f}/month")
                new_cost = st.number_input(
                    "Cost per Storage Location (monthly) (€)",
                    value=wh["cost_per_loc"],
                    min_value=0.0,
                    step=0.01,
                    format="%.2f"
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update Warehouse Cost", type="primary"):
                        upd = {"cost_per_loc": new_cost}
                        res = val.validate_warehouse(upd)
                        if res["is_valid"]:
                            dm.update_warehouse(wh["cost_per_loc"], upd)
                            st.success("Warehouse cost updated.")
                            st.session_state[f"edit_wh_{i}"] = False
                            st.rerun()
                        else:
                            for e in res["errors"]:
                                st.error(e)
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_wh_{i}"] = False
                        st.rerun()

if __name__ == "__main__":
    main()
