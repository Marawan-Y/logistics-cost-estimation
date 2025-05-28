"""
Logistics Cost Calculation Engine

This module contains the core calculation logic for computing logistics costs
based on material, supplier, packaging, transport, and warehouse parameters.
"""

class LogisticsCostCalculator:
    """
    Main calculator class for logistics cost computations.
    """
    
    def __init__(self):
        self.calculation_errors = []
    
    def calculate_packaging_cost_per_piece(self, material, packaging_config):
        """
        Calculate packaging cost per piece.
        
        Formula: (Plant + CoC + Maintenance + Scrap + Tooling amortized) / total volume
        """
        try:
            # Basic packaging cost
            base_cost = packaging_config.get('packaging_cost_per_part', 0.0)
            
            # Additional costs
            plant_cost = packaging_config.get('plant_cost', 0.0)
            coc_cost = packaging_config.get('coc_cost', 0.0)
            maintenance_cost = packaging_config.get('maintenance_cost', 0.0)
            
            # Scrap adjustment
            scrap_rate = packaging_config.get('scrap_rate', 0.0) / 100.0
            scrap_adjustment = base_cost * scrap_rate
            
            # Tooling cost amortization
            tooling_cost = packaging_config.get('tooling_cost', 0.0)
            lifetime_volume = material.get('lifetime_volume', material.get('annual_volume', 1))
            tooling_cost_per_piece = tooling_cost / lifetime_volume if lifetime_volume > 0 else 0
            
            # Total packaging cost per piece
            total_cost = (
                base_cost + 
                plant_cost + 
                coc_cost + 
                maintenance_cost + 
                scrap_adjustment + 
                tooling_cost_per_piece
            )
            
            return max(0.0, total_cost)
            
        except Exception as e:
            self.calculation_errors.append(f"Packaging cost calculation error: {str(e)}")
            return 0.0
    
    def calculate_transport_cost_per_piece(self, material, transport_config, include_co2=True):
        """
        Calculate transport cost per piece.
        
        Formula: (LU cost + fuel surcharge + customs + handling + insurance) / LU quantity
        """
        try:
            # Base transport cost
            base_cost_per_lu = transport_config.get('transport_cost_per_lu', 0.0)
            lu_capacity = transport_config.get('lu_capacity', 1)
            
            # Additional costs
            fuel_surcharge_rate = transport_config.get('fuel_surcharge_rate', 0.0) / 100.0
            fuel_surcharge = base_cost_per_lu * fuel_surcharge_rate
            
            customs_handling = transport_config.get('customs_handling', 0.0)
            handling_cost = transport_config.get('handling_cost', 0.0)
            
            # Insurance cost (based on material value)
            insurance_rate = transport_config.get('insurance_rate', 0.0) / 100.0
            material_value = material.get('material_value', 0.0)
            insurance_cost_per_piece = material_value * insurance_rate
            insurance_cost_per_lu = insurance_cost_per_piece * lu_capacity
            
            # Total cost per load unit
            total_cost_per_lu = (
                base_cost_per_lu + 
                fuel_surcharge + 
                customs_handling + 
                handling_cost + 
                insurance_cost_per_lu
            )
            
            # Cost per piece
            cost_per_piece = total_cost_per_lu / lu_capacity if lu_capacity > 0 else 0
            
            # CO2 cost calculation
            co2_cost_per_piece = 0.0
            if include_co2:
                co2_cost_per_piece = self.calculate_co2_cost_per_piece(material, transport_config)
            
            return max(0.0, cost_per_piece), max(0.0, co2_cost_per_piece)
            
        except Exception as e:
            self.calculation_errors.append(f"Transport cost calculation error: {str(e)}")
            return 0.0, 0.0
    
    def calculate_co2_cost_per_piece(self, material, transport_config):
        """
        Calculate CO2 emission cost per piece.
        
        Formula: (emission factor × weight per piece × distance × CO2 cost per ton) / 1000
        """
        try:
            emission_factor = transport_config.get('co2_emission_factor', 0.0)  # kg CO2/ton-km
            distance_km = transport_config.get('distance_km', 0.0)
            co2_cost_per_ton = transport_config.get('co2_cost_per_ton', 0.0)
            weight_per_piece = material.get('weight_per_pcs', 0.0)  # kg
            
            # Convert weight to tons and calculate emissions
            weight_tons = weight_per_piece / 1000.0
            co2_emissions_kg = emission_factor * weight_tons * distance_km * 1000  # kg CO2
            co2_emissions_tons = co2_emissions_kg / 1000.0  # tons CO2
            
            co2_cost = co2_emissions_tons * co2_cost_per_ton
            
            return max(0.0, co2_cost)
            
        except Exception as e:
            self.calculation_errors.append(f"CO2 cost calculation error: {str(e)}")
            return 0.0
    
    def calculate_warehouse_cost_per_piece(self, material, warehouse_config):
        """
        Calculate warehouse cost per piece.
        
        Formula: (storage cost × days × 12 + handling costs + interest) / annual volume
        """
        try:
            # Base warehouse cost
            base_cost_per_piece = warehouse_config.get('warehouse_cost_per_piece', 0.0)
            
            # Storage parameters
            storage_days = warehouse_config.get('storage_days', 30)
            pieces_per_pallet = warehouse_config.get('pieces_per_pallet', 100)
            storage_cost_per_pallet_day = warehouse_config.get('storage_cost_per_pallet_day', 0.0)
            
            # Calculate storage cost per piece
            storage_cost_per_piece_per_day = storage_cost_per_pallet_day / pieces_per_pallet if pieces_per_pallet > 0 else 0
            total_storage_cost_per_piece = storage_cost_per_piece_per_day * storage_days
            
            # Handling costs
            handling_cost_in = warehouse_config.get('handling_cost_in', 0.0)
            handling_cost_out = warehouse_config.get('handling_cost_out', 0.0)
            total_handling_cost_per_piece = (handling_cost_in + handling_cost_out) / pieces_per_pallet if pieces_per_pallet > 0 else 0
            
            # Inventory interest cost
            inventory_interest_rate = warehouse_config.get('inventory_interest_rate', 0.0) / 100.0  # Convert percentage
            material_value = material.get('material_value', 0.0)
            storage_period_years = storage_days / 365.0
            interest_cost_per_piece = material_value * inventory_interest_rate * storage_period_years
            
            # Risk costs
            obsolescence_rate = warehouse_config.get('obsolescence_rate', 0.0) / 100.0
            damage_rate = warehouse_config.get('damage_rate', 0.0) / 100.0
            risk_cost_per_piece = material_value * (obsolescence_rate + damage_rate) * storage_period_years
            
            # Total warehouse cost per piece
            total_cost = (
                base_cost_per_piece + 
                total_storage_cost_per_piece + 
                total_handling_cost_per_piece + 
                interest_cost_per_piece + 
                risk_cost_per_piece
            )
            
            return max(0.0, total_cost)
            
        except Exception as e:
            self.calculation_errors.append(f"Warehouse cost calculation error: {str(e)}")
            return 0.0
    
    def calculate_total_logistics_cost(self, material, supplier, packaging_config, transport_config, warehouse_config, include_co2=True):
        """
        Calculate total logistics cost per piece for a specific material-supplier combination.
        """
        try:
            # Calculate individual cost components
            packaging_cost = self.calculate_packaging_cost_per_piece(material, packaging_config)
            transport_cost, co2_cost = self.calculate_transport_cost_per_piece(material, transport_config, include_co2)
            warehouse_cost = self.calculate_warehouse_cost_per_piece(material, warehouse_config)
            
            # Total cost per piece
            total_cost_per_piece = packaging_cost + transport_cost + warehouse_cost
            
            if include_co2:
                total_cost_per_piece += co2_cost
            
            # Calculate annual cost
            annual_volume = material.get('annual_volume', 0)
            total_annual_cost = total_cost_per_piece * annual_volume
            
            return {
                'material_id': material['material_no'],
                'material_desc': material['material_desc'],
                'supplier_id': supplier['vendor_id'],
                'supplier_name': supplier['vendor_name'],
                'packaging_cost_per_piece': packaging_cost,
                'transport_cost_per_piece': transport_cost,
                'warehouse_cost_per_piece': warehouse_cost,
                'co2_cost_per_piece': co2_cost if include_co2 else 0.0,
                'total_cost_per_piece': total_cost_per_piece,
                'annual_volume': annual_volume,
                'total_annual_cost': total_annual_cost,
                'calculation_date': str(pd.Timestamp.now()) if 'pd' in globals() else str(datetime.now())
            }
            
        except Exception as e:
            self.calculation_errors.append(f"Total cost calculation error for {material.get('material_no', 'Unknown')} - {supplier.get('vendor_id', 'Unknown')}: {str(e)}")
            return None
    
    def calculate_all_costs(self, materials, suppliers, packaging_configs, transport_configs, warehouse_configs, include_co2=True):
        """
        Calculate logistics costs for all configured material-supplier combinations.
        """
        results = []
        self.calculation_errors = []
        
        # Create lookup dictionaries for faster access
        packaging_lookup = {f"{p['material_id']}_{p['supplier_id']}": p for p in packaging_configs}
        transport_lookup = {f"{t['material_id']}_{t['supplier_id']}": t for t in transport_configs}
        warehouse_lookup = {f"{w['material_id']}_{w['supplier_id']}": w for w in warehouse_configs}
        
        for material in materials:
            for supplier in suppliers:
                # Create lookup key
                lookup_key = f"{material['material_no']}_{supplier['vendor_id']}"
                
                # Check if all configurations exist for this combination
                if (lookup_key in packaging_lookup and 
                    lookup_key in transport_lookup and 
                    lookup_key in warehouse_lookup):
                    
                    packaging_config = packaging_lookup[lookup_key]
                    transport_config = transport_lookup[lookup_key]
                    warehouse_config = warehouse_lookup[lookup_key]
                    
                    # Calculate costs
                    result = self.calculate_total_logistics_cost(
                        material, supplier, packaging_config, 
                        transport_config, warehouse_config, include_co2
                    )
                    
                    if result:
                        results.append(result)
        
        return results
    
    def get_calculation_errors(self):
        """
        Return any calculation errors that occurred.
        """
        return self.calculation_errors
    
    def validate_configuration(self, material, supplier, packaging_config, transport_config, warehouse_config):
        """
        Validate that all required configuration parameters are present and valid.
        """
        errors = []
        
        # Material validation
        if not material.get('material_no'):
            errors.append("Material number is required")
        if not material.get('weight_per_pcs') or material.get('weight_per_pcs') <= 0:
            errors.append("Valid weight per piece is required")
        if not material.get('annual_volume') or material.get('annual_volume') <= 0:
            errors.append("Valid annual volume is required")
        
        # Supplier validation
        if not supplier.get('vendor_id'):
            errors.append("Supplier vendor ID is required")
        
        # Packaging validation
        if not packaging_config.get('filling_degree') or packaging_config.get('filling_degree') <= 0:
            errors.append("Valid filling degree is required")
        
        # Transport validation
        if not transport_config.get('lu_capacity') or transport_config.get('lu_capacity') <= 0:
            errors.append("Valid load unit capacity is required")
        if transport_config.get('distance_km', 0) < 0:
            errors.append("Distance cannot be negative")
        
        # Warehouse validation
        if warehouse_config.get('storage_days', 0) <= 0:
            errors.append("Valid storage days is required")
        
        return errors


# Import datetime if pandas is not available
try:
    import pandas as pd
except ImportError:
    from datetime import datetime
