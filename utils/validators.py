"""
Validation utilities for Logistics Cost Application

This module contains validation classes for all input forms to ensure
data integrity and provide meaningful error messages to users.
"""

import re
from typing import Dict, List, Any

class BaseValidator:
    """Base validator class with common validation methods."""
    
    @staticmethod
    def is_empty_or_none(value) -> bool:
        """Check if value is None, empty string, or whitespace only."""
        if value is None:
            return True
        if isinstance(value, str):
            return len(value.strip()) == 0
        return False
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format."""
        if BaseValidator.is_empty_or_none(email):
            return True  # Email is optional in most cases
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email.strip()) is not None
    
    @staticmethod
    def is_positive_number(value, allow_zero: bool = False) -> bool:
        """Check if value is a positive number."""
        try:
            num = float(value)
            return num > 0 if not allow_zero else num >= 0
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def is_valid_percentage(value) -> bool:
        """Check if value is a valid percentage (0-100)."""
        try:
            num = float(value)
            return 0 <= num <= 100
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def is_positive_integer(value, allow_zero: bool = False) -> bool:
        """Check if value is a positive integer."""
        try:
            num = int(value)
            return num > 0 if not allow_zero else num >= 0
        except (TypeError, ValueError):
            return False


class MaterialValidator(BaseValidator):
    """Validator for material information - matching 1_Material_Information.py"""
    
    def validate_material(self, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate material data and return validation result.
        """
        errors = []
        
        # Required fields from 1_Material_Information.py
        project_name = material_data.get('project_name', '').strip()
        if self.is_empty_or_none(project_name):
            errors.append("Project Name is required")
        elif len(project_name) > 100:
            errors.append("Project Name must be 100 characters or less")
        
        material_no = material_data.get('material_no', '').strip()
        if self.is_empty_or_none(material_no):
            errors.append("Material Number is required")
        elif len(material_no) > 50:
            errors.append("Material Number must be 50 characters or less")
        
        material_desc = material_data.get('material_desc', '').strip()
        if self.is_empty_or_none(material_desc):
            errors.append("Material Description is required")
        elif len(material_desc) > 200:
            errors.append("Material Description must be 200 characters or less")
        
        weight_per_pcs = material_data.get('weight_per_pcs')
        if weight_per_pcs is None:
            errors.append("Weight per piece is required")
        elif not self.is_positive_number(weight_per_pcs):
            errors.append("Weight per piece must be a positive number")
        elif weight_per_pcs > 10000:
            errors.append("Weight per piece seems unreasonably high (max 10,000 kg)")
        
        annual_volume = material_data.get('annual_volume')
        if annual_volume is None:
            errors.append("Annual Volume is required")
        elif not self.is_positive_integer(annual_volume):
            errors.append("Annual Volume must be a positive integer")
        elif annual_volume > 100000000:
            errors.append("Annual Volume seems unreasonably high (max 100,000,000 pieces)")
        
        # Optional fields from 1_Material_Information.py
        usage = material_data.get('usage', '').strip()
        if usage and len(usage) > 200:
            errors.append("Usage must be 200 characters or less")
        
        daily_demand = material_data.get('daily_demand')
        if daily_demand is not None and not self.is_positive_number(daily_demand, allow_zero=True):
            errors.append("Daily demand must be a non-negative number")
        
        lifetime_volume = material_data.get('lifetime_volume')
        if lifetime_volume is not None and not self.is_positive_number(lifetime_volume, allow_zero=True):
            errors.append("Lifetime must be a non-negative number")
        
        peak_year = material_data.get('peak_year', '').strip()
        if peak_year and len(peak_year) > 20:
            errors.append("Peak year must be 20 characters or less")
        
        peak_year_volume = material_data.get('peak_year_volume')
        if peak_year_volume is not None and not self.is_positive_integer(peak_year_volume, allow_zero=True):
            errors.append("Peak year volume must be a non-negative integer")
        
        working_days = material_data.get('working_days')
        if working_days is not None:
            if not self.is_positive_integer(working_days, allow_zero=True):
                errors.append("Working days must be a non-negative integer")
            elif working_days > 365:
                errors.append("Working days cannot exceed 365")
        
        sop = material_data.get('sop', '').strip()
        if sop and len(sop) > 50:
            errors.append("SOP must be 50 characters or less")

        Pcs_Price = material_data.get('Pcs_Price')
        if Pcs_Price is not None and not self.is_positive_number(Pcs_Price, allow_zero=True):
            errors.append("Pcs_Price must be a non-negative number")        
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class SupplierValidator(BaseValidator):
    """Validator for supplier information - matching 2_Supplier_Information.py"""
    
    def validate_supplier(self, supplier_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate supplier data and return validation result.
        """
        errors = []
        
        # Required fields from 2_Supplier_Information.py
        vendor_id = supplier_data.get('vendor_id', '').strip()
        if self.is_empty_or_none(vendor_id):
            errors.append("Vendor ID is required")
        elif len(vendor_id) > 20:
            errors.append("Vendor ID must be 20 characters or less")
        
        vendor_name = supplier_data.get('vendor_name', '').strip()
        if self.is_empty_or_none(vendor_name):
            errors.append("Vendor Name is required")
        elif len(vendor_name) > 100:
            errors.append("Vendor Name must be 100 characters or less")
        
        vendor_country = supplier_data.get('vendor_country', '').strip()
        if self.is_empty_or_none(vendor_country):
            errors.append("Vendor Country is required")
        elif len(vendor_country) > 50:
            errors.append("Vendor Country must be 50 characters or less")
        
        city_of_manufacture = supplier_data.get('city_of_manufacture', '').strip()
        if self.is_empty_or_none(city_of_manufacture):
            errors.append("City of Manufacture is required")
        elif len(city_of_manufacture) > 50:
            errors.append("City of Manufacture must be 50 characters or less")
        
        vendor_zip = supplier_data.get('vendor_zip', '').strip()
        if self.is_empty_or_none(vendor_zip):
            errors.append("Vendor ZIP is required")
        elif len(vendor_zip) > 20:
            errors.append("Vendor ZIP must be 20 characters or less")
        
        delivery_performance = supplier_data.get('delivery_performance')
        if delivery_performance is None:
            errors.append("Delivery Performance is required")
        elif not self.is_valid_percentage(delivery_performance):
            errors.append("Delivery Performance must be between 0 and 100 percent")
        
        deliveries_per_month = supplier_data.get('deliveries_per_month')
        if deliveries_per_month is None:
            errors.append("Deliveries per Month is required")
        elif not self.is_positive_integer(deliveries_per_month, allow_zero=True):
            errors.append("Deliveries per Month must be a non-negative integer")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class LocationValidator(BaseValidator):
    """Validator for KB/Bendix location information - matching 3_KB_Bendix_Location_Info.py"""
    
    def validate_location(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate location data and return validation result.
        """
        errors = []
        
        plant = location_data.get('plant', '').strip()
        if self.is_empty_or_none(plant):
            errors.append("KB/Bendix Plant is required")
        elif len(plant) > 100:
            errors.append("KB/Bendix Plant must be 100 characters or less")
        
        country = location_data.get('country', '').strip()
        if self.is_empty_or_none(country):
            errors.append("KB/Bendix Country is required")
        elif len(country) > 50:
            errors.append("KB/Bendix Country must be 50 characters or less")
        
        distance = location_data.get('distance')
        if distance is None:
            errors.append("Distance is required")
        elif not self.is_positive_number(distance, allow_zero=True):
            errors.append("Distance must be a non-negative number")
        elif distance > 50000:
            errors.append("Distance seems unreasonably high (max 50,000 km)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class OperationsValidator(BaseValidator):
    """Validator for operations information - matching updated 4_Operations_Information.py"""
    
    def validate_operations(self, operations_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate operations data and return validation result.
        Updated to make certain fields optional based on requirements.
        """
        errors = []
        
        # Required fields
        incoterm_code = operations_data.get('incoterm_code', '').strip()
        if self.is_empty_or_none(incoterm_code):
            errors.append("Incoterm Code is required")
        
        incoterm_place = operations_data.get('incoterm_place', '').strip()
        if self.is_empty_or_none(incoterm_place):
            errors.append("Incoterm Named Place is required")
        elif len(incoterm_place) > 100:
            errors.append("Incoterm Named Place must be 100 characters or less")
        
        part_class = operations_data.get('part_class', '').strip()
        if self.is_empty_or_none(part_class):
            errors.append("Part Classification is required")
        
        calloff_type = operations_data.get('calloff_type', '').strip()
        if self.is_empty_or_none(calloff_type):
            errors.append("Call-off Transfer Type is required")
        
        # Directive is now OPTIONAL - no validation required
        directive = operations_data.get('directive', '').strip()
        # Only validate format if provided
        if directive and directive not in ['Yes', 'No']:
            errors.append("Logistics Directive must be Yes or No if provided")
        
        lead_time = operations_data.get('lead_time')
        if lead_time is None:
            errors.append("Lead Time is required")
        elif not self.is_positive_integer(lead_time, allow_zero=True):
            errors.append("Lead Time must be a non-negative integer")
        elif lead_time > 365:
            errors.append("Lead Time seems unreasonably high (max 365 days)")
        
        subsupplier_used = operations_data.get('subsupplier_used', '').strip()
        if self.is_empty_or_none(subsupplier_used):
            errors.append("Sub-supplier used field is required")
        elif subsupplier_used not in ['Yes', 'No']:
            errors.append("Sub-supplier used must be Yes or No")
        
        # Packaging Tool Ownership is now OPTIONAL - no validation required
        packaging_tool_owner = operations_data.get('packaging_tool_owner', '').strip()
        # Only validate format if provided
        if packaging_tool_owner and len(packaging_tool_owner) > 50:
            errors.append("Packaging Tool Ownership must be 50 characters or less")
        
        # Responsible is REQUIRED only if sub-supplier is used
        responsible = operations_data.get('responsible', '').strip()
        if subsupplier_used == 'Yes' and self.is_empty_or_none(responsible):
            errors.append("Responsible party is required when sub-supplier is used")
        # Validate format if provided
        elif responsible and len(responsible) > 50:
            errors.append("Responsible party must be 50 characters or less")
        
        # Currency is now OPTIONAL - no validation required
        currency = operations_data.get('currency', '').strip()
        # Only validate format if provided
        if currency and len(currency) > 3:
            errors.append("Currency code must be 3 characters or less")
        
        # Sub-supplier box days - only validate if sub-supplier is used
        subsupplier_box_days = operations_data.get('subsupplier_box_days')
        if subsupplier_used == 'Yes' and subsupplier_box_days is not None:
            if not self.is_positive_integer(subsupplier_box_days, allow_zero=True):
                errors.append("Sub-supplier box days must be a non-negative integer")
            elif subsupplier_box_days > 365:
                errors.append("Sub-supplier box days seems unreasonably high (max 365 days)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }

class PackagingValidator(BaseValidator):
    """Validator for packaging configuration - matching 6_Packaging_Cost.py"""
    
    def validate_packaging(self, packaging_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate packaging data and return validation result.
        """
        errors = []
        
        # 6.1 Per-part costs
        pack_maint = packaging_data.get('pack_maint')
        if pack_maint is not None and not self.is_positive_number(pack_maint, allow_zero=True):
            errors.append("Packaging maintenance must be a non-negative number")
        
        empties_scrap = packaging_data.get('empties_scrap')
        if empties_scrap is not None and not self.is_positive_number(empties_scrap, allow_zero=True):
            errors.append("Empties scrapping must be a non-negative number")
        
        # 6.2 Standard packaging
        box_type = packaging_data.get('box_type', '').strip()
        if self.is_empty_or_none(box_type):
            errors.append("Packaging Type (box) is required")
        
        fill_qty_box = packaging_data.get('fill_qty_box')
        if fill_qty_box is not None and not self.is_positive_integer(fill_qty_box, allow_zero=True):
            errors.append("Filling quantity per box must be a non-negative integer")
        
        pallet_type = packaging_data.get('pallet_type', '').strip()
        if self.is_empty_or_none(pallet_type):
            errors.append("LU Type (pallet) is required")
        
        fill_qty_lu_oversea = packaging_data.get('fill_qty_lu_oversea')
        if fill_qty_lu_oversea is not None and not self.is_positive_integer(fill_qty_lu_oversea, allow_zero=True):
            errors.append("Filling quantity per LU (overseas) must be a non-negative integer")
        
        add_pack_price = packaging_data.get('add_pack_price')
        if add_pack_price is not None and not self.is_positive_number(add_pack_price, allow_zero=True):
            errors.append("Additional packaging price must be a non-negative number")
        
        # 6.3 Special packaging
        sp_needed = packaging_data.get('sp_needed', '').strip()
        if self.is_empty_or_none(sp_needed):
            errors.append("Special packaging needed field is required")
        elif sp_needed not in ['Yes', 'No']:
            errors.append("Special packaging needed must be Yes or No")
        
        sp_type = packaging_data.get('sp_type', '').strip()
        if self.is_empty_or_none(sp_type):
            errors.append("Special packaging type is required")
        
        fill_qty_tray = packaging_data.get('fill_qty_tray')
        if fill_qty_tray is not None and not self.is_positive_integer(fill_qty_tray, allow_zero=True):
            errors.append("Filling quantity per tray must be a non-negative integer")
        
        tooling_cost = packaging_data.get('tooling_cost')
        if tooling_cost is not None and not self.is_positive_number(tooling_cost, allow_zero=True):
            errors.append("Tooling cost must be a non-negative number")
        
        add_sp_pack = packaging_data.get('add_sp_pack', '').strip()
        if self.is_empty_or_none(add_sp_pack):
            errors.append("Additional packaging needed field is required")
        elif add_sp_pack not in ['Yes', 'No']:
            errors.append("Additional packaging needed must be Yes or No")
        
        trays_per_sp_pal = packaging_data.get('trays_per_sp_pal')
        if trays_per_sp_pal is not None and not self.is_positive_integer(trays_per_sp_pal, allow_zero=True):
            errors.append("Trays per SP-pallet must be a non-negative integer")
        
        sp_pallets_per_lu = packaging_data.get('sp_pallets_per_lu')
        if sp_pallets_per_lu is not None and not self.is_positive_integer(sp_pallets_per_lu, allow_zero=True):
            errors.append("SP-pallets per LU must be a non-negative integer")
        
        # 6.4 Loop data validation
        loop_data = packaging_data.get('loop_data', {})
        if not isinstance(loop_data, dict):
            errors.append("Loop data must be a dictionary")
        else:
            for stage, qty in loop_data.items():
                if qty is not None and not self.is_positive_integer(qty, allow_zero=True):
                    errors.append(f"Loop quantity for {stage} must be a non-negative integer")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }

class RepackingValidator(BaseValidator):
    """Validator for repacking configuration - matching updated 7_Repacking_Cost.py"""

    def validate_repacking(self, repacking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate repacking data with fields:
          - pcs_weight
          - packaging_one_way
          - packaging_returnable
        Return validation result.
        """
        errors = []

        # Allowed options must match those in the Streamlit page:
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

        # pcs_weight
        pcs_weight = repacking_data.get('pcs_weight')
        if not pcs_weight or pcs_weight not in weight_options:
            errors.append(
                "Weight (pcs_weight) is required and must be one of: "
                + ", ".join(weight_options)
            )

        # packaging_one_way
        packaging_one_way = repacking_data.get('packaging_one_way')
        if not packaging_one_way or packaging_one_way not in packaging_one_way_options:
            errors.append(
                "Packaging one-way (supplier) is required and must be one of: "
                + ", ".join(packaging_one_way_options)
            )

        # packaging_returnable
        packaging_returnable = repacking_data.get('packaging_returnable')
        if not packaging_returnable or packaging_returnable not in packaging_returnable_options:
            errors.append(
                "Packaging returnable (KB) is required and must be one of: "
                + ", ".join(packaging_returnable_options)
            )

        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class CustomsValidator(BaseValidator):
    """Validator for customs configuration - matching 8_Customs_Cost.py"""
    def validate_customs(self, customs_data: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        pref_usage = customs_data.get('pref_usage', '').strip()
        if not pref_usage:
            errors.append("Customs Preference Usage is required")
        elif pref_usage not in ['Yes', 'No']:
            errors.append("Customs Preference Usage must be Yes or No")

        # Duty rate only required when preference not used
        if pref_usage == 'No':
            duty_rate = customs_data.get('duty_rate')
            if duty_rate is None:
                errors.append("Duty Rate is required when no preference is used")
            elif not self.is_valid_percentage(duty_rate):
                errors.append("Duty Rate must be between 0 and 100 percent")
        return {'is_valid': len(errors) == 0, 'errors': errors}


class TransportValidator(BaseValidator):
    """Validator for transport configuration - matching 9_Transport_Cost.py"""
    
    def validate_transport(self, transport_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate transport data and return validation result.
        """
        errors = []
        
        # Validation for 9_Transport_Cost.py
        mode1 = transport_data.get('mode1', '').strip()
        if self.is_empty_or_none(mode1):
            errors.append("Transportation Mode I is required")
        
        cost_lu = transport_data.get('cost_lu')
        if cost_lu is None:
            errors.append("Transportation Cost per LU is required")
        elif not self.is_positive_number(cost_lu, allow_zero=True):
            errors.append("Transportation Cost per LU must be a non-negative number")
        
        stack_factor = transport_data.get('stack_factor', '').strip()
        if self.is_empty_or_none(stack_factor):
            errors.append("Stackability Factor is required")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class CO2Validator(BaseValidator):
    """Validator for CO2 configuration - matching 10_Annual_CO2_Cost.py"""
    
    def validate_co2(self, co2_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate CO2 data and return validation result.
        """
        errors = []
        
        cost_per_ton = co2_data.get('cost_per_ton')
        if cost_per_ton is None:
            errors.append("CO₂ Cost per Ton is required")
        elif not self.is_positive_number(cost_per_ton, allow_zero=True):
            errors.append("CO₂ Cost per Ton must be a non-negative number")
        elif cost_per_ton > 1000:
            errors.append("CO₂ Cost per Ton seems unreasonably high (max €1,000/ton)")
        
        co2_conversion_factor = co2_data.get('co2_conversion_factor', '').strip()
        if self.is_empty_or_none(co2_conversion_factor):
            errors.append("CO₂ Conversion Factor is required")
        elif co2_conversion_factor not in ["2.65", "3.17", "3.31"]:
            errors.append("CO₂ Conversion Factor must be one of: 2.65, 3.17, 3.31")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class WarehouseValidator(BaseValidator):
    """Validator for warehouse configuration - matching 11_Warehouse_Cost.py"""
    
    def validate_warehouse(self, warehouse_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate warehouse data and return validation result.
        """
        errors = []
        
        cost_per_loc = warehouse_data.get('cost_per_loc')
        if cost_per_loc is None:
            errors.append("Cost per Storage Location is required")
        elif not self.is_positive_number(cost_per_loc, allow_zero=True):
            errors.append("Cost per Storage Location must be a non-negative number")
        elif cost_per_loc > 10000:
            errors.append("Cost per Storage Location seems unreasonably high (max €10,000/month)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class InterestValidator(BaseValidator):
    """Validator for inventory interest configuration - matching 12_Inventory_Cost.py"""
    
    def validate_interest(self, interest_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate interest data and return validation result.
        """
        errors = []
        
        rate = interest_data.get('rate')
        if rate is None:
            errors.append("Inventory Interest Rate is required")
        elif not self.is_valid_percentage(rate):
            errors.append("Inventory Interest Rate must be between 0 and 100 percent")
        elif rate > 50:
            errors.append("Inventory Interest Rate seems unreasonably high (max 50%)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class AdditionalCostValidator(BaseValidator):
    """Validator for additional cost items - matching 14_Additional_Cost.py"""
    
    def validate_additional_cost(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate additional cost data and return validation result.
        """
        errors = []
        
        cost_name = cost_data.get('cost_name', '').strip()
        if self.is_empty_or_none(cost_name):
            errors.append("Cost Name is required")
        elif len(cost_name) > 100:
            errors.append("Cost Name must be 100 characters or less")
        
        cost_value = cost_data.get('cost_value')
        if cost_value is None:
            errors.append("Cost Value is required")
        elif not self.is_positive_number(cost_value, allow_zero=True):
            errors.append("Cost Value must be a non-negative number")
        elif cost_value > 1000000:
            errors.append("Cost Value seems unreasonably high (max €1,000,000)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class CalculationValidator(BaseValidator):
    """Validator for calculation parameters and results."""
    
    def validate_calculation_inputs(self, materials: List[Dict], suppliers: List[Dict], 
                                  packaging_configs: List[Dict], transport_configs: List[Dict],
                                  warehouse_configs: List[Dict], co2_configs: List[Dict],
                                  operations_configs: List[Dict] = None,
                                  location_configs: List[Dict] = None,
                                  repacking_configs: List[Dict] = None,
                                  customs_configs: List[Dict] = None,
                                  interest_configs: List[Dict] = None,
                                  additional_costs: List[Dict] = None):
        """
        Validate that all required data is present for calculations.
        
        Returns:
            Dictionary with 'is_valid' boolean, 'errors' list, and 'warnings' list
        """
        errors = []
        warnings = []
        
        # Check if basic data exists
        if not materials:
            errors.append("No materials configured - at least one material is required")
        
        if not suppliers:
            errors.append("No suppliers configured - at least one supplier is required")
        
        if not packaging_configs:
            errors.append("No packaging configurations - at least one packaging configuration is required")
        
        if not transport_configs:
            errors.append("No transport configurations - at least one transport configuration is required")
        
        if not warehouse_configs:
            errors.append("No warehouse configurations - at least one warehouse configuration is required")
        
        if not co2_configs:
            errors.append("No CO₂ configurations - at least one CO₂ configuration is required")
        
        # Check optional configurations and provide warnings
        if not operations_configs:
            warnings.append("No operations configurations found - default values will be used")
        
        if not location_configs:
            warnings.append("No location configurations found - distance calculations may be affected")
        
        if not repacking_configs:
            warnings.append("No repacking configurations found - repacking costs will be zero")
        
        if not customs_configs:
            warnings.append("No customs configurations found - customs costs will be zero")
        
        if not interest_configs:
            warnings.append("No interest configurations found - inventory carrying costs may be incomplete")
        
        if not additional_costs:
            warnings.append("No additional costs configured")
        
        # Check for complete material-supplier pairs
        if materials and suppliers:
            complete_configs = 0
            for material in materials:
                for supplier in suppliers:
                    # A complete config needs at least material, supplier, packaging, transport, warehouse
                    material_id = material.get('material_no')
                    supplier_id = supplier.get('vendor_id')
                    
                    # Since configs are now simpler (not tied to specific pairs), just count pairs
                    complete_configs += 1
            
            if complete_configs == 0:
                errors.append("No valid material-supplier combinations found")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'complete_configurations': complete_configs if 'complete_configs' in locals() else 0
        }