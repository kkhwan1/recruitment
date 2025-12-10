"""
데이터베이스 모델 정의
Python dataclasses로 데이터 구조 표현
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Job:
    """채용 공고 기본 정보"""
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
    crawled_weekday: int  # 0=월요일, 6=일요일
    crawled_hour: int     # 0-23
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class KeywordMatch:
    """키워드 매칭 결과"""
    job_id: int
    tier: int  # 1, 2, 3
    keyword: str
    category: str
    weight: int
    match_count: int
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class PatternMatch:
    """복합 패턴 매칭 결과"""
    job_id: int
    pattern_id: str
    pattern_name: str
    keywords: List[str]
    weight: int
    description: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class RiskAnalysis:
    """위험도 분석 결과"""
    job_id: int
    base_score: int
    combo_multiplier: float
    final_score: int
    risk_level: str  # 고위험, 중위험, 저위험
    risk_factors: List[str]
    recommendations: List[str]
    analysis_summary: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class DailyReport:
    """일일 리포트"""
    report_date: str
    detection_target: str
    total_jobs: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    main_keywords: List[str]
    recommended_action: str
    high_risk_jobs: List[dict]
    id: Optional[int] = None
    created_at: Optional[datetime] = None
