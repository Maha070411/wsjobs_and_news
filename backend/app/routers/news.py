from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import News
from ..schemas import NewsResponse

router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/")
def get_news(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(News)
    total = query.count()
    items = query.order_by(News.published_date.desc()).offset((page - 1) * limit).limit(limit).all()
    
    serialized_items = [NewsResponse.model_validate(item) for item in items]
    
    return {
        "items": serialized_items,
        "total": total,
        "page": page,
        "pages": (total // limit) + (1 if total % limit > 0 else 0)
    }

@router.get("/{news_id}", response_model=NewsResponse)
def get_news_detail(news_id: int, db: Session = Depends(get_db)):
    news_item = db.query(News).filter(News.id == news_id).first()
    if not news_item:
        raise HTTPException(status_code=404, detail="News not found")
    return news_item
