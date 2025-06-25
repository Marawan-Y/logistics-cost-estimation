# pages/4_Operations_Information.py
import streamlit as st
from utils.validators import OperationsValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="Operations Information", page_icon="⚙️")

def main():
    st.title("Operations Information")
    st.markdown("Configure operational parameters relevant to logistics")
    st.markdown("---")

    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    data_manager = st.session_state.data_manager
    validator = OperationsValidator()

    incoterm_options = ["EXW", "FCA", "FAS", "FOB", "CFR", "CIF", "CPT", "CIP", "DAP", "DPU", "DDP"]  # sample list
    classification_options = ["A-Part", "B-Part", "C-Part"]
    calloff_options = ["Supply Web", "EDI", "Mail", "other"]
    yes_no = ["Yes", "No"]
    ownership_options = ["Supplier", "KB", "Customer"]
    responsible_opts = ["Supplier", "CoC"]
    currency_opts = ["EUR", "USD", "RMB", "YEN", "GBP"]

    # ---------- Add ----------
    with st.form("operations_form"):
        st.subheader("Add New Operations Record")
        col1, col2 = st.columns(2)

        with col1:
            incoterm_code = st.selectbox("Incoterm Code *", incoterm_options)
            incoterm_place = st.text_input("Incoterm Named Place *")
            part_class = st.selectbox("Part Classification *", classification_options)
            calloff_type = st.selectbox("Call-off Transfer Type *", calloff_options)
            directive = st.selectbox(
                "Latest Version (Y031010) of Logistics Directive *", yes_no
            )
            lead_time = st.number_input("Lead Time (days) *", min_value=0, step=1)
        with col2:
            subsupplier_used = st.selectbox(
                "Sub-supplier used *", yes_no
            )
            subsupplier_box_days = st.number_input(
                "Sub-supplier need for boxes (days)", min_value=0, step=1
            )
            packaging_tool_owner = st.selectbox(
                "Packaging Tool Ownership *", ownership_options
            )
            responsible = st.selectbox("Responsible *", responsible_opts)
            currency = st.selectbox("Currency *", currency_opts)

        submitted = st.form_submit_button("Add Operations", type="primary")
        if submitted:
            ops = {
                "incoterm_code": incoterm_code,
                "incoterm_place": incoterm_place,
                "part_class": part_class,
                "calloff_type": calloff_type,
                "directive": directive,
                "lead_time": lead_time,
                "subsupplier_used": subsupplier_used,
                "subsupplier_box_days": subsupplier_box_days,
                "packaging_tool_owner": packaging_tool_owner,
                "responsible": responsible,
                "currency": currency,
            }
            res = validator.validate_operations(ops)
            if res["is_valid"]:
                data_manager.add_operations(ops)
                st.success("Operations record added")
                st.rerun()
            else:
                for e in res["errors"]:
                    st.error(e)

    st.markdown("---")

    # ---------- Existing ----------
    st.subheader("Existing Operations Records")
    ops_records = data_manager.get_operations()
    if not ops_records:
        st.info("No operations records yet.")
    for i, rec in enumerate(ops_records):
        with st.expander(
            f"{rec['incoterm_code']} @ {rec['incoterm_place']} ({rec['currency']})"
        ):
            col1, col2, col3 = st.columns([3,1,1])
            with col1:
                st.write(f"**Part Classification:** {rec['part_class']}")
                st.write(f"**Call-off Type:** {rec['calloff_type']}")
                st.write(f"**Directive:** {rec['directive']}")
                st.write(f"**Lead Time:** {rec['lead_time']} d")
                st.write(f"**Sub-supplier used:** {rec['subsupplier_used']}")
                st.write(
                    f"**Sub-supplier box days:** {rec['subsupplier_box_days']} d"
                )
                st.write(f"**Packaging Tool Owner:** {rec['packaging_tool_owner']}")
                st.write(f"**Responsible:** {rec['responsible']}")
            with col2:
                if st.button("Edit", key=f"edit_ops_{i}"):
                    st.session_state[f"edit_ops_{i}"] = True
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"del_ops_{i}", type="secondary"):
                    data_manager.remove_operations(i)
                    st.success("Record deleted")
                    st.rerun()

    # ---------- Edit ----------
    for i, rec in enumerate(ops_records):
        if st.session_state.get(f"edit_ops_{i}", False):
            with st.form(f"edit_ops_form_{i}"):
                st.subheader("Edit Operations Record")
                col1, col2 = st.columns(2)
                with col1:
                    new_incoterm_code = st.selectbox(
                        "Incoterm Code", incoterm_options, index=incoterm_options.index(rec["incoterm_code"])
                    )
                    new_incoterm_place = st.text_input(
                        "Incoterm Named Place", value=rec["incoterm_place"]
                    )
                    new_part_class = st.selectbox(
                        "Part Classification", classification_options,
                        index=classification_options.index(rec["part_class"])
                    )
                    new_calloff_type = st.selectbox(
                        "Call-off Transfer Type", calloff_options,
                        index=calloff_options.index(rec["calloff_type"])
                    )
                    new_directive = st.selectbox(
                        "Directive", directive_options,
                        index=directive_options.index(rec["directive"])
                    )
                    new_lead_time = st.number_input(
                        "Lead Time (days)",
                        value=rec["lead_time"], min_value=0, step=1
                    )
                with col2:
                    new_subsupplier_used = st.selectbox(
                        "Sub-supplier used", yes_no,
                        index=yes_no.index(rec["subsupplier_used"])
                    )
                    new_subsupplier_box_days = st.number_input(
                        "Sub-supplier need for boxes (days)",
                        value=rec["subsupplier_box_days"], min_value=0, step=1
                    )
                    new_packaging_tool_owner = st.selectbox(
                        "Packaging Tool Ownership", ownership_options,
                        index=ownership_options.index(rec["packaging_tool_owner"])
                    )
                    new_responsible = st.selectbox(
                        "Responsible", responsible_opts,
                        index=responsible_opts.index(rec["responsible"])
                    )
                    new_currency = st.selectbox(
                        "Currency", currency_opts,
                        index=currency_opts.index(rec["currency"])
                    )

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update", type="primary"):
                        upd = {
                            "incoterm_code": new_incoterm_code,
                            "incoterm_place": new_incoterm_place,
                            "part_class": new_part_class,
                            "calloff_type": new_calloff_type,
                            "directive": new_directive,
                            "lead_time": new_lead_time,
                            "subsupplier_used": new_subsupplier_used,
                            "subsupplier_box_days": new_subsupplier_box_days,
                            "packaging_tool_owner": new_packaging_tool_owner,
                            "responsible": new_responsible,
                            "currency": new_currency,
                        }
                        res = validator.validate_operations(upd)
                        if res["is_valid"]:
                            data_manager.update_operations(i, upd)
                            st.success("Record updated")
                            st.session_state[f"edit_ops_{i}"] = False
                            st.rerun()
                        else:
                            for e in res["errors"]:
                                st.error(e)
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_ops_{i}"] = False
                        st.rerun()

if __name__ == "__main__":
    main()
