"""
리포트 API 엔드포인트
일일 리포트 조회 및 생성
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import date
from backend.database.repositories import JobRepository, AnalysisRepository, ReportRepository
import json

router = APIRouter()
job_repo = JobRepository()
analysis_repo = AnalysisRepository()
report_repo = ReportRepository()


@router.get("/reports/daily")
def get_daily_reports(limit: int = 30, skip: int = 0) -> List[Dict[str, Any]]:
    """
    일일 리포트 목록 조회

    Args:
        limit: 조회할 리포트 개수 (기본값: 30)
        skip: 건너뛸 리포트 개수 (기본값: 0)

    Returns:
        [{
            "id": int,
            "report_date": str,
            "detection_target": str,
            "total_jobs": int,
            "high_risk_count": int,
            "medium_risk_count": int,
            "low_risk_count": int,
            "main_keywords": List[str],
            "recommended_action": str
        }]
    """
    with job_repo.db as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                report_date,
                detection_target,
                total_jobs,
                high_risk_count,
                medium_risk_count,
                low_risk_count,
                main_keywords,
                recommended_action
            FROM daily_reports
            ORDER BY report_date DESC
            LIMIT ? OFFSET ?
        """, (limit, skip))

        reports = []
        for row in cursor.fetchall():
            report_dict = dict(row)
            try:
                report_dict['main_keywords'] = json.loads(report_dict['main_keywords'])
            except:
                report_dict['main_keywords'] = []
            reports.append(report_dict)

    return reports


@router.get("/reports/daily/{report_date}")
def get_daily_report(report_date: str) -> Dict[str, Any]:
    """
    특정 날짜 일일 리포트 조회 (상세)

    Args:
        report_date: 리포트 날짜 (YYYY-MM-DD)

    Returns:
        {
            "id": int,
            "report_date": str,
            "detection_target": str,
            "total_jobs": int,
            "high_risk_count": int,
            "medium_risk_count": int,
            "low_risk_count": int,
            "main_keywords": List[str],
            "recommended_action": str,
            "high_risk_jobs": List[Dict]
        }
    """
    with job_repo.db as conn:
        cursor = conn.cursor()

        # 일일 리포트 조회
        cursor.execute("""
            SELECT
                id,
                report_date,
                detection_target,
                total_jobs,
                high_risk_count,
                medium_risk_count,
                low_risk_count,
                main_keywords,
                recommended_action,
                high_risk_jobs
            FROM daily_reports
            WHERE report_date = ?
        """, (report_date,))

        report_row = cursor.fetchone()
        if not report_row:
            raise HTTPException(status_code=404, detail=f"Report not found for date: {report_date}")

        report_dict = dict(report_row)
        try:
            report_dict['main_keywords'] = json.loads(report_dict['main_keywords'])
        except:
            report_dict['main_keywords'] = []

        try:
            report_dict['high_risk_jobs'] = json.loads(report_dict['high_risk_jobs'])
        except:
            report_dict['high_risk_jobs'] = []

    return report_dict


@router.get("/reports/summary")
def get_reports_summary() -> Dict[str, Any]:
    """
    리포트 요약 통계

    Returns:
        {
            "total_reports": int,               # 전체 리포트 수
            "latest_report_date": str,          # 최신 리포트 날짜
            "avg_high_risk_count": float,       # 평균 고위험 공고 수
            "total_jobs_analyzed": int          # 분석된 전체 공고 수
        }
    """
    with job_repo.db as conn:
        cursor = conn.cursor()

        # 전체 리포트 수
        cursor.execute("SELECT COUNT(*) as total FROM daily_reports")
        total_reports = cursor.fetchone()['total']

        # 최신 리포트 날짜
        cursor.execute("SELECT MAX(report_date) as latest FROM daily_reports")
        latest_result = cursor.fetchone()
        latest_report_date = latest_result['latest'] if latest_result['latest'] else None

        # 평균 고위험 공고 수
        cursor.execute("SELECT AVG(high_risk_count) as avg_high_risk FROM daily_reports")
        avg_result = cursor.fetchone()
        avg_high_risk_count = round(avg_result['avg_high_risk'], 2) if avg_result['avg_high_risk'] else 0

        # 분석된 전체 공고 수
        cursor.execute("SELECT SUM(total_jobs) as total_analyzed FROM daily_reports")
        total_result = cursor.fetchone()
        total_jobs_analyzed = total_result['total_analyzed'] if total_result['total_analyzed'] else 0

    return {
        "total_reports": total_reports,
        "latest_report_date": latest_report_date,
        "avg_high_risk_count": avg_high_risk_count,
        "total_jobs_analyzed": total_jobs_analyzed
    }
