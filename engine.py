import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class VeraEngine:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def compose(self, trigger: dict, merchant: dict, category: dict, customer: dict = None) -> dict:
        """
        Generates a message based on the rubric: 
        1. Specificity (2+ numbers) 
        2. Engagement (<160 chars) 
        3. Decision Quality (High-impact)
        """
        
        prompt = f"""
        You are Vera, an AI growth assistant for Magicpin merchants.
        
        MERCHANT CONTEXT: {merchant}
        CATEGORY CONTEXT: {category}
        TRIGGER: {trigger}
        
        STRICT RULES:
        1. SPECIFICITY: You MUST include at least two specific numbers (percentages, currency, or counts) from the context.
        2. LENGTH: The 'message' must be under 160 characters.
        3. CTA: Provide a clear, low-friction yes/no CTA.
        4. RATIONALE: Explain why this trigger was chosen for this specific merchant.

        Output ONLY a JSON object:
        {{
            "message": "your specific growth message",
            "cta": "Single action question?",
            "rationale": "reasoning"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Basic cleaning of the LLM response
            raw_text = response.text.strip().replace('```json', '').replace('```', '')
            import json
            return json.loads(raw_text)
        except Exception as e:
            return {
                "message": f"Hey! I noticed a trend in {category.get('name', 'your area')}. Want to see the data?",
                "cta": "Show me?",
                "rationale": "Fallback due to processing error."
            }