import streamlit as st
from utils.validators import TransportValidator
from utils.data_manager import DataManager
import uuid

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
            cost_lu = st.number_input(
                "Transportation Cost per LU (€) *",
                min_value=0.0,
                step=0.01,
                format="%.2f"
            )
        with col2:
            stack_factor = st.selectbox(
                "Stackability Factor *",
                stack_factors,
                help="Factor by which items can be stacked"
            )

        submitted = st.form_submit_button("Add Transport Cost", type="primary")
        if submitted:
            obj = {
                "mode1": mode1,
                "cost_lu": cost_lu,
                "stack_factor": stack_factor,
                # assign a unique key for each entry
                "key": str(uuid.uuid4())
            }
            res = val.validate_transport(obj)
            if res["is_valid"]:
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
    for i in range(len(transport_list)):
        flag = f"is_editing_tr_{i}"
        if flag not in st.session_state:
            st.session_state[flag] = False

    for i, tr in enumerate(transport_list):
        with st.expander(f"{tr['mode1']}"):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**Cost per LU:** €{tr['cost_lu']:.2f}")
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
            with st.form(f"edit_tr_form_{i}"):
                st.subheader(f"Edit Transport Cost: {tr['mode1']}")
                col1, col2 = st.columns(2)
                with col1:
                    new_mode1 = st.selectbox(
                        "Transportation Mode I",
                        transport_modes,
                        index=transport_modes.index(tr["mode1"])
                    )
                    new_cost_lu = st.number_input(
                        "Transportation Cost per LU (€)",
                        value=tr["cost_lu"],
                        min_value=0.0,
                        step=0.01,
                        format="%.2f"
                    )
                with col2:
                    sf_index = stack_factors.index(tr.get("stack_factor", stack_factors[0]))
                    new_stack_factor = st.selectbox(
                        "Stackability Factor",
                        stack_factors,
                        index=sf_index
                    )

                col1b, col2b = st.columns(2)
                with col1b:
                    if st.form_submit_button("Update Transport Cost", type="primary"):
                        new_key = tr["key"]  # preserve unique key
                        upd = {
                            "mode1": new_mode1,
                            "cost_lu": new_cost_lu,
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
