# Project FORESIGHT — Data Quality & EDA Insight Memo
**Client**: NorthBay Living  
**Prepared by**: Data Science & Analytics Team  
**Scope**: 2-Year Transactional & Inventory Data Analysis (2009–2011)

---

## 1. Executive Summary & Context
This memo presents the data quality assessment and exploratory data analysis (EDA) conducted on NorthBay Living's retail operations data. The objective is to identify underlying demand drivers, catalog patterns, seasonal dynamics, and inventory risks to inform the demand forecasting and inventory risk scoring engine.

---

## 2. Data Quality Audit & Cleaning Decisions

### 2.1 Raw Data Profiling
* **Total Transactions Processed**: 1,067,371 records across 2 full years (01/12/2009 to 09/12/2011).
* **Catalog Size**: 5,305 unique SKUs (StockCodes).
* **Customer Base**: 5,942 unique registered customer accounts.

### 2.2 Anomalies Identified & Coded Remediations
1. **Cancelled / Returned Orders (Negative Quantities)**:
   * *Finding*: ~2% of transactions had negative quantity values corresponding to cancellation invoices (Invoice prefix 'C').
   * *Handling*: Filtered out records with `Quantity <= 0` for demand forecasting to represent pure customer buying demand.
2. **Zero and Negative Prices (Adjustments & Bad Debts)**:
   * *Finding*: Test entries and accounting write-offs had `Price <= 0`.
   * *Handling*: Excluded all `Price <= 0` transactions.
3. **Missing Customer Identifiers**:
   * *Finding*: Approximately 22% of guest checkout transactions lacked a `Customer ID`.
   * *Handling*: Retained for SKU demand volume and revenue aggregation while noting unsegmented guest demand.
4. **Missing or Inconsistent Category Taxonomies**:
   * *Finding*: Raw extracts contained unstructured `Description` text without standardized hierarchy.
   * *Handling*: Built an automated text categorization parser mapping items into 5 business categories (`Kitchen & Dining`, `Storage & Accessories`, `Home Decor & Lighting`, `Seasonal & Gifts`, `General Furnishings`).

---

## 3. Key Demand Patterns & Business Insights

### Insight 1: Heavy Q4 Seasonality Surge
* Monthly sales demonstrate marked seasonality, peaking heavily in **October, November, and December** (Q4).
* The Q4 volume represents over **38% of annual revenue**, driven by Holiday gifting and Black Friday/Christmas shopping.
* *Actionable Impact*: Time-series models must capture annual 52-week seasonal lags and holiday indicators.

### Insight 2: The 80/20 Pareto Volume Distribution
* Top **15% of active SKUs account for 68% of total unit sales volume**.
* A small core catalog drives the majority of operational throughput, making stockouts in top movers disproportionately damaging to overall business revenue.
* *Actionable Impact*: Fast-movers require tighter safety stock buffers and prioritized replenishment triggers.

### Insight 3: Long Tail & Dead Stock Vulnerability
* Approximately **18% of SKUs exhibited zero sales over consecutive 60-day windows**.
* Holding substantial stock on these slow-movers traps valuable working capital that depreciates over time.
* *Actionable Impact*: Automated overstock identification flags these items for promotional clearance and markdown discounting.

---

## 4. Star Schema Architecture Summary
The cleaned data has been structured into a standard Star Schema:
* `sales_daily.csv`: Daily sales fact table (532,839 records).
* `sku_master.csv`: SKU dimension with pricing, costs, and categories (4,917 SKUs).
* `calendar.csv`: Date dimension with seasonal and promotional attributes (739 days).
* `inventory_snapshots.csv`: Stock snapshot tracking on-hand, on-order, lead time, and reorder levels (200 core SKUs).
