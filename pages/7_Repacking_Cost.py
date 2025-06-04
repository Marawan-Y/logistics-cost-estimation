# pages/7_Repacking_Cost.py
import streamlit as st
from utils.validators import RepackingValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Repacking Cost", page_icon="🔄")

def main():
    st.title("Repacking Cost")
    st.markdown("Configure repacking cost parameters")
    st.markdown("---")

    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    dm = st.session_state.data_manager
    val = RepackingValidator()

    # ---------------- Add New Repacking Record ----------------
    with st.form("rep_form"):
        st.subheader("Add New Repacking Record")
        col1, col2 = st.columns(2)
        with col1:
            rep_cost_hr = st.number_input(
                "Repacking cost (€ per hour)",
                min_value=0.0, step=0.01, format="%.2f",
                help="Hourly labor cost for repacking"
            )
            goods_type = st.selectbox(
                "Type of goods",
                ["Bulk", "Fragile", "Hazardous", "Other"],
                help="Select the category of goods being repacked"
            )
        with col2:
            rep_cost_lu = st.number_input(
                "Repacking cost (€ per LU)",
                min_value=0.0, step=0.01, format="%.2f",
                help="Cost to repack one load unit"
            )

        submitted = st.form_submit_button("Add Repacking Cost", type="primary")
        if submitted:
            obj = {
                "rep_cost_hr": rep_cost_hr,
                "goods_type": goods_type,
                "rep_cost_lu": rep_cost_lu
            }
            res = val.validate_repacking(obj)
            if res["is_valid"]:
                dm.add_repacking(obj)
                st.success("Repacking record added successfully!")
                st.rerun()
            else:
                for e in res["errors"]:
                    st.error(e)

    st.markdown("---")

    # ---------------- Display Existing Repacking Records ----------------
    st.subheader("Existing Repacking Records")
    rep_list = dm.get_repacking()
    if not rep_list:
        st.info("No repacking records configured yet.")
    for i, rp in enumerate(rep_list):
        header = f"{rp['goods_type']} | €{rp['rep_cost_lu']:.2f} per LU"
        with st.expander(header):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**Repacking cost / hr:** €{rp['rep_cost_hr']:.2f}")
                st.write(f"**Type of goods:** {rp['goods_type']}")
                st.write(f"**Repacking cost per LU:** €{rp['rep_cost_lu']:.2f}")
            with col2:
                if st.button("Edit", key=f"edit_rep_{i}"):
                    st.session_state[f"edit_rep_{i}"] = True
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"del_rep_{i}", type="secondary"):
                    dm.remove_repacking(i)
                    st.success("Repacking record deleted")
                    st.rerun()

    # ---------------- Edit Repacking Record ----------------
    for i, rp in enumerate(rep_list):
        if st.session_state.get(f"edit_rep_{i}", False):
            with st.form(f"edit_rep_form_{i}"):
                st.subheader(f"Edit Repacking Record ({rp['goods_type']})")
                col1, col2 = st.columns(2)
                with col1:
                    new_rep_cost_hr = st.number_input(
                        "Repacking cost (€ per hour)",
                        value=rp["rep_cost_hr"], min_value=0.0, step=0.01, format="%.2f"
                    )
                    new_goods_type = st.selectbox(
                        "Type of goods",
                        ["Bulk", "Fragile", "Hazardous", "Other"],
                        index=["Bulk", "Fragile", "Hazardous", "Other"].index(rp["goods_type"])
                    )
                with col2:
                    new_rep_cost_lu = st.number_input(
                        "Repacking cost (€ per LU)",
                        value=rp["rep_cost_lu"], min_value=0.0, step=0.01, format="%.2f"
                    )

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update Repacking", type="primary"):
                        updated_rp = {
                            "rep_cost_hr": new_rep_cost_hr,
                            "goods_type": new_goods_type,
                            "rep_cost_lu": new_rep_cost_lu
                        }
                        res = val.validate_repacking(updated_rp)
                        if res["is_valid"]:
                            dm.update_repacking(i, updated_rp)
                            st.success("Repacking record updated")
                            st.session_state[f"edit_rep_{i}"] = False
                            st.rerun()
                        else:
                            for e in res["errors"]:
                                st.error(e)
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_rep_{i}"] = False
                        st.rerun()

if __name__ == "__main__":
    main()
