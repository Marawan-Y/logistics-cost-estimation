# --- calculations.py ---
"""
Logistics Cost Calculation Engine

This module contains the core calculation logic for computing logistics costs
based on material, supplier, packaging, transport, and warehouse parameters.
"""
import math
from .packaging_tables import STANDARD_BOXES, SPECIAL_PACKAGING, ADDITIONAL_PACKAGING, ACCESSORY_PACKAGING
from .repacking_table import PACKAGING_OPERATION_COSTS

class LogisticsCostCalculator:
    """
    Main calculator class for logistics cost computations.
    """
    def __init__(self):
        self.calculation_errors = []

    # --- Material-level calculations -----------------------------------------
    def lifetime_volume(self, material):
        """
        d = lifetime_volume = annual_volume * lifetime_years
        Using lifetime_volume directly from material if lifetime_years not available
        """
        lifetime_years = material.get('life_time_years', 0)
        annual_volume = material.get('annual_volume', 0)
        lifetime_vol= lifetime_years * annual_volume
        return lifetime_vol

    # --- Operations-level calculations -----------------------------------------
    def MOQ(self, material, supplier, packaging_config):
        """
        Minimum Order Quantity (MOQ) based on operations configuration.
        """
        daily_demand = material.get('daily_demand', 0)
        deliveries_per_month = supplier.get('deliveries_per_month', 1)
        fill_qty_tray = packaging_config.get('fill_qty_tray', 1)
        no_trays_per_sp_pal = packaging_config.get('trays_per_sp_pal', 1)
        sp_pallets_per_lu = packaging_config.get('sp_pallets_per_lu', 0)

        fill_qty_box = packaging_config.get('fill_qty_box', 0)
        b_per_layer = self.boxes_per_layer(packaging_config)

        sp_needed = packaging_config.get('sp_needed', 'No')
        sp_type = packaging_config.get('sp_type', '')

        if sp_needed == 'Yes' and sp_type == 'Standalone tray':
            moq = math.ceil((daily_demand * 20) / (deliveries_per_month * fill_qty_tray * no_trays_per_sp_pal * sp_pallets_per_lu)) * fill_qty_tray * no_trays_per_sp_pal * sp_pallets_per_lu
        else:
            moq = math.ceil((daily_demand * 20) / (deliveries_per_month * fill_qty_box * b_per_layer)) * fill_qty_box * b_per_layer

        return moq

    # --- Packaging-level calculations -----------------------------------------
    # ---------------- Standard Boxes Table Parameters ----------------
    def packaging_characteristics(self, packaging_config):
        """
        B [2:28] @ "Standard Boxes" Sheet -- wrt [A]
        This is a direct value from the packaging tables.
        """
        b_type = packaging_config.get('box_type', 'None')
        p_char = STANDARD_BOXES.get(b_type, {}).get("Packaging_Characteristics", "")
        return p_char

    def packaging_weight(self, packaging_config):
        """
        G [2:28] @ "Standard Boxes" Sheet -- wrt [A]
        This is a direct value from the packaging tables.
        """
        b_type = packaging_config.get('box_type', 'None')
        p_weight = STANDARD_BOXES.get(b_type, {}).get("MT_weight_kg", 0)
        return p_weight

    def no_boxes_per_lu(self, packaging_config):
        """
        H[#] @ "Standard Boxes" Sheet -- [A]
        This is a direct value from the packaging tables.
        """
        b_type = packaging_config.get('box_type', 'None')
        b_per_lu = STANDARD_BOXES.get(b_type, {}).get("Pcs_Boxes_per_LU", 1)
        return max(b_per_lu, 1)  # Avoid division by zero

    def price_per_box(self, packaging_config):
        """
        C[2:28] @ "Standard Boxes" Sheet -- [A]
        This is a direct value from the packaging tables.
        """
        b_type = packaging_config.get('box_type', 'None')
        b_price = STANDARD_BOXES.get(b_type, {}).get("Cost_per_pcs", 0)
        return b_price

    def sp_packaging_weight(self, packaging_config):
        """
        G [32:34] @ "Standard Boxes" Sheet -- [A][32:34]
        This is a direct value from the packaging tables.
        """
        sp_p_type = packaging_config.get('sp_type', '')
        sp_weight = SPECIAL_PACKAGING.get(sp_p_type, {}).get("MT_weight_kg", 0)
        return sp_weight

    def price_per_tray(self, packaging_config):
        """
        C[32:34] @ "Standard boxes" Sheet -- [A][32:34]
        This is a direct value from the packaging tables.
        """
        sp_p_type = packaging_config.get('sp_type', '')
        price_tray = SPECIAL_PACKAGING.get(sp_p_type, {}).get("Cost_per_pcs", 0)
        return price_tray

    def price_sp_pallets(self, packaging_config):
        """
        C[36] @ "Standard Boxes" Sheet
        This is a direct value from the packaging tables.
        """
        sp_pallet_price = ADDITIONAL_PACKAGING.get("Pallet", {}).get("Cost_per_pcs", 0)
        return sp_pallet_price

    def price_sp_cover(self, packaging_config):
        """
        C[37] @ "Standard Boxes" Sheet
        This is a direct value from the packaging tables.
        """
        price_cover = ADDITIONAL_PACKAGING.get("Cover", {}).get("Cost_per_pcs", 0)
        return price_cover

    def sp_pallet_weight(self, packaging_config):
        """
        G[36] @ "Standard Boxes" Sheet
        This is a direct value from the packaging tables.
        """
        sp_pallet_weight = ADDITIONAL_PACKAGING.get("Pallet", {}).get("MT_weight_kg", 0)
        return sp_pallet_weight

    def weight_pallet(self, packaging_config):
        """
        M [9/10] @ "Standard Boxes" Sheet -- [J][9/10]
        This is a direct value from the packaging tables.
        """
        p_type = packaging_config.get('pallet_type', 'EURO Pallet Price')
        pallet_weight = ACCESSORY_PACKAGING.get(p_type, {}).get("Ave_Weight_kg", 20)
        return pallet_weight

    def pallet_price(self, packaging_config):
        """
        L[9/10] @ "Standard Boxes" Sheet -- [J][9/10]
        This is a direct value from the packaging tables.
        """
        p_type = packaging_config.get('pallet_type', 'EURO Pallet Price')
        pallet_price = ACCESSORY_PACKAGING.get(p_type, {}).get("Ave_Price", 24.5)
        return pallet_price

    def boxes_per_layer(self, packaging_config):
        """
        H[#] @ "Standard Boxes" Sheet -- [A]
        This is a direct value from the packaging tables.
        """
        b_type = packaging_config.get('box_type', 'None')
        b_per_layer = STANDARD_BOXES.get(b_type, {}).get("Boxes_per_layer", 1)
        return max(b_per_layer, 1)  # Avoid division by zero

    # --- Packaging-level calculations continued ----------------------------
    def packaging_loop_days(self, packaging_config):
        """
        a1.1.2 = sum of all loop stages from loop_data dict
        """
        loop_data = packaging_config.get('loop_data', {})
        if isinstance(loop_data, dict):
            return sum(v for v in loop_data.values() if isinstance(v, (int, float)))
        return 0

    def loop_coc(self, packaging_config, operations_config=None):
        """
        a2.2.1.1 = Loop CoC = a1.1.2 (packaging loop days) + a2.1.1 (CoC-specific loop)
        """
        plant_loop = self.packaging_loop_days(packaging_config)
        if operations_config:
            sub_sup_days = operations_config.get('subsupplier_box_days', 0)
        else:
            sub_sup_days = 0
        return plant_loop + sub_sup_days

    def total_packaging_loop(self, packaging_config, operations_config=None):
        """
        a1.1.2.1 = total packaging loop days = sum of loop_data
        """
        return self.loop_coc(packaging_config, operations_config)

    def filling_qty_pcs_per_lu(self, packaging_config):
        """
        p = a1.1.3 * a1.4.1
        a1.1.3 = fill_qty_box
        a1.4.1 = boxes_per_lu from table
        """
        fill_qty_box = packaging_config.get('fill_qty_box', 1)
        boxes_per_lu = self.no_boxes_per_lu(packaging_config)
        fill_qty_lu = fill_qty_box * boxes_per_lu
        return max(fill_qty_lu, 1)  # Avoid division by zero

    def empties_scrapping_wood(self, material, packaging_config):
        """
        c = (a1.1.1.1 / a1.1.3) * (c1 / 1000)
        """
        av = material.get('annual_volume', 0)
        fill = packaging_config.get('fill_qty_box', 1)
        p_weight = self.packaging_weight(packaging_config)
        b_type = packaging_config.get('box_type', 'None')
        if fill > 0 and b_type == 'Wooden Box':
            return (av / fill) * (p_weight / 1000.0) * 160
        return 0.0

    # ** PLANT **
    def packaging_cost_plant(self, material, packaging_config):
        """
        Packaging cost plant total
        """
        try:
            daily_demand = material.get('daily_demand', 0)
            if daily_demand <= 0:
                return 0

            loop_plant_days = self.packaging_loop_days(packaging_config)
            fill_qty_box = max(packaging_config.get('fill_qty_box', 1), 1)
            b_per_lu = self.no_boxes_per_lu(packaging_config)
            adds = packaging_config.get('add_pack_price', 0)
            b_price = self.price_per_box(packaging_config)
            pallet_price = self.pallet_price(packaging_config)

            no_box_loop_plant = math.ceil(((daily_demand * loop_plant_days) / fill_qty_box if fill_qty_box > 0 else 0) / 10) * 10

            no_lu_loop_plant = math.ceil(no_box_loop_plant / b_per_lu if b_per_lu > 0 else 0)

            pck_cost_plant = (no_box_loop_plant * (adds + b_price)) + (no_lu_loop_plant * pallet_price)

            return max(pck_cost_plant, 0)
        except Exception as e:
            self.calculation_errors.append(f"Packaging plant cost error: {e}")
            return 0

    # ** CoC **
    def packaging_cost_coc(self, material, packaging_config, operations_config):
        """
        Packaging cost CoC total
        """
        try:
            daily_demand = material.get('daily_demand', 0)
            if daily_demand <= 0:
                return 0

            fill_box = max(packaging_config.get('fill_qty_box', 1), 1)
            b_price = self.price_per_box(packaging_config)
            pallet_price = self.pallet_price(packaging_config)

            if operations_config:
                subsupplier_days = operations_config.get('subsupplier_box_days', 0)
            else:
                subsupplier_days = 0

            b_per_lu = self.no_boxes_per_lu(packaging_config)
            fill_tray = max(packaging_config.get('fill_qty_tray', 1), 1)
            total_pck_loop_days = max(self.total_packaging_loop(packaging_config, operations_config), 1)
            sp_needed = packaging_config.get('sp_needed', 'No')
            add_sp_pack = packaging_config.get('add_sp_pack', 'No')
            trays_per_sp_pal = max(packaging_config.get('trays_per_sp_pal', 1), 1)
            price_tray = self.price_per_tray(packaging_config)
            sp_pallet_price = self.price_sp_pallets(packaging_config)
            price_cover = self.price_sp_cover(packaging_config)
            tooling_cost = packaging_config.get('tooling_cost', 0)

            no_box_coc = (daily_demand * subsupplier_days) / fill_box if fill_box > 0 else 0
            actual_no_lu_coc = no_box_coc / b_per_lu if b_per_lu > 0 else 0
            no_lu_coc = math.ceil(actual_no_lu_coc)

            if sp_needed == 'Yes':
                no_tray_coc = daily_demand / (fill_tray * total_pck_loop_days) if (fill_tray * total_pck_loop_days) > 0 else 0
            else:
                no_tray_coc = 0

            if add_sp_pack == 'Yes' and trays_per_sp_pal > 0:
                actual_no_sp_pallet_cover = no_tray_coc / trays_per_sp_pal
                no_sp_pallet_cover = math.ceil(actual_no_sp_pallet_cover)
            else:
                no_sp_pallet_cover = 0

            pck_cost_coc = (b_price * no_box_coc) + (no_lu_coc * pallet_price) + \
                           (no_tray_coc * price_tray) + (no_sp_pallet_cover * (sp_pallet_price + price_cover)) + \
                           (tooling_cost if sp_needed == 'Yes' else 0)

            return max(pck_cost_coc, 0)
        except Exception as e:
            self.calculation_errors.append(f"Packaging CoC cost error: {e}")
            return 0

    # ** Packaging Cost Total **
    def packaging_cost_total(self, material, packaging_config, operations_config=None):
        """
        Packaging cost total = plant + coc costs
        """
        coc_cost = self.packaging_cost_coc(material, packaging_config, operations_config)
        plant_cost = self.packaging_cost_plant(material, packaging_config)
        return coc_cost + plant_cost

    # ** Packaging Cost Per Piece **
    def packaging_cost_per_piece(self, material, packaging_config, operations_config=None):
        """
        X1 = packaging cost per part pcs
        """
        try:
            scrap_paper = packaging_config.get('empties_scrap', 0)  
            scrap_wood = self.empties_scrapping_wood(material, packaging_config)
            lifetime_vol = self.lifetime_volume(material)

            if lifetime_vol <= 0:
                return 0

            total_pck_cost = self.packaging_cost_total(material, packaging_config, operations_config)


            actual_pck_per_pcs = (scrap_paper + scrap_wood + total_pck_cost) / lifetime_vol
            pck_per_pcs = math.ceil(actual_pck_per_pcs * 1000) / 1000

            return max(0.0, pck_per_pcs)

        except Exception as e:
            self.calculation_errors.append(f"Packaging per-piece error: {e}")
            return 0.0

    # --- Repacking-level calculations -----------------------------------------
    def repacking_cost_characteristics(self, repacking_config):
        """
        Look up the repacking table entry based on weight, packaging types
        """
        try:
            if not repacking_config:
                return None

            pcs_weight = repacking_config.get('pcs_weight', '')
            supplier_pack = repacking_config.get('packaging_one_way', '')
            kb_pack = repacking_config.get('packaging_returnable', '')

            # Normalize weight key: replace newline with space and strip
            key = pcs_weight.replace("\n", " ").strip()

            entries = PACKAGING_OPERATION_COSTS.get(key, [])
            if not entries:
                self.calculation_errors.append(f"Repacking lookup: no table entries for weight '{key}'")
                return None

            match = next(
                (e for e in entries
                 if e.get('supplier_packaging') == supplier_pack
                 and e.get('kb_packaging') == kb_pack),
                None
            )

            if not match:
                self.calculation_errors.append(
                    f"Repacking lookup: no matching entry for supplier_packaging='{supplier_pack}', "
                    f"kb_packaging='{kb_pack}' under weight '{key}'"
                )
                return None

            return match

        except Exception as e:
            self.calculation_errors.append(f"Repacking lookup error: {str(e)}")
            return None

    def get_repacking_cost_value(self, repacking_config):
        """
        Return the numeric per-piece cost from the lookup table
        """
        try:
            if not repacking_config:
                return 0.0

            entry = self.repacking_cost_characteristics(repacking_config)
            if entry is None:
                return 0.0

            cost = entry.get("cost", 0.0)
            unit = entry.get("unit", "").strip().lower()

            if unit == "per part":
                return max(0.0, cost)
            else:
                self.calculation_errors.append(
                    f"Repacking cost unit is '{unit}'; cannot convert to per piece without additional data"
                )
                return 0.0

        except Exception as e:
            self.calculation_errors.append(f"Repacking cost calculation error: {str(e)}")
            return 0.0

    # --- Transport-level calculations -----------------------------------------
    def pallets_per_delivery(self, material, supplier, packaging_config):
        """""
        Pallets per delivery
        """
        daily_demand = material.get('daily_demand', 0)
        deliveries_per_month = supplier.get('deliveries_per_month', 1)
        fill_qty_lu = self.filling_qty_pcs_per_lu(packaging_config)
        sp_fill_qty_pcs_lu = self.SP_Filling_Qty_Pcs_lu(packaging_config)
        sp_needed = packaging_config.get('sp_needed', 'No')

        if sp_needed == 'Yes':
            pallets_per_delivery = math.ceil((daily_demand * 20) / (deliveries_per_month * sp_fill_qty_pcs_lu))
        else:
            pallets_per_delivery = math.ceil((daily_demand * 20) / (deliveries_per_month * fill_qty_lu))

        return pallets_per_delivery

    def transport_cost_per_piece(
        self,
        transport_config,
        packaging_config,
        operations_config,
        material=None,
        supplier=None
    ):
        """
        X4 = transport cost per piece
        Now supports automatic calculation from transport database using the 5-step workflow
        """
        try:
            # Check if we should use automatic calculation
            if transport_config.get('auto_calculate', False):
                # Need supplier and material information
                if not supplier or not material:
                    self.calculation_errors.append(
                        "Supplier and material info required for automatic transport calculation"
                    )
                    return 0.0

                # Load or retrieve transport database
                import streamlit as st
                if 'transport_db' in st.session_state:
                    transport_db = st.session_state.transport_db
                else:
                    from .transport_database import TransportDatabase
                    transport_db = TransportDatabase()
                    try:
                        transport_db.load_from_json('transport_database.json')
                    except:
                        self.calculation_errors.append(
                            "Transport database not available for automatic calculation"
                        )
                        return 0.0

                # Gather all required parameters for workflow calculation
                material_weight = material.get('weight_per_pcs', 0)
                pieces_per_packaging = packaging_config.get('fill_qty_box', 1)

                # Get packaging weight from tables
                box_type = packaging_config.get('box_type', 'None')
                packaging_weight = STANDARD_BOXES.get(box_type, {}).get("MT_weight_kg", 0)

                daily_demand = material.get('daily_demand', 0)
                deliveries_per_month = supplier.get('deliveries_per_month', 1)

                # Get packaging units per pallet from tables
                packaging_units_per_pallet = self.no_boxes_per_lu(packaging_config)

                # Pallet weight (standard Euro pallet)
                pallet_weight = self.weight_pallet(packaging_config)

                # Stackability factor
                stackability_factor = float(transport_config.get('stack_factor', '2'))

                # Location info
                supplier_country = supplier.get('vendor_country', '')
                supplier_zip = supplier.get('vendor_zip', '')[:2]  # First 2 digits
                dest_country = supplier.get('country', 'DE') if supplier else 'DE'
                dest_zip = '94'  # Aldersbach default

              # --- Compute fill per LU (pcs/LU) for correct per-piece logic ---
               # Sea: use oversea fill if available; SP: use special; else standard.
                mode1 = transport_config.get('mode1', 'Road')
                if mode1 == 'Sea':
                    fill_qty_lu = packaging_config.get('fill_qty_lu_oversea', 1) or 1
                else:
                    if packaging_config.get('sp_needed') == 'Yes':
                       fill_qty_lu = self.SP_Filling_Qty_Pcs_lu(packaging_config) or 1
                    else:
                       fill_qty_lu = self.filling_qty_pcs_per_lu(packaging_config) or 1
 
                # Calculate using the 5-step workflow
                result = transport_db.calculate_transport_cost_workflow(
                    material_weight_per_piece=material_weight,
                    pieces_per_packaging=pieces_per_packaging,
                    packaging_weight=packaging_weight,
                    daily_demand=daily_demand,
                    deliveries_per_month=deliveries_per_month,
                    packaging_units_per_pallet=packaging_units_per_pallet,
                    pallet_weight=pallet_weight,
                    stackability_factor=stackability_factor,
                    supplier_country=supplier_country,
                    supplier_zip=supplier_zip,
                    dest_country=dest_country,
                    dest_zip=dest_zip,
                    fill_qty_lu=fill_qty_lu
                )

                if result.get('success'):
                    # Handle bonded warehouse if needed
                    if transport_config.get('use_bonded_warehouse', False):
                        mode1 = transport_config.get('mode1', 'Road')
                        incoterm_code = operations_config.get('incoterm_code', '') if operations_config else ''
                        if mode1 == 'Sea' and incoterm_code in ['FCA', 'FOB']:
                            # Add bonded warehouse cost per piece
                            bonded_cost_per_delivery = 50.0  # Example bonded warehouse cost
                            monthly_demand = result['calculation_details']['monthly_demand_per_delivery']
                            bonded_cost_per_piece = bonded_cost_per_delivery / monthly_demand if monthly_demand > 0 else 0
                            return result['price_per_piece'] + bonded_cost_per_piece

                    return result['price_per_piece']
                else:
                    self.calculation_errors.append(result.get('error', 'Transport calculation failed'))
                    return 0.0
            else:
                # Legacy manual calculation
                mode1 = transport_config.get('mode1', 'Road')
                cost_lu = transport_config.get('cost_lu', 0)
                cost_bonded = transport_config.get('cost_bonded', 0)
                fill_qty_lu_oversea = packaging_config.get('fill_qty_lu_oversea', 1) or 1
                incoterm_code = operations_config.get('incoterm_code', '') if operations_config else ''
                fill_qty_lu = self.filling_qty_pcs_per_lu(packaging_config) or 1

                if mode1 == 'Sea':
                    if incoterm_code in ['FCA', 'FOB']:
                        tp_per_piece = (cost_lu / fill_qty_lu_oversea) + (cost_bonded / fill_qty_lu)
                    else:
                        tp_per_piece = cost_lu / fill_qty_lu_oversea
                else:
                    tp_per_piece = cost_lu / fill_qty_lu

                return max(0.0, tp_per_piece)
        except Exception as e:
            self.calculation_errors.append(f"Transport cost error: {e}")
            return 0.0

    # --- CO2-level calculations -----------------------------------------
    def energy_consumption(self, transport_config):
        """
        o2 = energy consumption factor based on transport mode
        """
        mode1 = transport_config.get('mode1', 'Road')

        if mode1 == 'Sea':
            return 0.006
        elif mode1 == 'Road':
            return 0.04415
        elif mode1 == 'Rail':
            return 0.0085
        else:
            return 0.04415  # Default to Road

    def weight_per_lu(self, packaging_config, material):
        """
        o1.1 = weight per LU (kg)
        """
        try:
            sp_needed = packaging_config.get('sp_needed', 'No')
            trays_per_sp_pal = packaging_config.get('trays_per_sp_pal', 0)
            sp_pallets_per_lu = packaging_config.get('sp_pallets_per_lu', 0)
            sp_p_type = packaging_config.get('sp_type', '')
            fill_qty_box = packaging_config.get('fill_qty_box', 0)
            fill_qty_tray = max(packaging_config.get('fill_qty_tray', 1), 1)
            add_sp_pack = packaging_config.get('add_sp_pack', 'No')
            weight_per_piece = material.get('weight_per_pcs', 0)

            boxes_per_lu = self.no_boxes_per_lu(packaging_config)
            sp_weight = self.sp_packaging_weight(packaging_config)
            p_weight = self.packaging_weight(packaging_config)
            fill_qty_lu = self.filling_qty_pcs_per_lu(packaging_config)
            pallet_weight = self.weight_pallet(packaging_config)
            sp_pallet_weight = self.sp_pallet_weight(packaging_config)

            if sp_needed == 'Yes' and sp_p_type == 'Inlay tray pallet size':
                weight_per_lu = (fill_qty_box * weight_per_piece) + \
                               ((fill_qty_box / fill_qty_tray) * sp_weight if fill_qty_tray > 0 else 0) + p_weight
            elif sp_needed == 'Yes' and sp_p_type == 'Inlay Tray':
                weight_per_lu = (fill_qty_lu * weight_per_piece) + \
                               ((fill_qty_box / fill_qty_tray) * sp_weight if fill_qty_tray > 0 else 0) + pallet_weight
            elif sp_needed == 'Yes' and sp_p_type == 'Standalone tray':
                weight_per_lu = (fill_qty_tray * trays_per_sp_pal * sp_pallets_per_lu * weight_per_piece) + \
                               (sp_pallets_per_lu * sp_pallet_weight)
            else:
                weight_per_lu = (weight_per_piece * fill_qty_lu) + (p_weight * boxes_per_lu) + pallet_weight

            return max(weight_per_lu, 0)
        except Exception as e:
            self.calculation_errors.append(f"Weight per LU error: {e}")
            return 1  # Return 1 to avoid division by zero

    def total_tons(self, material, packaging_config):
        """
        o1 = [o1.1 * (annual_volume/p)] / 1000
        """
        try:
            fill_qty_lu = self.filling_qty_pcs_per_lu(packaging_config)
            if fill_qty_lu <= 0:
                fill_qty_lu = 1

            weight_per_lu = self.weight_per_lu(packaging_config, material)
            annual_volume = material.get('annual_volume', 0)

            total_tons = (weight_per_lu * (annual_volume / fill_qty_lu)) / 1000.0
            return max(total_tons, 0)
        except Exception as e:
            self.calculation_errors.append(f"Total tons error: {e}")
            return 0

    def emission_kg_co2(self, material, transport_config, packaging_config, supplier, co2_config):
        """
        emission [kg CO2] = total_tons * energy_consumption * distance * conversion_factor
        """
        try:
            total_tons = self.total_tons(material, packaging_config)
            energy_consumption = self.energy_consumption(transport_config)

            # Get distance from location config
            distance_km = supplier.get('distance', 100) if supplier else 100

            # Get CO2 conversion factor from co2_config
            if co2_config:
                co2_conversion_factor = float(co2_config.get('co2_conversion_factor', '3.17'))
            else:
                co2_conversion_factor = 3.17  # Default

            emission = total_tons * energy_consumption * distance_km * co2_conversion_factor
            return max(emission, 0)
        except Exception as e:
            self.calculation_errors.append(f"CO2 emission error: {e}")
            return 0

    def co2_cost_per_piece(self, material, transport_config, packaging_config, supplier, co2_config):
        """
        X5 = CO2 cost per piece
        """
        try:
            emission = self.emission_kg_co2(material, transport_config, packaging_config, supplier, co2_config)
            annual_volume = material.get('annual_volume', 1)
            if annual_volume <= 0:
                annual_volume = 1

            # Get CO2 cost per ton from co2_config
            co2_cost_per_ton = co2_config.get('cost_per_ton', 0) if co2_config else 0

            actual_co2_per_pcs = (emission * (co2_cost_per_ton / 1000.0)) / annual_volume
            co2_per_pcs = math.ceil(actual_co2_per_pcs * 1000) / 1000
            return max(co2_per_pcs, 0)
        except Exception as e:
            self.calculation_errors.append(f"CO2 cost error: {e}")
            return 0

    # --- Customs-level calculations -----------------------------------------
    def duty_cost_per_piece(self, material, customs_config, transport_config, packaging_config, operations_config):
        """
        Duty cost calculation
        """
        try:
            if not customs_config:
                return 0

            Pcs_Price = material.get('Pcs_Price', 0)
            dr = customs_config.get('duty_rate', 0) / 100.0
            tp_per_piece = self.transport_cost_per_piece(transport_config, packaging_config, operations_config)

            dc = dr * (Pcs_Price + tp_per_piece)
            return max(dc, 0)
        except Exception as e:
            self.calculation_errors.append(f"Duty cost error: {e}")
            return 0

    def tariff_cost_per_piece(self, material, customs_config):
        """
        Tariff cost calculation
        """
        try:
            if not customs_config:
                return 0

            Pcs_Price = material.get('Pcs_Price', 0)
            tr = customs_config.get('tariff_rate', 0) / 100.0

            tc = tr * Pcs_Price
            return max(tc, 0)
        except Exception as e:
            self.calculation_errors.append(f"Tariff cost error: {e}")
            return 0

    def customs_cost_per_piece(self, material, duty_rate_percent, transport_config, packaging_config, operations_config):
        """
        X3 = customs cost per piece using direct duty rate input
        """
        try:
            if not duty_rate_percent or duty_rate_percent <= 0:
                return 0.0

            Pcs_Price = material.get('Pcs_Price', 0)
            dr = duty_rate_percent / 100.0
            tp_per_piece = self.transport_cost_per_piece(transport_config, packaging_config, operations_config)

            dc = dr * (Pcs_Price + tp_per_piece)
            return max(dc, 0)
        except Exception as e:
            self.calculation_errors.append(f"Duty cost error: {e}")
            return 0

    # --- Warehouse-level calculations -----------------------------------------
    def SP_Filling_Qty_Pcs_lu(self, packaging_config):
        """
        'Special Packaging' - Filling quantity Pcs Per LU
        """
        try:
            sp_needed = packaging_config.get('sp_needed', 'No')
            if sp_needed != 'Yes':
                return 0

            trays_per_sp_pal = packaging_config.get('trays_per_sp_pal', 0)
            sp_pallets_per_lu = packaging_config.get('sp_pallets_per_lu', 0)
            sp_p_type = packaging_config.get('sp_type', '')
            fill_qty_box = packaging_config.get('fill_qty_box', 0)
            fill_qty_tray = max(packaging_config.get('fill_qty_tray', 1), 1)
            boxes_per_lu = self.no_boxes_per_lu(packaging_config)

            if sp_p_type == 'Inlay tray pallet size':
                sp_fill_qty_pcs_lu = fill_qty_box / (fill_qty_tray ** 2) if fill_qty_tray > 0 else 0
            elif sp_p_type == 'Inlay Tray':
                sp_fill_qty_pcs_lu = fill_qty_box * boxes_per_lu
            elif sp_p_type == 'Standalone tray':
                sp_fill_qty_pcs_lu = fill_qty_tray * trays_per_sp_pal * sp_pallets_per_lu
            else:
                sp_fill_qty_pcs_lu = 0

            return max(sp_fill_qty_pcs_lu, 0)
        except Exception as e:
            self.calculation_errors.append(f"SP filling qty error: {e}")
            return 0

    def inventory_days(self, material, packaging_config):
        """
        s1.1 = No. of days
        """
        try:
            daily_demand = material.get('daily_demand', 0)
            if daily_demand <= 0:
                return 0

            sp_needed = packaging_config.get('sp_needed', 'No')
            sp_fill_qty_pcs_lu = self.SP_Filling_Qty_Pcs_lu(packaging_config)
            fill_qty_lu = self.filling_qty_pcs_per_lu(packaging_config)

            if sp_needed == 'Yes' and sp_fill_qty_pcs_lu > 0:
                no_days = sp_fill_qty_pcs_lu / daily_demand
            else:
                no_days = fill_qty_lu / daily_demand if daily_demand > 0 else 0

            return max(no_days, 0)
        except Exception as e:
            self.calculation_errors.append(f"Inventory days error: {e}")
            return 0

    def safety_stock_days(self, operations_config, packaging_config, material):
        """
        s2.1 = coverage per pallet (days)
        """
        try:
            if not operations_config:
                return 0

            daily_demand = material.get('daily_demand', 0)
            if daily_demand <= 0:
                return 0

            sp_needed = packaging_config.get('sp_needed', 'No')
            sp_fill_qty_pcs_lu = self.SP_Filling_Qty_Pcs_lu(packaging_config)
            fill_qty_lu = self.filling_qty_pcs_per_lu(packaging_config)
            lead_time = operations_config.get('lead_time', 0)

            if sp_needed == 'Yes' and sp_fill_qty_pcs_lu > 0:
                actual_safety_days = (lead_time * daily_demand) / sp_fill_qty_pcs_lu
                safety_days = math.ceil(actual_safety_days)
            elif fill_qty_lu > 0:
                actual_safety_days = (lead_time * daily_demand) / fill_qty_lu
                safety_days = math.ceil(actual_safety_days)
            else:
                safety_days = 0

            return max(safety_days, 0)
        except Exception as e:
            self.calculation_errors.append(f"Safety stock days error: {e}")
            return 0

    def storage_locations_local(self, material, packaging_config):
        """
        s1 = storage locations for local supply
        """
        try:
            no_days = self.inventory_days(material, packaging_config)
            if no_days > 0:
                actual_storage_loc_local = 5 / no_days
                storage_loc_local = math.ceil(actual_storage_loc_local)
            else:
                storage_loc_local = 5  # Default

            return max(storage_loc_local, 0)
        except Exception as e:
            self.calculation_errors.append(f"Storage locations error: {e}")
            return 0

    def storage_locations_total(self, material, packaging_config, operations_config):
        """
        X6: s = s1 + s2
        """
        try:
            storage_loc_local = self.storage_locations_local(material, packaging_config)
            safety_days = self.safety_stock_days(operations_config, packaging_config, material)

            storage_loc_total = storage_loc_local + safety_days
            return max(storage_loc_total, 0)
        except Exception as e:
            self.calculation_errors.append(f"Total storage locations error: {e}")
            return 0

    def warehouse_cost_per_piece(self, material, warehouse_config, packaging_config, operations_config):
        """
        X6 = (s * t * 12) / annual_volume
        """
        try:
            if not warehouse_config:
                return 0

            storage_loc_total = self.storage_locations_total(material, packaging_config, operations_config)
            cost_per_loc = warehouse_config.get('cost_per_loc', 0)
            annual_volume = material.get('annual_volume', 1)
            if annual_volume <= 0:
                annual_volume = 1

            actual_warehouse_per_pcs = (12 * storage_loc_total * cost_per_loc) / annual_volume
            warehouse_per_pcs = math.ceil(actual_warehouse_per_pcs * 1000) / 1000

            return max(warehouse_per_pcs, 0)

        except Exception as e:
            self.calculation_errors.append(f"Warehouse cost error: {e}")
            return 0.0

    # ---- Additional cost level -----------------
    def additional_costs_per_piece(self, material, additional_costs):
        """
        X7 = sum(u_i) / lifetime_volume
        """
        try:
            if not additional_costs:
                return 0

            total = sum(c.get('cost_value', 0) for c in (additional_costs or []))
            lifetime_volume = self.lifetime_volume(material)

            if lifetime_volume > 0:
                additional_per_pcs = total / lifetime_volume
            else:
                additional_per_pcs = 0

            return max(additional_per_pcs, 0)
        except Exception as e:
            self.calculation_errors.append(f"Additional costs error: {e}")
            return 0

    # --- Total cost aggregation ----------------
    def additional_costs_per_piece(self, material, additional_costs):
        """
        X7 = sum(u_i) / lifetime_volume
        """
        try:
            if not additional_costs:
                return 0

            total = sum(c.get('cost_value', 0) for c in (additional_costs or []))
            lifetime_volume = self.lifetime_volume(material)

            if lifetime_volume > 0:
                additional_per_pcs = total / lifetime_volume
            else:
                additional_per_pcs = 0

            return max(additional_per_pcs, 0)
        except Exception as e:
            self.calculation_errors.append(f"Additional costs error: {e}")
            return 0

    # --- Total cost aggregation ----------------
    def calculate_total_logistics_cost(
        self,
        material,
        supplier,
        packaging_config,
        transport_config,
        warehouse_config,
        repacking_config,
        duty_rate_percent=0,  # Changed from customs_config to direct rate
        co2_config=None,
        additional_costs=None,
        operations_config=None,
        inventory_config=None
    ):
        """
        Calculate total logistics cost per piece for a material-supplier combination.
        """
        try:
            packaging_cost = self.packaging_cost_per_piece(material, packaging_config, operations_config)
            repacking_cost = self.get_repacking_cost_value(repacking_config)
            customs_cost = self.customs_cost_per_piece(
                material, duty_rate_percent, transport_config, packaging_config, operations_config
            )
            transport_cost = self.transport_cost_per_piece(
                transport_config,
                packaging_config,
                operations_config,
                supplier=supplier,
                material=material
            )
            co2_cost = self.co2_cost_per_piece(
                material, transport_config, packaging_config, supplier, co2_config
            )
            warehouse_cost = self.warehouse_cost_per_piece(
                material, warehouse_config, packaging_config, operations_config
            )
            additional_cost = self.additional_costs_per_piece(material, additional_costs)

            # --- NEW: derive transport cost per LU from per-piece cost ---
            if transport_config.get('mode1') == 'Sea':
                fill_qty_used = packaging_config.get('fill_qty_lu_oversea', 1) or 1
            else:
                fill_qty_used = self.filling_qty_pcs_per_lu(packaging_config) or 1
            transport_cost_lu = transport_cost * fill_qty_used
            # --------------------------------------------------------------

            total_cost_per_piece = (
                packaging_cost
                + repacking_cost
                + customs_cost
                + transport_cost
                + warehouse_cost
                + additional_cost
                + co2_cost
            )
            annual_volume = material.get('annual_volume', 0)
            total_annual_cost = total_cost_per_piece * annual_volume

            # -- Result List --
            coc_cost = self.packaging_cost_coc(material, packaging_config, operations_config)
            plant_cost = self.packaging_cost_plant(material, packaging_config)
            packaging_cost_total = self.packaging_cost_total(material, packaging_config, operations_config)
            scrap_wood = self.empties_scrapping_wood(material, packaging_config)
            p_weight = self.packaging_weight(packaging_config)
            boxes_per_lu = self.no_boxes_per_lu(packaging_config)
            pallet_weight = self.weight_pallet(packaging_config)
            fill_qty_lu = self.filling_qty_pcs_per_lu(packaging_config)
            sp_fill_qty_pcs_lu = self.SP_Filling_Qty_Pcs_lu(packaging_config)
            b_price = self.price_per_box(packaging_config)
            sp_weight = self.sp_packaging_weight(packaging_config)
            price_tray = self.price_per_tray(packaging_config)
            sp_pallet_price = self.price_sp_pallets(packaging_config)
            price_cover = self.price_sp_cover(packaging_config)
            sp_pallet_weight = self.sp_pallet_weight(packaging_config)
            pallet_price = self.pallet_price(packaging_config)

            daily_demand = material.get('daily_demand', 0)
            loop_plant_days = self.packaging_loop_days(packaging_config)
            fill_qty_box = max(packaging_config.get('fill_qty_box', 1), 1)
            b_per_lu = self.no_boxes_per_lu(packaging_config)
            no_box_loop_plant = math.ceil(((daily_demand * loop_plant_days) / fill_qty_box if fill_qty_box > 0 else 0) / 10) * 10
            no_lu_loop_plant = math.ceil(no_box_loop_plant / b_per_lu if b_per_lu > 0 else 0)

            subsupplier_days = operations_config.get('subsupplier_box_days', 0) if operations_config else 0
            no_box_coc = (daily_demand * subsupplier_days) / fill_qty_box if fill_qty_box > 0 else 0
            no_lu_coc = no_box_coc / b_per_lu if b_per_lu > 0 else 0
            fill_tray = max(packaging_config.get('fill_qty_tray', 1), 1)
            total_pck_loop_days = max(self.total_packaging_loop(packaging_config, operations_config), 1)
            trays_per_sp_pal = max(packaging_config.get('trays_per_sp_pal', 1), 1)
            sp_needed = packaging_config.get('sp_needed', 'No')
            add_sp_pack = packaging_config.get('add_sp_pack', 'No')
            if sp_needed == 'Yes':
                no_tray_coc = daily_demand / (fill_tray * total_pck_loop_days) if (fill_tray * total_pck_loop_days) > 0 else 0
            else:
                no_tray_coc = 0

            if add_sp_pack == 'Yes' and trays_per_sp_pal > 0:
                no_sp_pallet_cover = no_tray_coc / trays_per_sp_pal
            else:
                no_sp_pallet_cover = 0

            weight_per_lu = self.weight_per_lu(packaging_config, material)
            emission = self.emission_kg_co2(material, transport_config, packaging_config, supplier, co2_config)
            total_tons = self.total_tons(material, packaging_config)

            no_days = self.inventory_days(material, packaging_config)
            safety_days = self.safety_stock_days(operations_config, packaging_config, material)
            storage_loc_local = self.storage_locations_local(material, packaging_config)
            storage_loc_total = self.storage_locations_total(material, packaging_config, operations_config)

            # Build result dictionary
            result = {
                # Material
                'Project Name': material.get('project_name'),
                'material_id': material.get('material_no'),
                'material_desc': material.get('material_desc'),
                'Annual Volume': annual_volume,
                'SOP': material.get('sop'),
                'Price (Pcs)': material.get('Pcs_Price'),
                'lifetime_volume' : self.lifetime_volume(material),
                # Supplier
                'supplier_id': supplier.get('vendor_id'),
                'supplier_name': supplier.get('vendor_name'),
                'Vendor Country': supplier.get('vendor_country'),
                'City of Manufacture': supplier.get('city_of_manufacture'),
                'Vendor ZIP': supplier.get('vendor_zip'),
                'Deliveries per Month': supplier.get('deliveries_per_month'),
                # Operations
                'Incoterm code': operations_config.get('incoterm_code') if operations_config else 'N/A',
                'Incoterm Named Place': operations_config.get('incoterm_place') if operations_config else 'N/A',
                'MOQ': self.MOQ(material, supplier, packaging_config),
                'Call-off transfer type': operations_config.get('calloff_type') if operations_config else 'N/A',
                'Lead time (d)': operations_config.get('lead_time') if operations_config else 0,
                'Sub-Supplier Used': operations_config.get('subsupplier_used') if operations_config else 'N/A',
                # Packaging
                # -- Packaging cost --
                'packaging_cost_coc': coc_cost,
                'packaging_cost_plant': plant_cost,
                'Empty scraping (wood)': scrap_wood,
                'packaging_cost_total': packaging_cost_total,
                'packaging_cost_per_piece': packaging_cost,
                # -- Standard Packaging (Plant) --
                'packaging_type': packaging_config.get('box_type'),
                'Filling degree per box': packaging_config.get('fill_qty_box', 0),
                'Filling degree per pallet': fill_qty_lu,
                'No. of Boxes per Layer': boxes_per_lu,
                'weight pallet (empty in kg)': pallet_weight,
                'packaging_weight (Plant)': p_weight,
                'packaging_price_per_box': b_price,
                'Filling quantity (pcs / LU)': fill_qty_lu,
                # -- CoC Packaging (CoC) --
                'Special packaging required': packaging_config.get('sp_needed'),
                'packaging weight (CoC)': sp_weight,
                'price per tray': price_tray,
                'Filling quantity (pcs / LU) - SP': sp_fill_qty_pcs_lu,
                'price of sp-pallet': sp_pallet_price,
                'price of sp-cover': price_cover,
                'weight of sp-pallet': sp_pallet_weight,
                'Price / pc': pallet_price,
                # -- Total Packaging Loop --
                'Packaging Loop': self.total_packaging_loop(packaging_config, operations_config),
                'goods_receipt': packaging_config.get("loop_data", {}).get("goods receipt", 0),
                'stock_raw_materials': packaging_config.get("loop_data", {}).get("stock raw materials", 0),
                'production': packaging_config.get("loop_data", {}).get("production", 0),
                'empties_return': packaging_config.get("loop_data", {}).get("empties return", 0),
                'cleaning': packaging_config.get("loop_data", {}).get("cleaning", 0),
                'dispatch': packaging_config.get("loop_data", {}).get("dispatch", 0),
                'empties_transit_kb_to_supplier': packaging_config.get("loop_data", {}).get("empties transit (KB → Supplier)", 0),
                'empties_receipt_at_supplier': packaging_config.get("loop_data", {}).get("empties receipt (at Supplier)", 0),
                'empties_in_stock_supplier': packaging_config.get("loop_data", {}).get("empties in stock (Supplier)", 0),
                'production_contrary_loop': packaging_config.get("loop_data", {}).get("production (contrary loop)", 0),
                'stock_finished_parts': packaging_config.get("loop_data", {}).get("stock finished parts", 0),
                'dispatch_finished_parts': packaging_config.get("loop_data", {}).get("dispatch (finished parts)", 0),
                'transit_supplier_to_plant': packaging_config.get("loop_data", {}).get("transit (Supplier → KB)", 0),
                # ---- Loop Plant ----
                'No. of boxes - Plant': no_box_loop_plant,
                'No. of LUs - Plant': no_lu_loop_plant,
                # ---- Loop CoC ----
                'No. of boxes - CoC': no_box_coc,
                'No. of LUs - CoC': no_lu_coc,
                'No. of trays - CoC': no_tray_coc,
                'No. of sp-pallet covers - CoC': no_sp_pallet_cover,
                # Repacking
                'repacking_cost_per_piece': repacking_cost,
                # Customs
                'customs_cost_per_piece': customs_cost,
                'Duty Rate (% Of pcs price)': duty_rate_percent,
                # Transport
                'transport_cost_per_piece': transport_cost,
                'Transport type': transport_config.get('mode1'),
                'pallets_per_delivery': self.pallets_per_delivery(material, supplier, packaging_config),
                # UPDATED: calculated transport cost per LU
                'Transport cost per LU': transport_cost_lu,
                # Warehouse
                'warehouse_cost_per_piece': warehouse_cost,
                'storage_locations_total': storage_loc_total,
                'safety_stock_no_pal': safety_days,
                'No. of Days': no_days,
                'storage_locations_local': storage_loc_local,
                # Additional Costs
                'additional_cost_per_piece': additional_cost,
                # CO2
                'co2_cost_per_piece': co2_cost,
                'CO2 emission (kg)': emission,
                'Total tons': total_tons,
                'weight_per_lu': weight_per_lu,
                # Total Costs
                'total_cost_per_piece': total_cost_per_piece,
                'total_annual_cost': total_annual_cost,
                # Metadata
                'calculation_date': str(pd.Timestamp.now()) if 'pd' in globals() else str(datetime.now())
            }

            return result

        except Exception as e:
            self.calculation_errors.append(
                f"Total cost calculation error for {material.get('material_no', 'Unknown')} - "
                f"{supplier.get('vendor_id', 'Unknown')}: {str(e)}"
            )
            return None

    def calculate_all_costs(self, materials, suppliers, packaging_configs, transport_configs,
                         warehouse_configs, co2_configs, operations_configs=None,
                         repacking_configs=None, customs_configs=None,
                         inventory_configs=None, additional_costs=None):
        """
        Calculate logistics costs for all configured material-supplier combinations.
        """
        results = []
        self.calculation_errors = []

        # Get first config for singleton configs
        operations_config = operations_configs[0] if operations_configs else None
        supplier = suppliers[0] if suppliers else None
        repacking_config = repacking_configs[0] if repacking_configs else None
        customs_config = customs_configs[0] if customs_configs else None
        co2_config = co2_configs[0] if co2_configs else None
        warehouse_config = warehouse_configs[0] if warehouse_configs else None
        packaging_config = packaging_configs[0] if packaging_configs else None
        transport_config = transport_configs[0] if transport_configs else None

        # Calculate for each material-supplier pair
        for material in materials:
            for supplier in suppliers:
                # For now, use the first configs available
                # In a real implementation, you might want to match configs to specific pairs

                if not all([packaging_config, transport_config, warehouse_config]):
                    self.calculation_errors.append(
                        f"Missing required configs for {material['material_no']} - {supplier['vendor_id']}"
                    )
                    continue

                # Calculate costs
                result = self.calculate_total_logistics_cost(
                    material=material,
                    supplier=supplier,
                    packaging_config=packaging_config,
                    transport_config=transport_config,
                    warehouse_config=warehouse_config,
                    repacking_config=repacking_config,
                    duty_rate_percent=customs_config.get('duty_rate', 0) if customs_config else 0,
                    co2_config=co2_config,
                    additional_costs=additional_costs,
                    operations_config=operations_config,
                    inventory_config=inventory_configs[0] if inventory_configs else None
                )

                if result:
                    results.append(result)

        return results

    def get_calculation_errors(self):
        """
        Return any calculation errors that occurred.
        """
        return self.calculation_errors

    def validate_configuration(self, material, supplier, packaging_config, transport_config, warehouse_config, co2_config):
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

        # Warehouse validation
        if not warehouse_config:
            errors.append("Warehouse configuration is required")

        # CO2 validation
        if not co2_config:
            errors.append("CO2 configuration is required")

        return errors


# Import datetime if pandas is not available
try:
    import pandas as pd
except ImportError:
    from datetime import datetime
