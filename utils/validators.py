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
    """Validator for material information."""
    
    def validate_material(self, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate material data and return validation result.
        
        Args:
            material_data: Dictionary containing material information
            
        Returns:
            Dictionary with 'is_valid' boolean and 'errors' list
        """
        errors = []
        
        # Required field validations
        material_no = material_data.get('material_no', '').strip()
        if self.is_empty_or_none(material_no):
            errors.append("Material Number is required")
        elif len(material_no) > 50:
            errors.append("Material Number must be 50 characters or less")
        elif not re.match(r'^[A-Za-z0-9\-_]+$', material_no):
            errors.append("Material Number can only contain letters, numbers, hyphens, and underscores")
        
        material_desc = material_data.get('material_desc', '').strip()
        if self.is_empty_or_none(material_desc):
            errors.append("Material Description is required")
        elif len(material_desc) > 200:
            errors.append("Material Description must be 200 characters or less")
        
        # Weight validation
        weight_per_pcs = material_data.get('weight_per_pcs')
        if weight_per_pcs is None:
            errors.append("Weight per piece is required")
        elif not self.is_positive_number(weight_per_pcs):
            errors.append("Weight per piece must be a positive number")
        elif weight_per_pcs > 10000:  # 10 tons seems reasonable as max
            errors.append("Weight per piece seems unreasonably high (max 10,000 kg)")
        
        # Annual volume validation
        annual_volume = material_data.get('annual_volume')
        if annual_volume is None:
            errors.append("Annual Volume is required")
        elif not self.is_positive_integer(annual_volume):
            errors.append("Annual Volume must be a positive integer")
        elif annual_volume > 100000000:  # 100M pieces seems like a reasonable max
            errors.append("Annual Volume seems unreasonably high (max 100,000,000 pieces)")
        
        # Optional field validations
        lifetime_volume = material_data.get('lifetime_volume')
        if lifetime_volume is not None:
            if not self.is_positive_integer(lifetime_volume, allow_zero=True):
                errors.append("Lifetime Volume must be a non-negative integer")
            elif annual_volume and lifetime_volume > 0 and lifetime_volume < annual_volume:
                errors.append("Lifetime Volume should not be less than Annual Volume")
        
        sop_year = material_data.get('sop_year')
        if sop_year is not None:
            if not isinstance(sop_year, int) or sop_year < 2020 or sop_year > 2050:
                errors.append("SOP Year must be between 2020 and 2050")
        
        material_value = material_data.get('material_value')
        if material_value is not None:
            if not self.is_positive_number(material_value, allow_zero=True):
                errors.append("Material Value must be a non-negative number")
            elif material_value > 1000000:  # 1M EUR per piece seems high
                errors.append("Material Value seems unreasonably high (max €1,000,000 per piece)")
        
        hs_code = material_data.get('hs_code', '').strip()
        if hs_code and not re.match(r'^\d{4,10}$', hs_code):
            errors.append("HS Code must be 4-10 digits")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class SupplierValidator(BaseValidator):
    """Validator for supplier information."""
    
    def validate_supplier(self, supplier_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate supplier data and return validation result.
        
        Args:
            supplier_data: Dictionary containing supplier information
            
        Returns:
            Dictionary with 'is_valid' boolean and 'errors' list
        """
        errors = []
        
        # Required field validations
        vendor_id = supplier_data.get('vendor_id', '').strip()
        if self.is_empty_or_none(vendor_id):
            errors.append("Vendor ID is required")
        elif len(vendor_id) > 20:
            errors.append("Vendor ID must be 20 characters or less")
        elif not re.match(r'^[A-Za-z0-9\-_]+$', vendor_id):
            errors.append("Vendor ID can only contain letters, numbers, hyphens, and underscores")
        
        vendor_name = supplier_data.get('vendor_name', '').strip()
        if self.is_empty_or_none(vendor_name):
            errors.append("Vendor Name is required")
        elif len(vendor_name) > 100:
            errors.append("Vendor Name must be 100 characters or less")
        
        vendor_country = supplier_data.get('vendor_country', '').strip()
        if self.is_empty_or_none(vendor_country):
            errors.append("Vendor Country is required")
        elif len(vendor_country) > 10:
            errors.append("Vendor Country code must be 10 characters or less")
        
        city_manufacture = supplier_data.get('city_manufacture', '').strip()
        if self.is_empty_or_none(city_manufacture):
            errors.append("City of Manufacture is required")
        elif len(city_manufacture) > 50:
            errors.append("City of Manufacture must be 50 characters or less")
        
        incoterm = supplier_data.get('incoterm', '').strip()
        if self.is_empty_or_none(incoterm):
            errors.append("Incoterm is required")
        
        # Optional field validations
        vendor_zip = supplier_data.get('vendor_zip', '').strip()
        if vendor_zip and not re.match(r'^[A-Za-z0-9\-\s]{3,20}$', vendor_zip):
            errors.append("ZIP Code format is invalid (3-20 characters, letters, numbers, hyphens, spaces)")
        
        contact_email = supplier_data.get('contact_email', '').strip()
        if contact_email and not self.is_valid_email(contact_email):
            errors.append("Contact Email format is invalid")
        
        lead_time_days = supplier_data.get('lead_time_days')
        if lead_time_days is not None:
            if not self.is_positive_integer(lead_time_days, allow_zero=True):
                errors.append("Lead Time must be a non-negative integer")
            elif lead_time_days > 365:
                errors.append("Lead Time seems unreasonably high (max 365 days)")
        
        min_order_qty = supplier_data.get('min_order_qty')
        if min_order_qty is not None:
            if not self.is_positive_integer(min_order_qty, allow_zero=True):
                errors.append("Minimum Order Quantity must be a non-negative integer")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class PackagingValidator(BaseValidator):
    """Validator for packaging configuration."""
    
    def validate_packaging(self, packaging_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate packaging data and return validation result.
        
        Args:
            packaging_data: Dictionary containing packaging information
            
        Returns:
            Dictionary with 'is_valid' boolean and 'errors' list
        """
        errors = []
        
        # Required field validations
        material_id = packaging_data.get('material_id', '').strip()
        if self.is_empty_or_none(material_id):
            errors.append("Material ID is required")
        
        supplier_id = packaging_data.get('supplier_id', '').strip()
        if self.is_empty_or_none(supplier_id):
            errors.append("Supplier ID is required")
        
        packaging_type = packaging_data.get('packaging_type', '').strip()
        if self.is_empty_or_none(packaging_type):
            errors.append("Packaging Type is required")
        
        filling_degree = packaging_data.get('filling_degree')
        if filling_degree is None:
            errors.append("Filling Degree is required")
        elif not self.is_positive_integer(filling_degree):
            errors.append("Filling Degree must be a positive integer")
        elif filling_degree > 100000:
            errors.append("Filling Degree seems unreasonably high (max 100,000 pieces)")
        
        packaging_cost_per_part = packaging_data.get('packaging_cost_per_part')
        if packaging_cost_per_part is None:
            errors.append("Packaging Cost per Part is required")
        elif not self.is_positive_number(packaging_cost_per_part, allow_zero=True):
            errors.append("Packaging Cost per Part must be a non-negative number")
        elif packaging_cost_per_part > 1000:
            errors.append("Packaging Cost per Part seems unreasonably high (max €1,000)")
        
        # Optional field validations
        tooling_cost = packaging_data.get('tooling_cost')
        if tooling_cost is not None:
            if not self.is_positive_number(tooling_cost, allow_zero=True):
                errors.append("Tooling Cost must be a non-negative number")
            elif tooling_cost > 10000000:  # 10M EUR seems high for tooling
                errors.append("Tooling Cost seems unreasonably high (max €10,000,000)")
        
        loop_time_days = packaging_data.get('loop_time_days')
        if loop_time_days is not None:
            if not self.is_positive_integer(loop_time_days):
                errors.append("Loop Time must be a positive integer")
            elif loop_time_days > 365:
                errors.append("Loop Time seems unreasonably high (max 365 days)")
        
        scrap_rate = packaging_data.get('scrap_rate')
        if scrap_rate is not None:
            if not self.is_valid_percentage(scrap_rate):
                errors.append("Scrap Rate must be between 0 and 100 percent")
        
        # Validate optional cost fields
        cost_fields = ['plant_cost', 'coc_cost', 'maintenance_cost', 'return_cost']
        for field in cost_fields:
            value = packaging_data.get(field)
            if value is not None:
                if not self.is_positive_number(value, allow_zero=True):
                    errors.append(f"{field.replace('_', ' ').title()} must be a non-negative number")
                elif value > 1000000:
                    errors.append(f"{field.replace('_', ' ').title()} seems unreasonably high (max €1,000,000)")
        
        packaging_weight = packaging_data.get('packaging_weight')
        if packaging_weight is not None:
            if not self.is_positive_number(packaging_weight, allow_zero=True):
                errors.append("Packaging Weight must be a non-negative number")
            elif packaging_weight > 1000:
                errors.append("Packaging Weight seems unreasonably high (max 1,000 kg)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class TransportValidator(BaseValidator):
    """Validator for transport configuration."""
    
    def validate_transport(self, transport_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate transport data and return validation result.
        
        Args:
            transport_data: Dictionary containing transport information
            
        Returns:
            Dictionary with 'is_valid' boolean and 'errors' list
        """
        errors = []
        
        # Required field validations
        material_id = transport_data.get('material_id', '').strip()
        if self.is_empty_or_none(material_id):
            errors.append("Material ID is required")
        
        supplier_id = transport_data.get('supplier_id', '').strip()
        if self.is_empty_or_none(supplier_id):
            errors.append("Supplier ID is required")
        
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
        elif distance_km > 50000:  # 50,000 km seems like reasonable max (around world circumference)
            errors.append("Distance seems unreasonably high (max 50,000 km)")
        
        transport_cost_per_lu = transport_data.get('transport_cost_per_lu')
        if transport_cost_per_lu is None:
            errors.append("Transport Cost per Load Unit is required")
        elif not self.is_positive_number(transport_cost_per_lu, allow_zero=True):
            errors.append("Transport Cost per Load Unit must be a non-negative number")
        elif transport_cost_per_lu > 100000:
            errors.append("Transport Cost per Load Unit seems unreasonably high (max €100,000)")
        
        lu_capacity = transport_data.get('lu_capacity')
        if lu_capacity is None:
            errors.append("Load Unit Capacity is required")
        elif not self.is_positive_integer(lu_capacity):
            errors.append("Load Unit Capacity must be a positive integer")
        elif lu_capacity > 1000000:
            errors.append("Load Unit Capacity seems unreasonably high (max 1,000,000 pieces)")
        
        # Optional field validations
        transit_time_days = transport_data.get('transit_time_days')
        if transit_time_days is not None:
            if not self.is_positive_number(transit_time_days, allow_zero=True):
                errors.append("Transit Time must be a non-negative number")
            elif transit_time_days > 365:
                errors.append("Transit Time seems unreasonably high (max 365 days)")
        
        co2_emission_factor = transport_data.get('co2_emission_factor')
        if co2_emission_factor is not None:
            if not self.is_positive_number(co2_emission_factor, allow_zero=True):
                errors.append("CO₂ Emission Factor must be a non-negative number")
            elif co2_emission_factor > 10:  # kg CO2/ton-km, seems reasonable max
                errors.append("CO₂ Emission Factor seems unreasonably high (max 10 kg CO₂/ton-km)")
        
        co2_cost_per_ton = transport_data.get('co2_cost_per_ton')
        if co2_cost_per_ton is not None:
            if not self.is_positive_number(co2_cost_per_ton, allow_zero=True):
                errors.append("CO₂ Cost per Ton must be a non-negative number")
            elif co2_cost_per_ton > 1000:  # EUR per ton CO2
                errors.append("CO₂ Cost per Ton seems unreasonably high (max €1,000/ton)")
        
        # Validate percentage fields
        percentage_fields = ['fuel_surcharge_rate', 'insurance_rate']
        for field in percentage_fields:
            value = transport_data.get(field)
            if value is not None:
                if not self.is_valid_percentage(value):
                    errors.append(f"{field.replace('_', ' ').title()} must be between 0 and 100 percent")
        
        # Validate cost fields
        cost_fields = ['customs_handling', 'handling_cost']
        for field in cost_fields:
            value = transport_data.get(field)
            if value is not None:
                if not self.is_positive_number(value, allow_zero=True):
                    errors.append(f"{field.replace('_', ' ').title()} must be a non-negative number")
                elif value > 100000:
                    errors.append(f"{field.replace('_', ' ').title()} seems unreasonably high (max €100,000)")
        
        frequency_per_week = transport_data.get('frequency_per_week')
        if frequency_per_week is not None:
            if not self.is_positive_number(frequency_per_week, allow_zero=True):
                errors.append("Frequency per Week must be a non-negative number")
            elif frequency_per_week > 50:  # More than daily seems unreasonable
                errors.append("Frequency per Week seems unreasonably high (max 50 shipments/week)")
        
        min_shipment_size = transport_data.get('min_shipment_size')
        if min_shipment_size is not None:
            if not self.is_positive_integer(min_shipment_size, allow_zero=True):
                errors.append("Minimum Shipment Size must be a non-negative integer")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class WarehouseValidator(BaseValidator):
    """Validator for warehouse configuration."""
    
    def validate_warehouse(self, warehouse_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate warehouse data and return validation result.
        
        Args:
            warehouse_data: Dictionary containing warehouse information
            
        Returns:
            Dictionary with 'is_valid' boolean and 'errors' list
        """
        errors = []
        
        # Required field validations
        material_id = warehouse_data.get('material_id', '').strip()
        if self.is_empty_or_none(material_id):
            errors.append("Material ID is required")
        
        supplier_id = warehouse_data.get('supplier_id', '').strip()
        if self.is_empty_or_none(supplier_id):
            errors.append("Supplier ID is required")
        
        storage_type = warehouse_data.get('storage_type', '').strip()
        if self.is_empty_or_none(storage_type):
            errors.append("Storage Type is required")
        
        storage_locations = warehouse_data.get('storage_locations')
        if storage_locations is None:
            errors.append("Number of Storage Locations is required")
        elif not self.is_positive_integer(storage_locations):
            errors.append("Number of Storage Locations must be a positive integer")
        elif storage_locations > 10000:
            errors.append("Number of Storage Locations seems unreasonably high (max 10,000)")
        
        safety_stock_pallets = warehouse_data.get('safety_stock_pallets')
        if safety_stock_pallets is None:
            errors.append("Safety Stock is required")
        elif not self.is_positive_integer(safety_stock_pallets, allow_zero=True):
            errors.append("Safety Stock must be a non-negative integer")
        elif safety_stock_pallets > 100000:
            errors.append("Safety Stock seems unreasonably high (max 100,000 pallets)")
        
        warehouse_cost_per_piece = warehouse_data.get('warehouse_cost_per_piece')
        if warehouse_cost_per_piece is None:
            errors.append("Warehouse Cost per Piece is required")
        elif not self.is_positive_number(warehouse_cost_per_piece, allow_zero=True):
            errors.append("Warehouse Cost per Piece must be a non-negative number")
        elif warehouse_cost_per_piece > 1000:
            errors.append("Warehouse Cost per Piece seems unreasonably high (max €1,000)")
        
        # Optional field validations
        pieces_per_pallet = warehouse_data.get('pieces_per_pallet')
        if pieces_per_pallet is not None:
            if not self.is_positive_integer(pieces_per_pallet):
                errors.append("Pieces per Pallet must be a positive integer")
            elif pieces_per_pallet > 100000:
                errors.append("Pieces per Pallet seems unreasonably high (max 100,000)")
        
        storage_days = warehouse_data.get('storage_days')
        if storage_days is not None:
            if not self.is_positive_integer(storage_days):
                errors.append("Storage Days must be a positive integer")
            elif storage_days > 3650:  # 10 years
                errors.append("Storage Days seems unreasonably high (max 3,650 days)")
        
        # Validate percentage fields
        percentage_fields = ['inventory_interest_rate', 'obsolescence_rate', 'damage_rate']
        for field in percentage_fields:
            value = warehouse_data.get(field)
            if value is not None:
                if field == 'inventory_interest_rate' and value > 50:  # Interest rates rarely exceed 50%
                    errors.append("Inventory Interest Rate seems unreasonably high (max 50%)")
                elif not self.is_valid_percentage(value):
                    errors.append(f"{field.replace('_', ' ').title()} must be between 0 and 100 percent")
        
        # Validate cost fields
        cost_fields = ['handling_cost_in', 'handling_cost_out', 'storage_cost_per_pallet_day']
        for field in cost_fields:
            value = warehouse_data.get(field)
            if value is not None:
                if not self.is_positive_number(value, allow_zero=True):
                    errors.append(f"{field.replace('_', ' ').title()} must be a non-negative number")
                elif value > 10000:
                    errors.append(f"{field.replace('_', ' ').title()} seems unreasonably high (max €10,000)")
        
        # Validate security level
        security_level = warehouse_data.get('security_level', '').strip()
        if security_level and security_level not in ['Standard', 'High', 'Maximum']:
            errors.append("Security Level must be Standard, High, or Maximum")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class CalculationValidator(BaseValidator):
    """Validator for calculation parameters and results."""
    
    def validate_calculation_inputs(self, materials: List[Dict], suppliers: List[Dict], 
                                  packaging_configs: List[Dict], transport_configs: List[Dict], 
                                  warehouse_configs: List[Dict]) -> Dict[str, Any]:
        """
        Validate that all required data is present for calculations.
        
        Args:
            materials: List of material configurations
            suppliers: List of supplier configurations
            packaging_configs: List of packaging configurations
            transport_configs: List of transport configurations
            warehouse_configs: List of warehouse configurations
            
        Returns:
            Dictionary with 'is_valid' boolean and 'errors' list
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
        
        # If basic data exists, check for complete configurations
        if materials and suppliers and packaging_configs and transport_configs and warehouse_configs:
            complete_configs = 0
            incomplete_pairs = []
            
            for material in materials:
                for supplier in suppliers:
                    material_id = material['material_no']
                    supplier_id = supplier['vendor_id']
                    
                    has_packaging = any(
                        p['material_id'] == material_id and p['supplier_id'] == supplier_id 
                        for p in packaging_configs
                    )
                    has_transport = any(
                        t['material_id'] == material_id and t['supplier_id'] == supplier_id 
                        for t in transport_configs
                    )
                    has_warehouse = any(
                        w['material_id'] == material_id and w['supplier_id'] == supplier_id 
                        for w in warehouse_configs
                    )
                    
                    if has_packaging and has_transport and has_warehouse:
                        complete_configs += 1
                    else:
                        missing = []
                        if not has_packaging:
                            missing.append("packaging")
                        if not has_transport:
                            missing.append("transport")
                        if not has_warehouse:
                            missing.append("warehouse")
                        
                        incomplete_pairs.append(
                            f"{material_id}-{supplier_id} (missing: {', '.join(missing)})"
                        )
            
            if complete_configs == 0:
                errors.append("No complete material-supplier configurations found")
                if incomplete_pairs:
                    errors.append(f"Incomplete configurations: {'; '.join(incomplete_pairs[:5])}")
                    if len(incomplete_pairs) > 5:
                        errors.append(f"... and {len(incomplete_pairs) - 5} more incomplete configurations")
            else:
                if incomplete_pairs:
                    warnings.append(f"Found {complete_configs} complete configurations")
                    warnings.append(f"{len(incomplete_pairs)} incomplete configurations will be skipped")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'complete_configurations': complete_configs if 'complete_configs' in locals() else 0
        }
