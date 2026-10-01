# Capstone-Project-Mamaearth-Returns-Growth-Intelligence-Pipeline

### Dhanumjay Rajesh Jagarapu

## Project Overview

This capstone builds an end-to-end returns and growth intelligence pipeline for Mamaearth using SQL, Python, data visualization, and GenAI-assisted business narration.

The pipeline cleans and validates customer, product, and order data, investigates return patterns, reconciles raw and cleaned revenue, identifies the true revenue trend after accounting for outliers, and converts verified analytical findings into a structured business narrative.

### Business Question

**Where are returns really coming from, and what is the true revenue picture once the data is cleaned?**

## Repository Structure

```text
Capstone-Project-Mamaearth-Returns-Growth-Intelligence-Pipeline/
├── README.md
├── requirements.txt
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── reports.sql
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── orders.csv
├── analysis/
│   ├── clean_and_eda.py
│   └── visualize.py
├── visualizations/
│   ├── return_rate_by_payment.png
│   └── monthly_revenue_trend.png
└── narrator/
    ├── findings.json
    ├── generate_narrative.py
    └── sample_output.txt

```

## How to Run the Project

Run the pipeline in the following order.

### Part 1 — SQL Database and Reports

The SQL stage creates the SQLite database structure, loads the raw CSV data, normalizes blank values to SQL `NULL`, and runs the required analytical reports.

From the project root, start SQLite:

```bash
sqlite3 mamaearth.db
```

Then run the SQL files in this order:

```sql
.read sql/schema.sql
.read sql/seed_data.sql
.read sql/reports.sql
```

The source datasets used by the SQL pipeline are located in the `data/` directory:

- `customers.csv`
- `products.csv`
- `orders.csv`

The SQL reports cover order and revenue summaries, rating completeness, customers with no orders, city-level return rates, top customers by revenue, category performance, customer-name filtering, acquisition channels, and loyalty-tier classification.

### Part 2 — Python Data Cleaning, EDA, and Visualization

Install the required Python packages from the project root:

```bash
pip install -r requirements.txt
```

Run the cleaning and exploratory data analysis script first:

```bash
python analysis/clean_and_eda.py
```

This script performs the required data-cleaning and analysis workflow, including duplicate removal, missing-value treatment, payment-method standardization, revenue calculation, return-rate analysis, city-tier segmentation, correlation analysis, and quantity-outlier identification.

It also generates the verified analytical findings used by the narrator and writes them to:

```text
narrator/findings.json
```

Next, generate the required visualizations:

```bash
python analysis/visualize.py
```

The visualization script creates:

```text
visualizations/return_rate_by_payment.png
visualizations/monthly_revenue_trend.png
```

The monthly revenue visualization uses the outlier-aware revenue series so that the genuine revenue peak can be distinguished from the apparent peak caused by flagged bulk-order outliers.

### Part 3 — GenAI Insight Narrator

The narrator reads only the verified analytical findings stored in:

```text
narrator/findings.json
```

Run the narrator from the project root:

```bash
python narrator/generate_narrative.py
```

#### Gemini API Mode

To use the Gemini API, set the API key as an environment variable named `GEMINI_API_KEY` before running the narrator.

Windows Command Prompt:

```bash
set GEMINI_API_KEY=your_api_key_here
python narrator/generate_narrative.py
```

Do not store or commit the actual API key in the repository.

#### Offline Fallback Mode

If `GEMINI_API_KEY` is not configured, or if the Gemini API returns an error, the script automatically uses the deterministic offline fallback.

The offline narrator requires no API key or network call and produces the same three-section business structure:

- Situation
- Complication
- Resolution

The generated narrative is saved to:

```text
narrator/sample_output.txt
```

A verification checker validates that the narrative contains all five mandatory findings: cleaned revenue, COD return rate, COD + Tier 2 highest-risk return rate, duplicate reconciliation delta, and the true March revenue peak.

The offline fallback was successfully tested and all five verification checks passed. The Gemini online path was also tested; during testing, the API returned a `503 UNAVAILABLE` high-demand response, after which the offline fallback executed successfully.

## Key Verified Findings

- Raw total revenue: **₹99,860.20**
- Cleaned total revenue after duplicate removal: **₹97,358.30**
- Duplicate reconciliation difference: **₹2,501.90**
- COD return rate: **44.4%**
- Card return rate: **14.7%**
- UPI return rate: **18.9%**
- Highest-risk segment: **COD + Tier 2 cities — 54.5% return rate**
- January 2026 apparent revenue: **₹29,582.10**
- January 2026 outlier-corrected revenue: **₹11,637.10**
- True peak revenue month: **March 2026 — ₹20,318.90**

These figures are generated from the analytical pipeline and passed to the narrative layer through `narrator/findings.json`.
