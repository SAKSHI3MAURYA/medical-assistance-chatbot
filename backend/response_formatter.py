import re
import pandas as pd

def load_doctor_data(filepath="all_doc-data_cleaned.csv"):
    """Load and prepare the doctor data for recommendations"""
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Warning: Doctor data file '{filepath}' not found.")
        return None

def format_medical_response(raw_response, symptoms=None, doctor_data=None):
    """
    Process the raw model response and guide it through the medical conversation flow
    
    Args:
        raw_response: Raw text from the language model
        symptoms: User's reported symptoms (if available)
        doctor_data: DataFrame containing doctor information
    """
    # Step 1: Clean the basic formatting (from your original function)
    formatted = clean_basic_formatting(raw_response)
    
    # Step 2: Determine which stage of the conversation we're in
    conversation_stage = determine_conversation_stage(formatted, symptoms)
    
    # Step 3: Apply specific formatting based on the conversation stage
    if conversation_stage == "initial_symptoms":
        return format_disease_prediction(formatted, symptoms)
    elif conversation_stage == "disease_selection":
        return format_disease_information(formatted)
    elif conversation_stage == "disease_information":
        return format_doctor_recommendations(formatted, doctor_data)
    elif conversation_stage == "recommendations_provided":
        return format_feedback_request(formatted)
    else:
        return formatted

def clean_basic_formatting(text):
    """Basic text cleaning from original function"""
    # Remove redundant intro/ending phrases
    formatted = text

    # Remove known repeated lines or boilerplate
    unwanted_phrases = [
        r"hello and welcome to ask a doctor service i have reviewed your query and here is my advice",
        r"hope i have answered your query let me know if i can assist you further",
        r"\bto\s+healthcaremagiccomi\b",
        r"\bfurtherregardsdr\s+shareef",
        r"\bdr\s+[a-z]+\s+[a-z]+\s+(cardiologist|physician|neurologist|dermatologist|infectious disease specialist|orthopedic|general physician|psychiatrist|gastroenterologist)\b",
        r"\bdr\s+[a-z]+\s+[a-z]+\b",  # catches names like "dr ilir sharka"
        r"\bdr\s+[a-z]+\b",           # catches single-name like "dr shareef"
        r"\bdr\s+shareef\b",
        r"\bdr\s+ilir\s+sharka\b",
        r"\bdr\s+shinas\s+hussain\b",
        r"\bhi\b|\bhello\b|\bgreetings\b|\bdear user\b|\bthanks\b|\bregards\b",
    ]
    for phrase in unwanted_phrases:
        formatted = re.sub(phrase, " ", formatted, flags=re.IGNORECASE)

    # Capitalize sentences
    sentences = re.split(r'(?<=[.!?])\s+', formatted)
    sentences = [s.strip().capitalize() for s in sentences if s.strip()]
    formatted = ' '.join([s.strip().capitalize() if s else '' for s in sentences])

    # Add line breaks for readability
    formatted = re.sub(r"(hi|hello).*?healthcaremagiccom.*?(dr\s+\w+)?", "\n\n\\1\n\n", formatted, flags=re.IGNORECASE)

    return formatted.strip()

def determine_conversation_stage(text, symptoms):
    """Determine which stage of the conversation we're in"""
    if symptoms and not re.search(r"(disease|condition|disorder)", text, re.IGNORECASE):
        return "initial_symptoms"
    elif re.search(r"which (disease|condition) would you like (more information|to know more) about", text, re.IGNORECASE):
        return "disease_selection"
    elif re.search(r"(doctor|specialist|physician) (recommendation|suggestion)", text, re.IGNORECASE):
        return "disease_information"
    elif re.search(r"(feedback|how was|rate|experience)", text, re.IGNORECASE):
        return "recommendations_provided"
    else:
        return "general_response"

def format_disease_prediction(text, symptoms):
    """Format the response to include disease predictions"""
    # Check if the model already predicted diseases
    if re.search(r"(possible diagnoses|possible conditions|potential diseases)", text, re.IGNORECASE):
        # Already formatted correctly
        return text + "\n\nWhich disease would you like more information about?"
    else:
        # Guide the model to make predictions
        prompt_addition = f"""
Based on your symptoms ({', '.join(symptoms) if symptoms else 'described'}), I believe these are the three most likely possibilities:

1. [Disease 1]
2. [Disease 2]
3. [Disease 3]

Which of these would you like more information about?
"""
        return text + prompt_addition

def format_disease_information(text):
    """Format the response to include detailed disease information"""
    # Extract the selected disease
    disease_match = re.search(r"information about (\w+)", text, re.IGNORECASE)
    selected_disease = disease_match.group(1) if disease_match else "the selected condition"
    
    if not re.search(r"(causes|symptoms|treatment|management)", text, re.IGNORECASE):
        # Guide the model to provide comprehensive information
        prompt_addition = f"""
Here's detailed information about {selected_disease}:

Description:
[Provide a brief description of {selected_disease}]

Common symptoms:
[List the common symptoms]

Causes:
[Explain potential causes]

Treatment options:
[Describe treatment approaches]

Would you like me to recommend doctors who specialize in treating {selected_disease}?
"""
        return text + prompt_addition
    else:
        return text

def format_doctor_recommendations(text, doctor_data):
    """Format the response to include doctor recommendations"""
    # Extract the disease being discussed
    disease_match = re.search(r"information about (\w+)", text, re.IGNORECASE) or re.search(r"treating (\w+)", text, re.IGNORECASE)
    disease = disease_match.group(1) if disease_match else "this condition"
    
    if doctor_data is not None and not re.search(r"(doctor|specialist|physician) (recommendation|suggestion)", text, re.IGNORECASE):
        # Get specialists based on the condition
        specialties = determine_relevant_specialties(disease)
        recommended_doctors = get_doctor_recommendations(doctor_data, specialties)
        
        doctor_text = "\n\nRecommended specialists for this condition:\n"
        for i, (name, specialty, location) in enumerate(recommended_doctors, 1):
            doctor_text += f"{i}. Dr. {name} - {specialty} ({location})\n"
        
        prompt_addition = doctor_text + "\n\nHow was this information? Would you like to provide any feedback on this consultation?"
        return text + prompt_addition
    else:
        return text

def format_feedback_request(text):
    """Format the response to include a feedback request"""
    if not re.search(r"(feedback|how was|rate|experience)", text, re.IGNORECASE):
        prompt_addition = """
Thank you for using our service. How was your experience with this consultation? 
Your feedback helps us improve our medical assistance.
"""
        return text + prompt_addition
    else:
        return text

def determine_relevant_specialties(disease):
    """Map diseases to relevant medical specialties"""
    # This is a simplified mapping - in a real system this would be more comprehensive
    disease_specialty_map = {
        "diabetes": ["Endocrinology", "Internal Medicine"],
        "hypertension": ["Cardiology", "Internal Medicine"],
        "migraine": ["Neurology", "Pain Management"],
        "asthma": ["Pulmonology", "Allergy and Immunology"],
        "arthritis": ["Rheumatology", "Orthopedics"],
        "depression": ["Psychiatry", "Psychology"],
        "anxiety": ["Psychiatry", "Psychology"],
        "influenza": ["Internal Medicine", "Family Medicine"],
        "pneumonia": ["Pulmonology", "Infectious Disease"],
        "bronchitis": ["Pulmonology", "Family Medicine"],
    }
    
    # Default to general practitioners if no specific match
    return disease_specialty_map.get(disease.lower(), ["Family Medicine", "Internal Medicine"])

def get_doctor_recommendations(doctor_data, specialties, limit=3):
    """Get doctor recommendations based on specialties"""
    recommended_doctors = []
    
    for specialty in specialties:
        specialty_doctors = doctor_data[doctor_data['specialty'].str.contains(specialty, case=False, na=False)]
        if not specialty_doctors.empty:
            for _, row in specialty_doctors.head(min(2, len(specialty_doctors))).iterrows():
                recommended_doctors.append((row['name'], row['specialty'], row['location']))
        
        if len(recommended_doctors) >= limit:
            break
    
    # If we couldn't find enough specialists, add some general practitioners
    if len(recommended_doctors) < limit and 'Family Medicine' not in specialties:
        gp_doctors = doctor_data[doctor_data['specialty'].str.contains('Family Medicine|General Practice', case=False, na=False)]
        if not gp_doctors.empty:
            for _, row in gp_doctors.head(limit - len(recommended_doctors)).iterrows():
                recommended_doctors.append((row['name'], row['specialty'], row['location']))
    
    return recommended_doctors[:limit]