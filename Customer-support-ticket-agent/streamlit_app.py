import streamlit as st
import requests

st.set_page_config(page_title="Customer Support & Ticket Agent", page_icon="💬", layout="wide")

API_BASE_URL = "http://127.0.0.1:8000"

# Initialize session state for messages and session management
if "session_id" not in st.session_state:
    st.session_state.session_id = "demo-session-1"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "draft_transcript" not in st.session_state:
    st.session_state.draft_transcript = ""

# Sidebar: Session & Ticket Management
with st.sidebar:
    st.header("Session Management")
    session_id_input = st.text_input("Session ID", value=st.session_state.session_id)
    if session_id_input != st.session_state.session_id:
        st.session_state.session_id = session_id_input
        st.session_state.messages = []

    st.markdown("---")
    st.header("Lookup Ticket")
    ticket_id_input = st.text_input("Enter Ticket ID", placeholder="TICK-XXXXXXXX")
    if st.button("Fetch Ticket"):
        if ticket_id_input.strip():
            try:
                res = requests.get(f"{API_BASE_URL}/ticket/{ticket_id_input.strip()}")
                if res.status_code == 200:
                    ticket_data = res.json()
                    st.success("Ticket Found!")
                    st.json(ticket_data)
                else:
                    st.error("Ticket not found!")
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")
        else:
            st.warning("Please enter a valid Ticket ID.")

# Main Chat Interface
st.title("💬 Customer Support & Ticket Agent")
st.markdown("Ask policy questions via text/voice or request help to create a support ticket.")

# Display chat history
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("ticket_id"):
            st.success(f"Created Ticket ID: {message['ticket_id']}")
        if message.get("sources"):
            st.caption(f"Sources: {', '.join(message['sources'])}")
            
        # TTS Speaker Button for Assistant messages
        if message["role"] == "assistant":
            if st.button("🔊 Play Audio", key=f"tts_btn_{idx}"):
                with st.spinner("Synthesizing audio..."):
                    try:
                        tts_res = requests.post(f"{API_BASE_URL}/voice/synthesize", json={"text": message["content"]})
                        if tts_res.status_code == 200:
                            st.audio(tts_res.content, format="audio/mp3")
                        else:
                            st.error("Failed to generate audio playback.")
                    except Exception as e:
                        st.error(f"TTS Error: {e}")

# Voice Input Section via Streamlit microphone audio recorder
st.markdown("---")
st.subheader("🎤 Voice Input")
audio_file = st.audio_input("Record your voice message")

if audio_file is not None:
    if st.button("Transcribe Audio"):
        with st.spinner("Processing speech-to-text..."):
            try:
                files = {"file": ("audio.wav", audio_file.getvalue(), "audio/wav")}
                res = requests.post(f"{API_BASE_URL}/voice/transcribe", files=files)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("success"):
                        st.session_state.draft_transcript = data.get("transcript", "")
                        st.success(f"Transcription successful ({data.get('processing_time_ms')} ms)")
                    else:
                        st.warning("Could not interpret audio clearly. Try again.")
                else:
                    st.error("Transcription API failed.")
            except Exception as e:
                st.error(f"Error connecting to server: {e}")

# Editable Transcript Section (Requirement: Allow user to review/correct transcript before submission)
if st.session_state.draft_transcript:
    st.markdown("### Review & Edit Transcript")
    edited_message = st.text_input("Edit text before sending:", value=st.session_state.draft_transcript, key="editable_transcript_input")
    
    if st.button("Confirm and Send Transcript"):
        if edited_message.strip():
            # Append user message
            st.session_state.messages.append({"role": "user", "content": edited_message})
            
            # Send to FastAPI chat endpoint
            try:
                payload = {"session_id": st.session_state.session_id, "message": edited_message}
                response = requests.post(f"{API_BASE_URL}/chat", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data.get("response"),
                        "ticket_id": data.get("ticket_id"),
                        "sources": data.get("sources", [])
                    })
                    # Clear draft after sending
                    st.session_state.draft_transcript = ""
                    st.rerun()
                else:
                    st.error("Failed to get response from backend agent.")
            except Exception as e:
                st.error(f"Error: {e}")

# Standard Typed Chat Input
if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    try:
        payload = {"session_id": st.session_state.session_id, "message": prompt}
        response = requests.post(f"{API_BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            st.session_state.messages.append({
                "role": "assistant",
                "content": data.get("response"),
                "ticket_id": data.get("ticket_id"),
                "sources": data.get("sources", [])
            })
            st.rerun()
        else:
            st.error("Error communicating with backend.")
    except Exception as e:
        st.error(f"Connection error: {e}")