from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ClaimStatus(str, Enum):
    VERIFIED = "VERIFIED"
    INACCURATE = "INACCURATE"
    FALSE = "FALSE"
    UNVERIFIED = "UNVERIFIED" # Initial state

class ClaimType(str, Enum):
    STATISTIC = "Statistic"
    PERCENTAGE = "Percentage"
    DATE = "Date"
    FINANCIAL = "Financial"
    TECHNICAL_METRIC = "Technical Metric"
    MARKET_SIZE = "Market Size"
    RANKING = "Ranking"
    QUANTITATIVE = "Quantitative"

class ExtractedClaim(BaseModel):
    claim_text: str = Field(..., description="The exact text of the claim extracted from the document.")
    claim_type: ClaimType = Field(..., description="The type of claim.")
    entities: List[str] = Field(default_factory=list, description="Key entities mentioned in the claim.")
    value: Optional[str] = Field(None, description="The quantitative value in the claim, if any.")
    year: Optional[str] = Field(None, description="The year or time period associated with the claim.")

class Evidence(BaseModel):
    source_url: str = Field(..., description="URL of the source.")
    source_title: str = Field(..., description="Title of the source.")
    content_snippet: str = Field(..., description="Relevant snippet from the source supporting or refuting the claim.")
    credibility_score: float = Field(0.0, description="A score from 0.0 to 1.0 indicating source credibility.")
    publication_date: Optional[str] = Field(None, description="Date the source was published.")

class VerificationResult(BaseModel):
    original_claim: ExtractedClaim
    status: ClaimStatus = Field(..., description="The verification status.")
    confidence_score: float = Field(..., description="Confidence in the verification result from 0.0 to 1.0.")
    evidence_sources: List[Evidence] = Field(default_factory=list, description="List of evidence gathered.")
    correct_value: Optional[str] = Field(None, description="The correct value if the original claim was INACCURATE or FALSE.")
    explanation: str = Field(..., description="Explanation of why this status was assigned.")

class DocumentReport(BaseModel):
    job_id: str
    filename: str
    total_claims: int
    verified_count: int
    inaccurate_count: int
    false_count: int
    claims: List[VerificationResult]

class UploadResponse(BaseModel):
    job_id: str
    message: str
    status: str
