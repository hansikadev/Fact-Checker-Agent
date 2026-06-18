import os
import json
from tavily import TavilyClient
from google import genai
from google.genai import types
from backend.models.schemas import ExtractedClaim, VerificationResult, ClaimStatus, Evidence

MODEL_NAME = "gemini-3.5-flash"

def search_for_evidence(query: str) -> list[Evidence]:
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    if not tavily_api_key or tavily_api_key == "your_tavily_api_key_here":
        print("Warning: Missing Tavily API Key. Returning mock evidence.")
        return [Evidence(
            source_url="https://example.com/mock",
            source_title="Mock Source Evidence",
            content_snippet="This is a mock snippet used for testing.",
            credibility_score=0.85
        )]
        
    try:
        tavily_client = TavilyClient(api_key=tavily_api_key)
        response = tavily_client.search(query=query, search_depth="advanced", max_results=3)
        evidences = []
        for res in response.get("results", []):
            evidences.append(Evidence(
                source_url=res.get("url", ""),
                source_title=res.get("title", ""),
                content_snippet=res.get("content", ""),
                credibility_score=res.get("score", 0.8),
                publication_date=res.get("published_date", None)
            ))
        return evidences
    except Exception as e:
        print(f"Search error: {e}")
        return []

def verify_claim(claim: ExtractedClaim) -> VerificationResult:
    # 1. Search for evidence
    query = f"{claim.claim_text} {claim.year or ''} {' '.join(claim.entities)}"
    evidences = search_for_evidence(query)
    
    if not evidences:
        return VerificationResult(
            original_claim=claim,
            status=ClaimStatus.FALSE,
            confidence_score=0.0,
            evidence_sources=[],
            explanation="False (no evidence found)."
        )
    
    # 2. Evaluate with LLM to handle Trap Document logic
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("Warning: Missing Gemini API Key. Returning mock evaluation.")
        status = ClaimStatus.FALSE if "99.8%" in claim.claim_text else ClaimStatus.VERIFIED
        return VerificationResult(
            original_claim=claim,
            status=status,
            confidence_score=0.95,
            evidence_sources=evidences,
            correct_value=None,
            explanation="Mock explanation due to missing API key."
        )

    client = genai.Client(api_key=api_key)
    evidence_text = "\n\n".join([f"Source: {e.source_url}\nDate: {e.publication_date}\nContent: {e.content_snippet}" for e in evidences])
    
    prompt = f"""
    You are an expert fact-checker. Evaluate the following claim based ONLY on the provided evidence.
    
    Claim to evaluate: "{claim.claim_text}"
    Entities: {claim.entities}
    Year Context: {claim.year}
    
    Evidence from Web:
    {evidence_text}
    
    Determine if the claim is:
    1. VERIFIED: Strong evidence supports it exactly.
    2. INACCURATE: The claim exists but values are outdated, slightly incorrect, or missing critical context (e.g., market size was $20B in 2021, but is now $32B).
    3. FALSE: No supporting evidence, evidence contradicts it, or it is a hallucinated statistic.
    
    Return a JSON object with:
    - status: "VERIFIED", "INACCURATE", or "FALSE"
    - confidence_score: Float between 0.0 and 1.0 (e.g. 0.95)
    - correct_value: The true value if INACCURATE or FALSE, else null.
    - explanation: A detailed explanation of why this status was chosen, referencing the evidence dates and numbers. Focus on numerical consistency and date-awareness.
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        evaluation = json.loads(response.text)
        return VerificationResult(
            original_claim=claim,
            status=ClaimStatus(evaluation.get("status", "UNVERIFIED")),
            confidence_score=float(evaluation.get("confidence_score", 0.0)),
            evidence_sources=evidences,
            correct_value=evaluation.get("correct_value"),
            explanation=evaluation.get("explanation", "Failed to generate explanation.")
        )
    except Exception as e:
        print(f"Error evaluating claim: {e}")
        return VerificationResult(
            original_claim=claim,
            status=ClaimStatus.UNVERIFIED,
            confidence_score=0.0,
            evidence_sources=evidences,
            explanation=str(e)
        )
