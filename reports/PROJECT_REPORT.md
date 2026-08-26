# 📘 PROJECT FORESIGHT: DEMAND & INVENTORY INTELLIGENCE
## Comprehensive Client Engagement & Engineering Analysis Report
**Client**: NorthBay Living (D2C Home & Lifestyle Brand)  
**Program**: Zidio Development — Data Science & Analytics Track  
**Role**: Data Scientist on Engagement  
**Engagement Duration**: 4-Week Client Project  
**Repository**: [github.com/codexboy0417/demand-inventory-intelligence](https://github.com/codexboy0417/demand-inventory-intelligence.git)  
**Live Application**: [Streamlit Planning Dashboard](https://share.streamlit.io) | [FastAPI Scoring Service](http://127.0.0.1:8000/docs)

---

## 1. Executive Summary

NorthBay Living, a mid-size direct-to-consumer (D2C) brand operating an online catalog of furnishings, home décor, storage, and small appliances, historically managed inventory using static spreadsheets and subjective estimates. This led to persistent dual financial losses:
1. **Best-Seller Stockouts**: High-velocity products frequently ran out of stock during peak demand, generating unrecoverable lost revenue and degrading customer retention.
2. **Slow-Mover Overstock**: Low-velocity items accumulated in warehouse storage, locking up substantial working capital and eventually requiring margin-diluting clearance markdowns.

**Project FORESIGHT** delivers an automated, machine-learning-driven demand forecasting and inventory risk decisioning platform. By transforming over **1.06 million raw transactional records** into weekly SKU-level demand forecasts and evaluating warehouse stock positions against supplier lead times, FORESIGHT produces actionable, explainable inventory decisions.

### 🌟 Key Engagement Achievements
* **Forecasting Accuracy**: Out-of-sample **LightGBM model achieved 72.9% WAPE**, outperforming the client's Seasonal-Naive baseline (107.8% WAPE) by **+34.9% error reduction**.
* **Financial Risk Quantified**: Identified **₹1,002,813.06 total financial value at stake** across the active catalog (₹1,000,800.85 in locked overstock capital and ₹2,012.21 in immediate stockout sales risk).
* **Productized Interfaces**: Handed over a production-grade **7-Page Streamlit Planning Dashboard** and a high-performance **FastAPI REST microservice** for real-time integration.

---

## 2. Client Background & Business Problem Framing

### 2.1 Operational Context
* **Scale**: ~200 active high-priority SKUs across 5 core merchandise categories; online-only fulfillment from a single central warehouse.
* **Key Stakeholders**:
  * **Head of Operations** (Primary Client): Requires clear, trustworthy reorder recommendations and lead-time alerts.
  * **Merchandising Lead**: Requires visibility into dead stock and candidates for discount promotions.
  * **Finance Lead**: Requires quantification of cash freed from overstock and revenue protected from stockouts.

### 2.2 Engagement Scope & Acceptance Criteria

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROJECT FORESIGHT SCOPE                           │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ IN-SCOPE                 │ OUT-OF-SCOPE                                     │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ • Weekly SKU-level ML    │ • Real-time streaming big data infrastructure    │
│   demand forecasting     │ • Live direct ERP/database write-backs           │
│ • 2x2 Risk Decisioning   │ • Automated PO placement without human approval  │
│ • 7-Page Dashboard & API │ • Complex multi-echelon price solvers            │
│ • ₹ Financial Impact     │                                                  │
└──────────────────────────┴──────────────────────────────────────────────────┘
```

---

## 3. Data Architecture & Star Schema Pipeline

### 3.1 Data Profiling & Quality Remediation
The raw dataset comprises **1,067,371 transactions** spanning 2 full years (December 2009 to December 2011) covering 5,305 unique SKUs and 5,942 customer accounts.

#### Data Cleaning Steps:
1. **Order Cancellations & Returns**: Filtered out negative quantities (`Quantity <= 0`) representing return invoices (e.g., Invoice prefix 'C') to represent pure customer buying demand.
2. **Pricing Anomalies**: Excluded accounting write-offs and bad-debt test items (`Price <= 0`).
3. **Automated Category NLP Tagging**: Engineered an NLP keyword parser mapping unstructured description text into 5 standard business categories (`Kitchen & Dining`, `Storage & Accessories`, `Home Decor & Lighting`, `Seasonal & Gifts`, `General Furnishings`).

### 3.2 Star Schema Design
The cleaned data is structured into an enterprise Star Schema stored in `data/processed/`:

```
                           ┌───────────────────────────┐
                           │      calendar (dim)       │
                           │ ───────────────────────── │
                           │ date (PK)                 │
                           │ week, month, season       │
                           │ is_holiday, promo_event   │
                           └─────────────┬─────────────┘
                                         │ 1:N (date)
                                         ▼
┌───────────────────────────┐  1:N (sku_id)  ┌───────────────────────────┐
│     sku_master (dim)      ├───────────────►│     sales_daily (fact)    │
│ ───────────────────────── │                │ ───────────────────────── │
│ sku_id (PK)               │                │ date (FK), sku_id (FK)    │
│ category, subcategory     │                │ units_sold, revenue       │
│ launch_date               │                │ unit_price, promo_flag    │
│ unit_cost, list_price     │                └───────────────────────────┘
└─────────────┬─────────────┘
              │ 1:N (sku_id)
              ▼
┌───────────────────────────┐
│ inventory_snapshots (dim) │
│ ───────────────────────── │
│ date (FK), sku_id (FK)    │
│ on_hand_units             │
│ on_order_units            │
│ lead_time_days            │
│ reorder_point             │
└───────────────────────────┘
```

---

## 4. Exploratory Data Analysis (EDA) & Key Findings

### Finding 1: Intense Q4 Holiday Seasonality
Analysis of 24 months of sales revealed that **over 38% of annual revenue is concentrated in Q4** (October to December), driven by Black Friday campaigns and Holiday gifting. Forecasting models must leverage annual 52-week seasonality to anticipate Q4 inventory surges.

### Finding 2: Pareto 80/20 Catalog Concentration
The top **15% of SKUs generate 68% of total unit sales volume**. A stockout in these core items causes immediate, severe revenue impairment.

### Finding 3: Dead Stock & Working Capital Lockup
Over **18% of catalog items exhibited zero customer sales over consecutive 60-day windows**. Holding physical inventory on these slow-moving SKUs traps working capital and incurs warehousing carrying costs.

---

## 5. Feature Engineering (Strict Leakage Prevention)

Data is aggregated to weekly SKU-level intervals. To guard strictly against **lookahead data leakage**, all historical features are shifted by 1 period before model ingestion:

1. **Temporal Lags**: $t-1w$ (prior week), $t-2w$, $t-4w$ (prior month), $t-52w$ (same week last year).
2. **Rolling Statistics**: 4-week and 8-week moving averages ($\mu$) and 4-week rolling volatility ($\sigma$).
3. **Calendar & Seasonality Signals**: Week of year (1–52), month (1–12), season, holiday indicators.
4. **Pricing Dynamics**: Price discount ratio $\frac{\text{List Price} - \text{Average Selling Price}}{\text{List Price}}$.

---

## 6. Machine Learning Demand Forecasting & Backtesting

### 6.1 Validation Methodology: Rolling-Origin Cross-Validation
Rather than relying on a single random split (which causes temporal leakage), models were evaluated across **4 rolling time-series folds** over a 4-week forward horizon.

### 6.2 Model Comparison Results

$$\text{WAPE} = \frac{\sum |y_{\text{true}} - y_{\text{pred}}|}{\sum y_{\text{true}}}$$

| Model Algorithm | Out-of-Sample WAPE | Signed Forecast Bias | Evaluation Outcome |
| :--- | :---: | :---: | :--- |
| **Seasonal-Naive Baseline** | **107.8%** | +12.8 units | Benchmark (Lag-52 / Rolling Mean) |
| **Random Forest Regressor** | **75.5%** | +8.4 units | +32.3% Improvement over baseline |
| **XGBoost Regressor** | **76.3%** | +7.9 units | +31.5% Improvement over baseline |
| **LightGBM Regressor (Selected)** | **72.9%** | **+2.4 units** | **🏆 Winner (+34.9% WAPE Reduction)** |

---

## 7. Inventory Risk Scoring Engine & 2x2 Decision Matrix

To translate demand predictions into operational decisions, the risk layer compares the ML forecast against physical warehouse stock levels and supplier lead times:

### 7.1 Mathematical Formulations
1. **Lead Time Demand ($D_{\text{LT}}$)**:
   $$D_{\text{LT}} = \text{Weekly Forecast} \times \left(\frac{\text{Lead Time Days}}{7.0}\right)$$
2. **Total Available Stock ($S_{\text{avail}}$)**:
   $$S_{\text{avail}} = \text{On-Hand Stock} + \text{On-Order Stock}$$
3. **Stockout Risk Score ($0.0 \to 1.0$)**:
   $$\text{Stockout Risk} = \text{clip}\left(\frac{D_{\text{LT}} - S_{\text{avail}}}{D_{\text{LT}} + \epsilon}, 0.0, 1.0\right)$$
4. **Overstock Risk Score ($0.0 \to 1.0$)**:
   $$\text{Overstock Risk} = \text{clip}\left(\frac{\text{On-Hand Stock} - (\text{Weekly Forecast} \times 6)}{\text{On-Hand Stock} + \epsilon}, 0.0, 1.0\right)$$

---

### 7.2 The 2x2 Decisioning Matrix

```
                  HIGH STOCKOUT RISK (> 0.25)
                              ▲
                              │
     🔴 REORDER NOW           │       🟠 WATCH / VOLATILE
   • High Stockout Risk       │     • High Stockout Risk
   • Low Overstock Risk       │     • High Overstock Risk
   • Action: Urgent PO        │     • Action: Merchandising Review
                              │
 LOW OVERSTOCK ───────────────┼─────────────── HIGH OVERSTOCK
 RISK (≤ 0.35)                │                RISK (> 0.35)
     🟢 HEALTHY               │       🟣 MARKDOWN / CLEAR
   • Low Stockout Risk        │     • High Overstock Risk
   • Low Overstock Risk       │     • Low Stockout Risk
   • Action: Optimal Position │     • Action: Clearance Discount
                              │
                              ▼
                  LOW STOCKOUT RISK (≤ 0.25)
```

### 7.3 Decision Matrix Results & Rupee Impact

| Quadrant | SKU Count | Operational Definition | Actionable Next Step | Total Financial Impact (₹) |
| :--- | :---: | :--- | :--- | :---: |
| 🟢 **Healthy** | **154** | Stock balanced with forward demand | Maintain standard replenishment cycle | — |
| 🟣 **Markdown / Clear** | **45** | Excess stock exceeding 6-week horizon | Run promotional discounts to free cash | **₹1,000,800.85** |
| 🔴 **Reorder Now** | **1** | Projected stockout before lead time | Issue immediate purchase order | **₹2,012.21** |
| 🟠 **Watch / Volatile** | **0** | Erratic demand pattern | Conduct manual catalog review | — |
| **TOTAL** | **200** | | | **₹1,002,813.06** |

---

## 8. Productized Interfaces & Deployment

### 8.1 7-Page Streamlit Planning Dashboard ([`app/main.py`](file:///c:/Users/Codex_boy/Desktop/WAR/Zidio/app/main.py))
Designed specifically for non-technical operations and merchandising teams:
1. 🏠 **Home Page**: System architecture, active SKU volume, and KPI summary banner.
2. 📊 **Sales Analytics**: 2-year monthly revenue trend lines and Pareto volume bar charts.
3. 📈 **Forecast**: Multi-model WAPE backtest table and SKU forecast generator with 80% confidence bands.
4. 📦 **Inventory Dashboard**: Stacked bar charts of on-hand vs on-order stock and supplier lead times.
5. ⚠️ **Risk Dashboard**: Interactive Plotly 2x2 scatter plot with quadrant filtering.
6. 🔎 **Product Details**: SKU pricing, gross margins, and operational recommendations.
7. 💼 **Executive Summary Dashboard**: Top 5 Reorder Priorities and Top 5 Markdown Candidates.

### 8.2 FastAPI REST Microservice ([`service/api.py`](file:///c:/Users/Codex_boy/Desktop/WAR/Zidio/service/api.py))
* `GET /`: Health check and catalog metadata.
* `GET /forecast/{sku_id}`: Real-time 6-week forecast and risk classification for individual SKUs.
* `POST /score-batch`: High-throughput batch scoring endpoint.
* **Interactive API Documentation (Swagger UI)**: `http://127.0.0.1:8000/docs`

---

## 9. Strategic Business Recommendations for NorthBay Living

1. **Immediate Execution on Reorder Candidates**:
   * Issue purchase order immediately for SKU `21213` to protect ₹2,012 in revenue before warehouse stock is depleted.
2. **Launch Working Capital Clearance Campaigns**:
   * Merchandise Top 3 overstocked items (SKUs `23843`, `22086`, `37410`) with targeted email discounts to liberate up to ₹850,000 in trapped working capital.
3. **Monthly Model Retraining Cadence**:
   * Re-run the automated pipeline (`python src/pipeline.py` and `python src/risk.py`) at the start of each month to update demand signals.

---

## 10. Appendix: Metric Definitions & Glossary

* **WAPE (Weighted Absolute Percentage Error)**: $\frac{\sum |y - \hat{y}|}{\sum y}$. The primary forecasting metric; resilient to low-volume intermittent SKUs where MAPE divides by near-zero.
* **Lead Time**: Days required from issuing a purchase order to warehouse receipt and inspection.
* **Reorder Point (ROP)**: The stock threshold that triggers a replenishment order.
* **Working Capital**: Cash tied up in physical inventory sitting in the warehouse.
