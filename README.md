# Customer Support Ticket Agent with Voice & RAG

Yeh project ek AI-powered Customer Support Ticket Agent hai jo FastAPI (backend) aur Streamlit (frontend) par bana hai[cite: 1, 2]. Yeh knowledge base (RAG) ke zariye policy aur troubleshooting ke sawalon ke jawab deta hai, support tickets generate karta hai, aur sath hi Speech-to-Text (STT) aur Text-to-Speech (Voice) integration bhi support karta hai[cite: 2, 6, 8].

---

## Features

1. **RAG Knowledge Base**: Markdown documents ko index karke policy aur troubleshooting queries ke accurate aur grounded jawab deta hai[cite: 2].
2. **Support Ticket Management**: User ki details (Name, Email, Issue Description, Category) validate karke mock ticket API ke zariye unique Ticket ID generate karta hai.
3. **Ticket Retrieval**: Kisi bhi purani ticket ki details `/tickets/{ticket_id}` endpoint ke zariye fetch ki ja sakti hain.
4. **Voice Input (STT)**: Browser/System microphone se audio record karke transcribe karne ki suvidha, jisme user transcript ko edit karke explicitly submit kar sakta hai.
5. **Voice Output (TTS)**: Har agent response ke sath ek speaker icon hota hai, jiss par click karke response ko audio mein sunaa ja sakta hai.

---

## Tech Stack

* **Python 3.11+**[cite: 2]
* **FastAPI** (Backend API & Endpoints)[cite: 2, 8]
* **Streamlit** (Interactive Frontend UI)[cite: 2, 8]
* **LangChain / LangGraph** (Agent Orchestration)[cite: 2]
* **ChromaDB / FAISS** (Vector Database for RAG)[cite: 2]
* **STT & TTS Adapters** (Voice Pipeline integration)[cite: 6, 8]

---

## Project Structure

```text
├── mid_session_requirements/        # Voice pipeline contracts, models & tests
├── src/                             # Core application source code
│   ├── agent/                       # LangChain/LangGraph agent & tools
│   ├── rag/                         # Document loading & vector store
│   ├── tickets/                     # Mock ticket repository & service
│   └── voice/                       # STT and TTS service implementations
├── tests/                           # Unit and integration tests
├── .env.example                     # Environment variables template
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
