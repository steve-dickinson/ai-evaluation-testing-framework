# Dashboard Guide

The **Streamlit Dashboard** is the primary interactive interface for the AI Evaluation Framework. It allows you to configure tests, run them, visualize results, and manage historical data without touching the command line.

## Accessing the Dashboard

If running via Docker Compose:
- **URL**: [http://localhost:8501](http://localhost:8501)

If running locally:
```bash
uv run streamlit run src/dashboard.py
```

## ⚙️ Configuration (Sidebar)

The sidebar controls the test parameters.

### 1. API Keys
- **OpenAI API Key**: Required for the `LLM-as-a-Judge` and for the `OpenAI (Direct)` chatbot mode. If you set `OPENAI_API_KEY` in your `.env` file, this will be pre-filled.

### 2. Chatbot Mode
- **OpenAI (Direct)**: Connects directly to an OpenAI-compatible API endpoint.
- **Playwright (UI Testing)**: Uses a headless browser to interact with a web-based chatbot (like the Target App).
    - **Target App URL**: The URL of the chatbot to test (default: `http://localhost:8503`).
    - **CSS Selectors**: Under "Advanced Configuration", you can customize how the framework finds the input box and chat messages.

### 3. Test Selection
- **Test Suite**: Select a YAML file from the `tests/` directory containing your scenarios.
- **Evaluator Type**:
    - **Keyword (Content Safety)**: fast, regex-based checking.
    - **LLM-as-a-Judge**: slower, semantic evaluation using GPT-4.

## 🚀 Running Tests

Click the **🚀 Run Evaluation** button to start. A progress bar will track execution.

## 📊 Views

Once tests differ, or if you load data from history, you can switch between three views:

### 1. Test Results
The default view showing the outcome of the current run.
- **Metrics**: Pass Rate, Total Tests, Average Latency.
- **Data Table**: Color-coded rows for each test scenario.
- **Detailed Logs**: Expandable sections showing the full Prompt, Response, and Judge's reasoning.

### 2. 🛡️ AI Recommendations
If tests fail, this intelligent engine helps you fix them.
- **Analyze Failures**: Click this to have an AI analyze *why* the chatbot failed (e.g., "It refused a safe prompt" or "It answered a blocked prompt").
- **Revised System Prompt**: The engine generates a *new, improved* System Prompt designed to fix the specific content safety failures observed.

### 3. 📜 History
Review past performance.
- **MongoDB Storage**: All runs are automatically saved to the database.
- **Browse**: View a list of recent runs with timestamps and pass rates.
- **Load**: Click "Load" to restore the results of a previous run into the dashboard for analysis or recommendation generation.
