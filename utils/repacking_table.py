# Packaging Operation Cost Table

PACKAGING_OPERATION_COSTS = {
    "None": [
        {
            "supplier_packaging": "N/A",
            "operation_type": "N/A",
            "kb_packaging": "N/A",
            "cost": 0.00,
            "unit": "per part"
        },
    ],
    "light (up to 0,050kg)": [
        {
            "supplier_packaging": "one-way tray in cardboard/wooden box",
            "operation_type": "each part individually",
            "kb_packaging": "returnable trays",
            "cost": 0.10,
            "unit": "per part"
        },
        {
            "supplier_packaging": "one-way tray in cardboard/wooden box",
            "operation_type": "each tray individually",
            "kb_packaging": "one-way tray in KLT",
            "cost": 0.12,
            "unit": "per tray"
        },
        {
            "supplier_packaging": "Bulk (poss. in bag) in cardboard/wooden box",
            "operation_type": "whole bag or dump without bag",
            "kb_packaging": "KLT",
            "cost": 0.24,
            "unit": "per bag/bulk transfer"
        }
    ],
    "moderate (up to 0,150kg)": [
        {
            "supplier_packaging": "Einwegblister im Karton/Holzkiste",
            "operation_type": "each part individually",
            "kb_packaging": "returnable trays",
            "cost": 0.15,
            "unit": "per part"
        },
        {
            "supplier_packaging": "Einwegblister im Karton/Holzkiste",
            "operation_type": "ganzer Tray",
            "kb_packaging": "one-way tray in KLT",
            "cost": 0.20,
            "unit": "per tray"
        },
        {
            "supplier_packaging": "Bulk (poss. in bag) in cardboard/wooden box",
            "operation_type": "whole bag or dump without bag",
            "kb_packaging": "KLT",
            "cost": 0.40,
            "unit": "per bag/bulk transfer"
        }
    ],
    "heavy (from 0,150kg)": [
        {
            "supplier_packaging": "Einwegblister im Karton/Holzkiste",
            "operation_type": "each part individually",
            "kb_packaging": "returnable trays",
            "cost": 0.33,
            "unit": "per part"
        },
        {
            "supplier_packaging": "Einwegblister im Karton/Holzkiste",
            "operation_type": "ganzer Tray",
            "kb_packaging": "one-way tray in KLT",
            "cost": 0.65,
            "unit": "per tray"
        },
        {
            "supplier_packaging": "Bulk (poss. in bag) in cardboard/wooden box",
            "operation_type": "whole bag or dump without bag",
            "kb_packaging": "KLT",
            "cost": 1.00,
            "unit": "per bag/bulk transfer"
        }
    ]
}
