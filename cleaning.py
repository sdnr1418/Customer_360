import pandas as pd
from preprocessing import get_master_df_via_sql, engine

def perform_cleaning(df):
    """
    Professional Cleaning logic for the Customer 360 project.
    """
    print("\n--- Starting Data Cleaning ---")
    initial_shape = df.shape

    # 1. Handle Missing Category Names
    null_categories = df['category'].isnull().sum()
    df['category'] = df['category'].fillna('others')
    print(f"-> Filled {null_categories} missing categories with 'others'.")

    # 2. Convert Timestamps to Datetime Objects
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    print("-> Successfully converted timestamps to datetime.")

    # 3. Remove Duplicate Rows
    before_dupes = len(df)
    df = df.drop_duplicates()
    after_dupes = len(df)
    print(f"-> Removed {before_dupes - after_dupes} duplicate rows.")

    # 4. Filter Out Extreme Outliers (Price)
    # E-commerce data often has "trash" entries (e.g., price = 0 or test items).
    # We remove items with price <= 0.
    invalid_prices = (df['price'] <= 0).sum()
    df = df[df['price'] > 0]
    print(f"-> Removed {invalid_prices} rows with invalid (<=0) pricing.")

    print(f"Cleaning complete. Shape changed from {initial_shape} to {df.shape}.")
    return df

def save_clean_data(df):
    """
    Saves the cleaned data back to Postgres and locally as a CSV.
    """
    # Save back to a new table in Postgres for the team
    print("Saving cleaned data to PostgreSQL table 'master_cleaned'...")
    df.to_sql('master_cleaned', engine, if_exists='replace', index=False)
    
    # Save a local CSV for quick reference (ignored by git)
    df.to_csv('data/master_cleaned.csv', index=False)
    print("Saved local copy to data/master_cleaned.csv")

if __name__ == "__main__":
    # 1. Extract data using the function from your preprocessing script
    raw_df = get_master_df_via_sql()
    
    # 2. Transform (Clean) the data
    cleaned_df = perform_cleaning(raw_df)
    
    # 3. Load the clean data back to the DB
    save_clean_data(cleaned_df)