# QUICK START GUIDE: E-commerce AI Agent (Final Version)

This guide provides the definitive steps to set up and run your E-commerce AI Agent. Please follow these instructions precisely.

## Step 1: Clean Up Previous Installation

To ensure no conflicts or old files cause issues, **delete your existing `e_commerce_ai_agent` folder** (the one you were previously working with). This is crucial for a clean start.

## Step 2: Extract the New Project Archive

I will provide a new archive named `e_commerce_ai_agent_final.tar.gz`. Download this archive and extract it. This will create a new directory named `e_commerce_ai_agent_final`.

**On Linux/macOS:**

Open your terminal and navigate to the directory where you downloaded the archive. Then run:

```bash
tar -xzf e_commerce_ai_agent_final.tar.gz
cd e_commerce_ai_agent_final
```

**On Windows:**

Use a tool like 7-Zip or WinRAR to extract the `.tar.gz` file. After extraction, open your Command Prompt or PowerShell and navigate into the `e_commerce_ai_agent_final` directory.

## Step 3: Install Required Python Packages

Once you are inside the `e_commerce_ai_agent_final` directory in your terminal, install all the necessary Python libraries by running:

```bash
pip install -r requirements.txt
```

## Step 4: Set Up Local LLM (Ollama)

This project uses a local Large Language Model (LLM) via Ollama. If you don't have Ollama installed, follow these sub-steps:

1.  **Download Ollama:** Go to [ollama.com](https://ollama.com/) and download the appropriate installer for your operating system.
2.  **Install Ollama:** Run the installer and follow the on-screen instructions.
3.  **Download the Mistral Model:** Open a new terminal and run the following command to download the `mistral` model:
    ```bash
    ollama run mistral
    ```
    Let it complete the download. You can then type `/bye` and press Enter to exit the interactive session.
4.  **Start Ollama Server:** In a dedicated terminal window, start the Ollama server. This terminal window must remain open while the AI Agent is running.
    ```bash
    ollama serve
    ```

## Step 5: Run the Data Ingestion Script (One-time)

This script will create the SQLite database (`ecommerce_data.db`) and populate it with data from the Excel files. You only need to run this once. From the `e_commerce_ai_agent_final` directory, run:

```bash
python src/data_ingestion.py
```

This will create `ecommerce_data.db` in the root of your `e_commerce_ai_agent_final` directory.

## Step 6: Start the Flask API Server

Open a **new terminal window** (keep the Ollama server terminal open from Step 4) and navigate to your `e_commerce_ai_agent_final` directory. Then run:

```bash
python src/app.py
```

You should see output indicating that the Flask server is running, typically on `http://127.0.0.1:5000/` or `http://localhost:5000/`.

## Step 7: Access the Frontend in Your Browser

Open your web browser and go to:

```
http://localhost:5000
```

## Step 8: Test the E-commerce AI Agent

Now you can interact with the AI Agent:

*   **Sample Questions:** Click on any of the sample question buttons provided on the frontend (e.g., "Total Sales", "Top Products", "Highest CPC"). The question will automatically populate the input field and trigger the query.
*   **Custom Questions:** Type your own questions into the input field and press Enter or click "Generate Chart".
*   **Verify Responses:** For every question, you should see:
    *   A clear answer (for single-value questions like total sales).
    *   A relevant graph visualization.
    *   No errors on the frontend.

If you encounter any issues, double-check each step, especially ensuring Ollama is running and the Flask server is active.

Enjoy using your E-commerce AI Agent!


