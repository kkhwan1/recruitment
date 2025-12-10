from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.database.repositories import JobRepository, AnalysisRepository
from backend.app.schemas import JobResponse, DashboardStats

router = APIRouter()
job_repo = JobRepository()
analysis_repo = AnalysisRepository()

@router.get("/jobs", response_model=List[JobResponse])
def get_jobs(
    limit: int = 50,
    skip: int = 0,
    risk_level: Optional[str] = None
):
    """
    Get list of jobs.
    TODO: Add more complex filtering in repository if needed.
    Currently returning list of high risk jobs if risk_level='High' or similar logic.
    For now, we will return high risk jobs if requested, otherwise recent jobs.
    """
    if risk_level == "고위험":
        jobs = analysis_repo.get_high_risk_jobs(limit=limit)
    else:
        # Default to getting recent jobs via raw SQL if get_all_jobs doesn't exist
        # We need to extend repository for simple pagination if not exists
        # Falling back to get_recent_reports logic or simple query
        with job_repo.db as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs ORDER BY crawled_at DESC LIMIT ? OFFSET ?", (limit, skip))
            jobs = [dict(row) for row in cursor.fetchall()]

    # Hydrate with risk analysis if possible (this is N+1, optimize later with JOINs)
    results = []
    with analysis_repo.db as conn:
        for job in jobs:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM risk_analysis WHERE job_id = ?", (job['id'],))
            risk_row = cursor.fetchone()
            risk_data = None
            if risk_row:
                risk_data = dict(risk_row)
                import json
                # Safe load JSON
                try:
                    risk_data['risk_factors'] = json.loads(risk_data['risk_factors'])
                except:
                    risk_data['risk_factors'] = []
                try:
                    risk_data['recommendations'] = json.loads(risk_data['recommendations'])
                except:
                    risk_data['recommendations'] = []
            
            job['risk_analysis'] = risk_data
            results.append(job)

    return results

@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats():
    import datetime
    today = datetime.date.today().isoformat()
    
    # Simple direct query for stats
    with job_repo.db as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE crawled_date = ?", (today,))
        total_today = cursor.fetchone()['count']
        
    risk_stats = analysis_repo.get_risk_statistics()
    high_risk = risk_stats.get('고위험', 0)
    
    return {
        "total_today": total_today,
        "high_risk_count": high_risk,
        "risk_distribution": risk_stats
    }
