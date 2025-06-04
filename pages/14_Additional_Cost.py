# pages/14_Additional_Cost.py
import streamlit as st
from utils.validators import AdditionalCostValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Additional Cost", page_icon="➕")

def main():
    st.title("Additional Cost")
    st.markdown("Configure any additional cost items")
    st.markdown("---")

    # Initialize DataManager & Validator
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    dm = st.session_state.data_manager
    val = AdditionalCostValidator()

    # ---------- Add New Additional Cost ----------
    with st.form("additional_form"):
        st.subheader("Add New Cost Item")

        col1, col2 = st.columns(2)
        with col1:
            cost_name = st.text_input(
                "Cost Name *",
                help="Descriptive name for the additional cost item"
            )
        with col2:
            cost_value = st.number_input(
                "Cost Value (€) *",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Monetary value of this cost item"
            )

        submitted = st.form_submit_button("Add Cost Item", type="primary")
        if submitted:
            obj = {"cost_name": cost_name, "cost_value": cost_value}
            res = val.validate_additional_cost(obj)
            if res["is_valid"]:
                if dm.additional_cost_exists(cost_name):
                    st.error(f"An additional cost named '{cost_name}' already exists.")
                else:
                    dm.add_additional_cost(obj)
                    st.success("Additional cost added successfully!")
                    st.rerun()
            else:
                for e in res["errors"]:
                    st.error(e)

    st.markdown("---")

    # ---------- Display Existing Additional Costs ----------
    st.subheader("Existing Additional Costs")
    costs_list = dm.get_additional_costs()
    if not costs_list:
        st.info("No additional costs configured yet.")
    for i, cost in enumerate(costs_list):
        with st.expander(f"{cost['cost_name']}"):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**Value:** €{cost['cost_value']:.2f}")
            with col2:
                if st.button("Edit", key=f"edit_addc_{i}"):
                    st.session_state[f"edit_addc_{i}"] = True
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"del_addc_{i}", type="secondary"):
                    dm.remove_additional_cost(cost["cost_name"])
                    st.success("Additional cost deleted.")
                    st.rerun()

    # ---------- Edit Additional Cost ----------
    for i, cost in enumerate(costs_list):
        if st.session_state.get(f"edit_addc_{i}", False):
            with st.form(f"edit_addc_form_{i}"):
                st.subheader(f"Edit Cost Item: {cost['cost_name']}")
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input(
                        "Cost Name",
                        value=cost["cost_name"]
                    )
                with col2:
                    new_value = st.number_input(
                        "Cost Value (€)",
                        value=cost["cost_value"],
                        min_value=0.0,
                        step=0.01,
                        format="%.2f"
                    )
                col1b, col2b = st.columns(2)
                with col1b:
                    if st.form_submit_button("Update Cost Item", type="primary"):
                        upd = {"cost_name": new_name, "cost_value": new_value}
                        res = val.validate_additional_cost(upd)
                        if res["is_valid"]:
                            dm.update_additional_cost(cost["cost_name"], upd)
                            st.success("Additional cost updated.")
                            st.session_state[f"edit_addc_{i}"] = False
                            st.rerun()
                        else:
                            for e in res["errors"]:
                                st.error(e)
                with col2b:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_addc_{i}"] = False
                        st.rerun()

if __name__ == "__main__":
    main()
