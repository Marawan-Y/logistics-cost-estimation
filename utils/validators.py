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
        
        lifetime_years = material_data.get('lifetime_years')
        if lifetime_years is not None and not self.is_positive_number(lifetime_years, allow_zero=True):
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
        
        # Add material_value for calculations (not in form but needed)
        material_value = material_data.get('material_value')
        if material_value is not None:
            if not self.is_positive_number(material_value, allow_zero=True):
                errors.append("Material Value must be a non-negative number")
            elif material_value > 1000000:
                errors.append("Material Value seems unreasonably high (max €1,000,000 per piece)")
        
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
    """Validator for operations information - matching 4_Operations_Information.py"""
    
    def validate_operations(self, operations_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate operations data and return validation result.
        """
        errors = []
        
        # Required fields from 4_Operations_Information.py
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
        
        directive = operations_data.get('directive', '').strip()
        if self.is_empty_or_none(directive):
            errors.append("Logistics Directive version is required")
        
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
        
        packaging_tool_owner = operations_data.get('packaging_tool_owner', '').strip()
        if self.is_empty_or_none(packaging_tool_owner):
            errors.append("Packaging Tool Ownership is required")
        
        responsible = operations_data.get('responsible', '').strip()
        if self.is_empty_or_none(responsible):
            errors.append("Responsible party is required")
        
        currency = operations_data.get('currency', '').strip()
        if self.is_empty_or_none(currency):
            errors.append("Currency is required")
        elif len(currency) > 3:
            errors.append("Currency code must be 3 characters or less")
        
        # Optional field
        subsupplier_box_days = operations_data.get('subsupplier_box_days')
        if subsupplier_box_days is not None and not self.is_positive_integer(subsupplier_box_days, allow_zero=True):
            errors.append("Sub-supplier box days must be a non-negative integer")
        
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
        
        fill_qty_lu = packaging_data.get('fill_qty_lu')
        if fill_qty_lu is not None and not self.is_positive_integer(fill_qty_lu, allow_zero=True):
            errors.append("Filling quantity per LU must be a non-negative integer")
        
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
        
        # Note: material_id and supplier_id are added by the form when used with transport
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class RepackingValidator(BaseValidator):
    """Validator for repacking configuration - matching 7_Repacking_Cost.py"""
    
    def validate_repacking(self, repacking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate repacking data and return validation result.
        """
        errors = []
        
        rep_cost_hr = repacking_data.get('rep_cost_hr')
        if rep_cost_hr is not None and not self.is_positive_number(rep_cost_hr, allow_zero=True):
            errors.append("Repacking cost per hour must be a non-negative number")
        
        goods_type = repacking_data.get('goods_type', '').strip()
        if self.is_empty_or_none(goods_type):
            errors.append("Type of goods is required")
        
        rep_cost_lu = repacking_data.get('rep_cost_lu')
        if rep_cost_lu is not None and not self.is_positive_number(rep_cost_lu, allow_zero=True):
            errors.append("Repacking cost per LU must be a non-negative number")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class CustomsValidator(BaseValidator):
    """Validator for customs configuration - matching 8_Customs_Cost.py"""
    
    def validate_customs(self, customs_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate customs data and return validation result.
        """
        errors = []
        
        pref_usage = customs_data.get('pref_usage', '').strip()
        if self.is_empty_or_none(pref_usage):
            errors.append("Customs Preference Usage is required")
        elif pref_usage not in ['Yes', 'No']:
            errors.append("Customs Preference Usage must be Yes or No")
        
        hs_code = customs_data.get('hs_code', '').strip()
        if self.is_empty_or_none(hs_code):
            errors.append("HS Code is required")
        elif len(hs_code) > 20:
            errors.append("HS Code must be 20 characters or less")
        
        duty_rate = customs_data.get('duty_rate')
        if duty_rate is None:
            errors.append("Duty Rate is required")
        elif not self.is_valid_percentage(duty_rate):
            errors.append("Duty Rate must be between 0 and 100 percent")
        
        tariff_rate = customs_data.get('tariff_rate')
        if tariff_rate is None:
            errors.append("Tariff Rate is required")
        elif not self.is_valid_percentage(tariff_rate):
            errors.append("Tariff Rate must be between 0 and 100 percent")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class TransportValidator(BaseValidator):
    """Validator for transport configuration - matching 4_Transport_Cost.py and 9_Transport_Cost.py"""
    
    def validate_transport(self, transport_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate transport data and return validation result.
        """
        errors = []
        
        # Check if this is from 4_Transport_Cost.py (has material_id/supplier_id)
        # or from 9_Transport_Cost.py (has mode1/mode2)
        is_material_transport = 'material_id' in transport_data
        
        if is_material_transport:
            # Validation for 4_Transport_Cost.py
            material_id = transport_data.get('material_id', '').strip()
            if self.is_empty_or_none(material_id):
                errors.append("Material is required")
            
            supplier_id = transport_data.get('supplier_id', '').strip()
            if self.is_empty_or_none(supplier_id):
                errors.append("Supplier is required")
            
            transport_mode = transport_data.get('transport_mode', '').strip()
            if self.is_empty_or_none(transport_mode):
                errors.append("Transport Mode is required")
            
            load_unit_type = transport_data.get('load_unit_type', '').strip()
            if self.is_empty_or_none(load_unit_type):
                errors.append("Load Unit Type is required")
            
            distance_km = transport_data.get('distance_km')
            if distance_km is None:
                errors.append("Distance is required")
            elif not self.is_positive_number(distance_km, allow_zero=True):
                errors.append("Distance must be a non-negative number")
            elif distance_km > 50000:
                errors.append("Distance seems unreasonably high (max 50,000 km)")
            
            transport_cost_per_lu = transport_data.get('transport_cost_per_lu')
            if transport_cost_per_lu is None:
                errors.append("Transport Cost per Load Unit is required")
            elif not self.is_positive_number(transport_cost_per_lu, allow_zero=True):
                errors.append("Transport Cost per Load Unit must be a non-negative number")
            
            lu_capacity = transport_data.get('lu_capacity')
            if lu_capacity is None:
                errors.append("Load Unit Capacity is required")
            elif not self.is_positive_integer(lu_capacity):
                errors.append("Load Unit Capacity must be a positive integer")
            
            # Optional fields for 4_Transport_Cost.py
            transit_time_days = transport_data.get('transit_time_days')
            if transit_time_days is not None and not self.is_positive_number(transit_time_days, allow_zero=True):
                errors.append("Transit Time must be a non-negative number")
            
            co2_emission_factor = transport_data.get('co2_emission_factor')
            if co2_emission_factor is not None and not self.is_positive_number(co2_emission_factor, allow_zero=True):
                errors.append("CO₂ Emission Factor must be a non-negative number")
            
            co2_cost_per_ton = transport_data.get('co2_cost_per_ton')
            if co2_cost_per_ton is not None and not self.is_positive_number(co2_cost_per_ton, allow_zero=True):
                errors.append("CO₂ Cost per Ton must be a non-negative number")
            
            fuel_surcharge_rate = transport_data.get('fuel_surcharge_rate')
            if fuel_surcharge_rate is not None and not self.is_valid_percentage(fuel_surcharge_rate):
                errors.append("Fuel Surcharge Rate must be between 0 and 100 percent")
            
            customs_handling = transport_data.get('customs_handling')
            if customs_handling is not None and not self.is_positive_number(customs_handling, allow_zero=True):
                errors.append("Customs Handling Cost must be a non-negative number")
            
            insurance_rate = transport_data.get('insurance_rate')
            if insurance_rate is not None and not self.is_valid_percentage(insurance_rate):
                errors.append("Insurance Rate must be between 0 and 100 percent")
            
            handling_cost = transport_data.get('handling_cost')
            if handling_cost is not None and not self.is_positive_number(handling_cost, allow_zero=True):
                errors.append("Handling Cost must be a non-negative number")
            
            frequency_per_week = transport_data.get('frequency_per_week')
            if frequency_per_week is not None and not self.is_positive_number(frequency_per_week):
                errors.append("Frequency must be a positive number")
            
            min_shipment_size = transport_data.get('min_shipment_size')
            if min_shipment_size is not None and not self.is_positive_integer(min_shipment_size):
                errors.append("Minimum Shipment Size must be a positive integer")
            
        else:
            # Validation for 9_Transport_Cost.py
            mode1 = transport_data.get('mode1', '').strip()
            if self.is_empty_or_none(mode1):
                errors.append("Transportation Mode I is required")
            
            mode2 = transport_data.get('mode2', '').strip()
            if self.is_empty_or_none(mode2):
                errors.append("Transportation Mode II is required")
            
            cost_lu = transport_data.get('cost_lu')
            if cost_lu is None:
                errors.append("Transportation Cost per LU is required")
            elif not self.is_positive_number(cost_lu, allow_zero=True):
                errors.append("Transportation Cost per LU must be a non-negative number")
            
            cost_bonded = transport_data.get('cost_bonded')
            if cost_bonded is None:
                errors.append("Transportation Cost (Bonded Warehouse) per LU is required")
            elif not self.is_positive_number(cost_bonded, allow_zero=True):
                errors.append("Transportation Cost (Bonded) per LU must be a non-negative number")
            
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
                                  transport_configs: List[Dict], warehouse_configs: List[Dict],
                                  packaging_configs: List[Dict] = None) -> Dict[str, Any]:
        """
        Validate that all required data is present for calculations.
        
        Args:
            materials: List of material configurations
            suppliers: List of supplier configurations
            transport_configs: List of transport configurations  
            warehouse_configs: List of warehouse configurations
            packaging_configs: List of packaging configurations (optional)
            
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
        
        if not transport_configs:
            errors.append("No transport configurations - at least one transport configuration is required")
        
        if not warehouse_configs:
            errors.append("No warehouse configurations - at least one warehouse configuration is required")
        
        # If basic data exists, check for complete configurations
        if materials and suppliers and transport_configs:
            complete_configs = 0
            incomplete_pairs = []
            
            # Check transport configurations (from 4_Transport_Cost.py)
            for transport in transport_configs:
                # Skip if this is from 9_Transport_Cost.py (has mode1/mode2 instead)
                if 'mode1' in transport:
                    continue
                    
                material_id = transport.get('material_id')
                supplier_id = transport.get('supplier_id')
                
                material_exists = any(m['material_no'] == material_id for m in materials)
                supplier_exists = any(s['vendor_id'] == supplier_id for s in suppliers)
                
                if material_exists and supplier_exists:
                    complete_configs += 1
                else:
                    missing = []
                    if not material_exists:
                        missing.append(f"material {material_id}")
                    if not supplier_exists:
                        missing.append(f"supplier {supplier_id}")
                    
                    incomplete_pairs.append(f"Transport config missing: {', '.join(missing)}")
            
            if complete_configs == 0:
                errors.append("No complete transport configurations found")
                if incomplete_pairs:
                    errors.extend(incomplete_pairs[:5])
                    if len(incomplete_pairs) > 5:
                        errors.append(f"... and {len(incomplete_pairs) - 5} more incomplete configurations")
            else:
                if incomplete_pairs:
                    warnings.append(f"Found {complete_configs} complete transport configurations")
                    warnings.append(f"{len(incomplete_pairs)} incomplete configurations will be skipped")
        
        # Check for material value in materials (needed for some calculations)
        if materials:
            materials_without_value = []
            for m in materials:
                if not m.get('material_value'):
                    # Check if there's a price/value field we might have missed
                    if not any(key in m for key in ['material_value', 'price', 'value', 'cost']):
                        materials_without_value.append(m['material_no'])
            
            if materials_without_value:
                warnings.append(f"Materials without value: {', '.join(materials_without_value[:5])}")
                if len(materials_without_value) > 5:
                    warnings.append(f"... and {len(materials_without_value) - 5} more")
                warnings.append("Some cost calculations (customs, insurance) may be incomplete without material values")
        
        # Check if packaging configurations exist (optional but recommended)
        if not packaging_configs:
            warnings.append("No packaging configurations found - default packaging costs will be used")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'complete_configurations': complete_configs if 'complete_configs' in locals() else 0
        }