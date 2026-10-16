import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

from langchain_google_genai import ChatGoogleGenerativeAI
from app.rag import rag_system
from app.ticket_service import ticket_store

class SupportAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, google_api_key=api_key)
        self.conversations = {}

    def process_message(self, session_id: str, message: str):
        if session_id not in self.conversations:
            self.conversations[session_id] = {
                "step": "idle",
                "name": None,
                "email": None,
                "description": None,
                "category": "other"
            }
        
        state = self.conversations[session_id]
        msg_lower = message.lower()

        if state["step"] == "idle" and any(w in msg_lower for w in ["ticket", "issue", "problem", "agent", "human", "refund"]):
            state["step"] = "collect_description"
            state["description"] = message
            return {
                "success": True,
                "session_id": session_id,
                "response": "I can help you create a support ticket. What is your full name?",
                "sources": [],
                "ticket_id": None
            }
        
        elif state["step"] == "collect_description":
            state["name"] = message
            state["step"] = "collect_email"
            return {
                "success": True,
                "session_id": session_id,
                "response": f"Thanks {message}. What email address should we use for your ticket?",
                "sources": [],
                "ticket_id": None
            }
            
        elif state["step"] == "collect_email":
            state["email"] = message
            state["step"] = "collect_category"
            return {
                "success": True,
                "session_id": session_id,
                "response": "Please choose a category for your issue: order, payment, account, technical, or other.",
                "sources": [],
                "ticket_id": None
            }
            
        elif state["step"] == "collect_category":
            category = msg_lower.strip()
            if category not in ["order", "payment", "account", "technical", "other"]:
                category = "other"
            state["category"] = category
            
            ticket = ticket_store.create_ticket(
                session_id=session_id,
                name=state["name"],
                email=state["email"],
                description=state["description"],
                category=state["category"]
            )
            
            state["step"] = "idle"
            
            return {
                "success": True,
                "session_id": session_id,
                "response": f"Ticket successfully created! Your Ticket ID is {ticket['ticket_id']}. Our team will reach out soon.",
                "sources": [],
                "ticket_id": ticket["ticket_id"]
            }

        context, sources = rag_system.query(message)
        prompt = f"""You are a helpful customer support agent. Answer the customer's question strictly using the provided context. If the answer is not in the context, clearly state that you do not know.

Context:
{context}

Customer Question: {message}
Answer:"""

        response = self.llm.invoke(prompt)
        answer_text = response.content if hasattr(response, 'content') else str(response)

        return {
            "success": True,
            "session_id": session_id,
            "response": answer_text,
            "sources": sources,
            "ticket_id": None
        }

agent = SupportAgent()