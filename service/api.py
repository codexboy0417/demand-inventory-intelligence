"""
Project FORESIGHT — FastAPI Scoring Endpoint
Provides REST API endpoints for batch and single-SKU forecasting and inventory risk scoring.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline import load_processed_data, build_weekly_dataset
from src.risk import score_inventory_risks

app = FastAPI(
    title="Project FORESIGHT Scoring Service",
    description="Demand forecasting & inventory risk decisioning API for NorthBay Living.",
    version="1.0.0"
)

# Load data on startup
sales_daily, sku_master, calendar, inventory_snapshots = load_processed_data()
weekly = build_weekly_dataset(sales_daily, sku_master, calendar)
recent_sales = weekly.groupby('sku_id')['units_sold'].tail(12).groupby(weekly['sku_id']).mean()
forecast_df = pd.DataFrame({'sku_id': recent_sales.index, 'weekly_forecast': recent_sales.values})
risk_df = score_inventory_risks(inventory_snapshots, forecast_df, sku_master)

class SKUQueryRequest(BaseModel):
    sku_ids: List[str]

class InventoryItem(BaseModel):
    sku_id: str
    on_hand_units: int
    on_order_units: int
    lead_time_days: int

@app.get("/")
def read_root():
    return {
        "service": "Project FORESIGHT Scoring Service",
        "status": "online",
        "total_skus": len(risk_df),
        "version": "1.0.0"
    }

@app.get("/forecast/{sku_id}")
def get_sku_forecast(sku_id: str):
    sku_data = risk_df[risk_df['sku_id'] == sku_id]
    if len(sku_data) == 0:
        raise HTTPException(status_code=404, detail=f"SKU '{sku_id}' not found in inventory registry.")
    
    row = sku_data.iloc[0]
    return {
        "sku_id": row['sku_id'],
        "category": row['category'],
        "weekly_forecast_units": float(row['weekly_forecast']),
        "lead_time_days": int(row['lead_time_days']),
        "on_hand_units": int(row['on_hand_units']),
        "on_order_units": int(row['on_order_units']),
        "stockout_risk": float(row['stockout_risk']),
        "overstock_risk": float(row['overstock_risk']),
        "quadrant": row['quadrant'],
        "recommended_action": row['recommended_action'],
        "rupee_sales_at_risk": float(row['rupee_sales_at_risk']),
        "rupee_capital_locked": float(row['rupee_capital_locked'])
    }

@app.post("/score-batch")
def score_batch(query: SKUQueryRequest):
    requested = risk_df[risk_df['sku_id'].isin(query.sku_ids)]
    results = []
    for _, row in requested.iterrows():
        results.append({
            "sku_id": row['sku_id'],
            "category": row['category'],
            "weekly_forecast_units": float(row['weekly_forecast']),
            "quadrant": row['quadrant'],
            "recommended_action": row['recommended_action'],
            "rupee_sales_at_risk": float(row['rupee_sales_at_risk']),
            "rupee_capital_locked": float(row['rupee_capital_locked'])
        })
    return {"count": len(results), "skus": results}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
