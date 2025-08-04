from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
import pandas as pd
import uuid
import traceback
import re
from typing import List, Dict, Optional, Any
import secrets
from pydantic import BaseModel
import os

# Import model service and formatter
from model_service import MedicalModel
from response_formatter import format_medical_response

# Secret key for sessions
SECRET_KEY = secrets.token_urlsafe(32)

app = FastAPI()

# CORS and session middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=3600,
)
conversations: Dict[str, List[Dict[str, str]]] = {} 

class ChatMessage(BaseModel):
    user_id: str  # or session_id
    conversation_id: Optional[str] = None
    message: str

# Pydantic schemas
class LoginRequest(BaseModel):
    email: str
    password: str

class MessageRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class SymptomsRequest(BaseModel):
    symptoms: List[str]

# Hardcoded demo user
DEMO_USER = {
    "id": 1,
    "username": "Sakshi Maurya",
    "email": "sakshimaurya@gmail.com",
    "password": "123",
}

# Load model and data
model = MedicalModel("../models/biobart-v2-medical-chatbot-final")
disease_data = pd.read_csv("../data/disease_symp_cleaned.csv")
doctors_data = pd.read_csv("../data/all_doc_data_cleaned.csv")

# In-memory stores
dconversations: Dict[str, Any] = {}
user_medical_history: Dict[int, List[str]] = {}

# Utility: get current user from session
def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

# Utility: derive possible diseases from symptoms
# Now with robust error handling and string conversion
def get_possible_diseases(symptoms: List[str]) -> List[Dict[str, str]]:
    try:
        # Lowercase-symptom match against stringified Symptoms column
        def match_row(cell: Any) -> bool:
            text = str(cell).lower()
            return all(sym.lower() in text for sym in symptoms)

        matched = disease_data[disease_data['symptoms'].apply(match_row)]
        if matched.empty:
            return [{"disease": "Unknown", "description": "No matches found."}]

        # Optionally sort by a Probability column if it exists
        if 'Probability' in matched.columns:
            top = matched.nlargest(3, 'Probability')
        else:
            top = matched.head(3)

        # Rename columns to expected keys
        result = top.rename(columns={'diseases': 'disease', 'descriptions': 'description'})
        return result[['disease', 'description']].to_dict(orient='records')

    except Exception as e:
        # Log and rethrow as HTTPException
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing symptoms: {str(e)}"
        )

# Health check
@app.get("/")
async def health_check():
    return {"status": "ok"}

# Auth endpoints
@app.post("/login")
async def login(request: Request, creds: LoginRequest):
    if creds.email == DEMO_USER['email'] and creds.password == DEMO_USER['password']:
        request.session['user'] = {
            'id': DEMO_USER['id'],
            'username': DEMO_USER['username'],
            'email': DEMO_USER['email'],
        }
        return request.session['user']
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@app.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return {"message": "Logged out"}

# Chat endpoint with doctor-location and model fallback

@app.post("/chat")
async def chat_with_bot(request_data: dict = Body(...)):
    try:
        # Extract fields manually
        user_id = request_data.get("user_id")
        message = request_data.get("message")
        conversation_id = request_data.get("conversation_id")
        
        # Validate required fields
        if not user_id:
            return JSONResponse(
                status_code=422,
                content={"detail": "user_id is required"}
            )
            
        if not message:
            return JSONResponse(
                status_code=422,
                content={"detail": "message is required"}
            )

        # Initialize conversation if not present
        if user_id not in conversations:
            conversations[user_id] = []

        # Append user's message
        conversations[user_id].append({"role": "user", "content": message})

        try:
            # Get response from medical model
            model_response = model.generate_response(message)  # Adjust method name as needed
            bot_response = format_medical_response(model_response)
        except Exception as e:
            print(f"Model error: {e}")
            # Fallback if model fails
            bot_response = "I'm sorry, I couldn't process your request. Could you try rephrasing?"

        # Append bot response
        conversations[user_id].append({"role": "assistant", "content": bot_response})

        # Generate new conversation ID if none provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        return {
            "response": bot_response,
            "conversation_id": conversation_id
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chatbot failed to respond: {str(e)}")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "../data/disease_symp_cleaned.csv")

disease_df = pd.read_csv(data_path)
class QuizRequest(BaseModel):
    symptoms: list
# Quiz endpoint
@app.post("/quiz")
def get_possible_diseases(request: QuizRequest):
    # Get the symptoms from the request
    symptoms = request.symptoms
    matched_diseases = []

    # Iterate through the disease dataframe
    for _, row in disease_df.iterrows():
        disease_symptoms = row["symptoms"].split(",")
        match_count = sum(1 for s in symptoms if s.lower() in map(str.lower, disease_symptoms))

        if match_count > 0:
            matched_diseases.append({
                "disease": row["diseases"],
                "match_count": match_count,
                "description": row["descriptions"],
                "precautions": row["precautions"]
            })

    # Sort by match count
    matched_diseases = sorted(matched_diseases, key=lambda x: x["match_count"], reverse=True)

    if not matched_diseases:
        return {"possible_diseases": ["No disease matched your symptoms."]}

    return {"possible_diseases": matched_diseases[:3]}  # Return top 3

# User conversations
@app.get("/user/conversations")
async def get_convs(user: dict = Depends(get_current_user)):
    return {
        cid: conv for cid, conv in conversations.items()
        if conv['user_id'] == user['id']
    }

# User history
@app.get("/user/history")
async def get_history(user: dict = Depends(get_current_user)):
    return {'medical_history': user_medical_history.get(user['id'], [])}

@app.post("/user/history")
async def update_history(history: List[str], user: dict = Depends(get_current_user)):
    user_medical_history[user['id']] = history
    return {'status': 'success'}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)