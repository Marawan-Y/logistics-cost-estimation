# Logistics Cost Automation Application

A comprehensive web application designed to automate logistics cost calculations for materials, suppliers, packaging, transport, and warehouse operations. Built with Streamlit for an intuitive user interface.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [User Guide](#user-guide)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## 🔍 Overview

This application streamlines the logistics cost calculation process by providing:
- Automated data collection and validation
- Multi-component cost calculations (packaging, transport, warehouse, CO₂)
- Material and supplier management
- Export capabilities for results
- Real-time cost analysis and reporting

## ✨ Features

- **Material Management**: Configure material specifications, weights, and volumes
- **Supplier Information**: Manage vendor details, locations, and Incoterms
- **Packaging Costs**: Calculate packaging costs with tooling amortization
- **Transport Costs**: Support for multiple transport modes with CO₂ calculations
- **Warehouse Costs**: Storage and inventory cost management
- **Cost Calculation Engine**: Comprehensive logistics cost calculations
- **Data Export**: Export results in CSV, Excel, and JSON formats
- **Configuration Management**: Save and load application configurations

## 📋 Prerequisites

- Python 3.8 or higher
- Web browser (Chrome, Firefox, Safari, or Edge)

## 🚀 Installation & Setup

### Manual Setup (Local Development)

If you're running locally outside of Replit:

```bash
# Clone the repository
git clone <your-repo-url>
cd logistics-cost-automation

# Install dependencies
pip install streamlit pandas

# Run the application
streamlit run app.py --server.port 5000
```

## 🏃‍♂️ Running the Application

### On Replit

1. **Click the "Run" button** at the top of the Replit interface
2. The application will start automatically on port 5000
3. Open the web view to access the application
4. The application will be available at the provided URL

### Command Line

```bash
streamlit run app.py --server.port 5000
```

The application will be accessible at:
- Local: `http://0.0.0.0:5000`

## 📖 User Guide

### Getting Started

1. **Dashboard Overview**: 
   - View the main dashboard showing configuration status
   - Check metrics for materials, suppliers, and calculation readiness

### Step-by-Step Configuration

#### 1. Material Information
- Navigate to "Material Information" page
- Add material details:
  - Material number and description
  - Weight per piece (kg)
  - Annual and lifetime volumes
  - Start of Production (SOP) year
- Save each material configuration

#### 2. Supplier Information
- Go to "Supplier Information" page
- Configure supplier details:
  - Vendor ID and name
  - Country and city of manufacture
  - ZIP code and Incoterms
- Link suppliers to specific materials

#### 3. Packaging Costs
- Access "Packaging Costs" page
- Set packaging parameters:
  - Packaging type and filling degree
  - Packaging cost per part
  - Tooling costs and maintenance
  - Scrap rates
- Configure for each material-supplier combination

#### 4. Transport Costs
- Open "Transport Costs" page
- Define transport parameters:
  - Transport mode (Road, Rail, Sea, Air)
  - Distance and cost per load unit
  - CO₂ emission factors
  - Fuel surcharges and handling costs
- Set frequency and reliability parameters

#### 5. Warehouse Costs
- Navigate to "Warehouse Costs" page
- Configure warehouse parameters:
  - Storage locations and capacity
  - Safety stock requirements
  - Warehouse cost per piece
  - Inventory interest rates

#### 6. Cost Calculation
- Go to "Cost Calculation" page
- Review configuration overview
- Select calculation mode:
  - **All Configurations**: Calculate for all material-supplier pairs
  - **Selected Pairs**: Choose specific combinations
- Configure calculation settings:
  - Include/exclude CO₂ costs
  - Choose export format (CSV, Excel, JSON)
  - Enable detailed breakdown
- Click "Calculate Logistics Costs"
- View results and export data

### Data Management

#### Exporting Configuration
- Click "Export Configuration" on the main dashboard
- Download JSON file with all current settings
- Use for backup or sharing configurations

#### Importing Configuration
- Use the file uploader on the main dashboard
- Select a previously exported JSON configuration
- All data will be restored from the file

#### Clearing Data
- Click "Clear All Data" on the main dashboard
- Confirm the action to reset all configurations

### Understanding Results

The cost calculation provides:
- **Cost per piece breakdown**:
  - Packaging costs
  - Transport costs
  - Warehouse costs
  - CO₂ costs (if enabled)
- **Annual cost projections**
- **Total logistics cost per piece**
- **Detailed component analysis**

## 📁 Project Structure

```
logistics-cost-automation/
├── app.py                          # Main Streamlit application
├── pages/                          # Multi-page application structure
│   ├── 1_Material_Information.py   # Material configuration page
│   ├── 2_Supplier_Information.py   # Supplier management page
│   ├── 3_Packaging_Costs.py        # Packaging cost configuration
│   ├── 4_Transport_Costs.py        # Transport cost setup
│   ├── 5_Warehouse_Costs.py        # Warehouse cost management
│   └── 6_Cost_Calculation.py       # Cost calculation and results
├── utils/                          # Utility modules
│   ├── calculations.py             # Cost calculation engine
│   ├── data_manager.py             # Data storage and management
│   └── validators.py               # Input validation utilities
├── .streamlit/                     # Streamlit configuration
│   └── config.toml                 # App configuration settings
├── attached_assets/                # Documentation and references
├── README.md                       # This file
├── pyproject.toml                  # Python project configuration
└── uv.lock                         # Dependency lock file
```

## 🔧 Configuration

### Application Settings

The application uses Streamlit's configuration system. Settings are defined in `.streamlit/config.toml`:

- Wide layout mode for better data visualization
- Custom theme settings
- Server configuration for optimal performance

### Data Storage

- All data is stored in Streamlit's session state
- Configurations can be exported/imported as JSON
- No external database required for basic operation

## 🛠️ Development

### Adding New Features

1. **New Cost Components**: Extend the `LogisticsCostCalculator` class in `utils/calculations.py`
2. **Additional Pages**: Create new pages in the `pages/` directory
3. **Data Validation**: Add validators in `utils/validators.py`
4. **Data Management**: Extend `DataManager` class for new data types

### Testing

Run the application and test each component:
1. Add sample data through each page
2. Verify calculations in the Cost Calculation page
3. Test export/import functionality
4. Validate error handling and edge cases

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 📞 Support

For questions or issues:
1. Check the application's built-in help text
2. Review this README
3. Create an issue in the repository
4. Contact the development team

---

**Built with ❤️ using Streamlit and Python**
