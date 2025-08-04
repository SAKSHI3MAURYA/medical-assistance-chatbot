# quiz.py
import streamlit as st
from datetime import datetime
from typing import List

def save_quiz_results(symptoms: List[str], possible_diseases: List[dict]):
    """Save quiz results for dashboard display."""
    if "medical_history" not in st.session_state:
        st.session_state.medical_history = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "symptoms": symptoms,
        "possible_diseases": possible_diseases,
    }
    st.session_state.medical_history.append(entry)

def medical_quiz(api_base: str, http_session):
    """
    Display medical symptom quiz and POST to /quiz.
    `api_base`  – e.g. http://localhost:8000
    `http_session` – your requests.Session()
    """
    st.header("🩺 Symptom Checker Quiz")
    # List all possible symptoms from your disease_symp dataset
    all_symptoms = [
        "fever", "cough", "fatigue", "headache", "shortness of breath",
        "sore throat", "chills", "nausea", "vomiting", "diarrhea",
        "body aches", "congestion", "loss of taste", "loss of smell",
        "rash", "dizziness", "chest pain", "abdominal pain"
    ]
    st.write("Select the symptoms you're experiencing:")
    cols = st.columns(3)
    selected = []
    for i, sym in enumerate(all_symptoms):
        with cols[i % 3]:
            if st.checkbox(sym.capitalize(), key=f"sym_{i}"):
                selected.append(sym)
    
    if st.button("Analyze Symptoms"):
        if not selected:
            st.warning("Please select at least one symptom.")
            return
        with st.spinner("Sending symptoms to the API…"):
            try:
                resp = http_session.post(
                    f"{api_base}/quiz",
                    json={"symptoms": selected}
                )
            except Exception as e:
                st.error(f"Error connecting to API: {e}")
                return
            if resp.status_code != 200:
                st.error(f"API returned {resp.status_code}: {resp.text}")
                return
            data = resp.json()
            if "possible_diseases" not in data:
                st.error("Unexpected response from /quiz. Check backend.")
                st.write(data)
                return
            
            # Show results
            st.subheader("Possible Conditions")
            try:
                for idx, d in enumerate(data["possible_diseases"], start=1):
                    with st.expander(f"{idx}. {d.get('disease', 'Unknown Disease')}"):
                        st.write(d.get("description", "No description available."))
            except Exception as e:
                st.error(f"Error displaying results: {e}")
                st.write("Raw data:", data)
            
            # Save to session for dashboard
            save_quiz_results(selected, data["possible_diseases"])
            # Switch back to chat automatically (optional)
            st.session_state.current_page = "chatbot"
            st.success("Quiz complete—check your Dashboard for history.")
