"""
Phase 7: Inventory Risk Scoring Engine & Decision Matrix
Integrates Machine Learning demand forecasts with current warehouse inventory positions
to evaluate Stockout Risk, Overstock Risk, and ₹ Financial Impact.
"""
import os
import sys
import numpy as np
import pandas as pd

# Add parent directory for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline import load_processed_data, build_weekly_dataset, engineer_features
from src.forecast import LightGBMForecaster, XGBoostForecaster, RandomForestForecaster, FEATURE_COLS

def train_forecasting_model(df_features, model_type='lightgbm'):
    """
    Trains the selected Machine Learning model on historical weekly features.
    
    Parameters:
    -----------
    df_features : pd.DataFrame
        Dataset containing engineered lag, rolling, and calendar features.
    model_type : str
        'lightgbm', 'xgboost', or 'random_forest'
        
    Returns:
    --------
    trained_model : fitted model object
    """
    clean_df = df_features.dropna(subset=['units_sold'] + FEATURE_COLS)
    
    if model_type == 'lightgbm':
        model = LightGBMForecaster().fit(clean_df)
    elif model_type == 'xgboost':
        model = XGBoostForecaster().fit(clean_df)
    elif model_type == 'random_forest':
        model = RandomForestForecaster().fit(clean_df)
    else:
        raise ValueError(f"Unknown model_type: {model_type}. Choose 'lightgbm', 'xgboost', or 'random_forest'.")
        
    return model

def generate_forward_sku_forecasts(trained_model, df_features, horizon_weeks=6):
    """
    Generates multi-week forward demand forecasts per SKU using the trained model.
    """
    # Extract the latest feature row for each active SKU
    latest_features = df_features.sort_values('start_date').groupby('sku_id').last().reset_index()
    
    # Predict weekly demand
    latest_features['predicted_weekly_demand'] = trained_model.predict(latest_features)
    
    # Aggregate forecast table
    forecast_df = latest_features[['sku_id', 'predicted_weekly_demand']].rename(
        columns={'predicted_weekly_demand': 'weekly_forecast'}
    )
    return forecast_df

def score_inventory_risks(
    inventory_snapshots,
    forecast_df,
    sku_master,
    stockout_threshold=0.25,
    overstock_threshold=0.35,
    forward_weeks=6
):
    """
    Evaluates inventory risk by comparing forward ML demand forecasts with stock positions.
    
    Risk Conditions & Logic:
    ------------------------
    1. Lead Time Demand (D_lt) = weekly_forecast * (lead_time_days / 7.0)
    2. Available Stock (S_avail) = on_hand_units + on_order_units
    3. Stockout Gap = max(0, D_lt - S_avail)
    4. Stockout Risk Score (0.0 to 1.0) = clip( (D_lt - S_avail) / D_lt, 0.0, 1.0 )
    5. Forward Window Demand (D_fwd) = weekly_forecast * forward_weeks
    6. Overstock Gap = max(0, on_hand_units - D_fwd)
    7. Overstock Risk Score (0.0 to 1.0) = clip( (on_hand_units - D_fwd) / on_hand_units, 0.0, 1.0 )
    
    2x2 Decision Matrix Quadrants:
    ------------------------------
    - 'Reorder Now'     : Stockout Risk > stockout_threshold AND Overstock Risk <= overstock_threshold
    - 'Markdown / Clear': Overstock Risk > overstock_threshold AND Stockout Risk <= stockout_threshold
    - 'Watch / Volatile': Stockout Risk > stockout_threshold AND Overstock Risk > overstock_threshold
    - 'Healthy'         : Stockout Risk <= stockout_threshold AND Overstock Risk <= overstock_threshold
    
    Financial Impact (INR):
    -----------------------
    - Rupee Sales at Risk = Stockout Gap * list_price
    - Rupee Capital Locked = Overstock Gap * unit_cost
    - Rupee Total at Stake = Sales at Risk + Capital Locked
    """
    # Merge inventory with model forecast and SKU product dimensions
    df = inventory_snapshots.merge(forecast_df, on='sku_id', how='inner')
    df = df.merge(sku_master[['sku_id', 'list_price', 'unit_cost', 'category']], on='sku_id', how='left')
    
    # 1. Demand computations
    df['lead_time_weeks'] = df['lead_time_days'] / 7.0
    df['forecast_lead_time_demand'] = df['weekly_forecast'] * df['lead_time_weeks']
    df['forecast_horizon_demand'] = df['weekly_forecast'] * float(forward_weeks)
    
    # 2. Inventory positions
    df['total_available_stock'] = df['on_hand_units'] + df['on_order_units']
    
    # 3. Stockout Risk Evaluation
    df['stockout_gap'] = np.maximum(0, df['forecast_lead_time_demand'] - df['total_available_stock'])
    df['stockout_risk'] = np.clip(
        (df['forecast_lead_time_demand'] - df['total_available_stock']) / (df['forecast_lead_time_demand'] + 1e-5),
        0.0, 1.0
    )
    
    # 4. Overstock Risk Evaluation
    df['overstock_gap'] = np.maximum(0, df['on_hand_units'] - df['forecast_horizon_demand'])
    df['overstock_risk'] = np.clip(
        (df['on_hand_units'] - df['forecast_horizon_demand']) / (df['on_hand_units'] + 1e-5),
        0.0, 1.0
    )
    
    # 5. 2x2 Decision Quadrant Assignment
    def assign_quadrant(row):
        is_stockout = row['stockout_risk'] > stockout_threshold
        is_overstock = row['overstock_risk'] > overstock_threshold
        
        if is_stockout and not is_overstock:
            return 'Reorder Now'
        elif is_overstock and not is_stockout:
            return 'Markdown / Clear'
        elif is_stockout and is_overstock:
            return 'Watch / Volatile'
        else:
            return 'Healthy'
            
    df['quadrant'] = df.apply(assign_quadrant, axis=1)
    
    # 6. Actionable recommendations
    action_map = {
        'Reorder Now': 'Raise replenishment order before stock runs out.',
        'Markdown / Clear': 'Promote or discount to free up locked capital.',
        'Watch / Volatile': 'Investigate erratic demand; review manually.',
        'Healthy': 'No action needed; inventory level optimal.'
    }
    df['recommended_action'] = df['quadrant'].map(action_map)
    
    # 7. Financial Quantification in Rupees (INR)
    df['rupee_sales_at_risk'] = df['stockout_gap'] * df['list_price']
    df['rupee_capital_locked'] = df['overstock_gap'] * df['unit_cost']
    df['rupee_total_at_stake'] = df['rupee_sales_at_risk'] + df['rupee_capital_locked']
    
    return df

def run_pipeline_and_train(model_choice='lightgbm', output_csv='reports/inventory_risk_decision_matrix.csv'):
    """
    Main orchestration function to train the ML model and compute the risk decisioning matrix.
    """
    print(f"=== Running Phase 7: Training {model_choice.upper()} Forecaster & Risk Engine ===")
    
    # 1. Load data
    sales_daily, sku_master, calendar, inventory_snapshots = load_processed_data()
    print(f"Loaded {len(sales_daily):,} sales records and {len(inventory_snapshots)} inventory records.")
    
    # 2. Build weekly feature dataset
    weekly = build_weekly_dataset(sales_daily, sku_master, calendar)
    df_features = engineer_features(weekly)
    print(f"Engineered feature matrix: {df_features.shape[0]:,} rows x {df_features.shape[1]} columns.")
    
    # 3. Train ML Model
    print(f"Training {model_choice} model on historical features...")
    model = train_forecasting_model(df_features, model_type=model_choice)
    print("Model training complete.")
    
    # 4. Generate forward SKU demand forecasts
    forecast_df = generate_forward_sku_forecasts(model, df_features, horizon_weeks=6)
    
    # 5. Apply inventory risk conditions & decision matrix
    risk_df = score_inventory_risks(inventory_snapshots, forecast_df, sku_master)
    
    # 6. Print summary
    print("\n--- Inventory Risk Decisioning Summary ---")
    print(risk_df['quadrant'].value_counts())
    print(f"\nTotal Revenue at Risk from Stockouts : INR {risk_df['rupee_sales_at_risk'].sum():,.2f}")
    print(f"Total Working Capital Locked in Stock  : INR {risk_df['rupee_capital_locked'].sum():,.2f}")
    print(f"Total Financial Value at Stake         : INR {risk_df['rupee_total_at_stake'].sum():,.2f}")
    
    # 7. Save report
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    risk_df.to_csv(output_csv, index=False)
    print(f"\nSuccessfully saved full decision matrix report to: {output_csv}")
    
    return risk_df

if __name__ == '__main__':
    # Default execution: prompt model or run lightgbm
    model_name = sys.argv[1] if len(sys.argv) > 1 else 'lightgbm'
    run_pipeline_and_train(model_choice=model_name)
