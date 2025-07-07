# pages/8_Customs_Cost.py
import streamlit as st
from utils.validators import CustomsValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Customs Cost", page_icon="🛃")

def main():
    st.title("Customs Cost")
    st.markdown("Configure customs-related cost parameters")
    st.markdown("---")

    # Initialize DataManager & Validator
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    dm = st.session_state.data_manager
    val = CustomsValidator()

    # ---------- Add New Customs Cost ----------
    with st.form("customs_form"):
        st.subheader("Add New Customs Cost")

        col1, col2 = st.columns(2)
        with col1:
            pref_usage = st.selectbox(
                "Customs Preference Usage (Y/N) *",
                ["Yes", "No"],
                help="Whether customs preference is used"
            )
            hs_code = st.text_input(
                "HS Code *",
                help="Harmonized System code for classification"
            )
        with col2:
            duty_rate = st.number_input(
                "Duty Rate (% of pcs price) *",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f",
                help="Duty rate as a percentage of piece price"
            )
            tariff_rate = st.number_input(
                "Tariff Rate (% of pcs price) *",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f",
                help="Tariff rate as a percentage of piece price"
            )

        submitted = st.form_submit_button("Add Customs Cost", type="primary")
        if submitted:
            obj = {
                "pref_usage": pref_usage,
                "hs_code": hs_code,
                "duty_rate": duty_rate,
                "tariff_rate": tariff_rate
            }
            res = val.validate_customs(obj)
            if res["is_valid"]:
                if dm.customs_exists(hs_code):
                    st.error(f"Customs entry for HS Code {hs_code} already exists.")
                else:
                    dm.add_customs(obj)
                    st.success("Customs cost added successfully!")
                    st.rerun()
            else:
                for e in res["errors"]:
                    st.error(e)

    st.markdown("---")

    # ---------- Display Existing Customs Costs ----------
    st.subheader("Existing Customs Costs")
    customs_list = dm.get_customs()
    if not customs_list:
        st.info("No customs costs configured yet.")
    for i, cust in enumerate(customs_list):
        with st.expander(f"{cust['hs_code']} (Preference: {cust['pref_usage']})"):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**Duty Rate:** {cust['duty_rate']:.2f}%")
                st.write(f"**Tariff Rate:** {cust['tariff_rate']:.2f}%")
            with col2:
                if st.button("Edit", key=f"btn_edit_cust_{i}"):
                    st.session_state[f"edit_cust_{i}"] = True
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"del_cust_{i}", type="secondary"):
                    dm.remove_customs(cust["hs_code"])
                    st.success("Customs cost deleted.")
                    st.rerun()

    # ---------- Edit Customs Cost ----------
    for i, cust in enumerate(customs_list):
        if st.session_state.get(f"edit_cust_{i}", False):
            with st.form(f"edit_cust_form_{i}"):
                st.subheader(f"Edit Customs Cost: {cust['hs_code']}")
                col1, col2 = st.columns(2)
                with col1:
                    new_pref_usage = st.selectbox(
                        "Customs Preference Usage (Y/N)",
                        ["Yes", "No"],
                        index=["Yes", "No"].index(cust["pref_usage"])
                    )
                    new_hs_code = st.text_input(
                        "HS Code",
                        value=cust["hs_code"]
                    )
                with col2:
                    new_duty_rate = st.number_input(
                        "Duty Rate (% of pcs price)",
                        value=cust["duty_rate"],
                        min_value=0.0,
                        max_value=100.0,
                        step=0.01,
                        format="%.2f"
                    )
                    new_tariff_rate = st.number_input(
                        "Tariff Rate (% of pcs price)",
                        value=cust["tariff_rate"],
                        min_value=0.0,
                        max_value=100.0,
                        step=0.01,
                        format="%.2f"
                    )

                col1b, col2b = st.columns(2)
                with col1b:
                    if st.form_submit_button("Update Customs Cost", type="primary"):
                        upd = {
                            "pref_usage": new_pref_usage,
                            "hs_code": new_hs_code,
                            "duty_rate": new_duty_rate,
                            "tariff_rate": new_tariff_rate
                        }
                        res = val.validate_customs(upd)
                        if res["is_valid"]:
                            dm.update_customs(cust["hs_code"], upd)
                            st.success("Customs cost updated.")
                            st.session_state[f"edit_cust_{i}"] = False
                            st.rerun()
                        else:
                            for e in res["errors"]:
                                st.error(e)
                with col2b:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_cust_{i}"] = False
                        st.rerun()

if __name__ == "__main__":
    main()