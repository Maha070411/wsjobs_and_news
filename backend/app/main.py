from fastapi import FastAPI, Depends, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import Job, Company, News
from .routers import auth, jobs, news, user, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="JobHub API", description="Cloud-Based Scalable Web Scraper with Trend Dashboard", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(news.router)
app.include_router(user.router)
app.include_router(admin.router)

@app.get("/api/stats/summary")
def get_app_summary(db: Session = Depends(get_db)):
    return {
        "jobs": db.query(Job).count(),
        "companies": db.query(Company).count(),
        "news": db.query(News).count()
    }

@app.get("/api/companies/top")
def get_top_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    return [{"name": c.name, "id": c.id, "industry": c.industry} for c in companies]

@app.get("/")
def read_root():
    return {"message": "Welcome to JobHub API"}

@app.get("/swagger")
def read_swagger():
    return RedirectResponse(url="/docs")
