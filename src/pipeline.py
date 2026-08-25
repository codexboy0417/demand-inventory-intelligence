"""
Data Pipeline Module for Project FORESIGHT
Handles data ingestion, cleaning, weekly aggregation, and feature engineering.
"""
import pandas as pd
import numpy as np
import os

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')

def generate_processed_tables():
    """Generates the 4 core Star Schema tables from raw data if missing."""
    raw_csv = os.path.join(RAW_DIR, 'online_retail_II_combined.csv')
    if not os.path.exists(raw_csv):
        raise FileNotFoundError(f"Raw dataset not found at {raw_csv}")
        
    df = pd.read_csv(raw_csv)
    df['date'] = pd.to_datetime(df['InvoiceDate']).dt.date
    df = df[df['Quantity'] > 0]
    df = df[df['Price'] > 0]
    df['revenue'] = df['Quantity'] * df['Price']
    df['sku_id'] = df['StockCode'].astype(str)

    # 1. sales_daily
    sales_daily = df.groupby(['date', 'sku_id']).agg(
        units_sold=('Quantity', 'sum'),
        revenue=('revenue', 'sum'),
        unit_price=('Price', 'mean')
    ).reset_index()
    sku_max_price = sales_daily.groupby('sku_id')['unit_price'].transform('max')
    sales_daily['promo_flag'] = (sales_daily['unit_price'] < 0.85 * sku_max_price).astype(int)

    # 2. sku_master
    sku_info = df.groupby('sku_id').agg(
        description=('Description', 'first'),
        launch_date=('date', 'min'),
        list_price=('Price', 'max')
    ).reset_index()

    def get_category(desc):
        if not isinstance(desc, str):
            return 'General Furnishings'
        desc = desc.upper()
        if any(k in desc for k in ['MUG', 'CUP', 'PLATE', 'GLASS', 'BOWL', 'BOTTLE', 'TEA', 'COFFEE']):
            return 'Kitchen & Dining'
        elif any(k in desc for k in ['BAG', 'BOX', 'HOLDER', 'CASE', 'STORAGE', 'BASKET']):
            return 'Storage & Accessories'
        elif any(k in desc for k in ['LIGHT', 'CANDLE', 'LANTERN', 'CLOCK', 'MIRROR', 'LAMP']):
            return 'Home Decor & Lighting'
        elif any(k in desc for k in ['CHRISTMAS', 'PARTY', 'HEART', 'STAR', 'VINTAGE', 'SIGN']):
            return 'Seasonal & Gifts'
        else:
            return 'General Furnishings'

    sku_info['category'] = sku_info['description'].apply(get_category)
    sku_info['subcategory'] = sku_info['category'] + ' Sub'
    sku_info['unit_cost'] = (sku_info['list_price'] * 0.6).round(2)
    sku_master = sku_info[['sku_id', 'category', 'subcategory', 'launch_date', 'unit_cost', 'list_price']]

    # 3. calendar
    min_date = sales_daily['date'].min()
    max_date = sales_daily['date'].max()
    date_range = pd.date_range(min_date, max_date)
    calendar = pd.DataFrame({'date': date_range.date})
    calendar_dt = pd.to_datetime(calendar['date'])
    calendar['week'] = calendar_dt.dt.isocalendar().week
    calendar['month'] = calendar_dt.dt.month

    def get_season(month):
        if month in [12, 1, 2]: return 'Winter'
        elif month in [3, 4, 5]: return 'Spring'
        elif month in [6, 7, 8]: return 'Summer'
        else: return 'Autumn'

    calendar['season'] = calendar['month'].apply(get_season)
    calendar['is_holiday'] = calendar_dt.dt.dayofweek.isin([5, 6]).astype(int)
    calendar['promo_event'] = np.where(calendar['month'] == 11, 'Black Friday', np.where(calendar['month'] == 12, 'Christmas Clearance', 'None'))

    # 4. inventory_snapshots
    top_skus = sales_daily.groupby('sku_id')['units_sold'].sum().nlargest(200).index
    inventory_list = []
    np.random.seed(42)

    for sku in top_skus:
        weekly_avg = sales_daily[sales_daily['sku_id'] == sku]['units_sold'].tail(30).mean() * 7
        if np.isnan(weekly_avg) or weekly_avg == 0:
            weekly_avg = 10
        
        lead_time = int(np.random.choice([7, 14, 21]))
        reorder_point = int(weekly_avg * (lead_time / 7.0) * 1.2)
        stock_factor = np.random.choice([0.3, 0.7, 1.5, 3.0], p=[0.2, 0.3, 0.3, 0.2])
        on_hand = int(reorder_point * stock_factor)
        on_order = int(reorder_point * 0.5) if stock_factor < 1.0 else 0
        
        inventory_list.append({
            'date': max_date,
            'sku_id': sku,
            'on_hand_units': on_hand,
            'on_order_units': on_order,
            'lead_time_days': lead_time,
            'reorder_point': reorder_point
        })

    inventory_snapshots = pd.DataFrame(inventory_list)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    sales_daily.to_csv(os.path.join(PROCESSED_DIR, 'sales_daily.csv'), index=False)
    sku_master.to_csv(os.path.join(PROCESSED_DIR, 'sku_master.csv'), index=False)
    calendar.to_csv(os.path.join(PROCESSED_DIR, 'calendar.csv'), index=False)
    inventory_snapshots.to_csv(os.path.join(PROCESSED_DIR, 'inventory_snapshots.csv'), index=False)

def load_processed_data():
    """Loads the four core tables from data/processed/, auto-generating them if missing."""
    sales_path = os.path.join(PROCESSED_DIR, 'sales_daily.csv')
    sku_path = os.path.join(PROCESSED_DIR, 'sku_master.csv')
    cal_path = os.path.join(PROCESSED_DIR, 'calendar.csv')
    inv_path = os.path.join(PROCESSED_DIR, 'inventory_snapshots.csv')
    
    if not (os.path.exists(sales_path) and os.path.exists(sku_path) and os.path.exists(cal_path) and os.path.exists(inv_path)):
        print("Processed tables missing. Auto-generating from raw data...")
        generate_processed_tables()

    sales_daily = pd.read_csv(sales_path)
    sku_master = pd.read_csv(sku_path)
    calendar = pd.read_csv(cal_path)
    inventory_snapshots = pd.read_csv(inv_path)
    
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
