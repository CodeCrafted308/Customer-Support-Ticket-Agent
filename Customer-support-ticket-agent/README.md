# Customer Support Ticket Agent

An AI-powered customer support application built with FastAPI, LangChain, Google Gemini, ChromaDB, and Streamlit.

## Features
- **Grounded RAG:** Answers policy and troubleshooting questions using local markdown knowledge bases with source attributions.
- **Multi-turn Ticket Creation:** Collects customer name, email, description, and category interactively before raising a mock ticket.
- **Duplicate Protection:** Prevents duplicate ticket creation within the same session.
- **FastAPI & Streamlit:** Clean REST API endpoints paired with an interactive session-aware chat UI.

## Setup & Installation

1. Clone or extract the repository and navigate to the project directory:
   ```bash
   cd customer-support-agent
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file from `.env.example` and add your Google Gemini API key:
   ```env
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

## Running the Application

### 1. Start the FastAPI Backend
```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Start the Streamlit Frontend (in a new terminal)
```bash
streamlit run streamlit_app.py
```

## API Endpoints
- `GET /health` - Component readiness check.
- `POST /chat` - Process a customer message.
- `GET /tickets/{ticket_id}` - Retrieve a created support ticket.
