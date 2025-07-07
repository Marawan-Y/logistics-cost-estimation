# Logistics Cost Automation Platform

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-org/logistics-cost-automation)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.45+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](docs/)

A comprehensive enterprise-grade platform for automating logistics cost calculations across the entire supply chain. Designed for procurement professionals, supply chain managers, and logistics teams to make data-driven sourcing decisions.

![Logistics Cost Automation Dashboard](docs/images/dashboard-preview.png)

## 🎯 Overview

The Logistics Cost Automation Platform revolutionizes how organizations calculate and analyze their total landed costs. By considering all cost components from supplier to warehouse, including packaging, transport, customs, and environmental factors, it provides a complete picture of logistics expenses.

### Key Benefits

- **💰 Cost Transparency**: Visualize all hidden costs in your supply chain
- **⚡ 90% Time Reduction**: Automate complex calculations that typically take hours
- **🎯 Data-Driven Decisions**: Compare suppliers and scenarios objectively
- **🌍 Sustainability Focus**: Integrated CO₂ cost calculations
- **📊 Professional Reports**: Export-ready Excel reports matching corporate templates

## ✨ Features

### Core Functionality

#### 📦 **Material & Supplier Management**
- Comprehensive material database with specifications
- Multi-supplier comparison capabilities
- Automated material-supplier pairing analysis
- Performance tracking and delivery metrics

#### 💵 **Cost Component Analysis**
- **Packaging Costs**: Dual-strategy optimization (Plant vs CoC)
- **Transport Costs**: Multi-modal transportation with route optimization
- **Warehouse Costs**: Dynamic safety stock calculations
- **Customs & Duties**: Automated tariff calculations
- **Environmental Costs**: CO₂ emissions pricing
- **Financial Costs**: Inventory carrying cost analysis

#### 🔄 **Advanced Calculations**
- 13-stage packaging loop optimization
- Minimum Order Quantity (MOQ) calculations
- Lead time impact analysis
- Special packaging requirements handling

#### 💾 **Data Management**
- Persistent JSON-based storage
- Automatic backup system (last 10 versions)
- Import/Export configuration templates
- Session recovery after browser closure

#### 📊 **Reporting & Analytics**
- Professional Excel exports with formatting
- Multi-format support (CSV, JSON, Excel)
- Cost breakdown visualizations
- Supplier comparison matrices

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.8 or higher
pip (Python package manager)
Modern web browser (Chrome, Firefox, Safari, Edge)
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/logistics-cost-automation.git
   cd logistics-cost-automation
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application**
   ```bash
   streamlit run Overview.py
   ```

5. **Access the platform**
   ```
   Open browser at http://localhost:8501
   ```

### Quick Start Guide

1. **Initial Setup**
   - Navigate to "Material Information" → Add your first material
   - Go to "Supplier Information" → Add supplier details
   - Configure at least one entry in Packaging, Transport, Warehouse, and CO₂ sections

2. **Run Calculation**
   - Navigate to "Cost Calculation" page
   - Select calculation mode (All or Selected pairs)
   - Click "Calculate Logistics Costs"
   - Export results in your preferred format

## 📖 User Guide

### Navigation Structure

```
🏠 Overview                    # Dashboard and system status
├── 📦 Material Information    # Product specifications
├── 🏭 Supplier Information    # Vendor details and performance
├── 📍 KB/Bendix Location Info # Plant locations and distances
├── ⚙️ Operations Information  # Incoterms, lead times, currencies
├── 📦 Packaging Cost          # Container and packaging setup
├── 🔄 Repacking Cost         # Material handling costs
├── 🛃 Customs Cost           # Import/export duties
├── 🚚 Transport Cost         # Shipping and logistics
├── 🌱 Annual CO₂ Cost        # Environmental impact costs
├── 🏗️ Warehouse Cost         # Storage expenses
├── 💰 Inventory Cost         # Interest rates
├── ➕ Additional Cost        # Other configurable costs
├── 🧮 Cost Calculation       # Run calculations and export
└── ⚙️ Settings              # Data persistence options
```

### Detailed Feature Documentation

#### Material Configuration
Configure materials with:
- Material number and description
- Weight per piece (kg)
- Annual and lifetime volumes
- Peak demand periods
- Start of Production (SOP) dates

#### Packaging Loop Optimization
The system tracks packaging through 13 stages:
1. Goods receipt
2. Stock raw materials
3. Production
4. Empties return
5. Cleaning
6. Dispatch
7. Transit (KB → Supplier)
8. Receipt at supplier
9. Stock at supplier
10. Production (return loop)
11. Stock finished parts
12. Dispatch finished parts
13. Transit (Supplier → KB)

#### Special Packaging Support
- Inlay trays (standard/pallet size)
- Standalone trays with tooling costs
- Additional packaging (pallets, covers)
- Automated filling quantity calculations

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit Web UI                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Pages     │  │   Forms     │  │   Reports   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────┐
│                  Business Logic Layer                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Validators  │  │ Calculator  │  │   Excel     │    │
│  │             │  │   Engine    │  │  Exporter   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────┐
│                    Data Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Session   │  │    JSON     │  │   Backup    │    │
│  │    State    │  │   Storage   │  │   System    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Key Algorithms

#### Packaging Cost Calculation
```python
Packaging Cost = (Plant Cost + CoC Cost + Maintenance + Scrapping) / Lifetime Volume

Where:
- Plant Cost = Σ(Box Cost × Quantity) + Σ(Pallet Cost × Quantity)
- CoC Cost = Special Packaging + Tooling Amortization
```

#### Transport Cost Formula
```python
Transport Cost per Piece = Cost per Load Unit / Filling Quantity per LU

Adjustments:
- Sea freight: Considers overseas packaging
- Incoterms: FCA/FOB include bonded warehouse costs
```

#### Warehouse Cost Model
```python
Warehouse Cost = (Storage Locations × Monthly Cost × 12) / Annual Volume

Where:
- Storage Locations = Local Supply + Safety Stock
- Safety Stock = ⌈(Lead Time × Daily Demand) / Fill Quantity⌉
```

## 🔧 Configuration

### Application Settings

Configuration file: `.streamlit/config.toml`

```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#f8f9fa"
secondaryBackgroundColor = "#e9ecef"
textColor = "#212529"
```

### Data Persistence

- **Location**: `logistics_data.json`
- **Backups**: `backups/` directory
- **Auto-save**: Enabled by default (configurable)
- **Format**: Human-readable JSON

### Environment Variables

```bash
# Optional configuration
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_THEME_PRIMARY_COLOR="#1f77b4"
```

## 📊 Data Formats

### Export Formats

#### Excel Report Structure
- Professional formatting matching corporate templates
- Color-coded sections for easy navigation
- Summary dashboard with key metrics
- Detailed breakdowns by cost component

#### JSON Configuration Schema
```json
{
  "materials": [...],
  "suppliers": [...],
  "packaging": [...],
  "transport": [...],
  "warehouse": [...],
  "metadata": {
    "version": "1.0.0",
    "timestamp": "ISO-8601"
  }
}
```

## 🚦 Validation Rules

The platform enforces strict validation to ensure data quality:

- **Material Numbers**: Unique, alphanumeric
- **Weights**: Positive numbers, max 10,000 kg
- **Percentages**: 0-100% range
- **Currencies**: Standard 3-letter codes
- **Lead Times**: 0-365 days

## 🔒 Security & Compliance

- Local data storage (no cloud dependencies)
- No external API calls for sensitive data
- GDPR-compliant data handling
- Role-based access control ready

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Check code style
flake8 utils/
black --check utils/
```

### Coding Standards

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update documentation accordingly

## 📈 Performance

- **Calculation Speed**: <1 second for 100 material-supplier pairs
- **Memory Usage**: ~50MB for typical datasets
- **Browser Support**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Concurrent Users**: Supports multiple simultaneous sessions

## 🐛 Troubleshooting

### Common Issues

1. **"No module named streamlit"**
   ```bash
   pip install streamlit==1.45.1
   ```

2. **Port already in use**
   ```bash
   streamlit run Overview.py --server.port 8502
   ```

3. **Data not persisting**
   - Check file permissions for `logistics_data.json`
   - Ensure auto-save is enabled in Settings

### Debug Mode

```bash
# Enable debug logging
streamlit run Overview.py --logger.level=debug
```

## 📚 API Reference

### Data Manager API

```python
from utils.data_manager import DataManager

dm = DataManager()

# Materials
dm.add_material(material_data)
dm.get_materials()
dm.update_material(material_no, updated_data)
dm.remove_material(material_no)

# Calculations
dm.is_calculation_ready()
dm.get_material_supplier_pairs()
```

### Calculator API

```python
from utils.calculations import LogisticsCostCalculator

calc = LogisticsCostCalculator()
result = calc.calculate_total_logistics_cost(
    material, supplier, packaging_config,
    transport_config, warehouse_config, ...
)
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- Developed by the Supply Chain Innovation Team
- Special thanks to all beta testers and contributors
- Icons by [Streamlit](https://streamlit.io)

## 📞 Support

- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/logistics-cost-automation/issues)
- **Email**: logistics-support@company.com
- **Wiki**: [Project Wiki](https://github.com/your-org/logistics-cost-automation/wiki)

---

**[⬆ back to top](#logistics-cost-automation-platform)**

<p align="center">Made with ❤️ by the Logistics Team</p>