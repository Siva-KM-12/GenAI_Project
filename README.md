# 🤖 E-commerce AI Agent

This project implements an AI-powered E-commerce Data Analyst Agent that allows users to query their sales and advertising data using natural language. The agent converts natural language questions into SQL queries, executes them against a SQLite database, and provides human-readable answers along with relevant data visualizations.

## ✨ Features

*   **Natural Language to SQL:** Converts user questions into executable SQLite SQL queries using a local Large Language Model (LLM) (Mistral via Ollama).
*   **Data Ingestion:** Automatically ingests sales, advertising, and product eligibility data from Excel files into a SQLite database.
*   **Dynamic Data Visualization:** Generates various types of charts (bar, line, pie, etc.) based on query results to provide visual insights.
*   **Flask API:** Provides a RESTful API for handling natural language queries and returning structured responses.
*   **Interactive Frontend:** A simple web interface for users to ask questions and view results and visualizations.
*   **Fallback Mechanism:** Includes a basic fallback system for common queries if the LLM fails to generate a valid SQL.
*   **Comprehensive Error Handling:** Gracefully handles errors during LLM interaction, SQL execution, and data processing.

## 🚀 Quick Start

Follow these steps to get your E-commerce AI Agent up and running locally.

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.8+**
*   **pip** (Python package installer)
*   **Ollama:** A platform for running large language models locally. Download and install it from [ollama.com](https://ollama.com/ ).

## IMPLEMENTATION SCREENSHOTS
<img width="1912" height="883" alt="image" src="https://github.com/user-attachments/assets/f4914ac2-d4af-4db2-b020-d3cc02a64829" />
<img width="752" height="862" alt="image" src="https://github.com/user-attachments/assets/543c9003-d04c-44e9-9ce4-a101d6bd2530" />
<img width="753" height="835" alt="image" src="https://github.com/user-attachments/assets/1fdc3763-cc31-490a-af23-452fc0cd8391" />


## VIDEO LINK
[Video link ](https://drive.google.com/file/d/1Aa3RiPbxFcGfTGR6FvOCAfz1LYsqZ-Uq/view?usp=sharing)



