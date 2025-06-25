"""
Logistics Cost Calculation Engine

Fully implements the Excel short-key formulas for:
Material, Packaging, Customs, Transport, CO₂, Warehouse costs.
"""
from packaging_tables import STANDARD_BOXES 
try:
    import pandas as pd
except ImportError:
    from datetime import datetime as _dt

import math


class LogisticsCostCalculator:
    """
    Main calculator class for logistics cost computations.
    """

    def __init__(self):
        self.calculation_errors = []

    # --- Material-level intermediates -----------------------------------------

    def lifetime_volume(self, material):
        """
        d = lifetime_volume = annual_volume * lifetime_years
        short-keys: 
          a1.1.1.1 = annual_volume
          d1 = lifetime_years
        """
        av = material.get('annual_volume', 0)
        ly = material.get('lifetime_years', 0)
        lifetime_vol = av * ly
        return lifetime_vol 

    # --- Packaging-level calculations -----------------------------------------
    # ---------------- Standart Boxes Table Parameters ----------------
    def packaging_characeristics(self, packaging_config):
        """
        B [2:28] @ "Standard Boxes" Sheet -- wrt [A]
        This is a direct value from the packaging tables.
        """
        b_type = packaging_config.get('box_type', 0)
        p_char = STANDARD_BOXES.get(b_type, {}).get("Packaging_Characteristics", 0)
        return p_char
    
    def packaging_weight(self, packaging_config):
        """
        G [2:28] @ "Standard Boxes" Sheet -- wrt [A]
        This is a direct value from the packaging tables.
        """
        b_type = packaging_config.get('box_type', 0)
        p_weight = STANDARD_BOXES.get(b_type, {}).get("MT_weight_kg", 0)
        return p_weight

    def no_boxes_per_lu(self, packaging_config):
        """
        H[2:28] @ "Standard Boxes" Sheet -- [A]
        This is a direct value from the packaging tables.
        """
        b_type = packaging_config.get('box_type', 0)
        b_per_lu = STANDARD_BOXES.get(b_type, {}).get("Pcs_Boxes_per_LU", 0)
        return b_per_lu

    def price_per_box(self, packaging_config):
        """
        C[2:28] @ "Standard Boxes" Sheet -- [A]
        This is a direct value from the packaging tables.
        """
        b_type = packaging_config.get('box_type', 0)
        b_price = STANDARD_BOXES.get(b_type, {}).get("Cost_per_pcs", 0)
        return b_price

    def sp_packaging_weight(self, packaging_config):
        """
        G [32:34] @ "Standard Boxes" Sheet -- [A][32:34]
        This is a direct value from the packaging tables.
        """
        sp_p_type = packaging_config.get('sp_type', 0)
        sp_weight = SPECIAL_PACKAGING.get(sp_p_type, {}).get("MT_weight_kg", 0)
        return sp_weight
    
    def price_per_tray(self, packaging_config):
        """
        C[32:34] @ "Standard boxes" Sheet -- [A][32:34]
        This is a direct value from the packaging tables.
        """
        sp_p_type = packaging_config.get('sp_type', 0)
        price_tray = SPECIAL_PACKAGING.get(sp_p_type, {}).get("Cost_per_pcs", 0)
        return price_tray
    
    def price_sp_pallets(self, packaging_config):
        """
        C[36] @ "Standard Boxes" Sheet
        This is a direct value from the packaging tables.
        """
        sp_pallet_price = ADDITIONAL_PACKAGING.get("Pallet").get("Cost_per_pcs", 0)
        return sp_pallet_price
    
    def price_sp_cover(self, packaging_config):
        """
        C[37] @ "Standard Boxes" Sheet
        This is a direct value from the packaging tables.
        """
        price_cover = ADDITIONAL_PACKAGING.get("Cover").get("Cost_per_pcs", 0)
        return price_cover
    
    def sp_pallet_weight(self, packaging_config):
        """
        G[36] @ "Standard Boxes" Sheet
        This is a direct value from the packaging tables.
        """
        sp_pallet_weight = ADDITIONAL_PACKAGING.get("Pallet").get("MT_weight_kg", 0)
        return sp_pallet_weight
    
    def weight_pallet(self, packaging_config):
        """
        M [9/10] @ "Standard Boxes" Sheet -- [J][9/10]
        This is a direct value from the packaging tables.
        """
        p_type = packaging_config.get('new_pallet_type', 0)
        pallet_weight = ACCESSORY_PACKAGING.get(p_type, {}).get("Ave_Weight_kg", 0)
        return pallet_weight
    
    def boxes_per_lu(self, packaging_config):
        """
        L[9/10] @ "Standard Boxes" Sheet -- [J][9/10]
        This is a direct value from the packaging tables.
        """
        p_type = packaging_config.get('new_pallet_type', 0)
        pallet_price = ACCESSORY_PACKAGING.get(p_type, {}).get("Ave_Price", 0)
        return pallet_price

    # --- Packaging-level calculations continued ----------------------------    
    def packaging_loop_days(self, packaging_config):
        """
        a1.1.2 = sum of all loop stages from loop_data dict
        """
        loop_plant = packaging_config.get('loop_data', {}) or {}
        return sum(loop_plant.values())
    
    def loop_coc(self, packaging_config):
        """
        a2.2.1.1 = Loop CoC = a1.1.2 (packaging loop days) + a2.1.1 (CoC-specific loop)
        Here we assume CoC loop_data stored under key 'coc_loop' or default 0.
        """
        plant_loop = self.packaging_loop_days(packaging_config)
        sub_sup_days = packaging_config.get('subsupplier_box_days', {}) or {}
        coc_loop = plant_loop + sub_sup_days
        return coc_loop
 
    def total_packaging_loop(self, packaging_config):
        """
        a1.1.2.1 = total packaging loop days = sum of loop_data
        """
        total_pck_loop_days = self.loop_coc(packaging_config)
        return total_pck_loop_days

    def filling_qty_pcs_per_lu(self, packaging_config):
        """
        p = a1.1.3 * a1.4.1
        a1.1.3 = fill_qty_box
        a1.4.1 = boxes_per_lu
        """
        f = packaging_config.get('fill_qty_box', 0)
        b = packaging_config.get('boxes_per_lu', 0)
        return f * b

    def empties_scrapping_wood(self, packaging_config):
        """
        c = (a1.1.1.1 / a1.1.3) * (c1 / 1000)
        a1.1.1.1 = annual_volume
        a1.1.3 = fill_qty_box
        c1 = packaging_weight (wood) in g from sheet
        """
        av = packaging_config.get('annual_volume', 0)  # we'll pull from material in real use
        fill = packaging_config.get('fill_qty_box', 0)
        p_weight = self.packaging_weight(packaging_config)
        if fill > 0:
            return (av / fill) * (p_weight / 1000.0)
        return 0.0

# ** PLANT **
    def packaging_cost_plant(self, material, packaging_config):
        """
        Packaging cost plant total: same as total if no distinction
        """
        daily_demand = material.get('daily_demand', 0)
        loop_plant_days = self.packaging_loop_days(packaging_config)
        fill = packaging_config.get('fill_qty_box', 0)
        b_per_lu = self.no_boxes_per_lu(packaging_config)
        adds = packaging_config.get('add_pack_price', 0)
        b_price = self.price_per_box(packaging_config)
        pallet_price = self.boxes_per_lu(packaging_config)

        no_box_loop_plant = (daily_demand * loop_plant_days) / fill
        no_lu_loop_plant = no_box_loop_plant / b_per_lu

        pck_cost_plant = ( no_box_loop_plant * ( adds + b_price )) + (no_lu_loop_plant * pallet_price) 

        return pck_cost_plant

# ** CoC **
    def packaging_cost_coc(self, material, packaging_config, operations_config):
        """
        Packaging cost CoC total: treat same as total for now
        """
        daily_demand = material.get('daily_demand', 0)
        fill_box = packaging_config.get('fill_qty_box', 0)
        b_price = self.price_per_box(packaging_config)
        pallet_price = self.boxes_per_lu(packaging_config)
        subsupplier_days = operations_config.get('subsupplier_box_days', 0)
        b_per_lu = self.no_boxes_per_lu(packaging_config)
        fill_tray = packaging_config.get('fill_qty_tray', 0)
        total_pck_loop_days = self.total_packaging_loop(packaging_config)
        sp_needed = packaging_config.get('sp_needed')
        add_sp_pack = packaging_config.get('add_sp_pack')
        trays_per_sp_pal = packaging_config.get('trays_per_sp_pal', 0)
        price_tray = self.price_per_tray(packaging_config)
        sp_pallet_price = self.price_sp_pallets(packaging_config)
        price_cover = self.price_sp_cover(packaging_config)
        tooling_cost = packaging_config.get('tooling_cost', 0)

        no_box_coc = (daily_demand * subsupplier_days) / fill_box
        no_lu_coc = no_box_coc / b_per_lu
        no_tray_coc = daily_demand / (fill_tray * total_pck_loop_days) if sp_needed == 'Yes' else 0
        no_sp_pallet_cover = no_tray_coc / trays_per_sp_pal if add_sp_pack == 'Yes' else 0

        pck_cost_coc = (b_price * no_box_coc) + (no_lu_coc * pallet_price) + (no_tray_coc * price_tray) + (no_sp_pallet_cover * (sp_pallet_price + price_cover)) + ((tooling_cost) if sp_needed == 'Yes' else 0)

        return pck_cost_coc

# ** Packaging Cost Total **
    def packaging_cost_total(self, packaging_config):
        """
        Packaging cost total = cost_per_piece * annual_volume
        """
        coc_cost = self.packaging_cost_coc(packaging_config)
        plant_cost = self.packaging_cost_plant(packaging_config)

        pck_cost = coc_cost + plant_cost
        return pck_cost

# ** Packaging Cost Per Piece **
    def packaging_cost_per_piece(self, material, packaging_config):
        """
        X1 = packaging cost per part pcs
          ...
        """
        try:
            scrap_paper = packaging_config.get('empties_scrap_cardboard', 0) 
            scrap_wood = self.empties_scrapping_wood(packaging_config) 
            lifetime_vol = self.lifetime_volume(material)
            total_pck_cost = self.packaging_cost_total(material, packaging_config)  

            pck_per_pcs = (scrap_paper + scrap_wood + total_pck_cost) / lifetime_vol  

            return max(0.0, pck_per_pcs)

        except Exception as e:
            self.calculation_errors.append(f"Packaging per-piece error: {e}")
            return 0.0

    # --- Transport-level calculations ----------------------------------------

    def transport_cost_per_piece(self, transport_config, packaging_config, operations_config):
        """
        X4 = transport cost per piece
        includes base cost, bonded cost, fuel surcharge, handling, insurance
        """
        try:
            # Transport
            mode1 = transport_config.get('mode1', 'Sea')  
            cost_lu = transport_config.get('cost_lu', 0)     
            bonded = transport_config.get('cost_bonded', 0)      
            fill_qty_lu_oversea = packaging_config.get('lu_capacity', 0) 
            incoterm_code = operations_config.get('incoterm_code')
            fill_qty_lu = self.filling_qty_pcs_per_lu(packaging_config) 

            if mode1 == 'Sea':
                # Sea transport
                if incoterm_code in ['FCA', 'FOB']:
                    # FCA/FOB includes bonded cost
                    tp_per_piece = (cost_lu / fill_qty_lu_oversea) + (bonded / fill_qty_lu)
                else:
                    # Other incoterms 
                    tp_per_piece = cost_lu / fill_qty_lu_oversea
            else:
                # other transport modes
                tp_per_piece = cost_lu / fill_qty_lu       

            return max(0.0, tp_per_piece)
        
        except Exception as e:
            self.calculation_errors.append(f"Transport cost error: {e}")
            return 0.0
        
    # --- CO2-level calculations ----------------------------------------------

    def energy_consumption(self, transport_config):
        """
        o2 = energy consumption factor
        from transport_config['co2_emission_factor']
        """
        mode1 = transport_config.get('mode1')

        if mode1 == 'Sea':
            energy_consumption = 0.006
        elif mode1 == 'Road':
            energy_consumption = 0.04415
        elif mode1 == 'Rail':
            energy_consumption = 0.0085
        else:
            energy_consumption = None

        return energy_consumption

    def weight_per_lu(self, packaging_config, material):
        """
        o1.1 = weight per LU (kg) 
        = p * weight_pcs + packaging weights
        TODO: combine piece weight and box/pallet weights
        """        
        sp_needed = packaging_config.get('sp_needed')
        trays_per_sp_pal = packaging_config.get('trays_per_sp_pal', 0)
        sp_pallets_per_lu = packaging_config.get('sp_pallets_per_lu', 0)
        sp_p_type = packaging_config.get('sp_type', 0)
        fill_qty_box = packaging_config.get('fill_qty_box', 0)
        fill_qty_tray = packaging_config.get('fill_qty_tray', 0)
        boxes_per_lu = packaging_config.get('boxes_per_lu', 0)
        add_sp_pack = packaging_config.get('add_sp_pack')
        weight_per_piece = material.get('weight_per_pcs', 0.0)
        sp_weight = self.sp_packaging_weight(packaging_config)
        p_weight = self.packaging_weight(packaging_config)
        fill_qty_lu = self.filling_qty_pcs_per_lu(packaging_config) 
        pallet_weight = self.weight_pallet(packaging_config)
        sp_pallet_weight = self.sp_pallet_weight(packaging_config)

        if sp_needed == 'Yes' and sp_p_type == 'Inlay tray pallet size':
            weight_per_lu = (fill_qty_box * weight_per_piece) + ((fill_qty_box / fill_qty_tray) * sp_weight) + p_weight
        elif sp_needed == 'Yes' and sp_p_type == 'Inlay Tray':
            weight_per_lu = (fill_qty_lu * weight_per_piece) + ((fill_qty_box / fill_qty_tray) * sp_weight) + pallet_weight
        elif sp_needed == 'Yes' and sp_p_type == 'Standalone tray':
            weight_per_lu = (fill_qty_tray * trays_per_sp_pal * sp_pallets_per_lu * weight_per_piece) + (sp_pallets_per_lu * sp_pallet_weight)
        elif sp_needed == 'No' and add_sp_pack == 'No':
            weight_per_lu = (weight_per_piece * fill_qty_lu) + (p_weight * boxes_per_lu) + pallet_weight

        return weight_per_lu  

    def total_tons(self, material, packaging_config):
        """
        o1 = [o1.1 * (annual_volume/p)] / 1000
        """
        fill_qty_lu = self.filling_qty_pcs_per_lu()
        weight_per_lu = self.weight_per_lu()
        annual_volume = material.get('annual_volume')

        total_tons = (weight_per_lu * (annual_volume / fill_qty_lu)) / 1000.0

        return total_tons

    def emission_kg_co2(self, transport_config):
        """
        emmission [kg CO2] = C181*C36*C173*C174
        """
        total_tons = self.total_tons() 
        distance_km = transport_config.get('distance_km') 
        energy_consumption = self.energy_consumption()
        co2_conversion_factor = transport_config.get('co2_conversion_factor')  

        emission = total_tons * energy_consumption * distance_km * co2_conversion_factor   
        return emission

    def co2_cost_per_piece(self, material, transport_config, location_config=None, co2_config=None):
        """
        X5 = [o * (r/1000)] / a1.1.1.1
        or emission formula:
        emission_tons = emission_factor * (weight_pcs/1000) * distance_km / 1000
        cost = emission_tons * co2_cost_per_ton
        """
        emission = self.emission_kg_co2()
        annual_volume = material.get('annual_volume')
        co2_cost_per_ton = transport_config.get('co2_cost_per_ton')

        co2_per_pcs = (emission * (co2_cost_per_ton / 1000.0)) / annual_volume

        return co2_per_pcs

    # --- Customs-level calculations ------------------------------------------

    def duty_cost_per_piece(self, material, customs_config):

        Pcs_Price = material.get('Pcs_Price', 0)
        dr = customs_config.get('duty_rate', 0) / 100.0
        tp_per_piece = self.transport_cost_per_piece()

        dc = dr * (Pcs_Price + tp_per_piece)

        return dc

    def tariff_cost_per_piece(self, material, customs_config):

        Pcs_Price = material.get('Pcs_Price', 0)
        tr = customs_config.get('tariff_rate', 0) / 100.0

        tc = tr * Pcs_Price

        return tc

    def customs_cost_per_piece(self, material, customs_config):
        """
        X3 = customs cost per piece = duty + tariff (with preference)
        """
        try:
            use_pref = customs_config.get('pref_usage', 'No')
            dc = self.duty_cost_per_piece(material, customs_config)
            tc = self.tariff_cost_per_piece(material, customs_config)

            if use_pref == 'No':

                cust_per_pcs = dc + tc

                return cust_per_pcs
            else:
                return 0.0
            
        except Exception as e:
            self.calculation_errors.append(f"Customs cost error: {e}")
            return 0.0

    # --- Warehouse-level calculations ----------------------------------------

    def SP_Filling_Qty_Pcs_lu(self, packaging_config):
        """
        'Special Packaging' - Filling quantity Pcs Per LU
        """
        sp_needed = packaging_config.get('sp_needed')
        trays_per_sp_pal = packaging_config.get('trays_per_sp_pal', 0)
        sp_pallets_per_lu = packaging_config.get('sp_pallets_per_lu', 0)
        sp_p_type = packaging_config.get('sp_type', 0)
        fill_qty_box = packaging_config.get('fill_qty_box', 0)
        fill_qty_tray = packaging_config.get('fill_qty_tray', 0)
        boxes_per_lu = packaging_config.get('boxes_per_lu', 0)

        if sp_needed == 'Yes':
            if sp_p_type == 'Inlay tray pallet size':
                sp_fill_qty_pcs_lu = (fill_qty_box / (fill_qty_tray)^2 ) 
            elif sp_p_type == 'Inlay Tray':      
                sp_fill_qty_pcs_lu = fill_qty_box * boxes_per_lu
            elif sp_p_type == 'Standalone tray':
                sp_fill_qty_pcs_lu = fill_qty_tray * trays_per_sp_pal * sp_pallets_per_lu 
       
            return max(sp_fill_qty_pcs_lu)
        else:
            return 0.0

    def inventory_days(self, material, packaging_config):
        """
        s1.1 = No. of days = 
          if sp_needed: s1.1.1 / annual_volume else p / annual_volume
          default: coverage_days
        """
        sp_needed = packaging_config.get('sp_needed')
        daily_demand = material.get('daily_demand', 0)
        sp_fill_qty_pcs_lu = self.SP_Filling_Qty_Pcs_lu()
        fill_qty_lu = self.filling_qty_pcs_per_lu()

        if sp_needed == 'Yes':
            no_days = fill_qty_lu / daily_demand
        else:
            no_days = sp_fill_qty_pcs_lu / daily_demand

        return no_days

    def safety_stock_days(self, operations_config, packaging_config, material):
        """
        s2.1 = coverage per pallet (days), default from config or 14
        """
        sp_needed = packaging_config.get('sp_needed')
        daily_demand = material.get('daily_demand', 0)
        sp_fill_qty_pcs_lu = self.SP_Filling_Qty_Pcs_lu()
        fill_qty_lu = self.filling_qty_pcs_per_lu()
        lead_time = operations_config.get('lead_time')  

        if sp_needed == 'Yes':
            safety_days = (lead_time * daily_demand) / sp_fill_qty_pcs_lu
        else:
            safety_days = (lead_time * daily_demand) / fill_qty_lu

        return safety_days

    def storage_locations_local(self, material, warehouse_config):
        """
        s1 = avg_inventory_pcs / pieces_per_location
        """
        no_days = self.inventory_days()

        storage_loc_local = 5 / no_days 

        return storage_loc_local

    def storage_locations_total(self, material, warehouse_config):
        """
        X6: s = s1 + s2 
        where s1 = No. Storage locations local supply
              s2 = No. additional locations if any
        """
        storage_loc_local = self.storage_locations_local(material, warehouse_config)
        safety_days = self.safety_stock_days(warehouse_config, material)

        storage_loc_total = storage_loc_local + safety_days

        return storage_loc_total

    def warehouse_cost_per_piece(self, material, warehouse_config, interest_config=None):
        """
        X6 = (s * t * 12) / annual_volume + interest_cost
        s = storage_locations_total
        t = cost_per_loc
        """ 
        try:
            storage_loc_total = self.storage_locations_total()
            cost_per_loc = warehouse_config.get('cost_per_loc')
            annual_volume = material.get('annual_volume')

            warehouse_per_pcs = (12 * storage_loc_total * cost_per_loc) / annual_volume

            return warehouse_per_pcs
        
        except Exception as e:
            self.calculation_errors.append(f"Warehouse cost error: {e}")
            return 0.0

    # --- Additional-cost-level ------------------------------------------------

    def additional_costs_per_piece(self, material, additional_costs):
        """
        X7 = sum(u_i) / annual_volume
        """
        total = sum(c.get('cost_value', 0) for c in (additional_costs or []))
        lifetime_volume = material.get('lifetime_volume', 0)

        additional_per_pcs = total / lifetime_volume

        return additional_per_pcs

    # --- Total cost aggregation ----------------------------------------------

    def calculate_total_logistics_cost(self, material):
        """
        Returns a dict including every calculated parameter.
        """
        try:
            # Material intermediates
            lif_vol = self.lifetime_volume(material)

            # Packaging
            pkg_pp = self.packaging_cost_per_piece(material, packaging_config)
            pkg_total = self.packaging_cost_total(material, packaging_config)
            pkg_plant = self.packaging_cost_plant_total(material, packaging_config)
            pkg_coc = self.packaging_cost_coc_total(material, packaging_config)

            # Customs
            cust_pp = self.customs_cost_per_piece(material, customs_config)

            # Transport & CO2
            tr_pp, co2_pp = self.transport_cost_per_piece(material, transport_config, location_config, co2_config)

            # Warehouse
            wh_pp = self.warehouse_cost_per_piece(material, warehouse_config, interest_config)

            # Additional & repacking
            rep_pp = self.calculate_repacking_cost_per_piece(material, repacking_config)
            add_pp = self.additional_costs_per_piece(material, additional_costs)

            # Totals
            total_pp = pkg_pp + rep_pp + cust_pp + tr_pp + wh_pp + add_pp + (co2_pp if include_co2 else 0)
            av = material.get('annual_volume', 0)
            total_annual = total_pp * av

            return {
                'material_id': material.get('material_no'),
                'supplier_id': supplier.get('vendor_id'),
                # Material
                'lifetime_volume': lif_vol,
                # Packaging
                'packaging_cost_per_piece': pkg_pp,
                'packaging_cost_total': pkg_total,
                'packaging_cost_plant_total': pkg_plant,
                'packaging_cost_coc_total': pkg_coc,
                # Customs
                'customs_cost_per_piece': cust_pp,
                # Transport
                'transport_cost_per_piece': tr_pp,
                'energy_consumption': self.energy_consumption(transport_config),
                'co2_conversion_factor': self.co2_conversion_factor(transport_config, location_config),
                # CO2
                'annual_co2_cost_per_piece': co2_pp,
                # Warehouse
                'warehouse_cost_per_piece': wh_pp,
                'storage_locations_total': self.storage_locations_total(material, warehouse_config),
                'local_storage_locations': self.storage_locations_local(material, warehouse_config),
                'inventory_days': self.inventory_days(material, warehouse_config),
                'safety_stock_days': self.safety_stock_days(warehouse_config),
                # Additional
                'repacking_cost_per_piece': rep_pp,
                'additional_cost_per_piece': add_pp,
                # Totals
                'total_cost_per_piece': total_pp,
                'total_annual_cost': total_annual,
                # Timestamp
                'calculation_date': str(pd.Timestamp.now()) if 'pd' in globals() else str(_dt.now()),
            }

        except Exception as e:
            self.calculation_errors.append(f"Total calculation error: {e}")
            return None

    def calculate_all_costs(
        self, materials, suppliers,
        packaging_configs, transport_configs, warehouse_configs,
        include_co2=True, operations_configs=None, location_configs=None,
        repacking_configs=None, customs_configs=None, co2_configs=None,
        interest_configs=None, additional_costs=None
    ):
        results = []
        self.calculation_errors.clear()
        co2_cfg = (co2_configs or [{}])[0]
        int_cfg = (interest_configs or [{}])[0]

        for m in materials:
            for s in suppliers:
                # pick the right configs by material/supplier
                pkg = next((p for p in packaging_configs 
                             if p.get('material_id') == m['material_no']
                             and p.get('supplier_id') == s['vendor_id']), {})
                tr = next((t for t in transport_configs 
                             if t.get('material_id') == m['material_no']
                             and t.get('supplier_id') == s['vendor_id']), {})
                wh = next((w for w in warehouse_configs 
                             if w.get('material_id') == m['material_no']
                             and w.get('supplier_id') == s['vendor_id']), {})

                res = self.calculate_total_logistics_cost(
                    m, s, pkg, tr, wh,
                    operations_configs and operations_configs[0],
                    location_configs and location_configs[0],
                    repacking_configs and repacking_configs[0],
                    next((c for c in customs_configs or [] if c.get('hs_code') == m.get('hs_code')), {}),
                    co2_cfg, int_cfg, additional_costs, include_co2
                )
                if res:
                    results.append(res)
        return results

    def get_calculation_errors(self):
        return self.calculation_errors

    def validate_configuration(self, *args, **kwargs):
        # (unchanged)
        return []
    


    
