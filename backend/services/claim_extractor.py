import os
import json
import google.generativeai as genai
from backend.models.schemas import ExtractedClaim

# Using recommended models, gemini-1.5-pro or 2.0-pro depending on availability.
MODEL_NAME = "gemini-1.5-pro" 

def extract_claims_from_text(text: str) -> list[ExtractedClaim]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("Warning: Missing Gemini API Key. Returning mock claims.")
        return [
            ExtractedClaim(claim_text="The Earth revolves around the Sun.", claim_type="Fact", entities=["Earth", "Sun"]),
            ExtractedClaim(claim_text="In 2025, over 99.8% of all Fortune 500 CEOs were replaced by artificial intelligence agents.", claim_type="Statistic", entities=["Fortune 500", "AI"], year="2025")
        ]
        
    genai.configure(api_key=api_key)
    prompt = f"""
    You are an expert data extractor and fact checker. 
    Analyze the following text and extract all quantitative claims, statistics, percentages, 
    dates, financial numbers, technical metrics, market size claims, rankings, and measurable statements.
    
    Return the result strictly as a JSON array of objects. Each object should have:
    - claim_text (string): The exact quote or tightly paraphrased claim.
    - claim_type (string): e.g., "Statistic", "Percentage", "Financial", "Market Size", "Ranking".
    - entities (array of strings): Key entities or companies involved.
    - value (string): The main numerical value.
    - year (string): The relevant year if mentioned, else null.
    
    If no claims are found, return [].
    
    TEXT:
    {text}
    """
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        data = json.loads(response.text)
        claims = [ExtractedClaim(**item) for item in data]
        return claims
    except Exception as e:
        print(f"Error extracting claims: {e}")
        return []
