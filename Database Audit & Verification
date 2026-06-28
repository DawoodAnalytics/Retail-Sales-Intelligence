import os
import sqlite3
import pandas as pd

# 1. SETUP DB PATH
data_folder = "/home/dawood-raza/Desktop/New Folder/Retail_Sales_Intelligence/Data"
db_path = os.path.join(data_folder, "retail_data.db")

if not os.path.exists(db_path):
    print(f"❌ Error: Database file not found at {db_path}")
    exit()

# 2. CONNECT TO DATABASE
conn = sqlite3.connect(db_path)

# 3. LIST ALL TABLES AND ROW COUNTS
print("====================================================")
print("             DATABASE TABLE AUDIT                    ")
print("====================================================")

tables = ['dim_customers', 'dim_products', 'dim_malls', 'dim_payments', 'fact_sales']

for table in tables:
    try:
        # Get row count
        count = pd.read_sql(f"SELECT COUNT(*) as total_rows FROM {table}", conn).iloc[0]['total_rows']
        print(f"📊 Table: {table:<16} | Rows: {count:,}")
    except Exception as e:
        print(f"❌ Could not read table {table}: {e}")

print("\n====================================================")
print("             PREVIEWING THE CENTRAL FACT TABLE       ")
print("====================================================")
# Fetch a 5-row preview of our central fact table to see the normalized IDs
fact_preview = pd.read_sql("SELECT * FROM fact_sales LIMIT 5", conn)
print(fact_preview)

conn.close()
