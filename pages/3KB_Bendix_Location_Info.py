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

    # Preference selector outside form for instant effect
    pref_usage = st.selectbox(
        "Customs Preference Usage (Y/N) *",
        ["Yes", "No"],
        help="Whether customs preference is used",
        key="cust_pref_usage"
    )

    # ---------- Add New Customs Cost ----------
    with st.form("customs_form"):
        st.subheader("Add New Customs Cost")
        col1, _ = st.columns(2)
        with col1:
            if pref_usage == "No":
                duty_rate = st.number_input(
                    "Duty Rate (% of pcs price) *",
                    min_value=0.0, max_value=100.0,
                    step=0.01, format="%.2f",
                    help="Duty rate as a percentage of piece price",
                    key="new_duty_rate_input"
                )
            else:
                duty_rate = 0.0
                st.write("Duty rate not required when preference is Yes.")

        submitted = st.form_submit_button("Add Customs Cost", type="primary")
        if submitted:
            obj = {
                "pref_usage": pref_usage,
                "duty_rate": duty_rate
            }
            res = val.validate_customs(obj)
            if res["is_valid"]:
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

    # Callbacks to manage edit flags
    def enter_edit(idx):
        st.session_state[f"edit_cust_{idx}"] = True

    def exit_edit(idx):
        st.session_state[f"edit_cust_{idx}"] = False

    # Display entries
    for i, cust in enumerate(customs_list):
        flag_key = f"edit_cust_{i}"
        if flag_key not in st.session_state:
            st.session_state[flag_key] = False

        with st.expander(f"Preference: {cust['pref_usage']}"):
            st.write(f"**Duty Rate:** {cust['duty_rate']:.2f}%")
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("Edit", key=f"edit_btn_{i}", on_click=enter_edit, args=(i,)):
                    pass
            with col2:
                if st.button("Delete", key=f"del_btn_{i}", type="secondary"):
                    dm.remove_customs(i)
                    st.success("Customs cost deleted.")
                    st.rerun()

    # ---------- Edit Customs Cost ----------
    for i, cust in enumerate(customs_list):
        if st.session_state.get(f"edit_cust_{i}", False):
            with st.form(f"edit_cust_form_{i}"):
                st.subheader(f"Edit Customs Cost: Preference {cust['pref_usage']}")
                st.write(f"**Customs Preference Usage:** {cust['pref_usage']}")
                if cust['pref_usage'] == "No":
                    new_duty_rate = st.number_input(
                        "Duty Rate (% of pcs price) *",
                        value=cust['duty_rate'],
                        min_value=0.0, max_value=100.0,
                        step=0.01, format="%.2f",
                        key=f"edit_duty_rate_{i}"
                    )
                else:
                    new_duty_rate = 0.0
                    st.write("Duty rate not editable when preference is Yes.")

                col_upd, col_cancel = st.columns(2)
                with col_upd:
                    if st.form_submit_button("Update Customs Cost", type="primary"):
                        upd = {
                            "pref_usage": cust['pref_usage'],
                            "duty_rate": new_duty_rate
                        }
                        res = val.validate_customs(upd)
                        if res["is_valid"]:
                            dm.update_customs(i, upd)
                            st.success("Customs cost updated.")
                            exit_edit(i)
                            st.rerun()
                        else:
                            for e in res["errors"]:
                                st.error(e)
                with col_cancel:
                    if st.form_submit_button("Cancel"):
                        exit_edit(i)
                        st.rerun()

if __name__ == "__main__":
    main()
