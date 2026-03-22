from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional
from ..database import get_db
from ..models import Job, Company
from ..schemas import JobResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("/")
def get_jobs(
    q: Optional[str] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
    experience: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Job).options(joinedload(Job.company))
    
    if q:
        query = query.filter(or_(Job.title.ilike(f"%{q}%"), Job.description.ilike(f"%{q}%")))
    if company:
        query = query.join(Company).filter(Company.name.ilike(f"%{company}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if experience:
        query = query.filter(Job.experience_level.ilike(f"%{experience}%"))
        
    total = query.count()
    items = query.order_by(Job.posted_date.desc()).offset((page - 1) * limit).limit(limit).all()
    
    # Convert to Pydantic models for proper serialization
    serialized_items = [JobResponse.model_validate(item) for item in items]
    
    return {
        "items": serialized_items,
        "total": total,
        "page": page,
        "pages": (total // limit) + (1 if total % limit > 0 else 0)
    }

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).options(joinedload(Job.company)).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/company/{company_id}", response_model=List[JobResponse])
def get_company_jobs(company_id: int, db: Session = Depends(get_db)):
    return db.query(Job).options(joinedload(Job.company)).filter(Job.company_id == company_id).all()

