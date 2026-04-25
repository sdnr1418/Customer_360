import pandas as pd
from preprocessing import get_master_df_via_sql, engine

def perform_cleaning(df):
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
    print("Saving cleaned data to PostgreSQL table 'master_cleaned'...")
    df.to_sql('master_cleaned', engine, if_exists='replace', index=False)
    
    df.to_csv('data/master_cleaned.csv', index=False)
    print("Saved local copy to data/master_cleaned.csv")

if __name__ == "__main__":
    raw_df = get_master_df_via_sql()
    cleaned_df = perform_cleaning(raw_df)
    save_clean_data(cleaned_df)