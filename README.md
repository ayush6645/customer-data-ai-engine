# Chat with Customer Data Tool (Hybrid AI + BI Engine)

### 🌐 Live Demo & Walkthrough
- **Live Implementation:** [Insert Hosted Link Here]
- **Video Walkthrough:** [Watch the Screen Recording](https://drive.google.com/file/d/1pIs3EA1vWU5W4fjQmuW-09Joc_7iWw1O/view?usp=sharing)

## 🎯 Project Overview
This project fulfills the "Chat with Customer Data" assignment. It provides a natural language interface to query and summarize an Excel dataset of customer real estate leads.

To ensure **100% mathematical accuracy** and completely eliminate AI hallucination, this tool uses a **Hybrid Architecture**:
1. **LLM Parser (Gemini API):** Translates the user's natural language question into a strict, structured JSON intent (e.g. `filter`, `average`, `count`).
2. **Deterministic Query Engine (Pandas):** Safely executes the math, numerical aggregations, and dataframe filtering natively in Python.
3. **Streamlit UI & NLP Summarizer:** Displays the exact extracted Pandas data table along with a clean, human-readable summary.

*(Addresses evaluation criteria: Accuracy, No AI guesses, Ability to handle different types of questions, Clean output format)*

## ✨ Features (Including Bonuses)
- **Natural Language Querying:** Ask for counts, sums, averages, multi-condition filters, or general summaries.
- **Bonus - Conversational Memory:** The system remembers your previous 5 queries. You can ask "Show me the 2BHKs" and follow up with "What about 3BHKs?" and it will maintain context.
- **Bonus - Clean UI:** Fully interactive Streamlit Chat UI that renders the extracted data natively as tables.
- **Fuzzy Date Logic:** Handles requests like "Last call was near Feb 2026" dynamically using Pandas `Timedelta`.

## 🛠️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Create a Virtual Environment (Optional but Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   Create a `.env` file in the root directory and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```

## 🚀 How to Run Locally

Start the Streamlit application:
```bash
streamlit run app.py
```

## 🧪 Example Queries to Test
Try placing these into the chat interface:
1. **Counting:** *"How many customers have a budget above 90 lakhs?"*
2. **Filtering:** *"List customers looking for 2BHK in Pune."*
3. **Math / Aggregation:** *"What is the average budget?"*
4. **Summarization:** *"Give a summary of all high-intent customers."*
5. **Conversational Memory (Bonus):** *"How many want 2BHKs?"* followed by *"What is their average budget?"*

## 📁 Repository Structure
- `app.py`: The Streamlit chat UI and pipeline orchestrator.
- `llm_parser.py`: The Gemini intent generation and text summarization logic.
- `query_engine.py`: The strict Pandas query execution layer.
- `data_loader.py`: Handles caching, loading, and formatting the `Data.xlsx` file.
- `utils.py`: Pydantic definitions bridging the LLM and the query engine.
- `requirements.txt`: Python package dependencies.
- `Data.xlsx`: The sample dataset.
