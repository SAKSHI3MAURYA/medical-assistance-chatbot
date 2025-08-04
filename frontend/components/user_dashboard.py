import streamlit as st
import pandas as pd
from datetime import datetime

def user_dashboard():
    """Display user dashboard with medical history"""
    st.title("Medical Dashboard")
    
    # Check if medical history exists
    if "medical_history" not in st.session_state or not st.session_state.medical_history:
        st.info("No medical history found. Complete a symptom quiz to see your history.")
        return
    
    # Display medical history
    st.header("Your Medical History")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Timeline View", "Table View"])
    
    with tab1:
        # Display history in reverse chronological order (newest first)
        for i, entry in enumerate(reversed(st.session_state.medical_history)):
            with st.expander(f"Consultation on {entry['timestamp']}"):
                st.subheader("Symptoms Reported")
                for symptom in entry['symptoms']:
                    st.write(f"- {symptom}")
                
                st.subheader("Possible Conditions")
                for disease in entry['possible_diseases']:
                    st.write(f"- {disease}")
    
    with tab2:
        # Create a dataframe for table view
        history_data = []
        for entry in st.session_state.medical_history:
            history_data.append({
                "Date": entry['timestamp'],
                "Symptoms": ", ".join(entry['symptoms']),
                "Possible Conditions": ", ".join(entry['possible_diseases'])
            })
        
        # Display as table
        if history_data:
            history_df = pd.DataFrame(history_data)
            st.dataframe(history_df, use_container_width=True)
    
    # Add option to clear history
    if st.button("Clear Medical History"):
        st.session_state.medical_history = []
        st.success("Medical history cleared successfully!")
        st.rerun()