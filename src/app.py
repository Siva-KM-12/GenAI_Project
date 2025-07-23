from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import json
import logging
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_integration import LLMIntegration
from database_manager import DatabaseManager
from visualization import VisualizationManager
from fallback_queries import FallbackQuerySystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Correctly set static_folder to the absolute path of the 'static' directory
# This ensures Flask knows where to find index.html, style.css, etc.
static_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
app = Flask(__name__, static_folder=static_folder_path, static_url_path='/static')
CORS(app)

# Initialize components
try:
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ecommerce_data.db')
    db_manager = DatabaseManager(db_path)
    llm = LLMIntegration()
    viz_manager = VisualizationManager()
    fallback_system = FallbackQuerySystem()
    logger.info("All components initialized successfully")
except Exception as e:
    logger.error(f"Error initializing components: {e}")
    raise

# Route to serve the main HTML file from the static folder
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Route to serve visualization images from the 'visualizations' folder
@app.route('/visualizations/<filename>')
def serve_visualization(filename):
    # Construct the absolute path to the 'visualizations' folder
    # This assumes 'visualizations' is at the project root level, like 'static' and 'src'
    visualizations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'visualizations')
    return send_from_directory(visualizations_dir, filename)

def format_answer(query_result, user_question):
    """Format the query result into a human-readable answer."""
    if not query_result["success"]:
        return f"Error executing query: {query_result['error']}"
    
    data = query_result["data"]
    
    if not data:
        return "No data found for your query."
    
    question_lower = user_question.lower()
    
    try:
        if "total sales" in question_lower and len(data) == 1 and len(data[0]) == 1:
            value = data[0][0]
            if value is not None:
                return f"The total sales are: ${value:,.2f}"
            else:
                return "No sales data available."
        
        elif "roas" in question_lower or "return on ad spend" in question_lower:
            if len(data) == 1 and len(data[0]) == 1:
                value = data[0][0]
                if value is not None:
                    return f"The Return on Ad Spend (RoAS) is: {value:.2f}%"
                else:
                    return "Cannot calculate RoAS. No ad spend data available."
        
        elif "highest cpc" in question_lower or "cost per click" in question_lower:
            if len(data) >= 1 and len(data[0]) >= 2:
                item_id = data[0][0]
                cpc = data[0][1]
                if item_id is not None and cpc is not None:
                    return f"The product with the highest CPC is item_id {item_id} with a CPC of ${cpc:.2f}"
                else:
                    return "Cannot determine the product with the highest CPC."
        
        elif "count" in question_lower and len(data) == 1 and len(data[0]) == 1:
            value = data[0][0]
            if value is not None:
                return f"Count: {value:,}"
            else:
                return "Count: 0"
        
        # Generic formatting for other queries
        if len(data) == 1 and len(data[0]) == 1:
            value = data[0][0]
            if value is not None:
                if isinstance(value, (int, float)):
                    return f"Result: {value:,.2f}" if isinstance(value, float) else f"Result: {value:,}"
                else:
                    return f"Result: {value}"
            else:
                return "Result: No data"
        
        # Format as table for multiple rows/columns
        result_text = "Query Results:\n"
        columns = query_result.get("columns", [])
        if columns:
            result_text += " | ".join(columns) + "\n"
            result_text += "-" * (len(" | ".join(columns))) + "\n"
        
        for row in data[:10]:
            formatted_row = []
            for cell in row:
                if cell is None:
                    formatted_row.append("N/A")
                elif isinstance(cell, float):
                    formatted_row.append(f"{cell:.2f}")
                else:
                    formatted_row.append(str(cell))
            result_text += " | ".join(formatted_row) + "\n"
        
        if len(data) > 10:
            result_text += f"... and {len(data) - 10} more rows"
        
        return result_text
    
    except Exception as e:
        logger.error(f"Error formatting answer: {e}")
        return f"Error formatting results: {str(e)}"

@app.route("/ask", methods=["POST"])
def ask_question():
    """Main endpoint for asking questions."""
    try:
        data = request.get_json()
        if not data or "question" not in data:
            return jsonify({"error": "No question provided"}), 400
        
        user_question = data["question"].strip()
        if not user_question:
            return jsonify({"error": "Empty question provided"}), 400
        
        logger.info(f"Received question: {user_question}")
        
        # Try to generate SQL query using LLM first
        sql_query = llm.generate_sql_query(user_question)
        
        # If LLM fails, try fallback system
        if not sql_query:
            logger.warning("LLM failed to generate query, trying fallback system")
            sql_query = fallback_system.get_fallback_query(user_question)
            
            if not sql_query:
                return jsonify({
                    "error": "Could not understand the question. Please try rephrasing or use one of the demo questions.",
                    "success": False
                }), 400
        
        logger.info(f"Generated SQL query: {sql_query}")
        
        # Execute the query
        query_result = db_manager.execute_query(sql_query)
        
        if not query_result["success"]:
            logger.error(f"Query execution failed: {query_result['error']}")
        
        # Format the answer
        answer = format_answer(query_result, user_question)
        
        # Create visualization
        visualization_path = None
        if query_result["success"]:
            try:
                visualization_path = viz_manager.create_visualization(query_result, user_question, sql_query)
                if visualization_path:
                    # Return only the filename, as Flask will serve it from /visualizations/
                    visualization_path = os.path.basename(visualization_path)
                    logger.info(f"Visualization created: {visualization_path}")
            except Exception as e:
                logger.error(f"Visualization creation failed: {e}")
        
        response = {
            "question": user_question,
            "sql_query": sql_query,
            "answer": answer,
            "success": query_result["success"],
            "timestamp": datetime.now().isoformat()
        }
        
        if visualization_path:
            response["visualization"] = f"/visualizations/{visualization_path}" # Prepend Flask route
        
        if not query_result["success"]:
            response["error"] = query_result['error']
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Unexpected error in ask_question: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}", "success": False}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "E-commerce AI Agent is running",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("Starting E-commerce AI Agent...")
    print("Available endpoints:")
    print("  GET  / - Frontend")
    print("  GET  /health - Health check")
    print("  POST /ask - Ask a question")
    print("  GET  /visualizations/<filename> - Serve visualization images")
    
    logger.info("Starting E-commerce AI Agent server")
    app.run(debug=True, host="0.0.0.0", port=5000)
