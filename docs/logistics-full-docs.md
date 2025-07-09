# Logistics Cost Automation Platform
## Complete Documentation Suite

Version 1.0.0 | Last Updated: July 2025

---

# Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Installation Guide](#3-installation-guide)
4. [User Manual](#4-user-manual)
   - [4.1 Material Management](#41-material-management)
   - [4.2 Supplier Management](#42-supplier-management)
   - [4.3 Location Configuration](#43-location-configuration)
   - [4.4 Operations Setup](#44-operations-setup)
   - [4.5 Packaging Configuration](#45-packaging-configuration)
   - [4.6 Repacking Setup](#46-repacking-setup)
   - [4.7 Customs Configuration](#47-customs-configuration)
   - [4.8 Transport Setup](#48-transport-setup)
   - [4.9 CO₂ Configuration](#49-co2-configuration)
   - [4.10 Warehouse Setup](#410-warehouse-setup)
   - [4.11 Inventory Costs](#411-inventory-costs)
   - [4.12 Additional Costs](#412-additional-costs)
   - [4.13 Cost Calculation](#413-cost-calculation)
   - [4.14 Settings & Data Management](#414-settings--data-management)
5. [Technical Documentation](#5-technical-documentation)
6. [API Reference](#6-api-reference)
7. [Configuration Guide](#7-configuration-guide)
8. [Deployment Guide](#8-deployment-guide)
9. [Troubleshooting](#9-troubleshooting)
10. [Best Practices](#10-best-practices)
11. [Glossary](#11-glossary)
12. [Appendices](#12-appendices)

---

# 1. Introduction

## 1.1 Purpose

The Logistics Cost Automation Platform is a comprehensive solution designed to automate and optimize the calculation of total landed costs in supply chain operations. It provides procurement professionals, supply chain managers, and logistics teams with accurate, data-driven insights for making informed sourcing decisions.

## 1.2 Scope

This documentation covers:
- Complete user guidance for all features
- Technical implementation details
- System architecture and design
- API specifications
- Deployment and maintenance procedures
- Troubleshooting and support

## 1.3 Target Audience

- **End Users**: Procurement specialists, supply chain analysts, logistics coordinators
- **Administrators**: System administrators, data managers
- **Developers**: Software engineers, integration specialists
- **Management**: Decision makers requiring cost analysis reports

## 1.4 Document Conventions

| Convention | Meaning |
|------------|---------|
| **Bold** | UI elements, buttons, menu items |
| `Code` | Code snippets, file names, commands |
| *Italic* | Emphasis, first occurrence of terms |
| 📌 Note | Important information |
| ⚠️ Warning | Critical warnings |
| 💡 Tip | Helpful suggestions |
| ✅ Example | Practical examples |

---

# 2. System Overview

## 2.1 Architecture

The Logistics Cost Automation Platform follows a three-tier architecture:

```
┌────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Streamlit  │  │   Material   │  │    Cost      │   │
│  │   Framework  │  │    Forms     │  │   Reports    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────┴───────────────────────────────┐
│                    Business Logic Layer                     │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Validators  │  │  Calculator  │  │    Excel     │   │
│  │              │  │   Engine     │  │   Exporter   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────┴───────────────────────────────┐
│                      Data Layer                            │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Session    │  │     JSON     │  │    Backup    │   │
│  │    State     │  │   Storage    │  │    System    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└────────────────────────────────────────────────────────────┘
```

## 2.2 Core Components

### 2.2.1 Data Management System
- **Session State Manager**: Handles real-time data during user sessions
- **Persistent Storage**: JSON-based file storage with automatic versioning
- **Backup System**: Maintains last 10 versions for data recovery

### 2.2.2 Calculation Engine
- **Cost Components**: Modular calculation for each cost type
- **Optimization Algorithms**: MOQ calculations, packaging loop optimization
- **Validation Framework**: Ensures data integrity before calculations

### 2.2.3 Reporting System
- **Excel Exporter**: Professional formatted reports
- **Multi-format Support**: CSV, JSON, Excel exports
- **Template Engine**: Customizable report templates

## 2.3 Key Features

1. **Material & Supplier Management**
   - Comprehensive material database
   - Multi-supplier comparison
   - Performance tracking

2. **Cost Analysis Components**
   - Packaging (Plant vs CoC strategies)
   - Transportation (multi-modal)
   - Warehousing (dynamic safety stock)
   - Customs & duties
   - Environmental (CO₂) costs
   - Financial (inventory carrying)

3. **Advanced Calculations**
   - 13-stage packaging loop
   - MOQ optimization
   - Lead time analysis
   - Special packaging handling

---

# 3. Installation Guide

## 3.1 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **Memory**: 4GB RAM
- **Storage**: 500MB free space
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

### Recommended Requirements
- **Memory**: 8GB RAM
- **Storage**: 2GB free space
- **Display**: 1920x1080 resolution

## 3.2 Installation Steps

### 3.2.1 Standard Installation

1. **Download the Application**
   ```bash
   git clone https://github.com/your-org/logistics-cost-automation.git
   cd logistics-cost-automation
   ```

2. **Set Up Python Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Installation**
   ```bash
   python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
   ```

### 3.2.2 Docker Installation

1. **Build Docker Image**
   ```dockerfile
   FROM python:3.8-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "Overview.py"]
   ```

2. **Run Container**
   ```bash
   docker build -t logistics-app .
   docker run -p 8501:8501 logistics-app
   ```

## 3.3 First-Time Setup

1. **Launch Application**
   ```bash
   streamlit run Overview.py
   ```

2. **Access Web Interface**
   - Open browser at `http://localhost:8501`
   - You should see the Overview dashboard

3. **Initial Configuration**
   - No initial data setup required
   - Application creates necessary files automatically

---

# 4. User Manual

## 4.1 Material Management

### Overview
The Material Information module manages all product specifications required for logistics cost calculations.

### Accessing Material Management
1. Click **📦 Material Information** in the sidebar
2. The material management page opens

### Adding a New Material

#### Required Fields
- **Project Name**: The project or product line identifier
- **Material Number**: Unique alphanumeric code (e.g., "K297402")
- **Material Description**: Detailed name/description
- **Weight per Piece (kg)**: Individual item weight
- **Annual Volume**: Expected yearly quantity

#### Optional Fields
- **Usage**: Application or purpose description
- **Daily Demand**: Average daily consumption
- **Lifetime Volume**: Total expected lifetime quantity
- **Peak Year**: Year with highest demand
- **Peak Year Volume**: Volume during peak year
- **Working Days**: Annual working days (default: 250)
- **SOP (Start of Production)**: Production start date
- **Piece Price**: Material cost per unit

#### Step-by-Step Process

1. **Fill Required Information**
   ```
   Project Name: EPS
   Material Number: K297402
   Material Description: Last Chance Filter
   Weight per pcs: 0.004 kg
   Annual Volume: 200,000
   ```

2. **Add Optional Details**
   ```
   Usage: Filtration system component
   Daily Demand: 800
   Working Days: 250
   SOP: 2026
   ```

3. **Click "Add Material"**
   - System validates input
   - Success message appears
   - Material appears in list below

### Editing Materials

1. **Locate Material** in the existing materials list
2. **Click "Edit"** button
3. **Modify Fields** as needed
4. **Click "Update Material"**

### Deleting Materials

⚠️ **Warning**: Deleting a material removes all associated calculations

1. **Find Material** in list
2. **Click "Delete"** button
3. **Confirm** deletion when prompted

### Best Practices

💡 **Tips**:
- Use consistent material numbering schemes
- Include detailed descriptions for clarity
- Verify weight units (kg) before entry
- Annual volume drives most calculations

---

## 4.2 Supplier Management

### Overview
Manage vendor information and performance metrics for logistics calculations.

### Adding Suppliers

#### Required Information
- **Vendor ID**: Unique supplier code
- **Vendor Name**: Company name
- **Vendor Country**: Country code (e.g., "DE")
- **City of Manufacture**: Production location
- **Vendor ZIP**: Postal code
- **Delivery Performance (%)**: On-time delivery rate
- **Deliveries per Month**: Frequency of shipments

#### Process

1. **Navigate** to **🏭 Supplier Information**

2. **Enter Supplier Details**
   ```
   Vendor ID: 903000
   Vendor Name: Keller & Kalmbach
   Country: DE
   City: Unterschleissheim
   ZIP: 85716
   Performance: 95%
   Deliveries: 2 per month
   ```

3. **Save Supplier**
   - Click "Add Supplier"
   - Verify success message

### Managing Suppliers

#### Performance Tracking
- **Delivery Performance**: Historical on-time percentage
- **Frequency**: Monthly delivery count affects inventory

#### Supplier Comparison
- System automatically pairs suppliers with materials
- Cost calculations consider supplier-specific factors

### Integration Points
- Links to packaging configurations
- Affects transport calculations
- Influences safety stock levels

---

## 4.3 Location Configuration

### Overview
Define plant locations and distances for accurate transport calculations.

### Configuration Steps

1. **Access** **📍 KB/Bendix Location Info**

2. **Add Location**
   ```
   Plant: Aldersbach
   Country: DE
   Distance: 150 km
   ```

3. **Distance Considerations**
   - Measure from supplier to plant
   - Consider actual transport routes
   - Include border crossings if applicable

### Impact on Calculations
- **Transport Costs**: Distance directly affects pricing
- **CO₂ Emissions**: Longer distances increase environmental costs
- **Lead Times**: May affect safety stock requirements

---

## 4.4 Operations Setup

### Overview
Configure business operations parameters that affect logistics calculations.

### Key Parameters

#### Incoterms
- **Code**: EXW, FCA, FAS, FOB, CFR, CIF, CPT, CIP, DAP, DPU, DDP
- **Named Place**: Specific location for terms
- **Impact**: Determines cost responsibility split

#### Part Classification
- **A-Part**: Critical, high-value items
- **B-Part**: Important, medium-value items
- **C-Part**: Standard, low-value items

#### Lead Time Management
- **Lead Time (days)**: Total order-to-delivery time
- **Sub-supplier**: Additional time if used
- **Impact**: Affects safety stock calculations

### Configuration Process

1. **Open** **⚙️ Operations Information**

2. **Set Parameters**
   ```
   Incoterm: FCA
   Place: Unterschleissheim
   Classification: C-Part
   Call-off: EDI
   Lead Time: 30 days
   Currency: EUR
   ```

3. **Special Considerations**
   - **Packaging Ownership**: Who owns packaging tools
   - **Responsible Party**: Supplier vs CoC
   - **Directive Compliance**: Logistics directive adherence

---

## 4.5 Packaging Configuration

### Overview
The most complex configuration module, handling standard and special packaging requirements.

### 4.5.1 Per-Part Costs

These costs apply to each individual piece:

- **Packaging Maintenance**: Cost for maintaining reusable packaging
- **Empties Scrapping**: Cost for disposing cardboard/paper

### 4.5.2 Standard Packaging (Plant)

#### Box Selection
Choose from predefined box types:
- **One-Way**: Cardboard boxes (S/M/L/XL)
- **Returnable**: KLT containers, ESD boxes
- **Special**: Gitterbox, wooden boxes

#### Configuration Fields
```
Box Type: KLT4314 / LID
Filling Quantity: 1400 pieces/box
Pallet Type: EURO Pallet
Additional Packaging: €10 (for inlays)
```

### 4.5.3 Special Packaging (CoC)

For items requiring special handling:

#### Types Available
- **Inlay Tray**: Fits within standard containers
- **Inlay Tray Pallet Size**: Full pallet trays
- **Standalone Tray**: Independent packaging

#### Special Packaging Setup
```
Special Needed: Yes
Type: Standalone tray
Filling/Tray: 12 pieces
Tooling Cost: €750
Additional Needed: Yes
Trays/SP-Pallet: 16
SP-Pallets/LU: 4
```

### 4.5.4 Packaging Loop Configuration

The 13-stage packaging loop tracks container movement:

| Stage | Location | Purpose | Typical Days |
|-------|----------|---------|--------------|
| 1 | Goods Receipt | Incoming at KB | 1 |
| 2 | Stock Raw Materials | Storage at KB | 4 |
| 3 | Production | KB manufacturing | 3 |
| 4 | Empties Return | Empty collection | 3 |
| 5 | Cleaning | Container cleaning | 2 |
| 6 | Dispatch | Send to supplier | 1 |
| 7 | Transit KB→Supplier | Transportation | 1 |
| 8 | Receipt at Supplier | Incoming empties | 1 |
| 9 | Stock at Supplier | Empty storage | 2 |
| 10 | Production (Supplier) | Manufacturing | 5 |
| 11 | Stock Finished | Product storage | 5 |
| 12 | Dispatch | Ship to KB | 1 |
| 13 | Transit Supplier→KB | Transportation | 1 |

**Total Loop**: 30 days (typical)

### 4.5.5 Calculation Impact

Packaging configuration affects:
- **Direct Costs**: Box and pallet expenses
- **Loop Costs**: Investment in returnable packaging
- **Tooling Amortization**: Special packaging tooling over lifetime
- **Maintenance**: Ongoing packaging upkeep

---

## 4.6 Repacking Setup

### Overview
Configure costs for transferring materials between packaging types.

### Weight Categories

1. **Light** (up to 0.050kg)
   - Small electronic components
   - Fasteners, clips

2. **Moderate** (up to 0.150kg)
   - Medium components
   - Assembled parts

3. **Heavy** (from 0.150kg)
   - Large components
   - Heavy assemblies

### Packaging Combinations

| Supplier Packaging | Operation | KB Packaging | Cost Impact |
|-------------------|-----------|--------------|-------------|
| One-way tray in box | Individual | Returnable trays | €0.10/part |
| One-way tray in box | Tray transfer | One-way in KLT | €0.12/tray |
| Bulk in box | Dump transfer | KLT | €0.24/transfer |

### Configuration Steps

1. **Access** **🔄 Repacking Cost**
2. **Select Weight Category**
3. **Choose Packaging Types**
4. **System Auto-calculates** cost per operation

---

## 4.7 Customs Configuration

### Overview
Manage import/export duties and tariffs for international shipments.

### Key Parameters

- **Preference Usage**: Utilize trade agreements (Yes/No)
- **HS Code**: Harmonized System classification
- **Duty Rate**: Percentage of piece price
- **Tariff Rate**: Additional tariffs (e.g., Section 301)

### Setup Process

1. **Navigate to** **🛃 Customs Cost**

2. **Configure Rates**
   ```
   Preference Usage: Yes
   HS Code: 8421.23.00
   Duty Rate: 2.5%
   Tariff Rate: 0%
   ```

3. **Impact Calculation**
   - With preference: No duty applied
   - Without preference: Duty on (Price + Transport)

### Trade Agreement Considerations

📌 **Note**: Preference usage typically eliminates duty but requires:
- Proper documentation
- Certificate of origin
- Compliance verification

---

## 4.8 Transport Setup

### Overview
Configure transportation modes and costs for logistics calculations.

### Transport Modes

#### Primary Modes
- **Road**: Truck transport
- **Rail**: Train freight
- **Sea**: Ocean freight

#### Mode Combinations
- Single mode (e.g., Road only)
- Multi-modal (e.g., Sea + Road)

### Configuration Parameters

```
Mode 1: Road
Mode 2: None
Cost/LU: €95.59
Bonded Warehouse Cost: €0
Stackability Factor: 2
```

### Stackability Factors

| Factor | Meaning | Use Case |
|--------|---------|----------|
| 1 | No stacking | Fragile items |
| 1.2 | Limited stacking | Heavy items |
| 1.5 | Moderate stacking | Standard boxes |
| 2 | Full double-stack | Lightweight items |

### Cost Considerations

- **Base Transport**: Cost per load unit
- **Bonded Warehouse**: Additional handling for customs
- **Mode-specific Factors**: Sea freight uses overseas packaging

---

## 4.9 CO₂ Configuration

### Overview
Environmental cost calculations based on transportation emissions.

### Parameters

1. **CO₂ Cost per Ton**: Market price for carbon
2. **Conversion Factor**: Mode-specific emission factors

### Conversion Factors

| Transport Mode | Factor | Explanation |
|----------------|--------|-------------|
| Sea | 3.31 | Higher fuel consumption |
| Road | 3.17 | Standard truck emissions |
| Rail | 2.65 | More efficient per ton-km |

### Configuration

1. **Access** **🌱 Annual CO₂ Cost**
2. **Set Parameters**
   ```
   Cost/Ton: €100
   Conversion Factor: 3.17 (Road)
   ```

### Calculation Method

```
CO₂ Emissions = Weight × Distance × Energy Factor × Conversion Factor
CO₂ Cost = Emissions × (Cost per Ton / 1000)
```

---

## 4.10 Warehouse Setup

### Overview
Configure storage costs and inventory parameters.

### Key Parameter

- **Cost per Storage Location (Monthly)**: €5.00 typical

### Storage Calculation Factors

1. **Local Supply Locations**
   - Based on 5-day coverage
   - Calculated from daily demand

2. **Safety Stock**
   - Lead time × Daily demand
   - Converted to pallet requirements

### Impact Areas

- **Direct Costs**: Monthly storage fees
- **Inventory Investment**: Tied-up capital
- **Space Optimization**: Efficient location usage

---

## 4.11 Inventory Costs

### Overview
Financial cost of holding inventory.

### Configuration

1. **Navigate to** **💰 Inventory Cost**
2. **Set Interest Rate** (e.g., 5% annually)

### Calculation Impact

- Applied to average inventory value
- Considers safety stock investment
- Includes pipeline inventory

---

## 4.12 Additional Costs

### Overview
Flexible module for company-specific cost items.

### Common Use Cases

- **Quality Inspections**: Third-party testing
- **Special Handling**: Temperature control
- **Documentation**: Compliance paperwork
- **Insurance**: Additional coverage

### Adding Costs

1. **Access** **➕ Additional Cost**
2. **Define Cost Item**
   ```
   Name: Quality Inspection
   Value: €500
   ```
3. **Allocation**: Spread across lifetime volume

---

## 4.13 Cost Calculation

### Overview
The calculation engine that processes all configurations to generate total landed costs.

### 4.13.1 Preparation Steps

Before calculating:

✅ **Verify Required Configurations**
- At least one material
- At least one supplier
- Packaging configuration
- Transport setup
- Warehouse parameters
- CO₂ settings

### 4.13.2 Calculation Process

1. **Navigate to** **🧮 Cost Calculation**

2. **Review Configuration Status**
   - Green checkmarks indicate ready components
   - Red X marks missing configurations

3. **Select Calculation Mode**
   - **All Pairs**: Calculate every material-supplier combination
   - **Selected Pairs**: Choose specific combinations

4. **Configure Options**
   ```
   ☑ Include CO₂ Costs
   ☑ Show Detailed Breakdown
   Export Format: Excel
   ```

5. **Execute Calculation**
   - Click "Calculate Logistics Costs"
   - Progress indicator shows status
   - Results appear below

### 4.13.3 Understanding Results

#### Summary Section
```
Total Cost per Piece: €0.247
├── Packaging: €0.089 (36%)
├── Transport: €0.068 (28%)
├── Warehouse: €0.045 (18%)
├── CO₂: €0.023 (9%)
├── Customs: €0.015 (6%)
└── Additional: €0.007 (3%)
```

#### Detailed Breakdown

Each cost component shows:
- Per-piece cost
- Annual cost projection
- Percentage of total
- Calculation factors used

### 4.13.4 Export Options

#### Excel Export (Recommended)
- Professional formatting
- Corporate template style
- Multiple worksheets
- Charts and summaries

#### CSV Export
- Raw data format
- Easy spreadsheet import
- Suitable for further analysis

#### JSON Export
- Complete data structure
- Integration-ready
- Includes metadata

### 4.13.5 Comparison Analysis

For multiple configurations:

1. **Best Configuration** (Lowest Cost)
   - Highlighted in green
   - Key differentiators shown

2. **Cost Drivers**
   - Components with highest impact
   - Optimization opportunities

3. **Sensitivity Indicators**
   - Volume impact
   - Distance sensitivity
   - Lead time effects

---

## 4.14 Settings & Data Management

### Overview
Manage application data, backups, and system preferences.

### 4.14.1 Auto-Save Configuration

**Default**: Enabled (Recommended)

Toggle auto-save:
1. Go to **⚙️ Settings**
2. Check/uncheck "Enable Auto-save"
3. Changes apply immediately

### 4.14.2 Manual Save

Force immediate save:
- Click "💾 Save Now"
- Useful before major changes
- Creates backup automatically

### 4.14.3 Data Import/Export

#### Exporting Configuration

1. **Click "Export Configuration"**
2. **Save JSON file**
3. **File contains**:
   - All materials
   - All suppliers
   - All configurations
   - Metadata and version

#### Importing Configuration

1. **Click "Import Configuration"**
2. **Select JSON file**
3. **Preview data**
4. **Confirm import**

⚠️ **Warning**: Importing replaces all current data

### 4.14.4 Backup Management

System maintains automatic backups:
- **Location**: `/backups` folder
- **Retention**: Last 10 versions
- **Naming**: `logistics_data_backup_YYYYMMDD_HHMMSS.json`

#### Restore from Backup

1. **View available backups**
2. **Select backup version**
3. **Click "Restore"**
4. **Confirm restoration**

### 4.14.5 Data Integrity

#### Run Integrity Check

1. **Click "Run Data Integrity Check"**
2. **Review results**:
   - ✅ No issues: System healthy
   - ⚠️ Warnings: Non-critical issues
   - ❌ Errors: Require attention

#### Common Issues
- Missing material-supplier pairs
- Incomplete configurations
- Invalid data ranges

### 4.14.6 Clear Data

**Complete Reset**:
1. Click "Clear All Data"
2. Confirm action
3. All data removed
4. Backups retained

---

# 5. Technical Documentation

## 5.1 System Architecture

### 5.1.1 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Streamlit 1.45+ | Web UI framework |
| Business Logic | Python 3.8+ | Core calculations |
| Data Storage | JSON | Persistent storage |
| Export | Openpyxl, Pandas | Report generation |
| Validation | Custom Python | Data integrity |

### 5.1.2 Module Structure

```
logistics-cost-automation/
├── Overview.py                 # Main entry point
├── pages/                      # Streamlit pages
│   ├── 1Material_Information.py
│   ├── 2Supplier_Information.py
│   ├── ...
│   └── 14Settings.py
├── utils/                      # Core modules
│   ├── calculations.py         # Calculation engine
│   ├── data_manager.py        # Data operations
│   ├── validators.py          # Input validation
│   ├── excel_exporter.py      # Report generation
│   ├── packaging_tables.py    # Reference data
│   └── repacking_table.py     # Lookup tables
├── backups/                   # Automatic backups
├── logistics_data.json        # Main data file
└── requirements.txt           # Dependencies
```

### 5.1.3 Data Flow

```mermaid
graph LR
    A[User Input] --> B[Validators]
    B --> C[Session State]
    C --> D[Data Manager]
    D --> E[JSON Storage]
    C --> F[Calculator]
    F --> G[Results]
    G --> H[Excel Export]
    G --> I[Display]
```

## 5.2 Calculation Engine

### 5.2.1 Core Algorithms

#### Packaging Cost Algorithm

```python
def packaging_cost_per_piece(material, packaging, operations):
    # Plant costs
    plant_loop_days = sum(packaging.loop_data.values())
    daily_demand = material.daily_demand
    fill_qty_box = packaging.fill_qty_box
    
    boxes_needed = ceil((daily_demand * plant_loop_days) / fill_qty_box)
    plant_cost = boxes_needed * (box_price + additional_packaging)
    
    # CoC costs
    if packaging.sp_needed == 'Yes':
        coc_cost = calculate_special_packaging_cost()
    else:
        coc_cost = 0
    
    # Total per piece
    total_cost = (plant_cost + coc_cost + maintenance) / lifetime_volume
    return round(total_cost, 3)
```

#### Transport Cost Calculation

```python
def transport_cost_per_piece(transport, packaging, operations):
    fill_qty_lu = calculate_filling_quantity_per_lu(packaging)
    
    if transport.mode1 == 'Sea':
        if operations.incoterm in ['FCA', 'FOB']:
            cost = (transport.cost_lu / packaging.fill_qty_lu_oversea) + \
                   (transport.cost_bonded / fill_qty_lu)
        else:
            cost = transport.cost_lu / packaging.fill_qty_lu_oversea
    else:
        cost = transport.cost_lu / fill_qty_lu
    
    return round(cost, 3)
```

### 5.2.2 Optimization Techniques

#### MOQ Calculation

```python
def calculate_moq(material, supplier, packaging):
    daily_demand = material.daily_demand
    deliveries_per_month = supplier.deliveries_per_month
    
    if packaging.sp_needed == 'Yes':
        base_qty = daily_demand * 20 / deliveries_per_month
        moq = ceil(base_qty / tray_capacity) * tray_capacity
    else:
        base_qty = daily_demand * 20 / deliveries_per_month
        moq = ceil(base_qty / box_capacity) * box_capacity
    
    return moq
```

## 5.3 Data Management

### 5.3.1 Session State Management

Streamlit session state handles:
- Active user data
- Temporary calculations
- UI state preservation
- Edit flags

### 5.3.2 Persistent Storage

JSON structure:
```json
{
  "materials": [...],
  "suppliers": [...],
  "packaging": [...],
  "settings": {
    "auto_save": true
  },
  "metadata": {
    "version": "1.0.0",
    "save_timestamp": "2025-07-09T10:30:00"
  }
}
```

### 5.3.3 Backup Strategy

- Triggered on every save
- Rotation maintains 10 versions
- Timestamp-based naming
- Automatic cleanup

---

# 6. API Reference

## 6.1 DataManager API

### Class: `DataManager`

Central data management interface.

#### Methods

##### `add_material(material_data: Dict) -> bool`
Add new material to database.

**Parameters:**
- `material_data`: Dictionary containing material fields

**Returns:**
- `bool`: Success status

**Example:**
```python
dm = DataManager()
material = {
    'material_no': 'K297402',
    'material_desc': 'Filter',
    'weight_per_pcs': 0.004,
    'annual_volume': 200000
}
success = dm.add_material(material)
```

##### `get_materials() -> List[Dict]`
Retrieve all materials.

**Returns:**
- `List[Dict]`: List of material dictionaries

##### `update_material(material_no: str, data: Dict) -> bool`
Update existing material.

**Parameters:**
- `material_no`: Material identifier
- `data`: Updated material data

##### `remove_material(material_no: str) -> bool`
Delete material and associated data.

### Similar methods exist for:
- Suppliers
- Packaging configurations
- Transport settings
- All other data types

## 6.2 Calculator API

### Class: `LogisticsCostCalculator`

Core calculation engine.

#### Primary Method

##### `calculate_total_logistics_cost(**kwargs) -> Dict`

**Parameters:**
- `material`: Material dictionary
- `supplier`: Supplier dictionary
- `packaging_config`: Packaging configuration
- `transport_config`: Transport settings
- `warehouse_config`: Warehouse parameters
- `repacking_config`: Optional repacking settings
- `customs_config`: Optional customs data
- `co2_config`: CO₂ parameters
- `additional_costs`: Optional extra costs
- `operations_config`: Optional operations data
- `location_config`: Optional location data

**Returns:**
Dictionary containing:
- Individual cost components
- Total cost per piece
- Annual cost projections
- Calculation metadata

## 6.3 Validator API

### Base Class: `BaseValidator`

Common validation methods.

### Specialized Validators

- `MaterialValidator`
- `SupplierValidator`
- `PackagingValidator`
- `TransportValidator`
- etc.

#### Common Method

##### `validate(data: Dict) -> Dict`

**Returns:**
```python
{
    'is_valid': bool,
    'errors': List[str]
}
```

---

# 7. Configuration Guide

## 7.1 Application Configuration

### 7.1.1 Streamlit Configuration

File: `.streamlit/config.toml`

```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#f8f9fa"
secondaryBackgroundColor = "#e9ecef"
textColor = "#212529"
font = "sans serif"
```

### 7.1.2 Environment Variables

```bash
# Server configuration
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true

# Performance tuning
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
export STREAMLIT_RUNNER_FAST_RERUNS=true

# Security
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
```

## 7.2 Data Configuration

### 7.2.1 Reference Data

Modify lookup tables in:
- `utils/packaging_tables.py`: Box specifications
- `utils/repacking_table.py`: Repacking costs

### 7.2.2 Calculation Parameters

Adjust formulas in:
- `utils/calculations.py`: Core algorithms

## 7.3 Security Configuration

### 7.3.1 Access Control

Currently file-based, extend with:
```python
# Example authentication wrapper
def require_auth(func):
    def wrapper(*args, **kwargs):
        if not check_authentication():
            st.error("Authentication required")
            return
        return func(*args, **kwargs)
    return wrapper
```

### 7.3.2 Data Encryption

For sensitive data:
```python
from cryptography.fernet import Fernet

def encrypt_sensitive_data(data):
    key = load_encryption_key()
    f = Fernet(key)
    return f.encrypt(data.encode())
```

---

# 8. Deployment Guide

## 8.1 Local Deployment

### 8.1.1 Development Setup

```bash
# Clone repository
git clone <repository>
cd logistics-cost-automation

# Setup environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run Overview.py
```

## 8.2 Production Deployment

### 8.2.1 Linux Server Deployment

1. **System Preparation**
   ```bash
   sudo apt update
   sudo apt install python3.8 python3-pip nginx
   ```

2. **Application Setup**
   ```bash
   # Create application directory
   sudo mkdir -p /opt/logistics-app
   sudo chown $USER:$USER /opt/logistics-app
   
   # Copy application files
   cp -r * /opt/logistics-app/
   
   # Install dependencies
   cd /opt/logistics-app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Systemd Service**
   
   Create `/etc/systemd/system/logistics-app.service`:
   ```ini
   [Unit]
   Description=Logistics Cost Automation Platform
   After=network.target
   
   [Service]
   Type=simple
   User=appuser
   WorkingDirectory=/opt/logistics-app
   Environment="PATH=/opt/logistics-app/venv/bin"
   ExecStart=/opt/logistics-app/venv/bin/streamlit run Overview.py --server.port=8501
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Nginx Configuration**
   
   `/etc/nginx/sites-available/logistics-app`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

### 8.2.2 Docker Deployment

1. **Dockerfile**
   ```dockerfile
   FROM python:3.8-slim
   
   WORKDIR /app
   
   # Install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application
   COPY . .
   
   # Create non-root user
   RUN useradd -m appuser && chown -R appuser:appuser /app
   USER appuser
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "Overview.py", "--server.port=8501"]
   ```

2. **Docker Compose**
   ```yaml
   version: '3.8'
   
   services:
     logistics-app:
       build: .
       ports:
         - "8501:8501"
       volumes:
         - ./logistics_data.json:/app/logistics_data.json
         - ./backups:/app/backups
       environment:
         - STREAMLIT_SERVER_HEADLESS=true
       restart: unless-stopped
   ```

### 8.2.3 Cloud Deployment

#### AWS EC2

1. **Launch EC2 Instance**
   - Amazon Linux 2 or Ubuntu 20.04
   - t3.medium or larger
   - Security group: Allow ports 80, 443, 8501

2. **Deploy Application**
   - Follow Linux server deployment steps
   - Configure AWS Application Load Balancer
   - Set up Auto Scaling Group

#### Azure App Service

1. **Create App Service**
   ```bash
   az webapp create --resource-group myRG --plan myPlan --name logistics-app --runtime "PYTHON:3.8"
   ```

2. **Deploy Code**
   ```bash
   az webapp deployment source config-local-git --name logistics-app --resource-group myRG
   git remote add azure <deployment-url>
   git push azure main
   ```

#### Google Cloud Run

1. **Build Container**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/logistics-app
   ```

2. **Deploy Service**
   ```bash
   gcloud run deploy --image gcr.io/PROJECT-ID/logistics-app --platform managed
   ```

## 8.3 Performance Optimization

### 8.3.1 Caching Strategy

```python
import streamlit as st
from functools import lru_cache

@st.cache_data
def load_reference_data():
    # Cache static reference data
    return load_packaging_tables()

@lru_cache(maxsize=128)
def calculate_expensive_operation(param1, param2):
    # Cache calculation results
    return complex_calculation(param1, param2)
```

### 8.3.2 Database Migration

For larger deployments:

```python
# PostgreSQL integration example
import psycopg2
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://user:password@localhost/logistics"
engine = create_engine(DATABASE_URL)

def migrate_to_postgresql():
    # Load JSON data
    with open('logistics_data.json', 'r') as f:
        data = json.load(f)
    
    # Create tables and insert data
    df_materials = pd.DataFrame(data['materials'])
    df_materials.to_sql('materials', engine, if_exists='replace')
```

---

# 9. Troubleshooting

## 9.1 Common Issues

### 9.1.1 Installation Problems

#### Issue: "No module named streamlit"
**Solution:**
```bash
pip install streamlit==1.45.1
```

#### Issue: "Permission denied" on Linux/Mac
**Solution:**
```bash
sudo pip install streamlit
# Or better:
python -m pip install --user streamlit
```

### 9.1.2 Runtime Errors

#### Issue: "Port 8501 already in use"
**Solution:**
```bash
# Find process using port
lsof -i :8501  # Linux/Mac
netstat -ano | findstr :8501  # Windows

# Kill process or use different port
streamlit run Overview.py --server.port 8502
```

#### Issue: "Session state error"
**Cause:** Browser cache conflict
**Solution:**
1. Clear browser cache
2. Restart application
3. Use incognito/private mode

### 9.1.3 Data Issues

#### Issue: "Cannot save data"
**Possible Causes:**
- No write permissions
- Disk full
- File locked by another process

**Solutions:**
```bash
# Check permissions
ls -la logistics_data.json

# Fix permissions
chmod 644 logistics_data.json

# Check disk space
df -h
```

#### Issue: "Data not persisting"
**Check:**
1. Auto-save enabled in Settings
2. File system permissions
3. Anti-virus not blocking

### 9.1.4 Calculation Errors

#### Issue: "Division by zero"
**Common Causes:**
- Zero filling quantity
- Missing annual volume
- Empty packaging loop

**Debug Steps:**
1. Check all input values
2. Verify packaging configuration
3. Review calculation logs

## 9.2 Debug Mode

### 9.2.1 Enable Debug Logging

```python
# In Overview.py, add:
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or via command line:
streamlit run Overview.py --logger.level debug
```

### 9.2.2 Calculation Debugging

```python
# In calculations.py, add debug prints:
def calculate_cost(self, ...):
    if DEBUG:
        print(f"Input values: {locals()}")
    
    result = perform_calculation()
    
    if DEBUG:
        print(f"Result: {result}")
    
    return result
```

## 9.3 Performance Issues

### 9.3.1 Slow Loading

**Optimize with:**
```python
# Cache static data
@st.cache_resource
def load_static_data():
    return expensive_operation()

# Cache user-specific data
@st.cache_data
def process_user_data(user_id):
    return user_specific_operation(user_id)
```

### 9.3.2 Memory Usage

Monitor with:
```python
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB
```

---

# 10. Best Practices

## 10.1 Data Entry Guidelines

### 10.1.1 Material Management

✅ **DO:**
- Use consistent material numbering
- Include units in descriptions
- Verify weight is in kilograms
- Update annual volumes regularly

❌ **DON'T:**
- Duplicate material numbers
- Mix units (kg vs lbs)
- Leave required fields empty
- Use special characters in IDs

### 10.1.2 Supplier Information

✅ **Best Practices:**
- Maintain current delivery performance
- Use standard country codes
- Update delivery frequency monthly
- Include complete addresses

### 10.1.3 Cost Configuration

💡 **Recommendations:**
- Review costs quarterly
- Document assumptions
- Validate against invoices
- Consider seasonal variations

## 10.2 Calculation Optimization

### 10.2.1 Efficiency Tips

1. **Batch Processing**
   - Calculate all materials at once
   - Export complete datasets
   - Minimize recalculations

2. **Data Preparation**
   - Complete all configurations first
   - Validate data before calculating
   - Use templates for similar items

### 10.2.2 Accuracy Improvements

1. **Regular Updates**
   - Transport costs (fuel prices)
   - Exchange rates
   - CO₂ pricing
   - Warehouse rates

2. **Validation Checks**
   - Cross-reference with actual invoices
   - Compare year-over-year trends
   - Audit calculation samples

## 10.3 System Maintenance

### 10.3.1 Regular Tasks

#### Daily
- Monitor system performance
- Check for calculation errors
- Verify auto-save functioning

#### Weekly
- Review backup integrity
- Clear old session data
- Update exchange rates

#### Monthly
- Full data backup
- Performance analysis
- User access review

### 10.3.2 Data Governance

1. **Version Control**
   ```bash
   git add logistics_data.json
   git commit -m "Monthly data snapshot"
   git tag -a v1.0-2025-07 -m "July 2025 data"
   ```

2. **Audit Trail**
   - Document major changes
   - Track configuration updates
   - Maintain change log

---

# 11. Glossary

## A-L

**Annual Volume**: Yearly quantity of material expected to be procured

**Auto-save**: Feature that automatically persists data changes

**Bonded Warehouse**: Secure facility where goods are stored under customs control

**CoC**: Center of Competence - specialized facility for specific operations

**Customs Preference**: Trade agreement benefits reducing or eliminating duties

**Daily Demand**: Average material consumption per working day

**Delivery Performance**: Percentage of on-time deliveries from supplier

**ERP**: Enterprise Resource Planning system

**Fill Quantity**: Number of pieces that fit in a container/box

**FCA**: Free Carrier - Incoterm where seller delivers to carrier

**FOB**: Free On Board - Incoterm where seller loads goods on vessel

**HS Code**: Harmonized System code for customs classification

**Incoterm**: International Commercial Terms defining trade responsibilities

**JSON**: JavaScript Object Notation - data storage format

**KLT**: Kleinladungsträger - standard plastic containers

**Lead Time**: Days from order placement to delivery

**Lifetime Volume**: Total quantity over product lifecycle

**Load Unit (LU)**: Standard shipping unit (pallet, container)

## M-Z

**MOQ**: Minimum Order Quantity - smallest order size accepted

**Material Number**: Unique identifier for a product/component

**Packaging Loop**: Complete cycle of packaging from plant to supplier and back

**Peak Year**: Year with highest expected demand

**Plant**: Manufacturing or distribution facility

**Repacking**: Transfer of goods between packaging types

**Safety Stock**: Buffer inventory to prevent stockouts

**Session State**: Temporary data storage during user session

**SOP**: Start of Production - when manufacturing begins

**Special Packaging**: Custom packaging for specific requirements

**Stackability Factor**: Multiplier indicating vertical stacking capability

**Tariff**: Government-imposed tax on imports

**Total Landed Cost**: Complete cost including product, logistics, and duties

**Transport Mode**: Method of transportation (road, rail, sea)

**Validation**: Process of checking data integrity

**Vendor**: Supplier or seller of goods

**Weight per Piece**: Individual item weight in kilograms

**Working Days**: Annual operating days for planning

---

# 12. Appendices

## Appendix A: Calculation Formulas

### A.1 Packaging Cost Formula

```
Packaging Cost per Piece = (Total Packaging Cost) / (Lifetime Volume)

Where:
Total Packaging Cost = Plant Cost + CoC Cost + Maintenance + Scrapping

Plant Cost = Σ(Boxes × Box Price) + Σ(Pallets × Pallet Price)
CoC Cost = Special Packaging Cost + Tooling Amortization
```

### A.2 Transport Cost Formula

```
Transport Cost per Piece = Transport Cost per LU / Filling Quantity per LU

Adjustments for Sea Transport:
- If Incoterm = FCA/FOB: Add bonded warehouse cost
- Use overseas packaging quantity
```

### A.3 Warehouse Cost Formula

```
Warehouse Cost per Piece = (Storage Locations × Monthly Cost × 12) / Annual Volume

Storage Locations = Local Supply Locations + Safety Stock Locations
Safety Stock = CEILING(Lead Time × Daily Demand / Fill Quantity)
```

### A.4 CO₂ Cost Formula

```
CO₂ Emissions = Total Tons × Energy Consumption × Distance × Conversion Factor
CO₂ Cost per Piece = (Emissions × CO₂ Price per Ton) / Annual Volume

Energy Consumption Factors:
- Sea: 0.006
- Road: 0.04415
- Rail: 0.0085
```

## Appendix B: Reference Tables

### B.1 Standard Box Specifications

| Box Type | Dimensions (mm) | Weight (kg) | Cost (€) | Boxes/Pallet |
|----------|----------------|-------------|----------|---------------|
| Cardboard S | 294×194×137 | 0.25 | 0.83 | 120 |
| Cardboard M | 394×294×137 | 0.50 | 1.64 | 60 |
| Cardboard L | 585×392×137 | 1.00 | 3.86 | 30 |
| KLT3214 | 300×200×147 | 1.17 | 6.86 | 96 |
| KLT4314 | 400×300×147 | 1.68 | 11.34 | 48 |

### B.2 Repacking Cost Matrix

| Weight Class | Supplier Pack | KB Pack | Cost/Operation |
|--------------|---------------|---------|----------------|
| Light (<50g) | Tray in box | Returnable tray | €0.10/piece |
| Light (<50g) | Bulk in box | KLT | €0.24/transfer |
| Moderate (<150g) | Tray in box | Returnable tray | €0.15/piece |
| Heavy (>150g) | Tray in box | Returnable tray | €0.33/piece |

## Appendix C: Integration Examples

### C.1 REST API Wrapper (Future)

```python
from flask import Flask, jsonify, request
from utils.calculations import LogisticsCostCalculator

app = Flask(__name__)
calculator = LogisticsCostCalculator()

@app.route('/api/calculate', methods=['POST'])
def calculate_cost():
    data = request.json
    
    result = calculator.calculate_total_logistics_cost(
        material=data['material'],
        supplier=data['supplier'],
        packaging_config=data['packaging'],
        # ... other parameters
    )
    
    return jsonify(result)
```

### C.2 ERP Integration Template

```python
import requests
from utils.data_manager import DataManager

class ERPConnector:
    def __init__(self, erp_url, api_key):
        self.erp_url = erp_url
        self.headers = {'Authorization': f'Bearer {api_key}'}
    
    def sync_materials(self):
        # Fetch from ERP
        response = requests.get(f'{self.erp_url}/materials', headers=self.headers)
        erp_materials = response.json()
        
        # Update local data
        dm = DataManager()
        for material in erp_materials:
            dm.add_material(self.transform_material(material))
    
    def transform_material(self, erp_material):
        # Map ERP fields to application fields
        return {
            'material_no': erp_material['ItemCode'],
            'material_desc': erp_material['Description'],
            'weight_per_pcs': erp_material['Weight'],
            # ... other mappings
        }
```

## Appendix D: Compliance & Standards

### D.1 Data Privacy

- All data stored locally
- No external data transmission
- User-controlled exports
- Backup encryption available

### D.2 Calculation Standards

- Based on industry best practices
- Aligned with APICS standards
- Compatible with ISO 28000
- Supports GS1 identifiers

### D.3 Environmental Compliance

- CO₂ calculations per GHG Protocol
- Supports carbon reporting
- Environmental cost tracking
- Sustainability metrics

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-07-09 | Marawan Younis | Initial complete documentation |

---

**End of Documentation**

For additional support, contact: marawan.younis@knorr-bremse.com