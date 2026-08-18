# Project FORESIGHT — Demand & Inventory Intelligence
### End-to-End Data Science System for NorthBay Living

---

## 📌 Executive Summary
**Project FORESIGHT** is an automated demand forecasting and inventory risk early-warning platform designed for **NorthBay Living** (a D2C home & lifestyle brand). By replacing legacy spreadsheet estimations with machine learning demand models and inventory risk decisioning, FORESIGHT helps prevent lost sales from stockouts and reduces tied-up capital from overstocking.

---

## 📊 Dataset & Schema
Built on real-world retail transactions from the **Online Retail II dataset** (UCI Machine Learning Repository / Kaggle):
* **Raw Dataset**: 1,067,371 transactions across 2009–2011 covering 5,305 SKUs.
* **Star Schema Architecture**:
  1. `sales_daily.csv`: Daily sales fact table (`date`, `sku_id`, `units_sold`, `revenue`, `unit_price`, `promo_flag`).
  2. `sku_master.csv`: SKU dimension (`sku_id`, `category`, `subcategory`, `launch_date`, `unit_cost`, `list_price`).
  3. `calendar.csv`: Calendar dimension (`date`, `week`, `month`, `season`, `is_holiday`, `promo_event`).
  4. `inventory_snapshots.csv`: Inventory status table (`date`, `sku_id`, `on_hand_units`, `on_order_units`, `lead_time_days`, `reorder_point`).

---

## 🚀 Model Performance & Backtesting
Evaluation performed using **Rolling-Origin Cross-Validation** (4 time-series folds, 4-week horizon) to guard against lookahead data leakage.

| Model | WAPE (Weighted Absolute Percentage Error) | Out-of-Sample Performance |
| :--- | :---: | :--- |
| **Seasonal-Naive Baseline** | **1.078 (107.8%)** | Simple lag benchmark |
| **LightGBM Forecast Model** | **0.729 (72.9%)** | **34.9% WAPE Reduction vs Baseline** |

---

## 🎯 Inventory Risk Decisioning Matrix
SKUs are dynamically categorized into a **2x2 Decisioning Grid** based on forecasted demand over lead time vs available inventory ($On\text{-}Hand + On\text{-}Order$):

1. **🔴 Reorder Now** (High Stockout, Low Overstock): Raise replenishment order before stock runs out.
2. **🟣 Markdown / Clear** (High Overstock, Low Stockout): Promote or discount to free up locked capital.
3. **🟠 Watch / Volatile** (High Stockout, High Overstock): Erratic demand pattern; requires manual review.
4. **🟢 Healthy** (Low Stockout, Low Overstock): Inventory position optimal.

---

## 🛠️ Repository & Execution Setup

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run Data Pipeline & Feature Engineering
```bash
python src/pipeline.py
```

### 3. Run Rolling-Origin Backtest
```bash
python src/forecast.py
```

### 4. Launch Interactive Streamlit Planning Dashboard
```bash
streamlit run app/main.py
```

### 5. Launch FastAPI Scoring REST API
```bash
python service/api.py
```
* Interactive API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`
