# pages/15Repacking_Data_Management.py - FULL FEATURED (Updated)
# Excel/CSV/JSON import with preview, templates, category rename/clear, CRUD, stats, advanced search
import streamlit as st
import pandas as pd
from io import BytesIO
import json
from pathlib import Path
from utils.data_manager import DataManager
from utils.repacking_database import RepackingDatabase

st.set_page_config(page_title="Repacking Data Management", page_icon="🔁", layout="wide")

REPACK_JSON_PATH = "repacking_database.json"

DB_DIR = Path("DB")
REPACK_JSON_CACHE = Path("repacking_database.json")

# Display schema (what users see in the table/template)
DISPLAY_COLUMNS = [
    "Weight Category",
    "Supplier Packaging",
    "Operation Type",
    "KB Packaging",
    "Cost",
    "Unit",
]

REQUIRED_COLUMNS = [
    "Weight Category",
    "Supplier Packaging",
    "Operation Type",
    "KB Packaging",
]

# Flexible header mapping: input headers -> internal keys / display mapping
COLUMN_MAPPING = {
    # Display headers:
    "Weight Category": "weight_category",
    "Supplier Packaging": "supplier_packaging",
    "Operation Type": "operation_type",
    "KB Packaging": "kb_packaging",
    "Cost": "cost",
    "Unit": "unit",
    # Alternate headers (supported by utils for Excel/CSV):
    "pcs_weight": "weight_category",
    "packaging_one_way": "supplier_packaging",
    "packaging_returnable": "kb_packaging",
}

PREFERRED_DISPLAY_ORDER = DISPLAY_COLUMNS[:]  # for rendering

def _autoload_repacking_once():
    """
    Load Repacking from DB/JSON/repacking_database.json (preferred),
    else DB/Excel/repacking_database.xlsx, else legacy local cache.
    Run once per session.
    """
    if st.session_state.get("_repacking_autoloaded"):
        return

    rep_db: RepackingDatabase = st.session_state.repacking_db
    json_path  = DB_DIR / "JSON"  / "repacking_database.json"
    excel_path = DB_DIR / "Excel" / "repacking_database.xlsx"

    loaded_from = None
    try:
        if json_path.exists():
            rep_db.reset_to_defaults()
            rep_db.load_from_json(str(json_path))
            loaded_from = str(json_path)
        elif excel_path.exists():
            rep_db.reset_to_defaults()
            rep_db.load_from_excel(str(excel_path))
            loaded_from = str(excel_path)
        elif REPACK_JSON_CACHE.exists():
            rep_db.reset_to_defaults()
            rep_db.load_from_json(str(REPACK_JSON_CACHE))
            loaded_from = str(REPACK_JSON_CACHE)
    except Exception as e:
        st.warning(f"Repacking autoload warning: {e}")

    if loaded_from:
        st.info(f"📥 Repacking auto-loaded from: `{loaded_from}`")
    else:
        st.info("📥 Repacking: no file found in /DB (JSON/Excel). Starting defaults.")

    st.session_state["_repacking_autoloaded"] = True

def _load_local_cache(db: RepackingDatabase):
    try:
        db.load_from_json(REPACK_JSON_PATH)
    except Exception:
        pass

def _df_order(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in PREFERRED_DISPLAY_ORDER if c in df.columns]
    rest = [c for c in df.columns if c not in cols]
    return df[cols + rest] if cols else df

def _make_template_df() -> pd.DataFrame:
    return pd.DataFrame(columns=DISPLAY_COLUMNS)

def _validate_schema(df: pd.DataFrame) -> dict:
    present = set(df.columns)
    missing = [c for c in REQUIRED_COLUMNS if c not in present]
    unknown = [c for c in present if c not in DISPLAY_COLUMNS]
    return {
        "ok": len(missing) == 0,
        "missing": missing,
        "unknown": unknown,
        "info": f"Detected columns: {list(df.columns)}"
    }

def _coerce_and_normalize_display_df(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure all display columns exist
    for c in DISPLAY_COLUMNS:
        if c not in df.columns:
            df[c] = ""

    # Numeric coercion
    if "Cost" in df.columns:
        df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce").fillna(0.0)

    # Unit default and whitespace trim
    for col in ["Weight Category", "Supplier Packaging", "Operation Type", "KB Packaging", "Unit"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return _df_order(df)

def _incoming_to_display_df(in_df: pd.DataFrame) -> pd.DataFrame:
    """Map flexible input headers to consistent display schema."""
    out = pd.DataFrame()
    for disp in DISPLAY_COLUMNS:
        # prefer exact display header:
        if disp in in_df.columns:
            out[disp] = in_df[disp]
            continue
        # else try alternate sources that map to same internal field
        internal = COLUMN_MAPPING.get(disp, None)
        src_series = None
        for src, tgt in COLUMN_MAPPING.items():
            if tgt == internal and src in in_df.columns:
                src_series = in_df[src]
                break
        out[disp] = src_series if src_series is not None else ""
    return _coerce_and_normalize_display_df(out)

def _display_df_to_internal_records(df: pd.DataFrame) -> list[dict]:
    """Convert display-schema DataFrame into internal dicts for DB."""
    recs = []
    for _, r in df.iterrows():
        recs.append({
            "weight_category": r.get("Weight Category", ""),
            "supplier_packaging": r.get("Supplier Packaging", ""),
            "operation_type": r.get("Operation Type", ""),
            "kb_packaging": r.get("KB Packaging", ""),
            "cost": float(r.get("Cost", 0.0)) if pd.notna(r.get("Cost", None)) else 0.0,
            "unit": r.get("Unit", ""),
        })
    return recs

def _commit_records(db: RepackingDatabase, recs: list[dict]) -> tuple[int, int, list[str]]:
    """
    Insert or update operations. Equality heuristic within a category:
    supplier_packaging + operation_type + kb_packaging.
    """
    added, updated = 0, 0
    errors: list[str] = []
    for rec in recs:
        cat = (rec.get("weight_category") or "").strip()
        if not cat:
            errors.append("Row rejected: Missing 'Weight Category'.")
            continue

        existing = db.get_operations_for_category(cat)
        match_idx = None
        for idx, op in enumerate(existing):
            if (
                op.get("supplier_packaging", "").strip().lower() == rec.get("supplier_packaging", "").strip().lower()
                and op.get("operation_type", "").strip().lower() == rec.get("operation_type", "").strip().lower()
                and op.get("kb_packaging", "").strip().lower() == rec.get("kb_packaging", "").strip().lower()
            ):
                match_idx = idx
                break

        if match_idx is not None:
            ok = db.update_operation_in_category(cat, match_idx, {
                "supplier_packaging": rec.get("supplier_packaging", ""),
                "operation_type": rec.get("operation_type", ""),
                "kb_packaging": rec.get("kb_packaging", ""),
                "cost": float(rec.get("cost", 0.0)),
                "unit": rec.get("unit", ""),
            })
            if ok:
                updated += 1
            else:
                errors.append(f"Failed to update existing operation in '{cat}'.")
        else:
            db.add_operation_to_category(cat, {
                "supplier_packaging": rec.get("supplier_packaging", ""),
                "operation_type": rec.get("operation_type", ""),
                "kb_packaging": rec.get("kb_packaging", ""),
                "cost": float(rec.get("cost", 0.0)),
                "unit": rec.get("unit", ""),
            })
            added += 1
    return added, updated, errors

# --- JSON category normalization helper for preview branch ---
def _normalize_category_for_preview(cat: str) -> str:
    mapping = {
        "none": "None",
        "light (up to 0,050kg)": "light\n(up to 0,050kg)",
        "moderate (up to 0,150kg)": "moderate\n(up to 0,150kg)",
        "heavy (from 0,150kg)": "heavy\n(from 0,150kg)",
    }
    import re
    s = (cat or "").strip()
    soft = re.sub(r"\s+", " ", s).lower()
    return mapping.get(soft, s)

def main():
    st.title("Repacking Data Management")
    st.markdown("Manage repacking operations with **Excel/CSV/JSON** import (with preview), full CRUD, category tools, stats, and search.")
    st.markdown("---")

    # Init state
    if "data_manager" not in st.session_state:
        st.session_state.data_manager = DataManager()
    if "repacking_db" not in st.session_state:
        st.session_state.repacking_db = RepackingDatabase()
        _load_local_cache(st.session_state.repacking_db)
    if "rep_import_preview_df" not in st.session_state:
        st.session_state.rep_import_preview_df = None

    # 🔄 AUTOLOAD from /DB once per session
    _autoload_repacking_once()
    repacking_db: RepackingDatabase = st.session_state.repacking_db

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 View & Stats",
        "🧰 Category & CRUD",
        "📁 Import/Export (with Preview)",
        "🔍 Search & Filter"
    ])

    # ------------------------------ TAB 1: VIEW & STATS ----------------------
    with tab1:
        st.subheader("Operations by Weight Category")

        stats = repacking_db.get_statistics()
        c1, c2 = st.columns(2)
        c1.metric("Weight Categories", stats.get("weight_categories", len(repacking_db.get_weight_categories())))
        c2.metric("Total Operations", stats.get("total_operations", 0))

        categories = repacking_db.get_weight_categories()
        if not categories or stats.get("total_operations", 0) == 0:
            st.info("No operations found. Import or add new operations.")
        else:
            cat_tabs = st.tabs(categories)
            for i, cat in enumerate(categories):
                with cat_tabs[i]:
                    ops = repacking_db.get_operations_for_category(cat)
                    if ops:
                        df = pd.DataFrame(ops)
                        disp = pd.DataFrame({
                            "Weight Category": [cat] * len(df),
                            "Supplier Packaging": df.get("supplier_packaging", ""),
                            "Operation Type": df.get("operation_type", ""),
                            "KB Packaging": df.get("kb_packaging", ""),
                            "Cost": df.get("cost", 0.0),
                            "Unit": df.get("unit", ""),
                        })
                        st.dataframe(_df_order(disp), use_container_width=True)
                    else:
                        st.info(f"No operations in '{cat}'.")

    # ------------------------- TAB 2: CATEGORY & CRUD ------------------------
    with tab2:
        st.subheader("Category Tools & CRUD")

        subtab1, subtab2, subtab3 = st.tabs(["➕ Add Operation", "✏️ Edit Operation / Move", "🗑️ Delete / Category Tools"])

        # ---------- Add Operation ----------
        with subtab1:
            st.markdown("### Add New Operation")
            categories = repacking_db.get_weight_categories()
            c1, c2 = st.columns(2)
            with c1:
                cat_mode = st.radio("Category Source", ["Existing", "New"], horizontal=True, key="rep_add_cat_mode")
                if cat_mode == "Existing" and categories:
                    category = st.selectbox("Weight Category", categories, key="rep_add_cat_sel")
                else:
                    category = st.text_input("New Weight Category *", key="rep_add_cat_new")
            with c2:
                st.write("")  # spacer

            with st.form("rep_add_form"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    supplier_packaging = st.text_input("Supplier Packaging")
                    operation_type = st.text_input("Operation Type")
                with col2:
                    kb_packaging = st.text_input("KB Packaging")
                    unit = st.text_input("Unit", value="pcs")
                with col3:
                    cost = st.number_input("Cost", min_value=0.0, step=0.01)

                add_btn = st.form_submit_button("Add Operation", type="primary")
                if add_btn:
                    if not (category or "").strip():
                        st.error("Weight Category is required.")
                    else:
                        repacking_db.add_operation_to_category(category.strip(), {
                            "supplier_packaging": supplier_packaging,
                            "operation_type": operation_type,
                            "kb_packaging": kb_packaging,
                            "cost": float(cost),
                            "unit": unit,
                        })
                        repacking_db.save_to_json(REPACK_JSON_PATH)
                        st.success(f"Operation added to '{category.strip()}'.")
                        st.rerun()

        # ---------- Edit Operation / Move ----------
        with subtab2:
            st.markdown("### Edit Existing Operation (and optionally move category)")
            categories = repacking_db.get_weight_categories()
            if not categories:
                st.warning("No categories available.")
            else:
                category = st.selectbox("Current Weight Category", categories, key="rep_edit_cat")
                ops = repacking_db.get_operations_for_category(category)
                if not ops:
                    st.warning(f"No operations to edit in '{category}'.")
                else:
                    ref_df = pd.DataFrame(ops)
                    disp = pd.DataFrame({
                        "Idx": range(len(ref_df)),
                        "Supplier Packaging": ref_df.get("supplier_packaging", ""),
                        "Operation Type": ref_df.get("operation_type", ""),
                        "KB Packaging": ref_df.get("kb_packaging", ""),
                        "Cost": ref_df.get("cost", 0.0),
                        "Unit": ref_df.get("unit", ""),
                    })
                    st.dataframe(disp, use_container_width=True)
                    idx = st.number_input("Select Operation Index (Idx)", min_value=0, max_value=max(0, len(ops) - 1), step=1, value=0)

                    current = ops[int(idx)]
                    with st.form("rep_edit_form"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            supplier_packaging = st.text_input("Supplier Packaging", value=current.get("supplier_packaging", ""))
                            operation_type = st.text_input("Operation Type", value=current.get("operation_type", ""))
                        with col2:
                            kb_packaging = st.text_input("KB Packaging", value=current.get("kb_packaging", ""))
                            unit = st.text_input("Unit", value=current.get("unit", "pcs"))
                        with col3:
                            cost = st.number_input("Cost", value=float(current.get("cost", 0.0)), min_value=0.0, step=0.01)

                        move_cat = st.checkbox("Move to another (or new) category", value=False)
                        if move_cat:
                            all_cats = repacking_db.get_weight_categories()
                            target_mode = st.radio("Target Category", ["Existing", "New"], horizontal=True, key="rep_move_mode")
                            if target_mode == "Existing" and all_cats:
                                target_category = st.selectbox("Select Existing Category", all_cats, key="rep_move_sel")
                            else:
                                target_category = st.text_input("New Target Category *", key="rep_move_new")
                        else:
                            target_category = category

                        upd_btn = st.form_submit_button("Save Changes", type="primary")

                        if upd_btn:
                            new_op = {
                                "supplier_packaging": supplier_packaging,
                                "operation_type": operation_type,
                                "kb_packaging": kb_packaging,
                                "cost": float(cost),
                                "unit": unit,
                            }

                            if move_cat and target_category.strip() != category:
                                # Move: add to target, remove from current
                                repacking_db.add_operation_to_category(target_category.strip(), new_op)
                                ok = repacking_db.remove_operation_from_category(category, int(idx))
                                if not ok:
                                    st.error("Move failed: could not remove from source category.")
                                    st.stop()
                            else:
                                # Update in place
                                ok = repacking_db.update_operation_in_category(category, int(idx), new_op)
                                if not ok:
                                    st.error("Update failed: invalid index/category.")
                                    st.stop()

                            repacking_db.save_to_json(REPACK_JSON_PATH)
                            st.success("Operation saved.")
                            st.rerun()

        # ---------- Delete / Category Tools ----------
        with subtab3:
            st.markdown("### Delete Operation / Category Tools")
            categories = repacking_db.get_weight_categories()
            if not categories:
                st.warning("No categories available.")
            else:
                tool = st.radio("Select Tool", ["Delete Operation", "Rename Category", "Clear Category"], horizontal=True)

                if tool == "Delete Operation":
                    category = st.selectbox("Weight Category", categories, key="rep_del_cat")
                    ops = repacking_db.get_operations_for_category(category)
                    if not ops:
                        st.warning(f"No operations to delete in '{category}'.")
                    else:
                        ref_df = pd.DataFrame(ops)
                        disp = pd.DataFrame({
                            "Idx": range(len(ref_df)),
                            "Supplier Packaging": ref_df.get("supplier_packaging", ""),
                            "Operation Type": ref_df.get("operation_type", ""),
                            "KB Packaging": ref_df.get("kb_packaging", ""),
                            "Cost": ref_df.get("cost", 0.0),
                            "Unit": ref_df.get("unit", ""),
                        })
                        st.dataframe(disp, use_container_width=True)
                        idx = st.number_input("Operation Index (Idx)", min_value=0, max_value=len(ops)-1, step=1, value=0)
                        st.warning(f"⚠️ You are about to delete operation #{idx} in **{category}**.")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("🗑️ Confirm Delete", type="secondary", use_container_width=True):
                                ok = repacking_db.remove_operation_from_category(category, int(idx))
                                if ok:
                                    repacking_db.save_to_json(REPACK_JSON_PATH)
                                    st.success(f"Operation #{idx} in '{category}' deleted.")
                                    st.rerun()
                                else:
                                    st.error("Delete failed (invalid index/category).")
                        with c2:
                            if st.button("Cancel", use_container_width=True):
                                st.rerun()

                elif tool == "Rename Category":
                    src_cat = st.selectbox("Current Category", categories, key="rep_cat_rename_src")
                    new_cat = st.text_input("New Category Name *", key="rep_cat_rename_dst")
                    if st.button("🔤 Rename Category", type="primary"):
                        if not new_cat.strip():
                            st.error("New category name cannot be empty.")
                        else:
                            ops = repacking_db.get_operations_for_category(src_cat)
                            if ops:
                                for op in ops:
                                    repacking_db.add_operation_to_category(new_cat.strip(), op)
                            for i in reversed(range(len(ops))):
                                repacking_db.remove_operation_from_category(src_cat, i)
                            repacking_db.save_to_json(REPACK_JSON_PATH)
                            st.success(f"Category '{src_cat}' renamed to '{new_cat.strip()}' (moved {len(ops)} operations).")
                            st.rerun()

                else:  # Clear Category
                    src_cat = st.selectbox("Category to Clear", categories, key="rep_cat_clear_src")
                    st.warning(f"⚠️ You are about to remove all operations in **{src_cat}**.")
                    if st.button("🧹 Clear Category", type="secondary"):
                        ops = repacking_db.get_operations_for_category(src_cat)
                        for i in reversed(range(len(ops))):
                            repacking_db.remove_operation_from_category(src_cat, i)
                        repacking_db.save_to_json(REPACK_JSON_PATH)
                        st.success(f"All operations cleared in '{src_cat}'.")
                        st.rerun()

    # --------------- TAB 3: IMPORT / EXPORT (Preview + Templates) ------------
    with tab3:
        st.subheader("Import / Export")
        c1, c2 = st.columns(2)

        # -------------------- IMPORT with preview --------------------
        with c1:
            st.markdown("### Import (with Preview)")
            fmt = st.radio("Format", ["Excel", "CSV", "JSON"], key="rep_import_fmt")

            if fmt == "Excel":
                f = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])
                if f and st.button("Preview Import", key="rep_prev_xlsx"):
                    try:
                        df_in = pd.read_excel(f)
                        df_in.columns = df_in.columns.str.strip()
                        disp_df = _incoming_to_display_df(df_in)
                        check = _validate_schema(disp_df)
                        if not check["ok"]:
                            st.error(f"Missing required columns: {check['missing']}")
                        else:
                            st.session_state.rep_import_preview_df = disp_df
                            st.success("Preview prepared. Review below, then click Commit Import.")
                            st.dataframe(_df_order(disp_df), use_container_width=True)
                    except Exception as e:
                        st.error(f"Excel import error: {e}")

            elif fmt == "CSV":
                f = st.file_uploader("Upload CSV", type=["csv"])
                if f and st.button("Preview Import", key="rep_prev_csv"):
                    try:
                        df_in = pd.read_csv(f)
                        df_in.columns = df_in.columns.str.strip()
                        disp_df = _incoming_to_display_df(df_in)
                        check = _validate_schema(disp_df)
                        if not check["ok"]:
                            st.error(f"Missing required columns: {check['missing']}")
                        else:
                            st.session_state.rep_import_preview_df = disp_df
                            st.success("Preview prepared. Review below, then click Commit Import.")
                            st.dataframe(_df_order(disp_df), use_container_width=True)
                    except Exception as e:
                        st.error(f"CSV import error: {e}")

            else:  # JSON
                f = st.file_uploader("Upload JSON", type=["json"])
                if f and st.button("Preview Import", key="rep_prev_json"):
                    try:
                        data = json.load(f)
                        # accept both {"operation_costs": {...}} and direct category mapping
                        op_costs = data.get("operation_costs", data if isinstance(data, dict) else {})

                        rows = []
                        for cat, ops in (op_costs or {}).items():
                            norm_cat = _normalize_category_for_preview(cat)
                            for op in (ops or []):
                                rows.append({
                                    "Weight Category": norm_cat,
                                    "Supplier Packaging": op.get("supplier_packaging", ""),
                                    "Operation Type": op.get("operation_type", ""),
                                    "KB Packaging": op.get("kb_packaging", ""),
                                    "Cost": op.get("cost", 0.0),
                                    "Unit": op.get("unit", ""),
                                })

                        disp_df = pd.DataFrame(rows)
                        disp_df = _coerce_and_normalize_display_df(disp_df)
                        check = _validate_schema(disp_df)
                        if not check["ok"]:
                            st.error(f"Missing required columns: {check['missing']}")
                        else:
                            st.session_state.rep_import_preview_df = disp_df
                            st.success("Preview prepared from JSON. Review below, then click Commit Import.")
                            st.dataframe(_df_order(disp_df), use_container_width=True)
                    except Exception as e:
                        st.error(f"JSON import error: {e}")

            if st.session_state.rep_import_preview_df is not None:
                if st.button("✅ Commit Import", type="primary", key="rep_commit"):
                    prev_df = st.session_state.rep_import_preview_df.copy()
                    recs = _display_df_to_internal_records(prev_df)
                    added, updated, errs = _commit_records(repacking_db, recs)
                    repacking_db.save_to_json(REPACK_JSON_PATH)
                    st.success(f"Import committed. Added: {added}, Updated: {updated}")
                    if errs:
                        with st.expander("Show row errors"):
                            for e in errs:
                                st.write("- " + e)
                    # reset preview
                    st.session_state.rep_import_preview_df = None
                    st.rerun()

            st.divider()
            if st.button("🔄 Reset Repacking (Defaults)"):
                repacking_db.reset_to_defaults()
                repacking_db.save_to_json(REPACK_JSON_PATH)
                st.warning("Repacking DB reset to default categories.")
                st.rerun()

        # -------------------- EXPORT + Templates --------------------
        with c2:
            st.markdown("### Export")
            df_all = repacking_db.to_dataframe()
            if not df_all.empty:
                # Ensure display schema for export
                disp = pd.DataFrame({
                    "Weight Category": df_all.get("Weight Category", df_all.get("weight_category", "")),
                    "Supplier Packaging": df_all.get("Supplier Packaging", df_all.get("supplier_packaging", "")),
                    "Operation Type": df_all.get("Operation Type", df_all.get("operation_type", "")),
                    "KB Packaging": df_all.get("KB Packaging", df_all.get("kb_packaging", "")),
                    "Cost": df_all.get("Cost", df_all.get("cost", 0.0)),
                    "Unit": df_all.get("Unit", df_all.get("unit", "")),
                })
                disp = _coerce_and_normalize_display_df(disp)

                fmt = st.radio("Format", ["JSON", "CSV", "Excel"], key="rep_export_fmt")
                # Optional compatibility for flat JSON (no wrapper, spaces instead of \n)
                compat_flat = st.checkbox("Export flat JSON (no wrapper, space instead of newline)", value=False)

                if fmt == "JSON":
                    if st.button("Download JSON", key="rep_export_json_btn"):
                        if compat_flat:
                            # flat mapping { "<category with spaces>": [ops...] }
                            def _canon_to_plain(cat: str) -> str:
                                return cat.replace("\n", " ")
                            flat = {}
                            for cat, ops in repacking_db.operation_costs.items():
                                flat[_canon_to_plain(cat)] = ops
                            payload = flat
                        else:
                            # canonical wrapped format
                            payload = {
                                "operation_costs": repacking_db.operation_costs,
                                "metadata": {
                                    "total_categories": len(repacking_db.operation_costs),
                                    "total_operations": sum(len(v) for v in repacking_db.operation_costs.values())
                                }
                            }
                        st.download_button(
                            "Save repacking_database.json",
                            data=json.dumps(payload, indent=2),
                            file_name="repacking_database.json",
                            mime="application/json"
                        )
                elif fmt == "CSV":
                    if st.button("Download CSV", key="rep_export_csv_btn"):
                        st.download_button(
                            "Save repacking_database.csv",
                            data=_df_order(disp).to_csv(index=False),
                            file_name="repacking_database.csv",
                            mime="text/csv"
                        )
                else:
                    if st.button("Download Excel", key="rep_export_xlsx_btn"):
                        out = BytesIO()
                        with pd.ExcelWriter(out, engine="openpyxl") as xw:
                            _df_order(disp).to_excel(xw, index=False, sheet_name="Repacking")
                        st.download_button(
                            "Save repacking_database.xlsx",
                            data=out.getvalue(),
                            file_name="repacking_database.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.info("No repacking data to export.")

            st.divider()
            st.markdown("### Download Templates")
            tdf = _make_template_df()
            # CSV template
            csv_bytes = tdf.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📄 Download CSV Template",
                data=csv_bytes,
                file_name="repacking_template.csv",
                mime="text/csv"
            )
            # Excel template
            out = BytesIO()
            with pd.ExcelWriter(out, engine="openpyxl") as xw:
                tdf.to_excel(xw, index=False, sheet_name="Repacking")
            st.download_button(
                "📄 Download Excel Template",
                data=out.getvalue(),
                file_name="repacking_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ------------------------------ TAB 4: SEARCH ----------------------------
    with tab4:
        st.subheader("Search Operations")

        c1, c2 = st.columns(2)
        with c1:
            q_category = st.text_input("Filter by Weight Category")
        with c2:
            q_text = st.text_input("Free-text search (supplier/kb/operation/unit)")

        if st.button("Search"):
            results = []
            for cat in repacking_db.get_weight_categories():
                if q_category.strip() and q_category.strip().lower() not in cat.lower():
                    continue
                ops = repacking_db.get_operations_for_category(cat)
                for op in ops:
                    results.append({
                        "Weight Category": cat,
                        "Supplier Packaging": op.get("supplier_packaging", ""),
                        "Operation Type": op.get("operation_type", ""),
                        "KB Packaging": op.get("kb_packaging", ""),
                        "Cost": op.get("cost", 0.0),
                        "Unit": op.get("unit", ""),
                    })

            df = pd.DataFrame(results)
            if not df.empty and q_text.strip():
                needle = q_text.strip().lower()
                cols = ["Supplier Packaging", "Operation Type", "KB Packaging", "Unit"]
                cols = [c for c in cols if c in df.columns]
                mask = pd.Series([False] * len(df))
                for c in cols:
                    mask = mask | df[c].astype(str).str.lower().str.contains(needle, na=False)
                df = df[mask]

            if not df.empty:
                st.success(f"Found {len(df)} operation(s).")
                st.dataframe(_df_order(df), use_container_width=True)
            else:
                st.warning("No operations match your filters.")

if __name__ == "__main__":
    main()
