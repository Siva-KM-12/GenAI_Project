import re

class FallbackQuerySystem:
    """
    Fallback system for when LLM is not available or fails to generate queries.
    Provides predefined SQL queries for common questions.
    """
    
    def __init__(self):
        self.query_patterns = {
            # Total sales queries
            r'(?i).*total\s+sales.*': "SELECT SUM(total_sales) as total_sales FROM total_sales_metrics;",
            r'(?i).*my\s+sales.*': "SELECT SUM(total_sales) as total_sales FROM total_sales_metrics;",
            
            # RoAS (Return on Ad Spend) queries
            r'(?i).*roas.*': "SELECT (SUM(ad_sales) * 100.0 / SUM(ad_spend)) as roas_percentage FROM ad_sales_metrics WHERE ad_spend > 0;",
            r'(?i).*return\s+on\s+ad\s+spend.*': "SELECT (SUM(ad_sales) * 100.0 / SUM(ad_spend)) as roas_percentage FROM ad_sales_metrics WHERE ad_spend > 0;",
            
            # CPC (Cost Per Click) queries
            r'(?i).*highest\s+cpc.*': "SELECT item_id, (ad_spend / clicks) as cpc FROM ad_sales_metrics WHERE clicks > 0 ORDER BY cpc DESC LIMIT 1;",
            r'(?i).*cost\s+per\s+click.*': "SELECT item_id, (ad_spend / clicks) as cpc FROM ad_sales_metrics WHERE clicks > 0 ORDER BY cpc DESC LIMIT 10;",
            
            # Top products queries
            r'(?i).*top.*products.*sales.*': "SELECT item_id, SUM(total_sales) as total_sales FROM total_sales_metrics GROUP BY item_id ORDER BY total_sales DESC LIMIT 10;",
            r'(?i).*top.*products.*ad.*sales.*': "SELECT item_id, SUM(ad_sales) as ad_sales FROM ad_sales_metrics GROUP BY item_id ORDER BY ad_sales DESC LIMIT 10;",
            r'(?i).*best.*performing.*products.*': "SELECT item_id, SUM(total_sales) as total_sales FROM total_sales_metrics GROUP BY item_id ORDER BY total_sales DESC LIMIT 10;",
            
            # Impressions queries
            r'(?i).*average.*impressions.*': "SELECT AVG(impressions) as avg_impressions FROM ad_sales_metrics;",
            r'(?i).*total.*impressions.*': "SELECT SUM(impressions) as total_impressions FROM ad_sales_metrics;",
            r'(?i).*impressions.*product.*': "SELECT item_id, SUM(impressions) as total_impressions FROM ad_sales_metrics GROUP BY item_id ORDER BY total_impressions DESC LIMIT 10;",
            
            # Eligibility queries
            r'(?i).*not\s+eligible.*': "SELECT item_id, message FROM product_eligibility WHERE eligibility = 0;",
            r'(?i).*eligible.*products.*': "SELECT item_id FROM product_eligibility WHERE eligibility = 1;",
            r'(?i).*eligibility.*status.*': "SELECT eligibility, COUNT(*) as count FROM product_eligibility GROUP BY eligibility;",
            
            # Ad spend queries
            r'(?i).*total.*ad.*spend.*': "SELECT SUM(ad_spend) as total_ad_spend FROM ad_sales_metrics;",
            r'(?i).*average.*ad.*spend.*': "SELECT AVG(ad_spend) as avg_ad_spend FROM ad_sales_metrics;",
            r'(?i).*ad.*spend.*product.*': "SELECT item_id, SUM(ad_spend) as total_ad_spend FROM ad_sales_metrics GROUP BY item_id ORDER BY total_ad_spend DESC LIMIT 10;",
            
            # Click queries
            r'(?i).*total.*clicks.*': "SELECT SUM(clicks) as total_clicks FROM ad_sales_metrics;",
            r'(?i).*average.*clicks.*': "SELECT AVG(clicks) as avg_clicks FROM ad_sales_metrics;",
            r'(?i).*clicks.*product.*': "SELECT item_id, SUM(clicks) as total_clicks FROM ad_sales_metrics GROUP BY item_id ORDER BY total_clicks DESC LIMIT 10;",
            
            # Units sold queries
            r'(?i).*total.*units.*sold.*': "SELECT SUM(total_units_ordered) as total_units FROM total_sales_metrics;",
            r'(?i).*units.*sold.*ad.*': "SELECT SUM(units_sold) as ad_units_sold FROM ad_sales_metrics;",
            
            # Count queries
            r'(?i).*how\s+many\s+products.*': "SELECT COUNT(DISTINCT item_id) as product_count FROM total_sales_metrics;",
            r'(?i).*number\s+of\s+products.*': "SELECT COUNT(DISTINCT item_id) as product_count FROM total_sales_metrics;",
            
            # Date range queries
            r'(?i).*sales.*today.*': "SELECT SUM(total_sales) as today_sales FROM total_sales_metrics WHERE date = date('now');",
            r'(?i).*sales.*yesterday.*': "SELECT SUM(total_sales) as yesterday_sales FROM total_sales_metrics WHERE date = date('now', '-1 day');",
            
            # Performance metrics
            r'(?i).*conversion.*rate.*': "SELECT (SUM(units_sold) * 100.0 / SUM(clicks)) as conversion_rate FROM ad_sales_metrics WHERE clicks > 0;",
            r'(?i).*ctr.*': "SELECT (SUM(clicks) * 100.0 / SUM(impressions)) as ctr FROM ad_sales_metrics WHERE impressions > 0;",
            r'(?i).*click.*through.*rate.*': "SELECT (SUM(clicks) * 100.0 / SUM(impressions)) as ctr FROM ad_sales_metrics WHERE impressions > 0;",
        }
    
    def get_fallback_query(self, user_question):
        """
        Try to match the user question with predefined patterns and return appropriate SQL query.
        """
        for pattern, query in self.query_patterns.items():
            if re.match(pattern, user_question):
                return query
        
        return None
    
    def get_available_queries(self):
        """
        Return a list of example questions that can be handled by the fallback system.
        """
        examples = [
            "What is my total sales?",
            "Calculate the RoAS (Return on Ad Spend).",
            "Which product had the highest CPC (Cost Per Click)?",
            "Show me the top 10 products by sales.",
            "What is the average number of impressions?",
            "Which products are not eligible for advertising?",
            "What is the total ad spend?",
            "Show me the total clicks.",
            "How many products do I have?",
            "What is the conversion rate?",
            "What is the click-through rate (CTR)?",
            "Show me products with highest ad spend.",
            "What are my sales today?",
            "Show me the eligibility status distribution."
        ]
        return examples

if __name__ == "__main__":
    # Test the fallback system
    fallback = FallbackQuerySystem()
    
    test_questions = [
        "What is my total sales?",
        "Calculate the RoAS",
        "Which product had the highest CPC?",
        "Show me products not eligible for advertising",
        "Random question that won't match"
    ]
    
    print("Testing Fallback Query System")
    print("=" * 50)
    
    for question in test_questions:
        query = fallback.get_fallback_query(question)
        print(f"\nQuestion: {question}")
        if query:
            print(f"Fallback Query: {query}")
        else:
            print("No fallback query available")
    
    print(f"\nAvailable example queries: {len(fallback.get_available_queries())}")

