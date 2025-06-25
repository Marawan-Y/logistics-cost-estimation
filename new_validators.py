"""
Validation utilities for Logistics Cost Application

Extended to allow the new parameters (defaults to 0) and ensure positivity.
"""

import re
from typing import Dict, List, Any


class BaseValidator:
    @staticmethod
    def is_empty_or_none(value) -> bool:
        if value is None: return True
        if isinstance(value, str) and not value.strip(): return True
        return False

    @staticmethod
    def is_positive_number(value, allow_zero: bool = False) -> bool:
        try:
            v = float(value)
            return v >= 0 if allow_zero else v > 0
        except:
            return False

    @staticmethod
    def is_positive_integer(value, allow_zero: bool = False) -> bool:
        try:
            v = int(value)
            return v >= 0 if allow_zero else v > 0
        except:
            return False

    @staticmethod
    def is_valid_percentage(value) -> bool:
        try:
            v = float(value)
            return 0 <= v <= 100
        except:
            return False


class MaterialValidator(BaseValidator):
    def validate_material(self, d: Dict[str, Any]) -> Dict[str, Any]:
        errs = []
        if self.is_empty_or_none(d.get('project_name')): errs.append("Project Name required")
        if self.is_empty_or_none(d.get('material_no')):  errs.append("Material Number required")
        if not self.is_positive_number(d.get('weight_per_pcs'), allow_zero=True):
            errs.append("Weight per pcs must be ≥ 0")
        if not self.is_positive_integer(d.get('annual_volume'), allow_zero=True):
            errs.append("Annual volume must be ≥ 0")
        if not self.is_positive_number(d.get('lifetime_years'), allow_zero=True):
            errs.append("Lifetime years must be ≥ 0")
        # allow optional material_value
        mv = d.get('material_value')
        if mv is not None and not self.is_positive_number(mv, allow_zero=True):
            errs.append("Material value must be ≥ 0")
        return {'is_valid': not errs, 'errors': errs}


class PackagingValidator(BaseValidator):
    def validate_packaging(self, d: Dict[str, Any]) -> Dict[str, Any]:
        errs = []
        if self.is_empty_or_none(d.get('material_id')): errs.append("material_id required")
        if self.is_empty_or_none(d.get('supplier_id')): errs.append("supplier_id required")
        if not self.is_positive_number(d.get('pack_maint'), allow_zero=True):
            errs.append("Packaging maintenance ≥ 0")
        if not self.is_positive_number(d.get('empties_scrap_cardboard'), allow_zero=True):
            errs.append("Empties scrap (cardboard) ≥ 0")
        if not self.is_positive_number(d.get('empties_scrap_wood'), allow_zero=True):
            errs.append("Empties scrap (wood) ≥ 0")
        if not self.is_positive_integer(d.get('fill_qty_box'), allow_zero=True):
            errs.append("Filling qty box ≥ 0")
        if not self.is_positive_integer(d.get('boxes_per_lu'), allow_zero=True):
            errs.append("Boxes per LU ≥ 0")
        if not self.is_positive_number(d.get('add_pack_price'), allow_zero=True):
            errs.append("Additional pack price ≥ 0")
        # sheet-extracted fields allowed 0
        for key in ['price_per_box', 'packaging_weight', 'tooling_cost',
                    'price_per_tray', 'price_sp_pallet', 'price_sp_cover',
                    'weight_sp_pallet']:
            val = d.get(key)
            if val is not None and not self.is_positive_number(val, allow_zero=True):
                errs.append(f"{key} must be ≥ 0")
        # loop_data dict
        ld = d.get('loop_data', {})
        if not isinstance(ld, dict):
            errs.append("loop_data must be a dict")
        else:
            for stage, qty in ld.items():
                if not self.is_positive_integer(qty, allow_zero=True):
                    errs.append(f"Loop {stage} quantity ≥ 0")
        return {'is_valid': not errs, 'errors': errs}


class CustomsValidator(BaseValidator):
    def validate_customs(self, d: Dict[str, Any]) -> Dict[str, Any]:
        errs = []
        if self.is_empty_or_none(d.get('pref_usage')): errs.append("pref_usage required")
        if not self.is_valid_percentage(d.get('duty_rate')):  errs.append("duty_rate 0–100%")
        if not self.is_valid_percentage(d.get('tariff_rate')): errs.append("tariff_rate 0–100%")
        return {'is_valid': not errs, 'errors': errs}


class TransportValidator(BaseValidator):
    def validate_transport(self, d: Dict[str, Any]) -> Dict[str, Any]:
        errs = []
        if self.is_empty_or_none(d.get('material_id')): errs.append("material_id required")
        if self.is_empty_or_none(d.get('supplier_id')): errs.append("supplier_id required")
        for key in ['cost_lu', 'cost_bonded', 'distance_km']:
            if not self.is_positive_number(d.get(key), allow_zero=True):
                errs.append(f"{key} must be ≥ 0")
        if not self.is_positive_integer(d.get('lu_capacity'), allow_zero=True):
            errs.append("lu_capacity must be ≥ 0")
        # optional surcharges
        for key in ['fuel_surcharge_rate', 'customs_handling', 'handling_cost', 'insurance_rate']:
            val = d.get(key)
            if val is not None and not self.is_positive_number(val, allow_zero=True):
                errs.append(f"{key} must be ≥ 0")
        # co2 factors
        if not self.is_positive_number(d.get('co2_emission_factor'), allow_zero=True):
            errs.append("co2_emission_factor must be ≥ 0")
        if not self.is_positive_number(d.get('co2_conversion_factor'), allow_zero=True):
            errs.append("co2_conversion_factor must be ≥ 0")
        return {'is_valid': not errs, 'errors': errs}


class WarehouseValidator(BaseValidator):
    def validate_warehouse(self, d: Dict[str, Any]) -> Dict[str, Any]:
        errs = []
        if self.is_empty_or_none(d.get('material_id')): errs.append("material_id required")
        if self.is_empty_or_none(d.get('supplier_id')): errs.append("supplier_id required")
        if not self.is_positive_number(d.get('cost_per_loc'), allow_zero=True):
            errs.append("cost_per_loc ≥ 0")
        # coverage_days, additional_locations, pieces_per_location
        for key in ['coverage_days', 'additional_locations', 'pieces_per_location']:
            val = d.get(key)
            if val is not None and not self.is_positive_number(val, allow_zero=True):
                errs.append(f"{key} must be ≥ 0")
        return {'is_valid': not errs, 'errors': errs}
