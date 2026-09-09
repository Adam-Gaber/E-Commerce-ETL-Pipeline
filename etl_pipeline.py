import pandas as pd
import sqlite3
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

RAW_DATA_DIR = './ECommerce_ETL/data/raw'
DB_NAME = 'ecommerce_warehouse.db'

def extract_data():
    logging.info("Starting Data Extraction Phase...")
    try:
        orders_df = pd.read_csv(os.path.join(RAW_DATA_DIR, 'olist_orders_dataset.csv'))
        items_df = pd.read_csv(os.path.join(RAW_DATA_DIR, 'olist_order_items_dataset.csv'))
        customers_df = pd.read_csv(os.path.join(RAW_DATA_DIR, 'olist_customers_dataset.csv'))
        
        logging.info(f"Orders extracted: {orders_df.shape[0]} rows")
        logging.info(f"Items extracted: {items_df.shape[0]} rows")
        logging.info(f"Customers extracted: {customers_df.shape[0]} rows")
        
        return orders_df, items_df, customers_df

    except FileNotFoundError as e:
        logging.error(f"Extraction failed: {e}")
        return None, None, None

def transform_data(orders, items, customers):
    logging.info("Starting Data Transformation Phase...")
    try:
        merged_df = pd.merge(orders, items, on='order_id', how='inner')
        final_df = pd.merge(merged_df, customers, on='customer_id', how='inner')
        
        final_df = final_df.dropna(subset=['price', 'freight_value'])
        final_df['total_order_value'] = final_df['price'] + final_df['freight_value']
        
        logging.info(f"Transformation complete. Final shape: {final_df.shape}")
        return final_df

    except Exception as e:
        logging.error(f"Transformation failed: {e}")
        return None

def load_data(df):
    logging.info("Starting Data Load Phase...")
    try:
        conn = sqlite3.connect(DB_NAME)
        df.to_sql('fact_sales', conn, if_exists='replace', index=False)
        conn.close()
        logging.info(f"Data successfully loaded into SQLite database: {DB_NAME}")
    except Exception as e:
        logging.error(f"Loading failed: {e}")

if __name__ == "__main__":
    orders, items, customers = extract_data()
    
    if orders is not None:
        cleaned_data = transform_data(orders, items, customers)
        if cleaned_data is not None:
            load_data(cleaned_data)