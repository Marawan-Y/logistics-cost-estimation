# pages/7_Repacking_Cost.py
import streamlit as st
from utils.validators import RepackingValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Repacking Cost", page_icon="🔄")

def main():
    st.title("Repacking Cost")
    st.markdown("Configure repacking parameters")
    st.markdown("---")

    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    dm = st.session_state.data_manager
    val = RepackingValidator()

    # New parameter options
    weight_options = [
        "None",
        "light\n(up to 0,050kg)",
        "moderate\n(up to 0,150kg)",
        "heavy\n(from 0,150kg)"
    ]
    packaging_one_way_options = [
        "N/A",
        "one-way tray in cardboard/wooden box",
        "Bulk (poss. in bag) in cardboard/wooden box",
        "Einwegblister im Karton/Holzkiste"
    ]
    packaging_returnable_options = [
        "N/A",
        "returnable trays",
        "one-way tray in KLT",
        "KLT"
    ]

    # ---------------- Add New Repacking Record ----------------
    with st.form("rep_form"):
        st.subheader("Add New Repacking Record")
        # Use three columns to lay out three selectboxes
        col1, col2, col3 = st.columns(3)
        with col1:
            pcs_weight = st.selectbox(
                "Weight (pcs_weight)",
                weight_options,
                help="Select weight category"
            )
        with col2:
            packaging_one_way = st.selectbox(
                "Packaging one-way (supplier)",
                packaging_one_way_options,
                help="Select one-way packaging"
            )
        with col3:
            packaging_returnable = st.selectbox(
                "Packaging returnable (KB)",
                packaging_returnable_options,
                help="Select returnable packaging"
            )

        submitted = st.form_submit_button("Add Repacking Record", type="primary")
        if submitted:
            obj = {
                "pcs_weight": pcs_weight,
                "packaging_one_way": packaging_one_way,
                "packaging_returnable": packaging_returnable
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

    # Initialize edit flags if not present
    for i, _ in enumerate(rep_list):
        flag = f"edit_rep_{i}"
        if flag not in st.session_state:
            st.session_state[flag] = False

    for i, rp in enumerate(rep_list):
        # Header shows key fields
        header = f"{rp.get('pcs_weight', '')} | {rp.get('packaging_one_way', '')} | {rp.get('packaging_returnable', '')}"
        with st.expander(header):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**Weight (pcs_weight):** {rp.get('pcs_weight', '')}")
                st.write(f"**Packaging one-way (supplier):** {rp.get('packaging_one_way', '')}")
                st.write(f"**Packaging returnable (KB):** {rp.get('packaging_returnable', '')}")
            with col2:
                if st.button("Edit", key=f"edit_rep_btn_{i}"):
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
                st.subheader(f"Edit Repacking Record")
                # Three selectboxes, pre-select current values
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Determine index of current weight in options
                    try:
                        idx_w = weight_options.index(rp.get("pcs_weight", weight_options[0]))
                    except ValueError:
                        idx_w = 0
                    new_pcs_weight = st.selectbox(
                        "Weight (pcs_weight)",
                        weight_options,
                        index=idx_w
                    )
                with col2:
                    try:
                        idx_ow = packaging_one_way_options.index(rp.get("packaging_one_way", packaging_one_way_options[0]))
                    except ValueError:
                        idx_ow = 0
                    new_packaging_one_way = st.selectbox(
                        "Packaging one-way (supplier)",
                        packaging_one_way_options,
                        index=idx_ow
                    )
                with col3:
                    try:
                        idx_rt = packaging_returnable_options.index(rp.get("packaging_returnable", packaging_returnable_options[0]))
                    except ValueError:
                        idx_rt = 0
                    new_packaging_returnable = st.selectbox(
                        "Packaging returnable (KB)",
                        packaging_returnable_options,
                        index=idx_rt
                    )

                col1b, col2b = st.columns(2)
                with col1b:
                    if st.form_submit_button("Update Repacking", type="primary"):
                        updated_rp = {
                            "pcs_weight": new_pcs_weight,
                            "packaging_one_way": new_packaging_one_way,
                            "packaging_returnable": new_packaging_returnable
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
                with col2b:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_rep_{i}"] = False
                        st.rerun()

if __name__ == "__main__":
    main()
