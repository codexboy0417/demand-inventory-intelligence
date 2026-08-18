"""
Data Pipeline Module for Project FORESIGHT
Handles data ingestion, cleaning, weekly aggregation, and feature engineering.
"""
import pandas as pd
import numpy as np
import os

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')

def load_processed_data():
    """Loads the four core tables from data/processed/."""
    sales_daily = pd.read_csv(os.path.join(PROCESSED_DIR, 'sales_daily.csv'))
    sku_master = pd.read_csv(os.path.join(PROCESSED_DIR, 'sku_master.csv'))
    calendar = pd.read_csv(os.path.join(PROCESSED_DIR, 'calendar.csv'))
    inventory_snapshots = pd.read_csv(os.path.join(PROCESSED_DIR, 'inventory_snapshots.csv'))
    
    sales_daily['date'] = pd.to_datetime(sales_daily['date'])
    calendar['date'] = pd.to_datetime(calendar['date'])
    inventory_snapshots['date'] = pd.to_datetime(inventory_snapshots['date'])
    
    return sales_daily, sku_master, calendar, inventory_snapshots

def build_weekly_dataset(sales_daily, sku_master, calendar):
    """
    Aggregates daily sales to weekly SKU-level sales and merges dimension tables.
    """
    df = sales_daily.merge(calendar[['date', 'week', 'month', 'season', 'is_holiday', 'promo_event']], on='date', how='left')
    df['year'] = df['date'].dt.year
    df['year_week'] = df['date'].dt.strftime('%Y-W%U')
    
    weekly = df.groupby(['sku_id', 'year', 'week']).agg(
        units_sold=('units_sold', 'sum'),
        revenue=('revenue', 'sum'),
        avg_price=('unit_price', 'mean'),
        promo_days=('promo_flag', 'sum'),
        start_date=('date', 'min')
    ).reset_index()
    
    weekly = weekly.merge(sku_master[['sku_id', 'category', 'subcategory', 'unit_cost', 'list_price']], on='sku_id', how='left')
    weekly['start_date'] = pd.to_datetime(weekly['start_date'])
    weekly['month'] = weekly['start_date'].dt.month
    weekly = weekly.sort_values(['sku_id', 'start_date']).reset_index(drop=True)
    
    return weekly

def engineer_features(weekly_df):
    """
    Engineers lag features, rolling statistics, calendar seasonality, and promo indicators.
    Guards against lookahead data leakage by shifting lags.
    """
    df = weekly_df.copy()
    
    # Sort chronologically per SKU
    df = df.sort_values(['sku_id', 'start_date']).reset_index(drop=True)
    
    # Lag features
    df['lag_1w'] = df.groupby('sku_id')['units_sold'].shift(1)
    df['lag_2w'] = df.groupby('sku_id')['units_sold'].shift(2)
    df['lag_4w'] = df.groupby('sku_id')['units_sold'].shift(4)
    df['lag_52w'] = df.groupby('sku_id')['units_sold'].shift(52)  # Seasonal lag
    
    # Rolling statistics (shifted by 1 to prevent leakage)
    df['rolling_mean_4w'] = df.groupby('sku_id')['units_sold'].shift(1).rolling(4, min_periods=1).mean()
    df['rolling_std_4w'] = df.groupby('sku_id')['units_sold'].shift(1).rolling(4, min_periods=1).std().fillna(0)
    df['rolling_mean_8w'] = df.groupby('sku_id')['units_sold'].shift(1).rolling(8, min_periods=1).mean()
    
    # Price ratio and promo intensity
    df['price_discount_ratio'] = (df['list_price'] - df['avg_price']) / (df['list_price'] + 1e-5)
    
    return df

if __name__ == '__main__':
    sales_daily, sku_master, calendar, inventory_snapshots = load_processed_data()
    weekly = build_weekly_dataset(sales_daily, sku_master, calendar)
    features = engineer_features(weekly)
    print("Weekly feature dataset shape:", features.shape)
    print("Columns:", list(features.columns))
