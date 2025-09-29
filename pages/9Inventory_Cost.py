# pages/13_Inventory_Interest.py
import streamlit as st
from utils.validators import InterestValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Inventory Cost", page_icon="💰")

def main():
    st.title("Inventory Cost - TBC")
    st.markdown("Configure inventory cost")
    st.markdown("---")

    # Initialize DataManager & Validator
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    dm = st.session_state.data_manager
    val = InterestValidator()

    # ---------- Add New Interest Rate ----------
    # with st.form("interest_form"):
        # st.subheader("Add Inventory Interest Rate")

    #     rate = st.number_input(
    #         "Inventory Interest Rate (%) *",
    #         min_value=0.0,
    #         max_value=100.0,
    #         step=0.01,
    #         format="%.2f",
    #         help="Annual inventory interest percentage"
    #     )

    #     submitted = st.form_submit_button("Add Interest Rate", type="primary")
    #     if submitted:
    #         obj = {"rate": rate}
    #         res = val.validate_interest(obj)
    #         if res["is_valid"]:
    #             if dm.interest_exists():
    #                 st.error("Interest rate already defined. Edit the existing entry instead.")
    #             else:
    #                 dm.add_interest(obj)
    #                 st.success("Inventory interest rate added successfully!")
    #                 st.rerun()
    #         else:
    #             for e in res["errors"]:
    #                 st.error(e)

    # st.markdown("---")

    # # ---------- Display Existing Interest Rate ----------
    # st.subheader("Existing Interest Rates")
    # interest_list = dm.get_interest()
    # if not interest_list:
    #     st.info("No interest rates configured yet.")
    # for i, intr in enumerate(interest_list):
    #     with st.expander(f"Interest Rate: {intr['rate']:.2f}%"):
    #         col1, col2, col3 = st.columns([3, 1, 1])
    #         with col1:
    #             st.write(f"**Rate:** {intr['rate']:.2f}%")
    #         with col2:
    #             if st.button("Edit", key=f"btn_edit_int_{i}"):
    #                 st.session_state[f"edit_int_{i}"] = True
    #                 st.rerun()
    #         with col3:
    #             if st.button("Delete", key=f"del_int_{i}", type="secondary"):
    #                 dm.remove_interest(intr["rate"])
    #                 st.success("Interest rate deleted.")
    #                 st.rerun()

    # # ---------- Edit Interest Rate ----------
    # for i, intr in enumerate(interest_list):
    #     if st.session_state.get(f"edit_int_{i}", False):
    #         with st.form(f"edit_int_form_{i}"):
    #             st.subheader(f"Edit Interest Rate: {intr['rate']:.2f}%")
    #             new_rate = st.number_input(
    #                 "Inventory Interest Rate (%)",
    #                 value=intr["rate"],
    #                 min_value=0.0,
    #                 max_value=100.0,
    #                 step=0.01,
    #                 format="%.2f"
    #             )
    #             col1, col2 = st.columns(2)
    #             with col1:
    #                 if st.form_submit_button("Update Interest Rate", type="primary"):
    #                     upd = {"rate": new_rate}
    #                     res = val.validate_interest(upd)
    #                     if res["is_valid"]:
    #                         dm.update_interest(intr["rate"], upd)
    #                         st.success("Interest rate updated.")
    #                         st.session_state[f"edit_int_{i}"] = False
    #                         st.rerun()
    #                     else:
    #                         for e in res["errors"]:
    #                             st.error(e)
    #             with col2:
    #                 if st.form_submit_button("Cancel"):
    #                     st.session_state[f"edit_int_{i}"] = False
    #                     st.rerun()

if __name__ == "__main__":
    main()