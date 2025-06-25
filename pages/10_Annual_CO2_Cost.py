import streamlit as st
from utils.validators import CO2Validator
from utils.data_manager import DataManager

st.set_page_config(page_title="Annual CO2 Cost", page_icon="🌿")

def main():
    st.title("Annual CO₂ Cost")
    st.markdown("Configure annual CO₂ cost parameter")
    st.markdown("---")

    # Initialize DataManager & Validator
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    dm = st.session_state.data_manager
    val = CO2Validator()

    # ---------- Add New CO2 Cost ----------
    with st.form("co2_form"):
        st.subheader("Add New CO₂ Cost")

        cost_per_ton = st.number_input(
            "CO₂ Cost per Ton (€) *",
            min_value=0.0,
            step=0.10,
            format="%.2f",
            help="Cost of CO₂ emissions per metric ton"
        )

        co2_conversion_factor = st.selectbox(
            "CO₂ Conversion Factor",
            ["2.65", "3.17", "3.31"],
            help="CO₂ conversion factor based on Transportation mode & location. Sea = 3.31 , Road/Rail = 3.17 / 2.65"
        )

        submitted = st.form_submit_button("Add CO₂ Cost", type="primary")
        if submitted:
            obj = {"cost_per_ton": cost_per_ton, "co2_conversion_factor": co2_conversion_factor}
            res = val.validate_co2(obj)
            if res["is_valid"]:
                if dm.co2_exists():
                    st.error("CO₂ cost already defined. Edit the existing entry instead.")
                else:
                    dm.add_co2(obj)
                    st.success("CO₂ cost added successfully!")
                    st.rerun()
            else:
                for e in res["errors"]:
                    st.error(e)

    st.markdown("---")

    # ---------- Display Existing CO2 Cost ----------
    st.subheader("Existing CO₂ Cost")
    co2_list = dm.get_co2()
    if not co2_list:
        st.info("No CO₂ cost configured yet.")
    for i, co2 in enumerate(co2_list):
        with st.expander(f"CO₂ Cost: €{co2['cost_per_ton']:.2f}/ton, Factor: {co2['co2_conversion_factor']}"):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**Cost per Ton:** €{co2['cost_per_ton']:.2f}")
                st.write(f"**CO₂ Conversion Factor:** {co2['co2_conversion_factor']}")
            with col2:
                if st.button("Edit", key=f"edit_co2_{i}"):
                    st.session_state[f"edit_co2_{i}"] = True
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"del_co2_{i}", type="secondary"):
                    dm.remove_co2(co2["cost_per_ton"])
                    st.success("CO₂ cost deleted.")
                    st.rerun()

    # ---------- Edit CO2 Cost ----------
    for i, co2 in enumerate(co2_list):
        if st.session_state.get(f"edit_co2_{i}", False):
            with st.form(f"edit_co2_form_{i}"):
                st.subheader(f"Edit CO₂ Cost: €{co2['cost_per_ton']:.2f}/ton, Factor: {co2['co2_conversion_factor']}")
                new_cost = st.number_input(
                    "CO₂ Cost per Ton (€)",
                    value=co2["cost_per_ton"],
                    min_value=0.0,
                    step=0.10,
                    format="%.2f"
                )
                new_factor = st.selectbox(
                    "CO₂ Conversion Factor",
                    ["2.65", "3.17", "3.31"],
                    index=["2.65", "3.17", "3.31"].index(co2["co2_conversion_factor"])
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update CO₂ Cost", type="primary"):
                        upd = {"cost_per_ton": new_cost, "co2_conversion_factor": new_factor}
                        res = val.validate_co2(upd)
                        if res["is_valid"]:
                            dm.update_co2(co2["cost_per_ton"], upd)
                            st.success("CO₂ cost updated.")
                            st.session_state[f"edit_co2_{i}"] = False
                            st.rerun()
                        else:
                            for e in res["errors"]:
                                st.error(e)
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_co2_{i}"] = False
                        st.rerun()

if __name__ == "__main__":
    main()
