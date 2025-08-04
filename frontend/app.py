import streamlit as st
import requests
from typing import Dict, Any, List
from components.quiz import medical_quiz
from components.user_dashboard import user_dashboard

# Default API endpoint
default_api_url = "http://localhost:8000"

# Initialize session state for API URL, auth, messages, and HTTP session
if 'api_url' not in st.session_state:
    st.session_state.api_url = default_api_url
if 'http_session' not in st.session_state:
    st.session_state.http_session = requests.Session()
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "chatbot"
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None

# Authentication functions
def login(email: str, password: str) -> bool:
    """Log in with email and password using persistent session"""
    try:
        base = st.session_state.api_url
        sess = st.session_state.http_session
        # Health check
        health = sess.get(base)
        if health.status_code != 200:
            st.error(f"API not responding: {health.status_code}")
            return False

        # Login request
        login_url = f"{base}/login"
        response = sess.post(login_url, json={"email": email, "password": password})
        if response.status_code == 200:
            user_data = response.json()
            st.session_state.user_info = user_data
            st.session_state.authenticated = True
            st.success(f"Welcome, {user_data['username']}!")
            return True
        else:
            st.error(f"Login failed: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error during login: {e}")
        return False


def logout():
    """Log out the user and clear session cookies"""
    try:
        sess = st.session_state.http_session
        sess.get(f"{st.session_state.api_url}/logout")
        sess.cookies.clear()
    except:
        pass
    st.session_state.user_info = None
    st.session_state.authenticated = False
    st.session_state.messages = []
    st.session_state.conversation_id = None
    st.rerun()

# Chat functions
def send_message(message: str) -> Dict[str, Any] | None:
    """Send a message to the chatbot API using persistent session"""
    if not st.session_state.authenticated:
        st.error("You must be logged in to send messages.")
        return None
    try:
        base = st.session_state.api_url
        sess = st.session_state.http_session
        
        # Add user_id to the request data
        data: Dict[str, Any] = {
            "message": message,
            "user_id": str(st.session_state.user_info['id']) if st.session_state.user_info else "guest-user"
        }
        
        if st.session_state.conversation_id:
            data["conversation_id"] = st.session_state.conversation_id

        # Debug the payload
        print(f"Sending data: {data}")
        
        response = sess.post(f"{base}/chat", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("conversation_id"):
                st.session_state.conversation_id = result["conversation_id"]
            return result
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return None

# UI components
def display_auth_status():
    """Display API settings and login/logout in sidebar"""
    with st.sidebar:
        with st.expander("API Settings"):
            st.session_state.api_url = st.text_input(
                "API URL",
                value=st.session_state.api_url,
                key="api_url_input"
            )
            st.write("Currently connecting to:", st.session_state.api_url)
            if st.button("Test Connection", key="test_conn"):
                try:
                    resp = st.session_state.http_session.get(st.session_state.api_url)
                    if resp.status_code == 200:
                        st.success("Connected to API server", icon="✅")
                    else:
                        st.warning(f"Bad status: {resp.status_code}", icon="⚠️")
                except Exception as e:
                    st.error(f"Connection failed: {e}")
        st.markdown("---")
        if not st.session_state.authenticated:
            st.subheader("Login")
            email = st.text_input("Email", key="email_input")
            password = st.text_input("Password", type="password", key="password_input")
            if st.button("Login", key="login_btn"):
                login(email, password)
        else:
            st.subheader(f"Hello, {st.session_state.user_info['username']}")
            if st.button("Logout", key="logout_btn"):
                logout()


def chatbot_ui():
    """Display chatbot UI"""
    st.title("Medical Assistant Chat")
    if st.session_state.authenticated:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        user_input = st.chat_input("Type your symptoms or health concerns...")
        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = send_message(user_input)
            if response:
                with st.chat_message("assistant"):
                    st.markdown(response["response"])
                st.session_state.messages.append({"role": "assistant", "content": response["response"]})
                st.rerun()
    else:
        st.info("Please log in to use the medical assistant.")


def main():
    st.set_page_config(page_title="Medical Assistant", page_icon="💉", layout="wide")
    display_auth_status()
    with st.sidebar:
        st.title("Navigate")
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.current_page = "chatbot"
            st.rerun()
        if st.button("🩺 Quiz", use_container_width=True):
            st.session_state.current_page = "quiz"
            st.rerun()
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
    if st.session_state.current_page == "chatbot":
        chatbot_ui()
    elif st.session_state.current_page == "quiz":
        medical_quiz(st.session_state.api_url, st.session_state.http_session)
    elif st.session_state.current_page == "dashboard":
        user_dashboard()

if __name__ == "__main__":
    main()
