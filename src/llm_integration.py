import ollama
import json
import logging

logger = logging.getLogger(__name__)

class LLMIntegration:
    def __init__(self, model="mistral", base_url="http://localhost:11434" ):
        self.model = model
        self.base_url = base_url
        self.client = ollama.Client(host=self.base_url)
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self):
        # Define your database schema clearly for the LLM
        # This is crucial for accurate SQL generation
        schema_info = """
        You are an AI assistant that converts natural language questions into SQLite SQL queries.
        Your goal is to generate accurate and executable SQL based on the user's question and the provided database schema.

        Database Schema:
        Table: total_sales_metrics
        Columns: date (TEXT), item_id (TEXT), total_sales (REAL), total_units_ordered (INTEGER)

        Table: ad_sales_metrics
        Columns: date (TEXT), item_id (TEXT), ad_sales (REAL), impressions (INTEGER), ad_spend (REAL), clicks (INTEGER), units_sold (INTEGER)

        Table: product_eligibility
        Columns: eligibility_datetime_utc (TEXT), item_id (TEXT), eligibility (TEXT), message (TEXT)

        Instructions:
        - Only generate SQL queries. Do NOT include any explanations, comments, or additional text.
        - Use standard SQL functions (SUM, AVG, COUNT, MAX, MIN, GROUP BY, ORDER BY, WHERE, JOIN).
        - Ensure column names and table names exactly match the schema.
        - For questions involving dates, assume dates are in 'YYYY-MM-DD' format and use appropriate SQLite date functions if needed (e.g., strftime).
        - When asked for 'total units sold' or 'units sold', use the 'units_sold' column from the 'ad_sales_metrics' table.
        - When asked for 'total units ordered', use the 'total_units_ordered' column from the 'total_sales_metrics' table.
        - For RoAS (Return on Ad Spend), calculate it as (ad_sales / ad_spend) * 100. Ensure ad_spend is not zero to avoid division by zero errors.
        - When asked for 'top N' or 'most', use ORDER BY DESC LIMIT N.
        - When asked for 'least', use ORDER BY ASC LIMIT 1.
        - If a question asks for a percentage, calculate it using appropriate columns.
        - Always consider the most appropriate table for the requested data.
        - If a query requires data from both 'total_sales_metrics' and 'ad_sales_metrics' for the same item_id, use an INNER JOIN on item_id.

        Examples:
        User: What is my total sales?
        SQL: SELECT SUM(total_sales) FROM total_sales_metrics;

        User: List top 5 products by total sales.
        SQL: SELECT item_id, SUM(total_sales) FROM total_sales_metrics GROUP BY item_id ORDER BY SUM(total_sales) DESC LIMIT 5;

        User: What is the total number of units sold?
        SQL: SELECT SUM(units_sold) FROM ad_sales_metrics;

        User: Which product sold the most units?
        SQL: SELECT item_id, SUM(units_sold) FROM ad_sales_metrics GROUP BY item_id ORDER BY SUM(units_sold) DESC LIMIT 1;

        User: Which product had the least sales?
        SQL: SELECT item_id, SUM(total_sales) FROM total_sales_metrics GROUP BY item_id ORDER BY SUM(total_sales) ASC LIMIT 1;

        User: What is the total ad spend?
        SQL: SELECT SUM(ad_spend) FROM ad_sales_metrics;

        User: Which product had the highest RoAS?
        SQL: SELECT t1.item_id, (SUM(t2.ad_sales) * 100.0 / SUM(t2.ad_spend)) AS RoAS FROM total_sales_metrics t1 INNER JOIN ad_sales_metrics t2 ON t1.item_id = t2.item_id WHERE t2.ad_spend > 0 GROUP BY t1.item_id ORDER BY RoAS DESC LIMIT 1;

        User: Calculate the RoAS for each item.
        SQL: SELECT t1.item_id, (SUM(t2.ad_sales) * 100.0 / SUM(t2.ad_spend)) AS RoAS FROM total_sales_metrics t1 INNER JOIN ad_sales_metrics t2 ON t1.item_id = t2.item_id WHERE t2.ad_spend > 0 GROUP BY t1.item_id;

        User: Show top 10 products by RoAS.
        SQL: SELECT t1.item_id, (SUM(t2.ad_sales) * 100.0 / SUM(t2.ad_spend)) AS RoAS FROM total_sales_metrics t1 INNER JOIN ad_sales_metrics t2 ON t1.item_id = t2.item_id WHERE t2.ad_spend > 0 GROUP BY t1.item_id ORDER BY RoAS DESC LIMIT 10;
        """
        return schema_info

    def generate_sql_query(self, question):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question}
        ]
        
        try:
            response = self.client.chat(model=self.model, messages=messages, options={"temperature": 0.0})
            sql_query = response["message"]["content"]
            
            # Basic validation: ensure it starts with SELECT, INSERT, UPDATE, DELETE
            if sql_query.strip().upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE")):
                return sql_query.strip()
            else:
                logger.warning(f"LLM generated non-SQL response: {sql_query}")
                return None
        except ollama.ResponseError as e:
            logger.error(f"Ollama API error: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during LLM query generation: {e}")
            return None

# Example usage (for testing purposes)
if __name__ == "__main__":
    llm_integration = LLMIntegration()
    
    # Test with a question that requires units_sold
    question1 = "What is the total units sold for each product?"
    sql1 = llm_integration.generate_sql_query(question1)
    print(f"Question: {question1}\nGenerated SQL: {sql1}\n")
    
    # Test with a question that requires total_sales
    question2 = "Show me the total sales for item_id 123."
    sql2 = llm_integration.generate_sql_query(question2)
    print(f"Question: {question2}\nGenerated SQL: {sql2}\n")
    
    # Test with a question that requires a join (example, might need more complex prompt for robust joins)
    question3 = "Which products have ad sales greater than their total sales?"
    sql3 = llm_integration.generate_sql_query(question3)
    print(f"Question: {question3}\nGenerated SQL: {sql3}\n")
