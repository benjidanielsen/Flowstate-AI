from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from backend.database import get_db
from backend.models import APIUsage, APIPerformance
from backend.schemas import APIUsageSchema, APIPerformanceSchema, AnalyticsSummary

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/usage", response_model=List[APIUsageSchema])
async def get_api_usage(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Retrieve API usage logs between start_date and end_date"""
    query = db.query(APIUsage)
    if start_date:
        query = query.filter(APIUsage.timestamp >= start_date)
    if end_date:
        query = query.filter(APIUsage.timestamp <= end_date)
    results = query.order_by(APIUsage.timestamp.desc()).all()
    return results

@router.get("/performance", response_model=List[APIPerformanceSchema])
async def get_api_performance(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Retrieve API performance metrics between start_date and end_date"""
    query = db.query(APIPerformance)
    if start_date:
        query = query.filter(APIPerformance.timestamp >= start_date)
    if end_date:
        query = query.filter(APIPerformance.timestamp <= end_date)
    results = query.order_by(APIPerformance.timestamp.desc()).all()
    return results

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    days: int = 7,
    db: Session = Depends(get_db),
):
    """Provide summary analytics for the past `days` days"""
    since = datetime.utcnow() - timedelta(days=days)

    total_calls = db.query(APIUsage).filter(APIUsage.timestamp >= since).count()
    avg_response_time = db.query(APIPerformance).filter(APIPerformance.timestamp >= since).with_entities(
        APIPerformance.response_time
    ).all()
    avg_response_time_value = 0
    if avg_response_time:
        avg_response_time_value = sum(r[0] for r in avg_response_time) / len(avg_response_time)

    error_count = db.query(APIUsage).filter(
        APIUsage.timestamp >= since,
        APIUsage.status_code >= 400
    ).count()

    return AnalyticsSummary(
        total_calls=total_calls,
        avg_response_time=avg_response_time_value,
        error_count=error_count,
        period_days=days
    )
