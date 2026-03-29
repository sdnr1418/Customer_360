import pandas as pd
df = pd.read_csv('data/master_cleaned.csv')
print(f'Unique customers: {df["customer_unique_id"].nunique():,}')
