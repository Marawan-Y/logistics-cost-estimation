# pages/12Supplier_Data_Management.py - FULL FEATURED with Excel/CSV/JSON Import, Preview, Templates,
# Duplicate checks, Safe Vendor-ID rename, Advanced Search, and Stats
import streamlit as st
import pandas as pd
from io import BytesIO
import json
from pathlib import Path
from utils.data_manager import DataManager
from utils.supplier_database import SupplierDatabase

st.set_page_config(page_title="Supplier Data Management", page_icon="🏭", layout="wide")

DB_DIR = Path("DB")
SUPPLIER_JSON_CACHE = Path("suppliers_database.json")

SUPPLIER_JSON_PATH = "suppliers_database.json"

DISPLAY_COLUMNS = [
    "Vendor ID",
    "Vendor Name",
    "Vendor Country",
    "City of Manufacture",
    "Vendor ZIP",
    "Delivery Performance (%)",
    "Deliveries per Month",
    "KB/Bendix Plant",
    "KB/Bendix Country",
    "Distance (km)",
]

REQUIRED_COLUMNS = [
    "Vendor ID",
    "Vendor Name",
    "Vendor Country",
    "City of Manufacture",
]

# Mapping the names expected by utils.supplier_database for flexible import headers
COLUMN_MAPPING = {
    'Vendor ID': 'vendor_id',
    'Vendor Name': 'vendor_name',
    'Vendor Country': 'vendor_country',
    'City of Manufacture': 'city_of_manufacture',
    'Vendor ZIP': 'vendor_zip',
    'Delivery Performance': 'delivery_performance',
    'Delivery Performance (%)': 'delivery_performance',
    'Deliveries per Month': 'deliveries_per_month',
    'KB/Bendix Plant': 'plant',
    'Plant': 'plant',
    'KB/Bendix Country': 'country',
    'Country': 'country',
    'Distance (km)': 'distance',
    'Distance': 'distance',
}

def _df_order_cols(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in DISPLAY_COLUMNS if c in df.columns]
    rest = [c for c in df.columns if c not in cols]
    return df[cols + rest] if cols else df

def _autoload_suppliers_once():
    """
    Load Suppliers from DB/Excel/Supplier.xlsx, else DB/JSON/suppliers_database.json,
    else legacy local cache. Run once per session.
    """
    if st.session_state.get("_suppliers_autoloaded"):
        return

    supplier_db: SupplierDatabase = st.session_state.supplier_db
    excel_path = DB_DIR / "Excel" / "Supplier.xlsx"
    json_path  = DB_DIR / "JSON"  / "suppliers_database.json"

    loaded_from = None
    try:
        if excel_path.exists():
            supplier_db.database = {}
            supplier_db.load_from_excel(str(excel_path))
            loaded_from = str(excel_path)
        elif json_path.exists():
            supplier_db.database = {}
            supplier_db.load_from_json(str(json_path))
            loaded_from = str(json_path)
        elif SUPPLIER_JSON_CACHE.exists():
            supplier_db.database = {}
            supplier_db.load_from_json(str(SUPPLIER_JSON_CACHE))
            loaded_from = str(SUPPLIER_JSON_CACHE)
    except Exception as e:
        st.warning(f"Suppliers autoload warning: {e}")

    if loaded_from:
        st.info(f"📥 Suppliers auto-loaded from: `{loaded_from}`")
    else:
        st.info("📥 Suppliers: no file found in /DB (Excel/JSON). Starting empty.")

    st.session_state["_suppliers_autoloaded"] = True

def _load_local_cache(db: SupplierDatabase):
    try:
        db.load_from_json(SUPPLIER_JSON_PATH)
    except Exception:
        pass

def _make_template_df() -> pd.DataFrame:
    # Template with headers and no data
    return pd.DataFrame(columns=DISPLAY_COLUMNS)

def _validate_schema(df: pd.DataFrame) -> dict:
    """Return dict with 'ok', 'missing', 'unknown', 'info' keys."""
    present = set(df.columns)
    required_missing = [c for c in REQUIRED_COLUMNS if c not in present]
    unknown = [c for c in present if c not in DISPLAY_COLUMNS]
    return {
        "ok": len(required_missing) == 0,
        "missing": required_missing,
        "unknown": unknown,
        "info": f"Detected columns: {list(df.columns)}"
    }

def _normalize_import_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce types and normalize column names to our display schema."""
    # Ensure all expected columns exist
    for col in DISPLAY_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # Coerce numeric columns
    if "Delivery Performance (%)" in df.columns:
        df["Delivery Performance (%)"] = pd.to_numeric(df["Delivery Performance (%)"], errors="coerce").fillna(0.0)
    if "Deliveries per Month" in df.columns:
        df["Deliveries per Month"] = pd.to_numeric(df["Deliveries per Month"], errors="coerce").fillna(0).astype(int)
    if "Distance (km)" in df.columns:
        df["Distance (km)"] = pd.to_numeric(df["Distance (km)"], errors="coerce").fillna(0.0)

    return _df_order_cols(df)

def _df_to_internal_records(df: pd.DataFrame) -> list[dict]:
    """Map display columns -> internal keys used by SupplierDatabase."""
    rows = []
    for _, r in df.iterrows():
        rec = {}
        for disp_col, internal in COLUMN_MAPPING.items():
            if disp_col in df.columns:
                rec[internal] = r.get(disp_col, "")
        rows.append(rec)
    return rows

def _add_or_update_from_records(db: SupplierDatabase, records: list[dict]) -> tuple[int,int,list[str]]:
    """Insert or update records into the DB. Return (added, updated, errors)."""
    added = 0
    updated = 0
    errors = []
    for rec in records:
        vid = str(rec.get("vendor_id", "")).strip()
        if not vid:
            errors.append("Row rejected: Missing Vendor ID")
            continue
        if db.supplier_exists(vid):
            # Update existing
            db.update_supplier(vid, rec)
            updated += 1
        else:
            db.add_supplier(vid, rec)
            added += 1
    return added, updated, errors

def main():
    st.title("Supplier Data Management")
    st.markdown("Manage Supplier Database with **Excel/CSV/JSON** Import (with preview), full CRUD, and advanced search.")
    st.markdown("---")

    # Initialize state
    if "data_manager" not in st.session_state:
        st.session_state.data_manager = DataManager()
    if "supplier_db" not in st.session_state:
        st.session_state.supplier_db = SupplierDatabase()
        _load_local_cache(st.session_state.supplier_db)
    if "import_preview_df" not in st.session_state:
        st.session_state.import_preview_df = None
    if "import_errors" not in st.session_state:
        st.session_state.import_errors = []

    # 🔄 AUTOLOAD from /DB once per session
    _autoload_suppliers_once()
    supplier_db: SupplierDatabase = st.session_state.supplier_db

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 View & Stats",
        "➕ Add/Edit/Delete Supplier",
        "📁 Import/Export (with Preview)",
        "🔍 Search & Filter"
    ])

    # ------------------------------ TAB 1: VIEW + STATS ----------------------
    with tab1:
        st.subheader("Suppliers")
        df = supplier_db.to_dataframe()
        if not df.empty:
            stats = supplier_db.get_statistics()
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Suppliers", stats.get("total_suppliers", len(df)))
            c2.metric("Countries", stats.get("total_countries", 0))
            c3.metric("Cities", stats.get("total_cities", 0))

            with st.expander("Show unique countries & cities"):
                col_a, col_b = st.columns(2)
                countries = stats.get("countries", [])
                cities = stats.get("cities", [])
                col_a.write("**Countries**")
                if countries:
                    col_a.write(", ".join(sorted(countries)))
                else:
                    col_a.info("No countries in data.")
                col_b.write("**Cities**")
                if cities:
                    col_b.write(", ".join(sorted(cities)))
                else:
                    col_b.info("No cities in data.")

            st.dataframe(_df_order_cols(df), use_container_width=True)
        else:
            st.info("No supplier data loaded. Please import data or add new suppliers.")

    # ------------------------- TAB 2: ADD / EDIT / DELETE --------------------
    with tab2:
        st.subheader("Add, Edit, or Delete Supplier")
        action = st.radio("Select Action", ["Add New Supplier", "Edit Existing Supplier", "Delete Supplier"], horizontal=True)

        # ---------------- ADD ----------------
        if action == "Add New Supplier":
            with st.form("add_supplier_form"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    vendor_id = st.text_input("Vendor ID *")
                    vendor_name = st.text_input("Vendor Name")
                    vendor_country = st.text_input("Vendor Country")
                    city_of_manufacture = st.text_input("City of Manufacture")
                with col2:
                    vendor_zip = st.text_input("Vendor ZIP")
                    delivery_performance = st.number_input("Delivery Performance (%)", min_value=0.0, max_value=100.0, step=0.1)
                    deliveries_per_month = st.number_input("Deliveries per Month", min_value=0, step=1)
                    plant = st.text_input("KB/Bendix Plant")
                with col3:
                    country = st.text_input("KB/Bendix Country")
                    distance = st.number_input("Distance (km)", min_value=0.0, step=0.1)

                add_btn = st.form_submit_button("Add Supplier", type="primary")
                if add_btn:
                    vid = (vendor_id or "").strip()
                    if not vid:
                        st.error("Vendor ID is required.")
                    elif supplier_db.supplier_exists(vid):
                        st.error(f"Vendor ID '{vid}' already exists. Please use a unique Vendor ID.")
                    else:
                        supplier_data = {
                            "vendor_id": vid,
                            "vendor_name": vendor_name,
                            "vendor_country": vendor_country,
                            "city_of_manufacture": city_of_manufacture,
                            "vendor_zip": vendor_zip,
                            "delivery_performance": delivery_performance,
                            "deliveries_per_month": deliveries_per_month,
                            "plant": plant,
                            "country": country,
                            "distance": distance,
                        }
                        supplier_db.add_supplier(vid, supplier_data)
                        supplier_db.save_to_json(SUPPLIER_JSON_PATH)
                        st.success(f"Supplier '{vid}' added.")
                        st.rerun()

        # ---------------- EDIT ----------------
        elif action == "Edit Existing Supplier":
            df = supplier_db.to_dataframe()
            if df.empty:
                st.warning("No suppliers to edit.")
            else:
                vendor_ids = list(supplier_db.database.keys())
                selected_id = st.selectbox("Select Vendor ID", vendor_ids)
                current = supplier_db.get_supplier(selected_id) or {}

                with st.form("edit_supplier_form"):
                    st.markdown(f"### Editing: `{selected_id}`")
                    allow_rename = st.checkbox("Change Vendor ID (safe rename)", value=False)
                    new_vendor_id = st.text_input("New Vendor ID", value=selected_id, disabled=not allow_rename)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        vendor_name = st.text_input("Vendor Name", value=current.get("vendor_name", ""))
                        vendor_country = st.text_input("Vendor Country", value=current.get("vendor_country", ""))
                        city_of_manufacture = st.text_input("City of Manufacture", value=current.get("city_of_manufacture", ""))
                    with col2:
                        vendor_zip = st.text_input("Vendor ZIP", value=current.get("vendor_zip", ""))
                        delivery_performance = st.number_input("Delivery Performance (%)", value=float(current.get("delivery_performance", 0.0)), min_value=0.0, max_value=100.0, step=0.1)
                        deliveries_per_month = st.number_input("Deliveries per Month", value=int(current.get("deliveries_per_month", 0)), min_value=0, step=1)
                        plant = st.text_input("KB/Bendix Plant", value=current.get("plant", ""))
                    with col3:
                        country = st.text_input("KB/Bendix Country", value=current.get("country", ""))
                        distance = st.number_input("Distance (km)", value=float(current.get("distance", 0.0)), min_value=0.0, step=0.1)

                    upd_btn = st.form_submit_button("Update Supplier", type="primary")
                    if upd_btn:
                        # handle rename
                        target_vid = selected_id
                        if allow_rename:
                            proposed = (new_vendor_id or "").strip()
                            if not proposed:
                                st.error("New Vendor ID cannot be empty.")
                                st.stop()
                            if proposed != selected_id and supplier_db.supplier_exists(proposed):
                                st.error(f"Cannot rename: Vendor ID '{proposed}' already exists.")
                                st.stop()
                            # safe migration: delete old, insert new
                            target_vid = proposed
                            # prepare new record with target_vid
                            new_record = {
                                "vendor_id": target_vid,
                                "vendor_name": vendor_name,
                                "vendor_country": vendor_country,
                                "city_of_manufacture": city_of_manufacture,
                                "vendor_zip": vendor_zip,
                                "delivery_performance": delivery_performance,
                                "deliveries_per_month": deliveries_per_month,
                                "plant": plant,
                                "country": country,
                                "distance": distance,
                            }
                            # remove old and add new
                            supplier_db.remove_supplier(selected_id)
                            supplier_db.add_supplier(target_vid, new_record)
                        else:
                            updated = {
                                "vendor_id": target_vid,  # keep key stable
                                "vendor_name": vendor_name,
                                "vendor_country": vendor_country,
                                "city_of_manufacture": city_of_manufacture,
                                "vendor_zip": vendor_zip,
                                "delivery_performance": delivery_performance,
                                "deliveries_per_month": deliveries_per_month,
                                "plant": plant,
                                "country": country,
                                "distance": distance,
                            }
                            supplier_db.update_supplier(target_vid, updated)

                        supplier_db.save_to_json(SUPPLIER_JSON_PATH)
                        st.success(f"Supplier '{target_vid}' updated.")
                        st.rerun()

        # ---------------- DELETE ----------------
        else:
            df = supplier_db.to_dataframe()
            if df.empty:
                st.warning("No suppliers to delete.")
            else:
                vendor_ids = list(supplier_db.database.keys())
                selected_id = st.selectbox("Select Vendor ID to Delete", vendor_ids, key="delete_supplier_select")
                st.warning(f"⚠️ You are about to delete: **{selected_id}**")
                st.info("This action cannot be undone. Make sure you have a backup if needed.")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🗑️ Confirm Delete", type="secondary", use_container_width=True):
                        supplier_db.remove_supplier(selected_id)
                        supplier_db.save_to_json(SUPPLIER_JSON_PATH)
                        st.success(f"Supplier '{selected_id}' deleted.")
                        st.rerun()
                with c2:
                    if st.button("Cancel", use_container_width=True):
                        st.rerun()

    # --------------- TAB 3: IMPORT / EXPORT (Preview + Templates) ------------
    with tab3:
        st.subheader("Import / Export")
        c1, c2 = st.columns(2)

        # IMPORT with preview
        with c1:
            st.markdown("### Import (with Preview)")
            fmt = st.radio("Format", ["Excel", "CSV", "JSON"], key="sup_import_fmt")

            preview_btn_key = "sup_preview_btn"
            commit_btn_key = "sup_commit_btn"

            if fmt == "Excel":
                f = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])
                if f and st.button("Preview Import", key=preview_btn_key):
                    try:
                        df = pd.read_excel(f)
                        df.columns = df.columns.str.strip()
                        check = _validate_schema(df)
                        if not check["ok"]:
                            st.error(f"Missing required columns: {check['missing']}")
                        else:
                            norm = _normalize_import_dataframe(df)
                            st.session_state.import_preview_df = norm
                            st.session_state.import_errors = []
                            st.success("Preview prepared. Review below, then click Commit Import.")
                            st.dataframe(_df_order_cols(norm), use_container_width=True)
                    except Exception as e:
                        st.error(f"Excel import error: {e}")

            elif fmt == "CSV":
                f = st.file_uploader("Upload CSV", type=["csv"])
                if f and st.button("Preview Import", key=preview_btn_key):
                    try:
                        df = pd.read_csv(f)
                        df.columns = df.columns.str.strip()
                        check = _validate_schema(df)
                        if not check["ok"]:
                            st.error(f"Missing required columns: {check['missing']}")
                        else:
                            norm = _normalize_import_dataframe(df)
                            st.session_state.import_preview_df = norm
                            st.session_state.import_errors = []
                            st.success("Preview prepared. Review below, then click Commit Import.")
                            st.dataframe(_df_order_cols(norm), use_container_width=True)
                    except Exception as e:
                        st.error(f"CSV import error: {e}")

            else:  # JSON
                f = st.file_uploader("Upload JSON", type=["json"])
                if f and st.button("Preview Import", key=preview_btn_key):
                    try:
                        # Load straight into DB preview by converting to df
                        loaded = json.load(f)
                        # Support either {"database": {...}} or raw dict
                        db_dict = loaded.get("database", loaded)
                        # Convert to df in display schema
                        rows = []
                        for vid, rec in db_dict.items():
                            rows.append({
                                "Vendor ID": rec.get("vendor_id", vid),
                                "Vendor Name": rec.get("vendor_name", ""),
                                "Vendor Country": rec.get("vendor_country", ""),
                                "City of Manufacture": rec.get("city_of_manufacture", ""),
                                "Vendor ZIP": rec.get("vendor_zip", ""),
                                "Delivery Performance (%)": rec.get("delivery_performance", 0.0),
                                "Deliveries per Month": rec.get("deliveries_per_month", 0),
                                "KB/Bendix Plant": rec.get("plant", ""),
                                "KB/Bendix Country": rec.get("country", ""),
                                "Distance (km)": rec.get("distance", 0.0),
                            })
                        df = pd.DataFrame(rows)
                        norm = _normalize_import_dataframe(df)
                        st.session_state.import_preview_df = norm
                        st.session_state.import_errors = []
                        st.success("Preview prepared from JSON. Review below, then click Commit Import.")
                        st.dataframe(_df_order_cols(norm), use_container_width=True)
                    except Exception as e:
                        st.error(f"JSON import error: {e}")

            # Commit preview
            if st.session_state.import_preview_df is not None:
                if st.button("✅ Commit Import", type="primary", key=commit_btn_key):
                    preview_df = st.session_state.import_preview_df.copy()
                    # Build internal records
                    recs = _df_to_internal_records(preview_df)
                    added, updated, errs = _add_or_update_from_records(supplier_db, recs)
                    supplier_db.save_to_json(SUPPLIER_JSON_PATH)
                    st.success(f"Import committed. Added: {added}, Updated: {updated}")
                    if errs:
                        with st.expander("Show row errors"):
                            for e in errs:
                                st.write("- " + e)
                    # reset preview
                    st.session_state.import_preview_df = None
                    st.session_state.import_errors = []
                    st.rerun()

            st.divider()
            if st.button("🔄 Reset Suppliers (Empty)"):
                supplier_db.database = {}
                supplier_db.save_to_json(SUPPLIER_JSON_PATH)
                st.warning("Supplier DB reset.")
                st.rerun()

        # EXPORT + TEMPLATES
        with c2:
            st.markdown("### Export")
            if supplier_db.database:
                fmt = st.radio("Format", ["JSON", "CSV", "Excel"], key="sup_export_fmt")
                if fmt == "JSON":
                    if st.button("Download JSON", key="sup_export_json_btn"):
                        data = {
                            "database": supplier_db.database,
                            "metadata": {
                                "exported_rows": len(supplier_db.database)
                            }
                        }
                        st.download_button(
                            "Save suppliers_database.json",
                            data=json.dumps(data, indent=2),
                            file_name="suppliers_database.json",
                            mime="application/json"
                        )
                elif fmt == "CSV":
                    if st.button("Download CSV", key="sup_export_csv_btn"):
                        df = supplier_db.to_dataframe()
                        st.download_button(
                            "Save suppliers_database.csv",
                            data=_df_order_cols(df).to_csv(index=False),
                            file_name="suppliers_database.csv",
                            mime="text/csv"
                        )
                else:
                    if st.button("Download Excel", key="sup_export_xlsx_btn"):
                        df = supplier_db.to_dataframe()
                        out = BytesIO()
                        with pd.ExcelWriter(out, engine="openpyxl") as xw:
                            _df_order_cols(df).to_excel(xw, index=False, sheet_name="Suppliers")
                        st.download_button(
                            "Save suppliers_database.xlsx",
                            data=out.getvalue(),
                            file_name="suppliers_database.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.info("No supplier data to export.")

            st.divider()
            st.markdown("### Download Templates")
            tdf = _make_template_df()
            # CSV template
            csv_bytes = tdf.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📄 Download CSV Template",
                data=csv_bytes,
                file_name="suppliers_template.csv",
                mime="text/csv"
            )
            # Excel template
            out = BytesIO()
            with pd.ExcelWriter(out, engine="openpyxl") as xw:
                tdf.to_excel(xw, index=False, sheet_name="Suppliers")
            st.download_button(
                "📄 Download Excel Template",
                data=out.getvalue(),
                file_name="suppliers_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ------------------------------ TAB 4: SEARCH ----------------------------
    with tab4:
        st.subheader("Search & Filter")
        c1, c2, c3 = st.columns(3)
        with c1:
            q_vendor_id = st.text_input("Filter by Vendor ID")
        with c2:
            q_country = st.text_input("Filter by Vendor Country")
        with c3:
            q_city = st.text_input("Filter by City of Manufacture")

        free_text = st.text_input("Free-text search (name/country/city/plant/ZIP)")

        if st.button("Search"):
            # Structured filter first
            matches = supplier_db.filter_suppliers(
                vendor_id=q_vendor_id or None,
                country=q_country or None,
                city=q_city or None
            )
            # Convert to df for free-text filtering
            res_df = pd.DataFrame(matches) if matches else supplier_db.to_dataframe()

            if free_text.strip():
                needle = free_text.strip().lower()
                if not res_df.empty:
                    subset_cols = [
                        "Vendor ID", "Vendor Name", "Vendor Country", "City of Manufacture",
                        "Vendor ZIP", "KB/Bendix Plant", "KB/Bendix Country"
                    ]
                    keep_cols = [c for c in subset_cols if c in res_df.columns]
                    mask = pd.Series([False] * len(res_df))
                    for c in keep_cols:
                        mask = mask | res_df[c].astype(str).str.lower().str.contains(needle, na=False)
                    res_df = res_df[mask]

            if not res_df.empty:
                st.success(f"Found {len(res_df)} supplier(s).")
                st.dataframe(_df_order_cols(res_df), use_container_width=True)
            else:
                st.warning("No suppliers match your filters.")

if __name__ == "__main__":
    main()
