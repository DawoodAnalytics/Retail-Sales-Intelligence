import os
import sqlite3
import pandas as pd

# 1. SETUP PATHS
data_folder = "/home/dawood-raza/Desktop/New Folder/Retail_Sales_Intelligence/Data"
csv_path = os.path.join(data_folder, "clean_customer_shopping_data.csv")
db_path = os.path.join(data_folder, "retail_data.db")

print(f"🚀 Loading clean data from: {csv_path}")
df = pd.read_csv(csv_path)

# 2. CONNECT TO SQLITE DATABASE (Creates it automatically if it doesn't exist)
print(f"📦 Connecting to SQLite Database at: {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 3. CREATE NORMALIZED TABLES (Our Schema Blueprint)
print("🏗️ Creating normalized schema tables...")
cursor.executescript('''
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id TEXT PRIMARY KEY,
    gender TEXT,
    age INTEGER
);

CREATE TABLE IF NOT EXISTS dim_products (
    product_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE,
    price REAL
);

CREATE TABLE IF NOT EXISTS dim_malls (
    mall_id INTEGER PRIMARY KEY AUTOINCREMENT,
    mall_name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_method TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS fact_sales (
    invoice_no TEXT PRIMARY KEY,
    customer_id TEXT,
    product_category_id INTEGER,
    mall_id INTEGER,
    payment_id INTEGER,
    invoice_date TEXT,
    quantity INTEGER,
    total_revenue REAL,
    FOREIGN KEY(customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY(product_category_id) REFERENCES dim_products(product_category_id),
    FOREIGN KEY(mall_id) REFERENCES dim_malls(mall_id),
    FOREIGN KEY(payment_id) REFERENCES dim_payments(payment_id)
);
''')
conn.commit()

# 4. PERFORM NORMALIZATION & POPULATE TABLES
print("🧼 Normalizing and extracting dimension data...")

# A. Populate Customers (Keep only unique customer IDs)
df_cust = df[['customer_id', 'gender', 'age']].drop_duplicates(subset=['customer_id'])
df_cust.to_sql('dim_customers', conn, if_exists='append', index=False)

# B. Populate Products
unique_categories = df[['category', 'price']].drop_duplicates(subset=['category'])
for _, row in unique_categories.iterrows():
    cursor.execute("INSERT OR IGNORE INTO dim_products (category_name, price) VALUES (?, ?)", (row['category'], row['price']))

# C. Populate Malls
for mall in df['shopping_mall'].unique():
    cursor.execute("INSERT OR IGNORE INTO dim_malls (mall_name) VALUES (?)", (mall,))

# D. Populate Payments
for method in df['payment_method'].unique():
    cursor.execute("INSERT OR IGNORE INTO dim_payments (payment_method) VALUES (?)", (method,))

conn.commit()

# 5. MAP AND BUILD THE CENTRAL FACT TABLE
print("🎯 Mapping relationships to build the Central Fact Table...")

# Fetch the generated IDs back from our database to replace the raw text in our sales table
products_map = pd.read_sql("SELECT product_category_id, category_name FROM dim_products", conn).set_index('category_name')['product_category_id'].to_dict()
malls_map = pd.read_sql("SELECT mall_id, mall_name FROM dim_malls", conn).set_index('mall_name')['mall_id'].to_dict()
payments_map = pd.read_sql("SELECT payment_id, payment_method FROM dim_payments", conn).set_index('payment_method')['payment_id'].to_dict()

# Swap the raw text columns with our new normalized IDs
df['product_category_id'] = df['category'].map(products_map)
df['mall_id'] = df['shopping_mall'].map(malls_map)
df['payment_id'] = df['payment_method'].map(payments_map)

# Select only the columns that belong in our normalized central Fact Table
fact_df = df[['invoice_no', 'customer_id', 'product_category_id', 'mall_id', 'payment_id', 'invoice_date', 'quantity', 'total_revenue']]
fact_df.to_sql('fact_sales', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print("\n🎉 SUCCESS! Your flat CSV data has been perfectly normalized into 5 SQL tables!")
print("🏁 Your local database file 'retail_data.db' is ready in your Data folder.")
