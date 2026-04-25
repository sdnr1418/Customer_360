import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

# 1. Database Connection Configuration
password = os.getenv('DB_PASSWORD')
DB_URI = f'postgresql://postgres:{password}@localhost:5432/customer_360'
engine = create_engine(DB_URI)


def load_raw_data_to_postgres(data_folder='data/'):
    """
    EXTRACT: Reads local CSV files
    LOAD:   Pushes them into PostgreSQL tables
    """
    files = {
        'customers': 'olist_customers_dataset.csv',
        'orders': 'olist_orders_dataset.csv',
        'items': 'olist_order_items_dataset.csv',
        'products': 'olist_products_dataset.csv',
        'translation': 'product_category_name_translation.csv'
    }
    
    for table_name, file_name in files.items():
        path = os.path.join(data_folder, file_name)
        print(f"Loading {file_name} into PostgreSQL table '{table_name}'...")
        df = pd.read_csv(path)
        df.to_sql(table_name, engine, if_exists='replace', index=False)

def get_master_df_via_sql():
    """
    TRANSFORM: Uses a SQL JOIN to create the 'Customer 360' view
    This moves the computational heavy lifting to the database.
    """
    query = """
    SELECT 
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        i.product_id,
        i.price,
        t.product_category_name_english AS category
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN items i ON o.order_id = i.order_id
    JOIN products p ON i.product_id = p.product_id
    LEFT JOIN translation t ON p.product_category_name = t.product_category_name
    WHERE o.order_status = 'delivered';
    """
    print("Executing SQL Join in PostgreSQL...")
    return pd.read_sql(query, engine)

if __name__ == "__main__":
    #Populate SQL Warehouse
    load_raw_data_to_postgres()
    
    # Extract the Denormalized Master Table
    master_df = get_master_df_via_sql()
    master_df.to_csv('data/master_df.csv', index=False)
    print("Saved local copy to data/master_df.csv")
    
    # Verification
    print("\n--- Preprocessing Complete ---")
    print(f"Master Table Shape: {master_df.shape}")
    print(master_df.head())
    print("\nData types:")
    print(master_df.info())