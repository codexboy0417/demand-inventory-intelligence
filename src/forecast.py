"""
Multi-Model Forecasting Engine for Project FORESIGHT
Compares Baseline (Seasonal-Naive), Random Forest, XGBoost, and LightGBM
using Rolling-Origin Cross-Validation.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

try:
    from lightgbm import LGBMRegressor
except ImportError:
    LGBMRegressor = None

try:
    from xgboost import XGBRegressor
except ImportError:
    XGBRegressor = None

FEATURE_COLS = [
    'week', 'month', 'unit_cost', 'list_price', 'avg_price',
    'promo_days', 'lag_1w', 'lag_2w', 'lag_4w', 'lag_52w',
    'rolling_mean_4w', 'rolling_std_4w', 'rolling_mean_8w',
    'price_discount_ratio'
]

def compute_wape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    total_actual = np.sum(y_true)
    return np.sum(np.abs(y_true - y_pred)) / total_actual if total_actual > 0 else 0.0

def compute_mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true > 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) if np.any(mask) else 0.0

def compute_bias(y_true, y_pred):
    return float(np.mean(np.array(y_pred) - np.array(y_true)))

class SeasonalNaiveBaseline:
    def predict(self, df):
        preds = []
        for idx, row in df.iterrows():
            if not np.isnan(row.get('lag_52w', np.nan)) and row.get('lag_52w', 0) > 0:
                preds.append(row['lag_52w'])
            elif not np.isnan(row.get('rolling_mean_4w', np.nan)):
                preds.append(row['rolling_mean_4w'])
            elif not np.isnan(row.get('lag_1w', np.nan)):
                preds.append(row['lag_1w'])
            else:
                preds.append(0.0)
        return np.array(preds)

class RandomForestForecaster:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
        
    def fit(self, df):
        clean_df = df.dropna(subset=['units_sold'] + FEATURE_COLS)
        self.model.fit(clean_df[FEATURE_COLS], clean_df['units_sold'])
        return self
        
    def predict(self, df):
        return np.maximum(0, self.model.predict(df[FEATURE_COLS].fillna(0)))

class XGBoostForecaster:
    def __init__(self):
        if XGBRegressor is not None:
            self.model = XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=6, random_state=42)
        else:
            self.model = RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42, n_jobs=-1)
        
    def fit(self, df):
        clean_df = df.dropna(subset=['units_sold'] + FEATURE_COLS)
        self.model.fit(clean_df[FEATURE_COLS], clean_df['units_sold'])
        return self
        
    def predict(self, df):
        return np.maximum(0, self.model.predict(df[FEATURE_COLS].fillna(0)))

class LightGBMForecaster:
    def __init__(self):
        if LGBMRegressor is not None:
            self.model = LGBMRegressor(n_estimators=150, learning_rate=0.05, num_leaves=31, random_state=42, verbose=-1)
        else:
            self.model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
        
    def fit(self, df):
        clean_df = df.dropna(subset=['units_sold'] + FEATURE_COLS)
        self.model.fit(clean_df[FEATURE_COLS], clean_df['units_sold'])
        return self
        
    def predict(self, df):
        return np.maximum(0, self.model.predict(df[FEATURE_COLS].fillna(0)))

def compare_all_models_rolling_cv(df, n_splits=4, horizon_weeks=4):
    dates = sorted(df['start_date'].unique())
    split_indices = np.linspace(len(dates) - (n_splits * horizon_weeks), len(dates) - horizon_weeks, n_splits, dtype=int)
    
    results = []
    
    for i, cutoff_idx in enumerate(split_indices):
        cutoff_date = dates[cutoff_idx]
        eval_dates = dates[cutoff_idx : cutoff_idx + horizon_weeks]
        
        train_df = df[df['start_date'] < cutoff_date]
        test_df = df[df['start_date'].isin(eval_dates)]
        
        if len(train_df) == 0 or len(test_df) == 0:
            continue
            
        y_true = test_df['units_sold'].values
        
        # Fit & Predict Models
        base = SeasonalNaiveBaseline().predict(test_df)
        rf = RandomForestForecaster().fit(train_df).predict(test_df)
        xgb = XGBoostForecaster().fit(train_df).predict(test_df)
        lgb = LightGBMForecaster().fit(train_df).predict(test_df)
        
        results.append({
            'fold': i + 1,
            'cutoff_date': str(cutoff_date),
            'baseline_wape': compute_wape(y_true, base),
            'rf_wape': compute_wape(y_true, rf),
            'xgb_wape': compute_wape(y_true, xgb),
            'lgb_wape': compute_wape(y_true, lgb),
        })
        
    return pd.DataFrame(results)

if __name__ == '__main__':
    from pipeline import load_processed_data, build_weekly_dataset, engineer_features
    sales_daily, sku_master, calendar, inventory_snapshots = load_processed_data()
    weekly = build_weekly_dataset(sales_daily, sku_master, calendar)
    df_feat = engineer_features(weekly)
    
    res = compare_all_models_rolling_cv(df_feat)
    print("--- Multi-Model Rolling Backtest Comparison ---")
    print(res)
    print("\nMean WAPE Results:")
    print("Baseline (Seasonal Naive):", res['baseline_wape'].mean())
    print("Random Forest           :", res['rf_wape'].mean())
    print("XGBoost                 :", res['xgb_wape'].mean())
    print("LightGBM                :", res['lgb_wape'].mean())
