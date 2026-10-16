import os
import json
import uuid
from datetime import datetime
from typing import Dict, Optional

DB_FILE = "tickets.json"

class TicketService:
    def __init__(self):
        self.tickets: Dict[str, dict] = {}
        self.session_tickets: Dict[str, str] = {}
        self.load_from_disk()

    def load_from_disk(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f:
                    data = json.load(f)
                    self.tickets = data.get("tickets", {})
                    self.session_tickets = data.get("session_tickets", {})
            except Exception:
                self.tickets = {}
                self.session_tickets = {}

    def save_to_disk(self):
        try:
            with open(DB_FILE, "w") as f:
                json.dump({
                    "tickets": self.tickets,
                    "session_tickets": self.session_tickets
                }, f, indent=4)
        except Exception as e:
            print(f"Error saving tickets: {e}")

    def create_ticket(self, session_id: str, name: str, email: str, description: str, category: str) -> dict:
        if session_id in self.session_tickets:
            existing_id = self.session_tickets[session_id]
            if existing_id in self.tickets:
                return self.tickets[existing_id]

        ticket_id = "TICK-" + str(uuid.uuid4())[:8].upper()
        timestamp = datetime.utcnow().isoformat()
        
        ticket_data = {
            "ticket_id": ticket_id,
            "category": category,
            "summary": description,
            "customer_details": {
                "name": name,
                "email": email
            },
            "initial_status": "Open",
            "created_at": timestamp
        }
        
        self.tickets[ticket_id] = ticket_data
        self.session_tickets[session_id] = ticket_id
        self.save_to_disk()  # Save to file immediately
        return ticket_data

    def get_ticket(self, ticket_id: str) -> Optional[dict]:
        self.load_from_disk() # Refresh from disk to ensure latest data
        return self.tickets.get(ticket_id)

ticket_store = TicketService()