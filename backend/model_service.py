# model_service.py

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

class MedicalModel:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model     = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        # Tell the pipeline to run on CPU by using device = -1
        self.pipe = pipeline(
            "text2text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=-1,                # -1 = CPU instead of GPU
            max_length=512,
            do_sample=True,
            top_p=0.9,
            temperature=0.7,
        )

    def generate_response(self, message: str) -> str:
        prompt = (
            #System role
                "You are an empathetic, highly knowledgeable medical assistant.\n"
                "When a patient describes their symptoms, you MUST:\n"
                "  1. List up to 3 most likely diseases, ordered by probability.\n"
                "     • For each, give a 1–2 sentence rationale.\n"
                "  2. For each predicted disease, provide:\n"
                "     - A brief (one‑sentence) description.\n"
                "     - Two key next‑step recommendations (e.g., tests, lifestyle changes).\n"
                "     - A recommended specialist (doctor type) and why.\n"
                "  3. If the patient later asks “Tell me more about X,” give:\n"
                "     – Detailed overview (cause, pathophysiology).\n"
                "     – Common symptoms and red flags.\n"
                "     – How it’s diagnosed.\n"
                "     – Standard treatments and precautions.\n"
                "Keep your tone warm, clear, and concise. Always answer in English.\n"
                "\n"
                "# Example 1\n"
                "Patient: I have a high fever, sore throat, and swollen glands in my neck.\n"
                "Assistant:\n"
                "1. Streptococcal Pharyngitis (Strep Throat) – Likely because fever + sore throat + tender lymph nodes suggest bacterial infection.\n"
                "   • Description: A bacterial infection of the throat caused by Streptococcus pyogenes.\n"
                "   • Next steps: Rapid antigen detection test; keep well‑hydrated and rest.\n"
                "   • Specialist: Otolaryngologist (ENT), to confirm with throat culture and manage complications.\n"
                "2. Infectious Mononucleosis – Fever and lymph node swelling could also signal EBV infection.\n"
                "   • Description: A viral infection often causing fatigue and enlarged spleen.\n"
                "   • Next steps: Monospot antibody test; avoid contact sports (risk to spleen).\n"
                "   • Specialist: Infectious disease physician, for antiviral guidance and monitoring.\n"
                "\n"
                "# Example 2 (deep dive)\n"
                "Patient: Tell me more about Streptococcal Pharyngitis.\n"
                "Assistant:\n"
                "Streptococcal Pharyngitis is caused by the group A Streptococcus bacteria… [detailed overview, symptoms, diagnostics, treatment, precautions].\n"
                "\n"
                # Actual user message
                f"Patient: {message}\n"
                "Assistant:"
        )
        out = self.pipe(prompt, max_length=512, num_return_sequences=1)[0]["generated_text"]
        return out.replace(prompt, "").strip()
