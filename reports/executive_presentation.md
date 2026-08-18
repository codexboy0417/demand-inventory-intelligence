# Project FORESIGHT — Executive Presentation Deck
## Demand & Inventory Intelligence for NorthBay Living

---

### Slide 1: Business Problem
* **The Dual-Loss Dilemma**: NorthBay Living faces inventory inefficiencies on both ends of the product spectrum:
  1. **Stockouts on Best-Sellers**: Depleted inventory results in lost revenue, unfulfilled customer demand, and lowered brand equity.
  2. **Overstock on Slow-Movers**: Capital remains trapped in slow-moving stock, eventually requiring margin-diluting markdowns.
* **Core Goal**: Transition from spreadsheet-based guessing to an automated demand forecasting and risk decisioning platform that guides stock reordering and clearance actions.

---

### Slide 2: Client Background
* **Client**: **NorthBay Living** (Direct-to-Consumer home & lifestyle brand).
* **Scope**: ~200 active SKUs across furnishings, décor, storage, and small appliances.
* **Operating Model**: Online-only, single-warehouse fulfillment.
* **Stakeholders**: Head of Operations (reorder planning), Merchandiser (promotions & markdowns), Finance Lead (working capital management).

---

### Slide 3: Dataset Architecture
* **Data Sources**: Real-world retail transaction database (Online Retail II dataset, 2009–2011).
* **Scale**: **1,067,371 raw transaction records** covering **5,305 SKUs** and **5,942 customers**.
* **Star Schema Structure**:
  * `sales_daily.csv` (532,839 transaction summary rows)
  * `sku_master.csv` (4,917 SKU catalog records)
  * `calendar.csv` (739 daily time dimension records)
  * `inventory_snapshots.csv` (200 active stock position snapshots)

---

### Slide 4: Data Cleaning & Preprocessing
* **Anomaly Removal**: Filtered out negative quantities (returns/cancellations) and zero-priced transactions.
* **Deduplication & Formatting**: Handled missing customer IDs, standardized SKU identifiers, formatted dates.
* **Category Auto-Tagging**: Derived product categories (`Kitchen & Dining`, `Storage & Accessories`, `Home Decor & Lighting`, `Seasonal & Gifts`) from unstructured description text.

---

### Slide 5: EDA Insights & Key Patterns
* **Seasonality**: Demand surges heavily during Q4 (Black Friday through Christmas clearance).
* **80/20 Pareto Rule**: Top 15% of SKUs generate 68% of total unit sales volume.
* **Dead Stock Identification**: 18% of SKUs registered zero sales over the last 60 consecutive days.

---

### Slide 6: Forecast Modeling Approach
* **Granularity**: Weekly SKU-level forecast over a 6-week horizon.
* **Engineered Features**:
  * Lags ($t-1w, t-2w, t-4w, t-52w$)
  * Rolling Statistics (4-week & 8-week moving averages and standard deviations)
  * Calendar & Seasonality (Week of year, month, season, holiday indicators)
  * Pricing & Promotional Discounts
* **Algorithms Evaluated**: Seasonal-Naive Baseline, Random Forest Regressor, XGBoost Regressor, LightGBM Regressor.

---

### Slide 7: Model Backtest & Performance

Evaluation performed using **Rolling-Origin Cross-Validation** (4 time-series folds) to eliminate lookahead data leakage.

| Model Algorithm | WAPE Error Rate | Out-of-Sample Accuracy |
| :--- | :---: | :---: |
| **Seasonal-Naive Baseline** | **107.8%** | Benchmark |
| **Random Forest Regressor** | **75.5%** | +32.3% Improvement |
| **XGBoost Regressor** | **76.3%** | +31.5% Improvement |
| **LightGBM Regressor (Winner)** | **72.9%** | **+34.9% WAPE Reduction** |

---

### Slide 8: Inventory Risk Scoring Engine
Integrates forecasted demand over lead time with physical stock levels ($On\text{-}Hand + On\text{-}Order$):

* **2x2 Decisioning Matrix**:
  * 🔴 **Reorder Now**: Stockout Risk > 25%, Overstock Risk ≤ 35% → *Action: Immediate PO placement.*
  * 🟣 **Markdown / Clear**: Overstock Risk > 35%, Stockout Risk ≤ 25% → *Action: Promote / discount.*
  * 🟠 **Watch / Volatile**: High Stockout & Overstock Risk → *Action: Manual review.*
  * 🟢 **Healthy**: Low Stockout & Overstock Risk → *Action: Optimal level.*
* **Financial Impact Quantified**:
  * **Sales at Risk**: ₹147,047
  * **Capital Locked**: ₹73,621

---

### Slide 9: Professional Streamlit Dashboard
7-Page Interactive Web Application ([`app/main.py`](file:///c:/Users/Codex_boy/Desktop/WAR/Zidio/app/main.py)):
1. 🏠 **Home Page**: System introduction & KPI summary.
2. 📊 **Sales Analytics**: Revenue trends & top movers.
3. 📈 **Forecast**: Interactive SKU demand forecaster & backtest metrics.
4. 📦 **Inventory Dashboard**: On-hand stock vs purchase orders.
5. ⚠️ **Risk Dashboard**: Interactive 2x2 decision grid & quadrant filtering.
6. 🔎 **Product Details**: SKU-level margin & risk profile.
7. 💼 **Executive Summary Dashboard**: Top 5 reorder & markdown action tables.

---

### Slide 10: Deployment & Business Recommendations
* **API Deployment**: FastAPI REST endpoint ([`service/api.py`](file:///c:/Users/Codex_boy/Desktop/WAR/Zidio/service/api.py)) serving real-time SKU predictions (`/forecast/{sku_id}`) and batch risk scoring (`/score-batch`).
* **Strategic Next Steps**:
  1. **Immediate Execution**: Place reorder requests for Top 5 Reorder Priority SKUs.
  2. **Clearance Campaign**: Launch targeted promotions on Top 5 Markdown Candidate SKUs to liberate working capital.
  3. **Monthly Refresh Cadence**: Re-run the automated pipeline (`python src/pipeline.py`) at the start of every month.
