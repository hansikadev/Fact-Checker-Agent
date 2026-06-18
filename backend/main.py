import uuid
import traceback
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base, get_db
from backend.models import domain, schemas
from backend.services.pdf_service import extract_text_from_pdf
from backend.services.claim_extractor import extract_claims_from_text
from backend.services.verifier import verify_claim

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fact-Check Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_document_background(job_id: str, file_bytes: bytes):
    db: Session = next(get_db())
    try:
        # 1. Extract text
        text = extract_text_from_pdf(file_bytes)
        
        # 2. Extract claims
        claims = extract_claims_from_text(text)
        
        # Save claims to DB
        for c in claims:
            db_claim = domain.ClaimRecord(
                job_id=job_id,
                claim_text=c.claim_text,
                claim_type=c.claim_type.value,
                entities=c.entities,
                value=c.value,
                year=c.year
            )
            db.add(db_claim)
        db.commit()
        
        # 3. Verify each claim
        db_claims = db.query(domain.ClaimRecord).filter(domain.ClaimRecord.job_id == job_id).all()
        for idx, db_claim in enumerate(db_claims):
            extracted_claim = claims[idx]
            result = verify_claim(extracted_claim)
            
            # Update DB with result
            db_claim.status = result.status.value
            db_claim.confidence_score = result.confidence_score
            db_claim.correct_value = result.correct_value
            db_claim.explanation = result.explanation
            db_claim.evidence_sources = [e.dict() for e in result.evidence_sources]
            db.commit()
        
        # 4. Update Job status
        job = db.query(domain.Job).filter(domain.Job.id == job_id).first()
        job.status = "COMPLETED"
        db.commit()
        
    except Exception as e:
        print(f"Background task failed: {e}")
        traceback.print_exc()
        job = db.query(domain.Job).filter(domain.Job.id == job_id).first()
        if job:
            job.status = "FAILED"
            db.commit()
    finally:
        db.close()

@app.post("/upload", response_model=schemas.UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    job_id = str(uuid.uuid4())
    file_bytes = await file.read()
    
    # Create job in DB
    new_job = domain.Job(id=job_id, filename=file.filename)
    db.add(new_job)
    db.commit()
    
    # Start background processing
    background_tasks.add_task(process_document_background, job_id, file_bytes)
    
    return schemas.UploadResponse(
        job_id=job_id,
        message="Document uploaded and processing started.",
        status="PROCESSING"
    )

@app.get("/status/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(domain.Job).filter(domain.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    total_claims = db.query(domain.ClaimRecord).filter(domain.ClaimRecord.job_id == job_id).count()
    verified_claims = db.query(domain.ClaimRecord).filter(domain.ClaimRecord.job_id == job_id, domain.ClaimRecord.status != 'UNVERIFIED').count()
    
    return {
        "job_id": job.id,
        "filename": job.filename,
        "status": job.status,
        "progress": f"{verified_claims}/{total_claims}" if total_claims > 0 else "Extracting claims..."
    }

@app.get("/report/{job_id}", response_model=schemas.DocumentReport)
def get_report(job_id: str, db: Session = Depends(get_db)):
    job = db.query(domain.Job).filter(domain.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    db_claims = db.query(domain.ClaimRecord).filter(domain.ClaimRecord.job_id == job_id).all()
    
    claims_list = []
    verified_count = 0
    inaccurate_count = 0
    false_count = 0
    
    for c in db_claims:
        if c.status == "VERIFIED": verified_count += 1
        elif c.status == "INACCURATE": inaccurate_count += 1
        elif c.status == "FALSE": false_count += 1
        
        original = schemas.ExtractedClaim(
            claim_text=c.claim_text,
            claim_type=c.claim_type,
            entities=c.entities or [],
            value=c.value,
            year=c.year
        )
        evidences = [schemas.Evidence(**e) for e in (c.evidence_sources or [])]
        
        claims_list.append(schemas.VerificationResult(
            original_claim=original,
            status=c.status,
            confidence_score=c.confidence_score or 0.0,
            correct_value=c.correct_value,
            explanation=c.explanation or "",
            evidence_sources=evidences
        ))
        
    return schemas.DocumentReport(
        job_id=job.id,
        filename=job.filename,
        total_claims=len(claims_list),
        verified_count=verified_count,
        inaccurate_count=inaccurate_count,
        false_count=false_count,
        claims=claims_list
    )
