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
    
    def calculate_packaging_cost_per_piece(self, material, packaging_config, operations_config=None):
        """
        Calculate packaging cost per piece including all packaging components.
        
        Includes:
        - Packaging maintenance
        - Empties scrapping
        - Additional packaging price
        - Special packaging costs
        - Tooling cost amortization
        """
        try:
            # Per-part costs (6.1)
            pack_maint = packaging_config.get('pack_maint', 0.0)
            empties_scrap = packaging_config.get('empties_scrap', 0.0)
            
            # Standard packaging costs (6.2)
            fill_qty_box = packaging_config.get('fill_qty_box', 1)
            fill_qty_lu = packaging_config.get('fill_qty_lu', 1)
            add_pack_price = packaging_config.get('add_pack_price', 0.0)
            
            # Calculate price per piece for additional packaging
            add_pack_per_piece = add_pack_price / fill_qty_box if fill_qty_box > 0 else 0
            
            # Special packaging costs (6.3)
            sp_needed = packaging_config.get('sp_needed', 'No')
            tooling_cost = packaging_config.get('tooling_cost', 0.0)
            
            # Tooling cost amortization
            tooling_cost_per_piece = 0.0
            if sp_needed == 'Yes' and tooling_cost > 0:
                annual_volume = material.get('annual_volume', 1)
                lifetime_years = material.get('lifetime_years', 1.0)
                lifetime_volume = annual_volume * lifetime_years if lifetime_years > 0 else annual_volume
                tooling_cost_per_piece = tooling_cost / lifetime_volume if lifetime_volume > 0 else 0
            
            # Total packaging cost per piece
            total_cost = (
                pack_maint + 
                empties_scrap + 
                add_pack_per_piece + 
                tooling_cost_per_piece
            )
            
            return max(0.0, total_cost)
            
        except Exception as e:
            self.calculation_errors.append(f"Packaging cost calculation error: {str(e)}")
            return 0.0
    
    def calculate_repacking_cost_per_piece(self, material, repacking_config=None):
        """
        Calculate repacking cost per piece if repacking is required.
        """
        try:
            if not repacking_config:
                return 0.0
            
            rep_cost_hr = repacking_config.get('rep_cost_hr', 0.0)
            rep_cost_lu = repacking_config.get('rep_cost_lu', 0.0)
            
            # Assume repacking cost applies to a portion of the volume
            # This could be refined based on actual repacking requirements
            repacking_percentage = 0.1  # Assume 10% needs repacking
            
            # Convert hourly cost to per piece (assuming productivity rate)
            pieces_per_hour = 100  # This should be configurable
            rep_cost_per_piece_hourly = rep_cost_hr / pieces_per_hour if pieces_per_hour > 0 else 0
            
            # Use the higher of hourly or per LU cost
            lu_capacity = 100  # Default, should come from transport config
            rep_cost_per_piece_lu = rep_cost_lu / lu_capacity if lu_capacity > 0 else 0
            
            repacking_cost = max(rep_cost_per_piece_hourly, rep_cost_per_piece_lu) * repacking_percentage
            
            return max(0.0, repacking_cost)
            
        except Exception as e:
            self.calculation_errors.append(f"Repacking cost calculation error: {str(e)}")
            return 0.0
    
    def calculate_customs_cost_per_piece(self, material, customs_config=None, operations_config=None):
        """
        Calculate customs cost per piece based on duty and tariff rates.
        """
        try:
            if not customs_config:
                return 0.0
            
            # Get material value (piece price)
            material_value = material.get('material_value', 0.0)
            if material_value <= 0:
                return 0.0
            
            # Get customs parameters
            pref_usage = customs_config.get('pref_usage', 'No')
            duty_rate = customs_config.get('duty_rate', 0.0) / 100.0
            tariff_rate = customs_config.get('tariff_rate', 0.0) / 100.0
            
            # Apply duty and tariff based on preference usage
            if pref_usage == 'Yes':
                # Reduced or zero duty with preference
                customs_cost = material_value * tariff_rate * 0.1  # 10% of normal rate with preference
            else:
                # Full duty and tariff without preference
                customs_cost = material_value * (duty_rate + tariff_rate)
            
            return max(0.0, customs_cost)
            
        except Exception as e:
            self.calculation_errors.append(f"Customs cost calculation error: {str(e)}")
            return 0.0
    
    def calculate_transport_cost_per_piece(self, material, transport_config, location_config=None, co2_config=None):
        """
        Calculate transport cost per piece including all transport components.
        
        Includes:
        - Base transport cost
        - Fuel surcharge
        - Customs handling
        - Insurance
        - CO2 emissions cost
        """
        try:
            # Base transport cost
            transport_cost_per_lu = transport_config.get('transport_cost_per_lu', 0.0)
            lu_capacity = transport_config.get('lu_capacity', 1)
            
            # Additional costs
            fuel_surcharge_rate = transport_config.get('fuel_surcharge_rate', 0.0) / 100.0
            fuel_surcharge = transport_cost_per_lu * fuel_surcharge_rate
            
            customs_handling = transport_config.get('customs_handling', 0.0)
            handling_cost = transport_config.get('handling_cost', 0.0)
            
            # Insurance cost
            insurance_rate = transport_config.get('insurance_rate', 0.0) / 100.0
            material_value = material.get('material_value', 0.0)
            insurance_cost_per_piece = material_value * insurance_rate
            insurance_cost_per_lu = insurance_cost_per_piece * lu_capacity
            
            # Total cost per load unit
            total_cost_per_lu = (
                transport_cost_per_lu + 
                fuel_surcharge + 
                customs_handling + 
                handling_cost + 
                insurance_cost_per_lu
            )
            
            # Cost per piece
            cost_per_piece = total_cost_per_lu / lu_capacity if lu_capacity > 0 else 0
            
            # CO2 cost calculation
            co2_cost_per_piece = 0.0
            if co2_config:
                co2_cost_per_piece = self.calculate_co2_cost_per_piece(
                    material, transport_config, location_config, co2_config
                )
            
            return max(0.0, cost_per_piece), max(0.0, co2_cost_per_piece)
            
        except Exception as e:
            self.calculation_errors.append(f"Transport cost calculation error: {str(e)}")
            return 0.0, 0.0
    
    def calculate_co2_cost_per_piece(self, material, transport_config, location_config=None, co2_config=None):
        """
        Calculate CO2 emission cost per piece.
        
        Formula: (emission factor × weight per piece × distance × CO2 cost per ton) / 1000
        """
        try:
            # Get CO2 parameters
            emission_factor = transport_config.get('co2_emission_factor', 0.06)  # default for road
            co2_cost_per_ton = transport_config.get('co2_cost_per_ton', 25.0)  # default EU ETS
            
            # Override with global CO2 config if available
            if co2_config:
                co2_cost_per_ton = co2_config.get('cost_per_ton', co2_cost_per_ton)
            
            # Get distance
            distance_km = transport_config.get('distance_km', 0.0)
            if location_config and distance_km == 0:
                distance_km = location_config.get('distance', 0.0)
            
            # Get weight
            weight_per_piece = material.get('weight_per_pcs', 0.0)  # kg
            
            # Convert weight to tons and calculate emissions
            weight_tons = weight_per_piece / 1000.0
            co2_emissions_tons = emission_factor * weight_tons * distance_km / 1000.0
            
            co2_cost = co2_emissions_tons * co2_cost_per_ton
            
            return max(0.0, co2_cost)
            
        except Exception as e:
            self.calculation_errors.append(f"CO2 cost calculation error: {str(e)}")
            return 0.0
    
    def calculate_warehouse_cost_per_piece(self, material, warehouse_config, interest_config=None):
        """
        Calculate warehouse cost per piece including storage and inventory costs.
        """
        try:
            # Get warehouse cost per location
            cost_per_loc = warehouse_config.get('cost_per_loc', 0.0)
            
            # Calculate based on annual volume and turnover
            annual_volume = material.get('annual_volume', 1)
            working_days = material.get('working_days', 250)
            daily_demand = material.get('daily_demand', annual_volume / working_days if working_days > 0 else 0)
            
            # Assume average inventory level (safety stock + cycle stock/2)
            safety_stock_days = 10  # Default safety stock in days
            cycle_stock_days = 5    # Default cycle stock in days
            avg_inventory_days = safety_stock_days + (cycle_stock_days / 2)
            avg_inventory_pieces = daily_demand * avg_inventory_days
            
            # Calculate storage locations needed (assume standard pallet size)
            pieces_per_location = 1000  # Default pieces per storage location
            locations_needed = avg_inventory_pieces / pieces_per_location if pieces_per_location > 0 else 1
            
            # Monthly storage cost
            monthly_storage_cost = cost_per_loc * locations_needed
            annual_storage_cost = monthly_storage_cost * 12
            storage_cost_per_piece = annual_storage_cost / annual_volume if annual_volume > 0 else 0
            
            # Inventory interest cost
            interest_cost_per_piece = 0.0
            if interest_config:
                interest_rate = interest_config.get('rate', 0.0) / 100.0
                material_value = material.get('material_value', 0.0)
                avg_inventory_value = material_value * avg_inventory_pieces
                annual_interest_cost = avg_inventory_value * interest_rate
                interest_cost_per_piece = annual_interest_cost / annual_volume if annual_volume > 0 else 0
            
            # Total warehouse cost per piece
            total_cost = storage_cost_per_piece + interest_cost_per_piece
            
            return max(0.0, total_cost)
            
        except Exception as e:
            self.calculation_errors.append(f"Warehouse cost calculation error: {str(e)}")
            return 0.0
    
    def calculate_additional_costs_per_piece(self, material, additional_costs=None):
        """
        Calculate additional costs per piece from the additional cost configurations.
        """
        try:
            if not additional_costs:
                return 0.0
            
            total_additional_cost = sum(cost.get('cost_value', 0.0) for cost in additional_costs)
            annual_volume = material.get('annual_volume', 1)
            
            # Distribute additional costs across annual volume
            additional_cost_per_piece = total_additional_cost / annual_volume if annual_volume > 0 else 0
            
            return max(0.0, additional_cost_per_piece)
            
        except Exception as e:
            self.calculation_errors.append(f"Additional cost calculation error: {str(e)}")
            return 0.0
    
    def calculate_total_logistics_cost(self, material, supplier, packaging_config, transport_config, 
                                     warehouse_config, operations_config=None, location_config=None,
                                     repacking_config=None, customs_config=None, co2_config=None,
                                     interest_config=None, additional_costs=None, include_co2=True):
        """
        Calculate total logistics cost per piece for a specific material-supplier combination.
        """
        try:
            # Calculate individual cost components
            packaging_cost = self.calculate_packaging_cost_per_piece(material, packaging_config, operations_config)
            repacking_cost = self.calculate_repacking_cost_per_piece(material, repacking_config)
            customs_cost = self.calculate_customs_cost_per_piece(material, customs_config, operations_config)
            transport_cost, co2_cost = self.calculate_transport_cost_per_piece(
                material, transport_config, location_config, co2_config if include_co2 else None
            )
            warehouse_cost = self.calculate_warehouse_cost_per_piece(material, warehouse_config, interest_config)
            additional_cost = self.calculate_additional_costs_per_piece(material, additional_costs)
            
            # Total cost per piece
            total_cost_per_piece = (
                packaging_cost + 
                repacking_cost + 
                customs_cost + 
                transport_cost + 
                warehouse_cost + 
                additional_cost
            )
            
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
                'repacking_cost_per_piece': repacking_cost,
                'customs_cost_per_piece': customs_cost,
                'transport_cost_per_piece': transport_cost,
                'warehouse_cost_per_piece': warehouse_cost,
                'additional_cost_per_piece': additional_cost,
                'co2_cost_per_piece': co2_cost if include_co2 else 0.0,
                'total_cost_per_piece': total_cost_per_piece,
                'annual_volume': annual_volume,
                'total_annual_cost': total_annual_cost,
                'calculation_date': str(pd.Timestamp.now()) if 'pd' in globals() else str(datetime.now())
            }
            
        except Exception as e:
            self.calculation_errors.append(
                f"Total cost calculation error for {material.get('material_no', 'Unknown')} - "
                f"{supplier.get('vendor_id', 'Unknown')}: {str(e)}"
            )
            return None
    
    def calculate_all_costs(self, materials, suppliers, packaging_configs, transport_configs, 
                           warehouse_configs, include_co2=True, operations_configs=None, 
                           location_configs=None, repacking_configs=None, customs_configs=None,
                           co2_configs=None, interest_configs=None, additional_costs=None):
        """
        Calculate logistics costs for all configured material-supplier combinations.
        """
        results = []
        self.calculation_errors = []
        
        # Get first config for singleton configs (like CO2, interest)
        co2_config = co2_configs[0] if co2_configs else None
        interest_config = interest_configs[0] if interest_configs else None
        
        for material in materials:
            for supplier in suppliers:
                # Check if basic configurations exist for this combination
                packaging_config = next(
                    (p for p in packaging_configs 
                     if p.get('material_id') == material['material_no'] and 
                        p.get('supplier_id') == supplier['vendor_id']), 
                    None
                )
                
                transport_config = next(
                    (t for t in transport_configs 
                     if t.get('material_id') == material['material_no'] and 
                        t.get('supplier_id') == supplier['vendor_id']), 
                    None
                )
                
                warehouse_config = next(
                    (w for w in warehouse_configs 
                     if w.get('material_id') == material['material_no'] and 
                        w.get('supplier_id') == supplier['vendor_id']), 
                    None
                )
                
                # Skip if essential configs are missing
                if not all([packaging_config, transport_config, warehouse_config]):
                    continue
                
                # Get optional configs
                operations_config = operations_configs[0] if operations_configs else None
                location_config = location_configs[0] if location_configs else None
                repacking_config = repacking_configs[0] if repacking_configs else None
                customs_config = next(
                    (c for c in customs_configs if c.get('hs_code') == material.get('hs_code')), 
                    customs_configs[0] if customs_configs else None
                )
                
                # Calculate costs
                result = self.calculate_total_logistics_cost(
                    material, supplier, packaging_config, transport_config, warehouse_config,
                    operations_config, location_config, repacking_config, customs_config,
                    co2_config, interest_config, additional_costs, include_co2
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
        if not packaging_config:
            errors.append("Packaging configuration is required")
        
        # Transport validation
        if not transport_config:
            errors.append("Transport configuration is required")
        elif not transport_config.get('lu_capacity') or transport_config.get('lu_capacity') <= 0:
            errors.append("Valid load unit capacity is required")
        
        # Warehouse validation
        if not warehouse_config:
            errors.append("Warehouse configuration is required")
        
        return errors


# Import datetime if pandas is not available
try:
    import pandas as pd
except ImportError:
    from datetime import datetime