import streamlit as st
import requests
import json
import uuid
import logging

logging.basicConfig(level=logging.DEBUG)

# Ensure user_id exists in session state
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

def chatbot_ui():
    """Chatbot interface component"""

    # Display title only once
    if "title_displayed" not in st.session_state:
        st.title("AI Medical Assistant")
        st.session_state.title_displayed = True

    # Initialize conversation state
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render existing chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Get user input
    user_input = st.chat_input("Ask me about your health concerns…")

    if not user_input:
        return

    # Append user message to history and UI
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Prepare payload - the key issue was here
    payload = {
        "user_id": st.session_state.user_id,
        "message": user_input
    }
    
    # Add conversation_id only if it exists
    if st.session_state.conversation_id:
        payload["conversation_id"] = st.session_state.conversation_id

    # Send to backend
    with st.spinner("Thinking…"):
        try:
            # Debug what we're about to send
            st.write(f"DEBUG - About to send: {payload}")
            print(f"DEBUG - About to send payload: {payload}")

            # Make request with explicit dump to string for logging
            payload_str = json.dumps(payload)
            st.write(f"Payload as string: {payload_str}")

            # Try with manual headers and data
            headers = {"Content-Type": "application/json"}
            resp = requests.post(
                "http://127.0.0.1:8000/chat",
                data=payload_str,  # Use data with string
                headers=headers,
                timeout=60
            )
            
        # Log what was sent and received
            st.write(f"Request headers: {headers}")
            st.write(f"Response status: {resp.status_code}")
            st.write(f"Response headers: {dict(resp.headers)}")
            st.write(f"Response text: {resp.text}")
            
            resp.raise_for_status()
            data = resp.json()
                # Extract and display assistant response
            assistant_text = data.get("response")
            if assistant_text is None:
                st.error("No `response` field in server reply.")
                return
            st.session_state.conversation_id = data.get("conversation_id")
            st.session_state.messages.append({"role": "assistant", "content": assistant_text})
            with st.chat_message("assistant"):
                st.write(assistant_text)

        except Exception as e:
            st.error(f"Chat request failed: {e}")
            if hasattr(e, 'response') and e.response:
                    st.error(f"Response content: {e.response.text}")