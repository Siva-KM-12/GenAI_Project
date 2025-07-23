import pandas as pd
import sqlite3
import os

class DataIngestion:
    def __init__(self, db_name="ecommerce_data.db"):
        # Construct the database path relative to the script location
        # This places ecommerce_data.db in the root of e_commerce_ai_agent_final
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", db_name)
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        self.connect()
        try:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS total_sales_metrics (
                date TEXT,
                item_id TEXT,
                total_sales REAL,
                total_units_ordered INTEGER
            );""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS ad_sales_metrics (
                date TEXT,
                item_id TEXT,
                ad_sales REAL,
                impressions INTEGER,
                ad_spend REAL,
                clicks INTEGER,
                units_sold INTEGER
            );""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS product_eligibility (
                eligibility_datetime_utc TEXT,
                item_id TEXT,
                eligibility TEXT,
                message TEXT
            );""")
            self.conn.commit()
            print("Tables created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            self.close()

    def insert_data(self, df, table_name):
        self.connect()
        try:
            df.to_sql(table_name, self.conn, if_exists="append", index=False)
            self.conn.commit()
            print(f"Data inserted into {table_name} successfully.")
        except sqlite3.Error as e:
            print(f"Error inserting data into {table_name}: {e}")
        finally:
            self.close()

    def process_excel_data(self, file_path, table_name):
        try:
            df = pd.read_excel(file_path)
            self.insert_data(df, table_name)
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"Error processing Excel file {file_path}: {e}")

if __name__ == "__main__":
    data_ingestion = DataIngestion()
    data_ingestion.create_tables()

    # Define paths to your Excel files using the absolute path you provided
    base_dir = r"C:\Users\Siva K M\Downloads\e_commerce_ai_agent_final\upload"
    
    total_sales_file = os.path.join(base_dir, "Product-LevelTotalSalesandMetrics(mapped).xlsx")
    ad_sales_file = os.path.join(base_dir, "Product-LevelAdSalesandMetrics(mapped).xlsx")
    eligibility_file = os.path.join(base_dir, "Product-LevelEligibilityTable(mapped).xlsx")

    # Process each Excel file
    data_ingestion.process_excel_data(total_sales_file, "total_sales_metrics")
    data_ingestion.process_excel_data(ad_sales_file, "ad_sales_metrics")
    data_ingestion.process_excel_data(eligibility_file, "product_eligibility")

    print("Data ingestion complete.")
