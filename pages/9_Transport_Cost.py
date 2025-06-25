# pages/9_Transport_Cost.py
import streamlit as st
from utils.validators import TransportValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Transport Cost", page_icon="🚚")

def main():
    st.title("Transport Cost")
    st.markdown("Configure transport-related cost parameters")
    st.markdown("---")

    # Initialize DataManager & Validator
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    dm = st.session_state.data_manager
    val = TransportValidator()

    transport_modes = ["Road", "Rail", "Sea"]
    stack_factors = ["1", "1.2", "1.25", "1.333333333", "1.166666667", "1.5", "2"]

    # ---------- Add New Transport Cost ----------
    with st.form("transport_form"):
        st.subheader("Add New Transport Cost")

        col1, col2 = st.columns(2)
        with col1:
            mode1 = st.selectbox(
                "Transportation Mode I *",
                transport_modes,
                help="Primary mode of transport"
            )
            mode2 = st.selectbox(
                "Transportation Mode II *",
                ["None"] + transport_modes,
                help="Secondary mode of transport (if any)"
            )
            cost_lu = st.number_input(
                "Transportation Cost per LU (€) *",
                min_value=0.0,
                step=0.01,
                format="%.2f"
            )
        with col2:
            cost_bonded = st.number_input(
                "Transportation Cost (Bonded Warehouse) per LU (€) *",
                min_value=0.0,
                step=0.01,
                format="%.2f"
            )
            stack_factor = st.selectbox(
                "Stackability Factor *",
                stack_factors,
                help="Factor by which items can be stacked"
            )

        submitted = st.form_submit_button("Add Transport Cost", type="primary")
        if submitted:
            obj = {
                "mode1": mode1,
                "mode2": mode2,
                "cost_lu": cost_lu,
                "cost_bonded": cost_bonded,
                "stack_factor": stack_factor
            }
            res = val.validate_transport(obj)
            if res["is_valid"]:
                key = f"{mode1}-{mode2}"
                if dm.transport_exists(key):
                    st.error(f"Transport entry for {mode1}/{mode2} already exists.")
                else:
                    obj["key"] = key  # create a unique key
                    dm.add_transport(obj)
                    st.success("Transport cost added successfully!")
                    st.rerun()
            else:
                for e in res["errors"]:
                    st.error(e)

    st.markdown("---")

    # ---------- Display Existing Transport Costs ----------
    st.subheader("Existing Transport Costs")
    transport_list = dm.get_transport()
    if not transport_list:
        st.info("No transport costs configured yet.")

    # Initialize edit flags if not present
    for i, _ in enumerate(transport_list):
        flag = f"is_editing_tr_{i}"
        if flag not in st.session_state:
            st.session_state[flag] = False

    for i, tr in enumerate(transport_list):
        with st.expander(f"{tr['mode1']} / {tr['mode2']}"):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**Cost per LU:** €{tr['cost_lu']:.2f}")
                st.write(f"**Cost (Bonded) per LU:** €{tr['cost_bonded']:.2f}")
                st.write(f"**Stackability Factor:** {tr['stack_factor']}")
            with col2:
                if st.button("Edit", key=f"edit_btn_{i}"):
                    st.session_state[f"is_editing_tr_{i}"] = True
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"del_btn_{i}", type="secondary"):
                    dm.remove_transport(tr["key"])
                    st.success("Transport cost deleted.")
                    st.rerun()

    # ---------- Edit Transport Cost ----------
    for i, tr in enumerate(transport_list):
        if st.session_state.get(f"is_editing_tr_{i}", False):
            # Show edit form
            with st.form(f"edit_tr_form_{i}"):
                st.subheader(f"Edit Transport Cost: {tr['mode1']} / {tr['mode2']}")
                col1, col2 = st.columns(2)
                with col1:
                    new_mode1 = st.selectbox(
                        "Transportation Mode I",
                        transport_modes,
                        index=transport_modes.index(tr["mode1"])
                    )
                    new_mode2 = st.selectbox(
                        "Transportation Mode II",
                        ["None"] + transport_modes,
                        index=(["None"] + transport_modes).index(tr["mode2"])
                    )
                    new_cost_lu = st.number_input(
                        "Transportation Cost per LU (€)",
                        value=tr["cost_lu"],
                        min_value=0.0,
                        step=0.01,
                        format="%.2f"
                    )
                with col2:
                    new_cost_bonded = st.number_input(
                        "Transportation Cost (Bonded) per LU (€)",
                        value=tr["cost_bonded"],
                        min_value=0.0,
                        step=0.01,
                        format="%.2f"
                    )
                    # Use same stack_factors list as in Add
                    # Pre-select index based on current value
                    sf_index = 0
                    if tr.get("stack_factor") in stack_factors:
                        sf_index = stack_factors.index(tr["stack_factor"])
                    new_stack_factor = st.selectbox(
                        "Stackability Factor",
                        stack_factors,
                        index=sf_index
                    )

                col1b, col2b = st.columns(2)
                with col1b:
                    if st.form_submit_button("Update Transport Cost", type="primary"):
                        new_key = f"{new_mode1}-{new_mode2}"
                        upd = {
                            "mode1": new_mode1,
                            "mode2": new_mode2,
                            "cost_lu": new_cost_lu,
                            "cost_bonded": new_cost_bonded,
                            "stack_factor": new_stack_factor,
                            "key": new_key
                        }
                        res = val.validate_transport(upd)
                        if res["is_valid"]:
                            dm.update_transport(tr["key"], upd)
                            st.success("Transport cost updated.")
                            st.session_state[f"is_editing_tr_{i}"] = False
                            st.rerun()
                        else:
                            for e in res["errors"]:
                                st.error(e)
                with col2b:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"is_editing_tr_{i}"] = False
                        st.rerun()

if __name__ == "__main__":
    main()
