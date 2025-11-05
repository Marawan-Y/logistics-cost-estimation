# Logistics Cost Estimation — Deployment Roadmap

This document provides a **complete step-by-step guide** to deploy the `logistics-cost-estimation` Streamlit application on your internal domain and migrate its data storage from local JSON files into **Snowflake**, which will serve as the central data warehouse.

The guidance is organized into sections covering current state analysis, schema design, Snowflake setup, application modifications and deployment instructions. Each step includes ready-to-use SQL and code snippets.

---

## 1. Current State Analysis

The application currently uses a local `data` directory to persist user configuration via JSON files. Each record type is stored in a separate file:

| Record Type | JSON File | Notes |
|-------------|-----------|-------|
| **Materials** | `materials.json` | Contains an array of material objects with properties like project name, material number, weight per piece, volumes, etc. |
| **Suppliers** | `suppliers.json` | Stores supplier details including vendor ID, name, location and plant information. |
| **Operations** | `operations.json` | Stores incoterm and logistics operation details. |
| **Packaging** | `packaging.json` | Contains packaging cost inputs and packaging loop details. |
| **Repacking** | `repacking.json` | Contains weight-category based repacking costs. |
| **Transport Config** | `transport.json` | Stores configuration for automatic or manual transport cost calculation. |
| **CO₂ Cost** | `co2.json` | Stores cost per ton and conversion factor. |
| **Warehouse** | `warehouse.json` | Stores cost per pallet. |
| **Interest** | `interest.json` | (placeholder) stores interest rate. |
| **Additional Costs** | `additional_costs.json` | Stores miscellaneous cost items. |
| **Transport DB** | `transport_db.json` | Contains lane definitions, weight clusters and pricing. |
| **Backups** | `logistics_data.json` | Consolidated backup of all configuration. |

The **DataManager** class orchestrates reading and writing these files and manages backups. When migrating to Snowflake, each JSON file will be represented by one or more tables.

---

## 2. Snowflake Schema Design

The following schema definitions transform the JSON structures into relational tables. All tables are created in the `LOGISTICS_DB.APP_DATA` schema. You can copy and paste these SQL statements directly into Snowflake.

### 2.1 Database and Schema

```sql
CREATE OR REPLACE DATABASE LOGISTICS_DB;
CREATE OR REPLACE SCHEMA LOGISTICS_DB.APP_DATA;
```

### 2.2 Materials

```sql
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.materials (
    id                 INTEGER AUTOINCREMENT,
    project_name       VARCHAR NOT NULL,
    material_no        VARCHAR NOT NULL,
    description        VARCHAR,
    weight_per_pcs     FLOAT,
    annual_volume      INTEGER,
    daily_demand       INTEGER,
    working_days       INTEGER,
    sop_date           DATE,
    price_per_pcs      FLOAT,
    life_time_years    INTEGER,
    created_at         TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at         TIMESTAMP_LTZ,
    PRIMARY KEY (id)
);
```

### 2.3 Suppliers

```sql
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.suppliers (
    id                    INTEGER AUTOINCREMENT,
    vendor_id             VARCHAR NOT NULL,
    supplier_name         VARCHAR NOT NULL,
    supplier_country      VARCHAR,
    supplier_city         VARCHAR,
    supplier_zip          VARCHAR,
    delivery_performance  FLOAT,
    deliveries_per_month  INTEGER,
    plant                 VARCHAR,
    plant_country         VARCHAR,
    plant_city            VARCHAR,
    plant_zip             VARCHAR,
    distance_km           FLOAT,
    created_at            TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at            TIMESTAMP_LTZ,
    PRIMARY KEY (id)
);
```

### 2.4 Operations

```sql
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.operations (
    id                   INTEGER AUTOINCREMENT,
    incoterm_code        VARCHAR NOT NULL,
    incoterm_place       VARCHAR,
    part_classification  VARCHAR,
    call_off_type        VARCHAR,
    directive            VARCHAR,
    lead_time_days       INTEGER,
    sub_supplier_used    BOOLEAN,
    packaging_tool_owner VARCHAR,
    responsible_party    VARCHAR,
    currency             VARCHAR,
    created_at           TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at           TIMESTAMP_LTZ,
    PRIMARY KEY (id)
);
```

### 2.5 Packaging

Packaging configuration contains several cost components and a nested **packaging loop** which describes the days spent in each stage (e.g. assembly, shipping, storage, cleaning). We normalize this into two tables.

```sql
-- Main packaging record
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.packaging (
    id                           INTEGER AUTOINCREMENT,
    maintenance_cost_per_pcs     FLOAT,
    empties_scrapping_cost       FLOAT,
    standard_box_type            VARCHAR,
    standard_fill_qty            INTEGER,
    standard_pallet_type         VARCHAR,
    additional_packaging_price   FLOAT,
    special_pack_needed          BOOLEAN,
    special_pack_type            VARCHAR,
    special_trays_per_pallet     INTEGER,
    special_pack_tooling_cost    FLOAT,
    one_way_packaging_cost       FLOAT,
    created_at                   TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at                   TIMESTAMP_LTZ,
    PRIMARY KEY (id)
);

-- Packaging loop stages for each packaging record
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.packaging_loop (
    packaging_id  INTEGER,
    stage_name    VARCHAR NOT NULL,
    days          INTEGER,
    PRIMARY KEY (packaging_id, stage_name),
    FOREIGN KEY (packaging_id) REFERENCES LOGISTICS_DB.APP_DATA.packaging(id)
);
```

### 2.6 Repacking

```sql
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.repacking (
    id               INTEGER AUTOINCREMENT,
    weight_category  VARCHAR NOT NULL,
    one_way_cost     FLOAT,
    returnable_cost  FLOAT,
    created_at       TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at       TIMESTAMP_LTZ,
    PRIMARY KEY (id)
);
```

### 2.7 Transport Configuration

```sql
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.transport_config (
    id                 INTEGER AUTOINCREMENT,
    mode               VARCHAR NOT NULL,  -- 'Automatic' or 'Manual'
    manual_cost_per_lu FLOAT,             -- cost per load unit (manual mode)
    stack_factor       FLOAT,             -- how many load units per pallet
    bonded_warehouse   BOOLEAN,
    created_at         TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at         TIMESTAMP_LTZ,
    PRIMARY KEY (id)
);
```

### 2.8 Transport Lanes

Transport lanes store weight-based pricing. We normalize weight clusters into a separate table.

```sql
-- Lane definitions
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.transport_lanes (
    id               INTEGER AUTOINCREMENT,
    origin_country   VARCHAR,
    origin_city      VARCHAR,
    origin_zip       VARCHAR,
    destination_country VARCHAR,
    destination_city VARCHAR,
    destination_zip  VARCHAR,
    lead_time_days   INTEGER,
    full_truck_price FLOAT,
    fuel_surcharge   VARCHAR,   -- e.g. '22.5%' or '0.25 EUR'
    created_at       TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at       TIMESTAMP_LTZ,
    PRIMARY KEY (id)
);

-- Weight cluster pricing for each lane
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.transport_lane_prices (
    lane_id      INTEGER,
    weight_min   FLOAT,
    weight_max   FLOAT,
    price_per_kg FLOAT,
    PRIMARY KEY (lane_id, weight_min),
    FOREIGN KEY (lane_id) REFERENCES LOGISTICS_DB.APP_DATA.transport_lanes(id)
);
```

### 2.9 CO₂ Cost

```sql
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.co2_cost (
    id               INTEGER AUTOINCREMENT,
    cost_per_ton     FLOAT NOT NULL,
    conversion_factor FLOAT NOT NULL,
    created_at       TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at       TIMESTAMP_LTZ,
    PRIMARY KEY (id)
);
```

### 2.10 Warehouse Cost

```sql
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.warehouse_cost (
    id             INTEGER AUTOINCREMENT,
    cost_per_pallet FLOAT NOT NULL,
    created_at     TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at     TIMESTAMP_LTZ,
    PRIMARY KEY (id)
);
```

### 2.11 Interest Cost (Inventory)

```sql
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.interest_cost (
    id               INTEGER AUTOINCREMENT,
    interest_rate_pct FLOAT NOT NULL,
    created_at       TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at       TIMESTAMP_LTZ,
    PRIMARY KEY (id)
);
```

### 2.12 Additional Costs

```sql
CREATE OR REPLACE TABLE LOGISTICS_DB.APP_DATA.additional_costs (
    id            INTEGER AUTOINCREMENT,
    cost_name     VARCHAR NOT NULL,
    cost_per_pcs  FLOAT NOT NULL,
    created_at    TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at    TIMESTAMP_LTZ,
    PRIMARY KEY (id)
);
```

---

## 3. Snowflake Setup & Privileges

### 3.1 Warehouse and Role

Create a dedicated warehouse and role for the application. The role will have permissions to create and manipulate tables and to run the Streamlit app (if hosting directly in Snowflake).

```sql
-- Create warehouse
CREATE OR REPLACE WAREHOUSE LOGISTICS_WH
  WITH WAREHOUSE_SIZE = 'XSMALL'  -- adjust size based on expected load
  AUTO_SUSPEND = 300  -- suspend after 5 minutes of inactivity
  AUTO_RESUME = TRUE;

-- Create role
CREATE OR REPLACE ROLE LOGISTICS_APP_ROLE;

-- Grant privileges
GRANT USAGE ON WAREHOUSE LOGISTICS_WH TO ROLE LOGISTICS_APP_ROLE;
GRANT USAGE, CREATE TABLE ON DATABASE LOGISTICS_DB TO ROLE LOGISTICS_APP_ROLE;
GRANT USAGE, CREATE TABLE, SELECT, INSERT, UPDATE, DELETE ON SCHEMA LOGISTICS_DB.APP_DATA TO ROLE LOGISTICS_APP_ROLE;

-- Create service user
CREATE OR REPLACE USER logistics_app
  PASSWORD = '<STRONG_PASSWORD>'
  DEFAULT_ROLE = LOGISTICS_APP_ROLE
  DEFAULT_WAREHOUSE = LOGISTICS_WH
  MUST_CHANGE_PASSWORD = FALSE;

GRANT ROLE LOGISTICS_APP_ROLE TO USER logistics_app;
```

### 3.2 Streamlit App Privileges (Optional)

If you choose to **host the Streamlit app inside Snowflake** using *Streamlit in Snowflake*, you need an additional privilege:

```sql
-- Grant the ability to create Streamlit apps in the schema
GRANT CREATE STREAMLIT ON SCHEMA LOGISTICS_DB.APP_DATA TO ROLE LOGISTICS_APP_ROLE;
```

Only roles with this privilege can create or modify Streamlit apps. Viewers need `USAGE` on the database, schema and the Streamlit object.

---

## 4. Data Migration (Backfill)

To migrate existing JSON data into Snowflake, use Python and the `snowflake-connector-python` library.

### 4.1 Install the Snowflake Connector

In your local environment (or a temporary script), run:

```bash
pip install snowflake-connector-python
```

### 4.2 Migration Script Template

Save the following script as `data_migration.py`. It reads each JSON file from the `data` directory and inserts records into the Snowflake tables.

```python
import json
import os
import snowflake.connector

# Load Snowflake credentials from environment variables
conn = snowflake.connector.connect(
    user=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    account=os.getenv('SNOWFLAKE_ACCOUNT'),
    warehouse='LOGISTICS_WH',
    database='LOGISTICS_DB',
    schema='APP_DATA'
)

cursor = conn.cursor()

def load_json(file_name):
    path = os.path.join('data', file_name)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 1. Load materials
materials = load_json('materials.json')
for m in materials:
    cursor.execute(
        """
        INSERT INTO materials (
            project_name, material_no, description, weight_per_pcs,
            annual_volume, daily_demand, working_days, sop_date,
            price_per_pcs, life_time_years
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            m.get('project_name'), m.get('material_no'), m.get('material_desc'),
            m.get('weight_per_pcs'), m.get('annual_volume'), m.get('daily_demand'),
            m.get('working_days'), m.get('sop'), m.get('price_per_pcs'), m.get('life_time_years')
        )
    )

# 2. Load suppliers
suppliers = load_json('suppliers.json')
for s in suppliers:
    cursor.execute(
        """
        INSERT INTO suppliers (
            vendor_id, supplier_name, supplier_country, supplier_city, supplier_zip,
            delivery_performance, deliveries_per_month, plant, plant_country,
            plant_city, plant_zip, distance_km
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            s.get('vendor_id'), s.get('supplier_name'), s.get('supplier_country'),
            s.get('supplier_city'), s.get('supplier_zip'), s.get('delivery_performance'),
            s.get('deliveries_per_month'), s.get('plant'), s.get('plant_country'),
            s.get('plant_city'), s.get('plant_zip'), s.get('distance_km')
        )
    )

# Repeat similarly for other tables...

conn.commit()
cursor.close()
conn.close()
```

> **Note:** Adjust the script for other tables (operations, packaging, packaging_loop, repacking, transport_config, transport_lanes, transport_lane_prices, co2_cost, warehouse_cost, interest_cost, additional_costs) by reading the corresponding JSON files and mapping their fields to table columns.

---

## 5. Application Code Modifications

After migrating data, modify the application to use Snowflake instead of local JSON files.

### 5.1 Install the Snowflake Connector in the App

Add the package to your `requirements.txt` or install it in the environment:

```bash
pip install snowflake-connector-python
```

### 5.2 Provide Credentials as Environment Variables

Define these variables on the host server or in a `.env` file (do **not** hard-code credentials):

```bash
SNOWFLAKE_USER=logistics_app
SNOWFLAKE_PASSWORD=<STRONG_PASSWORD>
SNOWFLAKE_ACCOUNT=<your_account_identifier>
SNOWFLAKE_WAREHOUSE=LOGISTICS_WH
SNOWFLAKE_DATABASE=LOGISTICS_DB
SNOWFLAKE_SCHEMA=APP_DATA
```

### 5.3 Add a Snowflake Connection Helper

Inside the project (e.g. `utils/snowflake_helper.py`), create a function to open a connection:

```python
import os
import snowflake.connector

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
    )
```

### 5.4 Refactor DataManager

- Add a flag `use_snowflake` in `DataManager.__init__()` that reads an environment variable such as `USE_SNOWFLAKE`.
- For each CRUD operation (load, add, update, delete), call Snowflake queries if `use_snowflake` is `True`; otherwise, fall back to the existing JSON logic.
- Example for loading materials:

```python
from utils.snowflake_helper import get_snowflake_connection

class DataManager:
    def __init__(self):
        self.use_snowflake = os.getenv('USE_SNOWFLAKE', 'false').lower() == 'true'
        # existing init code...

    def load_materials(self):
        if self.use_snowflake:
            conn = get_snowflake_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, project_name, material_no, description, weight_per_pcs, annual_volume, daily_demand, working_days, sop_date, price_per_pcs, life_time_years FROM materials")
            rows = cursor.fetchall()
            # Convert to list of dicts
            return [
                {
                    'id': r[0], 'project_name': r[1], 'material_no': r[2],
                    'material_desc': r[3], 'weight_per_pcs': r[4],
                    'annual_volume': r[5], 'daily_demand': r[6],
                    'working_days': r[7], 'sop': r[8],
                    'price_per_pcs': r[9], 'life_time_years': r[10]
                }
                for r in rows
            ]
        else:
            return self._load_json('materials.json')
```

- Write similar functions for saving, updating and deleting records. Use parameterized SQL statements to prevent SQL injection.
- Update code where session state lists are used to fetch or save data accordingly.

### 5.5 Update Export/Import Functions

Since data is now stored in Snowflake, the export functionality can query Snowflake tables and produce JSON/CSV files using pandas:

```python
import pandas as pd
from utils.snowflake_helper import get_snowflake_connection

def export_all_data_to_json():
    conn = get_snowflake_connection()
    full_data = {}
    for table_name in [
        'materials', 'suppliers', 'operations', 'packaging', 'packaging_loop',
        'repacking', 'transport_config', 'transport_lanes', 'transport_lane_prices',
        'co2_cost', 'warehouse_cost', 'interest_cost', 'additional_costs']:
        df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
        full_data[table_name] = df.to_dict(orient='records')
    with open('logistics_data.json', 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2, default=str)
```

Modify import functions to insert data into Snowflake tables accordingly.

---

## 6. Deployment on the Internal Domain

### 6.1 Server Preparation

1. **Provision a server** (virtual machine or container) in your internal network. Ensure it has Python 3.10 or later.

2. **Clone the repository** and set up a virtual environment:

```bash
git clone https://github.com/Marawan-Y/logistics-cost-estimation.git
cd logistics-cost-estimation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install snowflake-connector-python
```

3. **Define environment variables** for Snowflake credentials and set `USE_SNOWFLAKE=true`. Place them in a secure file (e.g. `/etc/logistics-app.env`).

4. **Configure a process manager** such as **systemd** to run the app at boot. Example unit file `/etc/systemd/system/logistics-app.service`:

```ini
[Unit]
Description=Logistics Cost Estimation App
After=network.target

[Service]
Type=simple
User=logistics
EnvironmentFile=/etc/logistics-app.env
WorkingDirectory=/opt/logistics-app
ExecStart=/opt/logistics-app/venv/bin/streamlit run Overview.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Reverse proxy & TLS:** Use Nginx or Apache to expose the app at `https://logistics-app.company.internal` and terminate TLS. Forward requests to `localhost:8501`.

### 6.2 Optional: Hosting Inside Snowflake

If you choose to host the Streamlit app directly in Snowflake:

1. **Grant the** `CREATE STREAMLIT` **privilege** to your role (see step 3.2).

2. **Upload your code** using Snowsight: Projects → Streamlit → `+ Streamlit` → name the app, select `LOGISTICS_WH` and `LOGISTICS_DB.APP_DATA`. Upload `Overview.py` as the main file and all `pages/*.py` files plus `utils/*` using the file manager. Because multi-file editing is limited, this process can be cumbersome for large apps.

3. **Refactor unsupported functionality:** Remove or replace dependencies unavailable in Snowflake (e.g. `llama_cpp`) and external file writes. Use `st.connection('snowflake')` within Streamlit to access data.

4. **Share the app** with other roles by granting `USAGE` on the app and the containing database and schema.

Due to limitations around multi-file uploads and third-party libraries, hosting outside of Snowflake and connecting to Snowflake for data is often simpler for complex applications.

---

## 7. Summary

By following this roadmap:

1. You map the existing JSON-based storage to a well-structured Snowflake schema and create all necessary tables.
2. You configure Snowflake roles and warehouses with appropriate privileges to run the application and, if desired, to host the Streamlit app inside Snowflake.
3. You migrate existing data into Snowflake using a Python script.
4. You refactor the application to use Snowflake as its data store, switching behaviour based on the `USE_SNOWFLAKE` flag.
5. You deploy the Streamlit app on an internal server (or inside Snowflake) with secure environment variables and appropriate process management.

This document is designed to be copied and executed by an IT engineer as a complete deployment manual. Modify names, passwords, and account identifiers to match your organization's conventions.

---

## References

- [Getting started with Streamlit in Snowflake | Snowflake Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/getting-started)
- [Create and deploy Streamlit apps using Snowsight | Snowflake Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/create-streamlit-ui)
- [Multi-page Streamlit apps | Snowflake Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/example-multi-page)