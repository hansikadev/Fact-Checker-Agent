from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="PROCESSING") # PROCESSING, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Store the final report summary as JSON
    report_data = Column(JSON, nullable=True)

class ClaimRecord(Base):
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id"))
    
    # Extracted Claim details
    claim_text = Column(Text, nullable=False)
    claim_type = Column(String, nullable=False)
    entities = Column(JSON, nullable=True)
    value = Column(String, nullable=True)
    year = Column(String, nullable=True)
    
    # Verification Result
    status = Column(String, default="UNVERIFIED")
    confidence_score = Column(Float, nullable=True)
    correct_value = Column(String, nullable=True)
    explanation = Column(Text, nullable=True)
    
    # Evidence stored as JSON array
    evidence_sources = Column(JSON, nullable=True)
    
    job = relationship("Job")
