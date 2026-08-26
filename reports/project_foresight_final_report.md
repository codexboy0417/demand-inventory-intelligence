# Project FORESIGHT — Comprehensive Final Project Report
## Demand & Inventory Intelligence Platform for NorthBay Living

---

### Document Control
* **Client**: NorthBay Living (D2C Home & Lifestyle Brand)
* **Domain**: Data Science & Supply Chain Analytics
* **Author**: Data Scientist / Analytics Intern
* **Program**: Zidio Development Client Engagement (4 Weeks)
* **Status**: Complete &bull; Version 1.0
* **Repository**: [github.com/codexboy0417/demand-inventory-intelligence](https://github.com/codexboy0417/demand-inventory-intelligence.git)
* **PDF Report Path**: [`reports/Project_FORESIGHT_Final_Report.pdf`](file:///c:/Users/Codex_boy/Desktop/WAR/Zidio/reports/Project_FORESIGHT_Final_Report.pdf)

---

## 1. Executive Summary
**Project FORESIGHT** is an enterprise-grade demand forecasting and inventory risk intelligence engine built for **NorthBay Living**, a mid-size direct-to-consumer (D2C) home & lifestyle brand. Prior to this engagement, NorthBay Living managed inventory across ~200 active SKUs through intuition and static spreadsheets. This led to severe working capital inefficiencies: high-demand bestsellers frequently stocked out (causing unrecoverable lost revenue), while slow-moving products accumulated, trapping capital and forcing margin-eroding clearance markdowns.

By ingesting and processing **1,067,371 historical transaction records** spanning two full operational years (2009–2011), Project FORESIGHT constructs a reproducible Star-Schema data pipeline, trains multi-model machine learning demand forecasters, and connects these forward projections into an explainable **2x2 Inventory Decisioning Matrix**.

### Key Quantified Highlights:
* **Dataset Scale**: 1,067,371 raw transaction records | 5,305 SKUs | 5,942 registered customer accounts.
* **Forecast Accuracy**: **LightGBM achieved 72.9% out-of-sample WAPE** on a 4-fold rolling-origin backtest, beating the Seasonal-Naive baseline (107.8% WAPE) by **+34.9% error reduction**.
* **Financial Value at Stake**: **₹1,002,813.06 total financial exposure identified**:
  * **₹1,000,800.85 locked in overstock capital** across 45 markdown clearance candidate SKUs.
  * **₹2,012.21 sales at risk from immediate stockouts** requiring purchase order replenishment.
  * **154 Healthy SKUs** running at optimal stock velocity.
* **Productized Interfaces**: Deployed as an interactive **7-Page Streamlit Planning Dashboard** and a **FastAPI REST Scoring Microservice**.

---

## 2. Client Background & Problem Statement
NorthBay Living operates an online-only e-commerce store fulfilling customer orders from a single central warehouse. The product catalog spans furnishings, home decor, storage solutions, kitchenware, and seasonal gifts. The operations, merchandising, and finance teams faced three fundamental bottlenecks:
1. **Dual Financial Loss**: Frequent stockouts on velocity items (lost revenue, customer churn) combined with excess buffer stock on dead inventory (trapped liquidity, warehouse holding costs).
2. **Lack of Algorithmic Visibility**: Planning decisions were made ad-hoc in spreadsheets without statistical feature extraction or seasonality tracking.
3. **Tooling Usability Gap**: Prior data science models remained trapped in code notebooks that operational and merchandising teams could not interact with or interpret.

---

## 3. Data Architecture & Data Quality Audit
The data foundation was modeled using real-world retail transactions from the **Online Retail II dataset**. Raw records were transformed into a production **Star Schema** comprising four structured tables:

| Table Name | Grain & Key Dimensions | Record Count | Core Attributes |
| :--- | :--- | :---: | :--- |
| **`sales_daily`** | Daily SKU Transactions (Fact) | 532,839 | `date`, `sku_id`, `units_sold`, `revenue`, `unit_price`, `promo_flag` |
| **`sku_master`** | Product Catalog (Dimension) | 4,917 | `sku_id`, `category`, `subcategory`, `launch_date`, `unit_cost`, `list_price` |
| **`calendar`** | Date Calendar (Dimension) | 739 | `date`, `week`, `month`, `season`, `is_holiday`, `promo_event` |
| **`inventory_snapshots`** | Current Warehouse Positions | 200 | `date`, `sku_id`, `on_hand_units`, `on_order_units`, `lead_time_days`, `reorder_point` |

### 3.1 Data Cleaning & Preprocessing Decisions:
* **Order Cancellations & Returns**: Negative quantities (invoice prefix 'C') were isolated and excluded from positive sales volume to avoid demand under-counting.
* **Bad Debt & Adjustments**: Transactions with `Price <= 0` (internal tests, accounting write-offs) were systematically purged.
* **Missing Customer IDs**: Handled guest checkout transactions by retaining sales volumes for SKU aggregation while tagging unauthenticated customer rows.
* **Catalog Categorization NLP**: Raw item descriptions lacked standard taxonomies. An automated keyword categorization parser mapped products into 5 structured categories: *Kitchen & Dining, Storage & Accessories, Home Decor & Lighting, Seasonal & Gifts, and General Furnishings*.

---

## 4. Exploratory Data Analysis (EDA) & Key Findings
Exploratory data analysis revealed three critical operational dynamics:
1. **Severe Q4 Holiday Seasonality**: Monthly revenue surges dramatically between October and December. Over **38% of annual revenue** is concentrated in Q4 due to Black Friday promotions and holiday gift purchasing.
2. **The 80/20 Pareto Volume Distribution**: Catalog sales are heavily skewed—the **top 15% of active SKUs generate 68% of total unit volume**. Stockouts in these high-velocity items disproportionately impact brand revenue.
3. **Catalog Dormancy & Dead Stock**: Approximately **18% of catalog SKUs exhibited zero unit sales over consecutive 60-day windows**. Holding substantial warehouse stock on these items represents locked working capital that degrades over time.

---

## 5. Feature Engineering Pipeline
Daily sales were aggregated into weekly SKU observations. To guarantee zero lookahead data leakage during backtesting and live inference, all temporal features were strictly shifted by at least one period before calculation:
* **Temporal Lags**: `lag_1w`, `lag_2w`, `lag_4w`, `lag_52w` (captures immediate momentum and exact same-week annual seasonality).
* **Rolling Moving Statistics**: `rolling_mean_4w`, `rolling_std_4w`, `rolling_mean_8w` (measures moving demand baselines and volatility).
* **Calendar & Cyclical Signals**: `week`, `month`, `season`, `is_holiday`.
* **Pricing Dynamics**: `promo_days`, `price_discount_ratio` (quantifies discount depth and promotional elasticity).

---

## 6. Machine Learning Demand Forecasting & Backtesting
In accordance with professional forecasting governance, models were evaluated using **4-fold Rolling-Origin Cross-Validation** over a 4-week test horizon against a **Seasonal-Naive Baseline**:

| Model Algorithm | Mean Out-of-Sample WAPE | Accuracy vs Baseline | Evaluation Status |
| :--- | :---: | :---: | :--- |
| **Seasonal-Naive Baseline** | **107.8%** | *Reference Benchmark* | Baseline benchmark to clear. |
| **XGBoost Regressor** | **76.3%** | +31.5% Better | High accuracy; gradient boosted trees. |
| **Random Forest Regressor** | **75.5%** | +32.3% Better | Robust ensemble baseline. |
| **LightGBM Regressor (Winner)** | **72.9%** | **+34.9% WAPE Reduction** | 🏆 **Selected Production Forecaster**. |

---

## 7. Inventory Risk Scoring Engine & 2x2 Decision Matrix
Machine learning predictions are decoupled from inventory risk rules to guarantee transparency and explainability for operations managers. The engine evaluates stock positions by comparing forward demand against current physical inventory:

### 7.1 Mathematical Formulations:
* **Lead Time Demand ($D_{LT}$)**: $D_{LT} = \text{Weekly Forecast} \times \left(\frac{\text{Lead Time Days}}{7.0}\right)$
* **Total Available Stock ($S_{avail}$)**: $S_{avail} = \text{On-Hand Stock} + \text{On-Order Stock}$
* **Stockout Risk Score ($0.0 \to 1.0$)**: $\text{clip}\left(\frac{D_{LT} - S_{avail}}{D_{LT} + \epsilon}, 0.0, 1.0\right)$
* **Overstock Risk Score ($0.0 \to 1.0$)**: $\text{clip}\left(\frac{\text{On-Hand Stock} - (\text{Weekly Forecast} \times 6)}{\text{On-Hand Stock} + \epsilon}, 0.0, 1.0\right)$
* **Financial Risk (₹ INR)**:
  * $\text{Sales at Risk} = \text{Stockout Gap} \times \text{List Price}$
  * $\text{Capital Locked} = \text{Overstock Gap} \times \text{Unit Cost}$

### 7.2 2x2 Decision Matrix Results:
* 🔴 **Reorder Now (1 SKU)**: $\text{Stockout Risk} > 0.25$ &bull; ₹2,012.21 Sales at Risk *(Action: Immediate purchase order replenishment)*.
* 🟣 **Markdown / Clear (45 SKUs)**: $\text{Overstock Risk} > 0.35$ &bull; ₹1,000,800.85 Capital Locked *(Action: Promotional discounting campaign)*.
* 🟢 **Healthy (154 SKUs)**: Optimal inventory position *(Action: Maintain standard replenishment)*.
* 🟠 **Watch / Volatile (0 SKUs)**: Stable demand pattern.

---

## 8. Productized Interfaces & Deployment
The analytics stack is packaged into two stakeholder-facing interfaces:
1. **7-Page Streamlit Planning Dashboard (`app/main.py`)**:
   * *Home Page*: Executive summary banner, active SKU counters, architecture flow.
   * *Sales Analytics*: Monthly revenue trends, Pareto 80/20 top-mover bar charts, category revenue share.
   * *Forecast*: Backtest comparison table and interactive SKU forward forecast generator with 80% confidence bands.
   * *Inventory Dashboard*: On-hand vs on-order stacked bar charts and supplier lead-time breakdowns.
   * *Risk Dashboard*: Dynamic 2x2 Plotly scatter plot (bubble size = ₹ value at stake) with quadrant filter tabs.
   * *Product Details*: SKU deep-dive searching, margin economics, and prescribed operational actions.
   * *Executive Summary Dashboard*: High-level ROI metrics, Top 5 Reorder Priorities, Top 5 Markdown Candidates.
2. **FastAPI Scoring Microservice (`service/api.py`)**:
   * `GET /forecast/{sku_id}`: Real-time single-SKU forward demand and risk score lookup.
   * `POST /score-batch`: Batch scoring microservice for ERP/WMS system integrations.

---

## 9. Strategic Business Recommendations & Next Steps
1. **Immediate Reorder Execution**: Execute purchase order replenishment for **SKU 21213** (Storage & Accessories) to protect against imminent stockout revenue losses.
2. **Capital Liberation Clearance Campaign**: Launch structured markdown promotions across the **Top 3 Overstock SKUs (23843, 22086, 37410)**, liberating ₹1,000,800.85 in trapped working capital to reinvest into high-velocity inventory lines.
3. **Monthly Automated Pipeline Cadence**: Run `python src/risk.py lightgbm` at the start of every month to refresh forecasts as new inventory snapshots arrive.
