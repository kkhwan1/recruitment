from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class RiskAnalysisBase(BaseModel):
    base_score: float
    combo_multiplier: float
    final_score: float
    risk_level: str
    risk_factors: List[str]
    recommendations: List[str]
    analysis_summary: str

class JobBase(BaseModel):
    title: str
    company: str
    location: str
    salary: str
    conditions: str
    recruit_summary: str
    detail: str
    url: str
    posted_date: str
    source_site: str
    search_keyword: str
    crawled_at: datetime
    crawled_date: str
    crawled_weekday: int
    crawled_hour: int

class JobResponse(JobBase):
    id: int
    risk_analysis: Optional[RiskAnalysisBase] = None

class CrawlRequest(BaseModel):
    site: str
    keyword: Optional[str] = None
    max_jobs: int = 10

class DashboardStats(BaseModel):
    total_today: int
    high_risk_count: int
    risk_distribution: Dict[str, int]
