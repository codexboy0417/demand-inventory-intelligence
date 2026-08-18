"""
Risk Scoring & Decisioning Module for Project FORESIGHT
Evaluates stockout and overstock risk per SKU, calculates ₹ financial impact,
and maps products to decisioning matrix.
"""
import pandas as pd
import numpy as np

def score_inventory_risks(inventory_snapshots, forecast_df, sku_master):
    """
    Combines 6-week forecast demand with current inventory position to score risk.
    
    forecast_df must contain ['sku_id', 'weekly_forecast']
    """
    df = inventory_snapshots.merge(forecast_df, on='sku_id', how='inner')
    df = df.merge(sku_master[['sku_id', 'list_price', 'unit_cost', 'category']], on='sku_id', how='left')
    
    # 1. Demand over lead time (weeks)
    df['lead_time_weeks'] = df['lead_time_days'] / 7.0
    df['forecast_lead_time_demand'] = df['weekly_forecast'] * df['lead_time_weeks']
    df['forecast_6w_demand'] = df['weekly_forecast'] * 6.0
    
    # Total available inventory
    df['total_available_stock'] = df['on_hand_units'] + df['on_order_units']
    
    # 2. Risk Metrics & Scores (0.0 to 1.0)
    # Stockout risk: higher if available stock < lead time demand
    df['stockout_gap'] = df['forecast_lead_time_demand'] - df['total_available_stock']
    df['stockout_risk'] = np.clip(df['stockout_gap'] / (df['forecast_lead_time_demand'] + 1e-5), 0.0, 1.0)
    
    # Overstock risk: higher if on-hand > 6-week demand
    df['overstock_gap'] = df['on_hand_units'] - df['forecast_6w_demand']
    df['overstock_risk'] = np.clip(df['overstock_gap'] / (df['on_hand_units'] + 1e-5), 0.0, 1.0)
    
    # 3. Decisioning Quadrants
    # Thresholds: 0.3 for risk activation
    def assign_quadrant(row):
        is_stockout = row['stockout_risk'] > 0.25
        is_overstock = row['overstock_risk'] > 0.35
        
        if is_stockout and not is_overstock:
            return 'Reorder Now'
        elif is_overstock and not is_stockout:
            return 'Markdown / Clear'
        elif is_stockout and is_overstock:
            return 'Watch / Volatile'
        else:
            return 'Healthy'
            
    df['quadrant'] = df.apply(assign_quadrant, axis=1)
    
    # 4. Recommended Actions
    action_map = {
        'Reorder Now': 'Raise replenishment order before stock runs out.',
        'Markdown / Clear': 'Promote or discount to free up locked capital.',
        'Watch / Volatile': 'Investigate erratic demand; review manually.',
        'Healthy': 'No action needed; inventory level optimal.'
    }
    df['recommended_action'] = df['quadrant'].map(action_map)
    
    # 5. Financial Impact in Rupees (₹)
    df['rupee_sales_at_risk'] = np.maximum(0, df['stockout_gap']) * df['list_price']
    df['rupee_capital_locked'] = np.maximum(0, df['overstock_gap']) * df['unit_cost']
    df['rupee_total_at_stake'] = df['rupee_sales_at_risk'] + df['rupee_capital_locked']
    
    return df

if __name__ == '__main__':
    from pipeline import load_processed_data
    sales_daily, sku_master, calendar, inventory_snapshots = load_processed_data()
    
    # Create dummy 6-week forecast
    recent_sales = sales_daily.groupby('sku_id')['units_sold'].tail(30).groupby(sales_daily['sku_id']).mean() * 7
    forecast_df = pd.DataFrame({'sku_id': recent_sales.index, 'weekly_forecast': recent_sales.values})
    
    risk_df = score_inventory_risks(inventory_snapshots, forecast_df, sku_master)
    print("Quadrant Distribution:")
    print(risk_df['quadrant'].value_counts())
    print("\nTotal Sales at Risk (INR):", risk_df['rupee_sales_at_risk'].sum())
    print("Total Capital Locked (INR):", risk_df['rupee_capital_locked'].sum())
