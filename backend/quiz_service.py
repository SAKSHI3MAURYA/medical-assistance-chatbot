# quiz_service.py
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    category: str
    follow_up: Optional[Dict[str, List[str]]] = None

class HealthAssessment:
    def __init__(self):
        self.questions = self._initialize_questions()
        self.symptom_mapping = self._initialize_symptom_mapping()
        
    def _initialize_questions(self) -> List[QuizQuestion]:
        """Initialize the list of health assessment questions"""
        return [
            QuizQuestion(
                id="q1",
                question="Which of these general symptoms have you experienced in the past week?",
                options=["Fever", "Fatigue", "Weight loss", "Night sweats", "None of the above"],
                category="general"
            ),
            QuizQuestion(
                id="q2",
                question="Do you have any pain or discomfort? If yes, where is it mainly located?",
                options=["Head/Neck", "Chest", "Abdomen", "Back", "Joints/Limbs", "No pain"],
                category="pain",
                follow_up={
                    "Head/Neck": ["Is it throbbing?", "Is it constant?", "Does it worsen with light/sound?"],
                    "Chest": ["Is it sharp?", "Does it worsen with breathing?", "Does it radiate to your arm?"],
                    "Abdomen": ["Is it cramping?", "Is it associated with meals?", "Does it come and go?"]
                }
            ),
            QuizQuestion(
                id="q3",
                question="Have you experienced any respiratory symptoms?",
                options=["Cough", "Shortness of breath", "Wheezing", "Sore throat", "None of the above"],
                category="respiratory"
            ),
            QuizQuestion(
                id="q4",
                question="Have you noticed any digestive issues?",
                options=["Nausea/Vomiting", "Diarrhea", "Constipation", "Heartburn", "None of the above"],
                category="digestive"
            ),
            QuizQuestion(
                id="q5",
                question="Have you experienced any of these neurological symptoms?",
                options=["Headache", "Dizziness", "Confusion", "Numbness/Tingling", "None of the above"],
                category="neurological"
            ),
            QuizQuestion(
                id="q6",
                question="How would you describe your sleep quality?",
                options=["Excellent", "Good", "Fair", "Poor", "Very poor"],
                category="lifestyle"
            ),
            QuizQuestion(
                id="q7",
                question="Do you have any diagnosed chronic conditions?",
                options=["Diabetes", "Hypertension", "Asthma", "Heart disease", "Thyroid disorder", "None of the above"],
                category="medical_history",
                follow_up={
                    "Diabetes": ["Type 1", "Type 2", "Gestational", "Prediabetes"],
                    "Hypertension": ["How long have you had it?", "Is it controlled with medication?"],
                    "Asthma": ["How often do you use rescue inhalers?"]
                }
            ),
            QuizQuestion(
                id="q8",
                question="Are you currently taking any medications regularly?",
                options=["Blood pressure medication", "Diabetes medication", "Pain relievers", "Antidepressants", "Other", "None"],
                category="medications"
            ),
            QuizQuestion(
                id="q9",
                question="Do you have any known allergies?",
                options=["Medications", "Food", "Environmental (pollen, dust)", "Insect stings", "None known"],
                category="allergies"
            ),
            QuizQuestion(
                id="q10",
                question="How would you describe your stress level over the past month?",
                options=["Very low", "Low", "Moderate", "High", "Very high"],
                category="mental_health"
            ),
            QuizQuestion(
                id="q11",
                question="How often do you exercise?",
                options=["Daily", "3-5 times per week", "1-2 times per week", "Rarely", "Never"],
                category="lifestyle"
            ),
            QuizQuestion(
                id="q12",
                question="Have you recently experienced any changes in vision, hearing, or other senses?",
                options=["Vision changes", "Hearing changes", "Taste/smell changes", "Balance issues", "None of the above"],
                category="sensory"
            )
        ]
    
    def _initialize_symptom_mapping(self) -> Dict[str, List[str]]:
        """Map question options to potential conditions/symptoms"""
        return {
            "Fever": ["infection", "inflammation"],
            "Fatigue": ["anemia", "sleep disorder", "thyroid disorder"],
            "Weight loss": ["diabetes", "thyroid disorder", "nutritional deficiency"],
            "Night sweats": ["infection", "hormone imbalance"],
            "Cough": ["respiratory infection", "asthma"],
            "Shortness of breath": ["asthma", "heart condition", "anxiety"],
            "Wheezing": ["asthma", "allergic reaction"],
            "Sore throat": ["upper respiratory infection"],
            "Headache": ["migraine", "tension headache", "sinus issue"],
            "Dizziness": ["vertigo", "low blood pressure", "inner ear issue"],
            "Confusion": ["neurological condition", "infection", "medication side effect"],
            "Numbness/Tingling": ["nerve compression", "vitamin deficiency", "neurological condition"],
            "Nausea/Vomiting": ["gastroenteritis", "food poisoning", "migraine"],
            "Diarrhea": ["infection", "irritable bowel syndrome", "food intolerance"],
            "Constipation": ["dehydration", "low fiber diet", "medication side effect"],
            "Heartburn": ["acid reflux", "GERD"],
            "Diabetes": ["diabetes"],
            "Hypertension": ["hypertension"],
            "Asthma": ["asthma"],
            "Heart disease": ["heart disease"],
            "Thyroid disorder": ["thyroid disorder"],
            "Poor": ["sleep disorder"],
            "Very poor": ["sleep disorder", "anxiety", "depression"],
            "High": ["stress", "anxiety"],
            "Very high": ["stress", "anxiety", "depression"],
            "Vision changes": ["eye condition", "neurological issue", "diabetes complication"],
            "Hearing changes": ["ear infection", "age-related hearing loss"],
            "Taste/smell changes": ["upper respiratory infection", "neurological condition"],
            "Balance issues": ["inner ear disorder", "neurological condition"]
        }
    
    def get_question(self, question_idx: int) -> Optional[QuizQuestion]:
        """Get a question by index"""
        if 0 <= question_idx < len(self.questions):
            return self.questions[question_idx]
        return None
    
    def get_question_by_id(self, question_id: str) -> Optional[QuizQuestion]:
        """Get a question by ID"""
        for question in self.questions:
            if question.id == question_id:
                return question
        return None
    
    def analyze_answers(self, answers: Dict[str, str]) -> Dict[str, Any]:
        """Analyze quiz answers to determine potential health conditions"""
        potential_conditions = []
        symptoms = []
        
        # Extract symptoms from answers
        for q_id, answer in answers.items():
            if answer in self.symptom_mapping:
                symptoms.append(answer)
                potential_conditions.extend(self.symptom_mapping[answer])
        
        # Count and sort conditions by frequency
        condition_count = {}
        for condition in potential_conditions:
            if condition in condition_count:
                condition_count[condition] += 1
            else:
                condition_count[condition] = 1
        
        # Sort by count (descending)
        sorted_conditions = sorted(condition_count.items(), key=lambda x: x[1], reverse=True)
        top_conditions = [cond for cond, count in sorted_conditions[:5]]
        
        # General health assessment based on answers
        severity_level = self._assess_severity(answers, symptoms)
        
        return {
            "symptoms": symptoms,
            "potential_conditions": top_conditions,
            "severity_level": severity_level,
            "follow_up_required": len(top_conditions) > 0 and severity_level != "low"
        }
    
    def _assess_severity(self, answers: Dict[str, str], symptoms: List[str]) -> str:
        """Assess the potential severity of the condition"""
        # This is a very simplified severity assessment
        high_severity_symptoms = ["Chest", "Shortness of breath", "Confusion"]
        medium_severity_symptoms = ["Fever", "Headache", "Dizziness", "Numbness/Tingling"]
        
        for symptom in symptoms:
            if symptom in high_severity_symptoms:
                return "high"
        
        for symptom in symptoms:
            if symptom in medium_severity_symptoms:
                return "medium"
        
        return "low"
    
    def get_follow_up_questions(self, question_id: str, answer: str) -> List[str]:
        """Get follow-up questions based on an answer"""
        question = self.get_question_by_id(question_id)
        if question and question.follow_up and answer in question.follow_up:
            return question.follow_up[answer]
        return []
    
    def get_specialist_recommendation(self, symptoms: List[str]) -> Optional[str]:
        """Recommend a medical specialist based on symptoms"""
        # Mapping of symptoms to specialists
        specialist_mapping = {
            "respiratory": ["Cough", "Shortness of breath", "Wheezing"],
            "cardiology": ["Chest", "Heart disease"],
            "gastroenterology": ["Nausea/Vomiting", "Diarrhea", "Constipation", "Heartburn"],
            "neurology": ["Headache", "Dizziness", "Confusion", "Numbness/Tingling", "Balance issues"],
            "endocrinology": ["Diabetes", "Thyroid disorder", "Weight loss"],
            "psychiatry": ["Very high", "High", "Very poor", "anxiety", "depression"],
            "ophthalmology": ["Vision changes"],
            "otolaryngology": ["Hearing changes", "Taste/smell changes", "Sore throat"],
            "rheumatology": ["Joints/Limbs"],
            "general_practice": []  # Default
        }
        
        # Count which specialist appears most frequently
        specialist_count = {specialist: 0 for specialist in specialist_mapping}
        
        for symptom in symptoms:
            for specialist, related_symptoms in specialist_mapping.items():
                if symptom in related_symptoms:
                    specialist_count[specialist] += 1
        
        # Get specialist with highest count
        max_count = 0
        recommended_specialist = "general_practice"
        
        for specialist, count in specialist_count.items():
            if count > max_count:
                max_count = count
                recommended_specialist = specialist
        
        specialist_names = {
            "respiratory": "Pulmonologist",
            "cardiology": "Cardiologist",
            "gastroenterology": "Gastroenterologist",
            "neurology": "Neurologist",
            "endocrinology": "Endocrinologist",
            "psychiatry": "Psychiatrist",
            "ophthalmology": "Ophthalmologist",
            "otolaryngology": "ENT Specialist",
            "rheumatology": "Rheumatologist",
            "general_practice": "General Practitioner"
        }
        
        return specialist_names.get(recommended_specialist)

# Example usage
health_assessment = HealthAssessment()