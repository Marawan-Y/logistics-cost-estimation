# utils/repacking_database.py - UPDATED
import json
import pandas as pd
import re
from typing import Dict, List, Optional
from pathlib import Path

class RepackingDatabase:
    """
    Enhanced Repacking Database with Excel/CSV/JSON import capabilities,
    tolerant JSON loader (wrapper or flat mapping), and category normalization.
    """

    # --- Canonical weight category names used internally (with newlines) ---
    _CANON_DEFAULTS = [
        "None",
        "light\n(up to 0,050kg)",
        "moderate\n(up to 0,150kg)",
        "heavy\n(from 0,150kg)"
    ]

    # --- Aliases for category normalization (lowercased, whitespace-collapsed) ---
    _CAT_ALIASES = {
        "none": "None",
        "light (up to 0,050kg)": "light\n(up to 0,050kg)",
        "moderate (up to 0,150kg)": "moderate\n(up to 0,150kg)",
        "heavy (from 0,150kg)": "heavy\n(from 0,150kg)",
    }

    def __init__(self):
        # Structure: weight_category (canonical) -> list[operation dict]
        self.operation_costs: Dict[str, List[Dict]] = {}
        self.initialize_default_categories()

    # ------------------- Category helpers -------------------

    @staticmethod
    def _normalize_category(cat: str) -> str:
        """
        Normalize an incoming category string to one of the canonical buckets.
        Logic:
          - If empty -> "None"
          - Collapse whitespace for comparison, lower-case match against aliases.
          - If matches alias -> return canonical name with newline variant.
          - Else keep original (allows custom categories to exist).
        """
        if not cat:
            return "None"
        s = str(cat).strip()
        soft = re.sub(r"\s+", " ", s).lower()
        return RepackingDatabase._CAT_ALIASES.get(soft, s)

    def initialize_default_categories(self):
        """Ensure canonical default categories are present."""
        for category in self._CANON_DEFAULTS:
            if category not in self.operation_costs:
                self.operation_costs[category] = []

    def get_weight_categories(self) -> List[str]:
        return list(self.operation_costs.keys())

    # ------------------- CRUD ops per category -------------------

    def add_operation_to_category(self, category: str, operation_data: Dict) -> None:
        cat = self._normalize_category(category)
        if cat not in self.operation_costs:
            self.operation_costs[cat] = []
        self.operation_costs[cat].append({
            "supplier_packaging": operation_data.get("supplier_packaging", ""),
            "operation_type": operation_data.get("operation_type", ""),
            "kb_packaging": operation_data.get("kb_packaging", ""),
            "cost": float(operation_data.get("cost", 0.0)),
            "unit": operation_data.get("unit", ""),
        })

    def update_operation_in_category(self, category: str, index: int, operation_data: Dict) -> bool:
        cat = self._normalize_category(category)
        if cat in self.operation_costs and 0 <= index < len(self.operation_costs[cat]):
            self.operation_costs[cat][index] = {
                "supplier_packaging": operation_data.get("supplier_packaging", ""),
                "operation_type": operation_data.get("operation_type", ""),
                "kb_packaging": operation_data.get("kb_packaging", ""),
                "cost": float(operation_data.get("cost", 0.0)),
                "unit": operation_data.get("unit", ""),
            }
            return True
        return False

    def remove_operation_from_category(self, category: str, index: int) -> bool:
        cat = self._normalize_category(category)
        if cat in self.operation_costs and 0 <= index < len(self.operation_costs[cat]):
            self.operation_costs[cat].pop(index)
            return True
        return False

    def get_operations_for_category(self, category: str) -> List[Dict]:
        return self.operation_costs.get(self._normalize_category(category), [])

    # ------------------- Search -------------------

    def search_operations(self, search_term: str) -> Dict[str, List[Dict]]:
        """Search by packaging fields or operation type across all categories."""
        results: Dict[str, List[Dict]] = {}
        needle = (search_term or "").lower()
        for cat, ops in self.operation_costs.items():
            matches = []
            for op in ops:
                if (
                    needle in op.get('supplier_packaging', '').lower() or
                    needle in op.get('kb_packaging', '').lower() or
                    needle in op.get('operation_type', '').lower() or
                    needle in op.get('unit', '').lower()
                ):
                    matches.append(op)
            if matches:
                results[cat] = matches
        return results

    # ------------------- Importers -------------------

    def load_from_excel(self, file_path: str) -> None:
        """
        Load repacking data from Excel file.
        Accepts both standard and alternate headers as seen in source sheets.
        """
        try:
            df = pd.read_excel(file_path)
            self._load_from_dataframe(df)
        except Exception as e:
            raise Exception(f"Error loading Excel file: {str(e)}")

    def load_from_csv(self, file_path: str) -> None:
        """Load repacking data from CSV file."""
        try:
            df = pd.read_csv(file_path)
            self._load_from_dataframe(df)
        except Exception as e:
            raise Exception(f"Error loading CSV file: {str(e)}")

    def _load_from_dataframe(self, df: pd.DataFrame) -> None:
        """Shared logic for Excel/CSV to populate operation_costs."""
        # Clean column names
        df.columns = df.columns.str.strip()

        # Column mapping (input -> internal)
        column_mapping = {
            'Weight Category': 'weight_category',
            'pcs_weight': 'weight_category',
            'Supplier Packaging': 'supplier_packaging',
            'packaging_one_way': 'supplier_packaging',
            'Operation Type': 'operation_type',
            'KB Packaging': 'kb_packaging',
            'packaging_returnable': 'kb_packaging',
            'Cost': 'cost',
            'Unit': 'unit'
        }

        for _, row in df.iterrows():
            op = {}
            weight_category = None

            for src, tgt in column_mapping.items():
                if src in df.columns:
                    value = row[src]
                    if pd.isna(value):
                        if tgt == 'cost':
                            value = 0.0
                        else:
                            value = ""
                    if tgt == 'weight_category':
                        weight_category = str(value)
                    else:
                        op[tgt] = value

            if weight_category:
                self.add_operation_to_category(weight_category, op)

    def load_from_json(self, file_path: str) -> None:
        """
        Load repacking data from JSON file.

        Tolerates two shapes:
          1) {"operation_costs": { "<category>": [ ... ] , ... }}
          2) { "<category>": [ ... ], ... }   <-- flat mapping (no wrapper)

        Also normalizes category labels (newline vs space variants).
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict) and "operation_costs" in data:
                src = data["operation_costs"]
            else:
                src = data if isinstance(data, dict) else {}

            merged: Dict[str, List[Dict]] = {}
            for cat, ops in (src or {}).items():
                ncat = self._normalize_category(cat)
                merged.setdefault(ncat, [])
                for op in (ops or []):
                    merged[ncat].append({
                        "supplier_packaging": op.get("supplier_packaging", ""),
                        "operation_type": op.get("operation_type", ""),
                        "kb_packaging": op.get("kb_packaging", ""),
                        "cost": float(op.get("cost", 0.0)),
                        "unit": op.get("unit", ""),
                    })

            self.operation_costs = merged
            self.initialize_default_categories()

        except FileNotFoundError:
            self.initialize_default_categories()
        except Exception as e:
            raise Exception(f"Error loading JSON file: {str(e)}")

    # ------------------- Exporters -------------------

    def save_to_json(self, file_path: str) -> None:
        """Save repacking data in the canonical wrapped format."""
        total_operations = sum(len(ops) for ops in self.operation_costs.values())
        data = {
            'operation_costs': self.operation_costs,
            'metadata': {
                'save_timestamp': pd.Timestamp.now().isoformat(),
                'version': '1.0.0',
                'total_categories': len(self.operation_costs),
                'total_operations': total_operations
            }
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    # ------------------- Views & Stats -------------------

    def to_dataframe(self) -> pd.DataFrame:
        """Convert all operations to a display-friendly DataFrame."""
        rows = []
        for cat, ops in self.operation_costs.items():
            for op in ops:
                rows.append({
                    'Weight Category': cat,
                    'Supplier Packaging': op.get('supplier_packaging', ''),
                    'Operation Type': op.get('operation_type', ''),
                    'KB Packaging': op.get('kb_packaging', ''),
                    'Cost': op.get('cost', 0.0),
                    'Unit': op.get('unit', '')
                })
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    def get_statistics(self) -> Dict:
        total_ops = sum(len(ops) for ops in self.operation_costs.values())
        return {
            'weight_categories': len(self.operation_costs),
            'total_operations': total_ops,
            'categories': list(self.operation_costs.keys())
        }

    def reset_to_defaults(self) -> None:
        """Reset to default categories with no operations."""
        self.operation_costs = {}
        self.initialize_default_categories()
