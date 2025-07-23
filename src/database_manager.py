import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="ecommerce_data.db"):
        self.db_path = db_path
        
    def execute_query(self, query):
        """Execute a SQL query and return the results."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            conn.close()
            return {"success": True, "data": results, "columns": column_names}
        except sqlite3.Error as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    def get_table_info(self):
        """Get information about all tables in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            table_info = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                table_info[table_name] = columns
            
            conn.close()
            return {"success": True, "tables": table_info}
        except sqlite3.Error as e:
            return {"success": False, "error": str(e)}
    
    def validate_query(self, query):
        """Basic validation to prevent dangerous SQL operations."""
        dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE"]
        query_upper = query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False
        return True

if __name__ == "__main__":
    # Test the database manager
    db_manager = DatabaseManager()
    
    # Test getting table info
    table_info = db_manager.get_table_info()
    if table_info["success"]:
        print("Database tables:")
        for table_name, columns in table_info["tables"].items():
            print(f"  {table_name}: {[col[1] for col in columns]}")
    else:
        print(f"Error getting table info: {table_info['error']}")
    
    # Test a simple query
    test_query = "SELECT COUNT(*) FROM total_sales_metrics;"
    result = db_manager.execute_query(test_query)
    if result["success"]:
        print(f"Total sales records: {result['data'][0][0]}")
    else:
        print(f"Error executing query: {result['error']}")

