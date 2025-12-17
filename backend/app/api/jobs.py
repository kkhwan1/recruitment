from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from backend.database.repositories import JobRepository, AnalysisRepository
from backend.app.schemas import JobResponse
import json

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
    공고 목록 조회 (JOIN으로 N+1 쿼리 해결)

    Args:
        limit: 조회할 공고 개수 (기본값: 50)
        skip: 건너뛸 공고 개수 (기본값: 0)
        risk_level: 위험도 필터 (고위험, 중위험, 저위험)

    Returns:
        공고 목록 (위험도 분석 포함)
    """
    with job_repo.db as conn:
        cursor = conn.cursor()

        # JOIN으로 한번에 조회 (N+1 쿼리 해결)
        if risk_level:
            cursor.execute("""
                SELECT
                    j.*,
                    r.id as risk_id,
                    r.base_score,
                    r.combo_multiplier,
                    r.final_score,
                    r.risk_level,
                    r.risk_factors,
                    r.recommendations,
                    r.analysis_summary
                FROM jobs j
                LEFT JOIN risk_analysis r ON j.id = r.job_id
                WHERE r.risk_level = ?
                ORDER BY j.crawled_at DESC
                LIMIT ? OFFSET ?
            """, (risk_level, limit, skip))
        else:
            cursor.execute("""
                SELECT
                    j.*,
                    r.id as risk_id,
                    r.base_score,
                    r.combo_multiplier,
                    r.final_score,
                    r.risk_level,
                    r.risk_factors,
                    r.recommendations,
                    r.analysis_summary
                FROM jobs j
                LEFT JOIN risk_analysis r ON j.id = r.job_id
                ORDER BY j.crawled_at DESC
                LIMIT ? OFFSET ?
            """, (limit, skip))

        results = []
        for row in cursor.fetchall():
            job_dict = dict(row)

            # risk_analysis 분리
            risk_data = None
            if job_dict.get('risk_id'):
                risk_data = {
                    'base_score': job_dict.pop('base_score'),
                    'combo_multiplier': job_dict.pop('combo_multiplier'),
                    'final_score': job_dict.pop('final_score'),
                    'risk_level': job_dict.pop('risk_level'),
                    'risk_factors': json.loads(job_dict.pop('risk_factors', '[]')),
                    'recommendations': json.loads(job_dict.pop('recommendations', '[]')),
                    'analysis_summary': job_dict.pop('analysis_summary', '')
                }
                job_dict.pop('risk_id')

            job_dict['risk_analysis'] = risk_data
            results.append(job_dict)

    return results

@router.get("/jobs/{job_id}")
def get_job_detail(job_id: int) -> Dict[str, Any]:
    """
    공고 상세 조회 (키워드 매칭, 패턴 매칭 포함)

    Args:
        job_id: 공고 ID

    Returns:
        {
            "job": {...},                    # 공고 기본 정보
            "risk_analysis": {...},          # 위험도 분석
            "keyword_matches": [...],        # 키워드 매칭 결과
            "pattern_matches": [...]         # 패턴 매칭 결과
        }
    """
    with job_repo.db as conn:
        cursor = conn.cursor()

        # 1. 공고 기본 정보 + 위험도 분석 (JOIN으로 한번에)
        cursor.execute("""
            SELECT
                j.*,
                r.base_score,
                r.combo_multiplier,
                r.final_score,
                r.risk_level,
                r.risk_factors,
                r.recommendations,
                r.analysis_summary
            FROM jobs j
            LEFT JOIN risk_analysis r ON j.id = r.job_id
            WHERE j.id = ?
        """, (job_id,))

        job_row = cursor.fetchone()
        if not job_row:
            raise HTTPException(status_code=404, detail="Job not found")

        job_dict = dict(job_row)

        # risk_analysis 분리
        risk_data = None
        if job_dict.get('base_score') is not None:
            risk_data = {
                'base_score': job_dict.pop('base_score'),
                'combo_multiplier': job_dict.pop('combo_multiplier'),
                'final_score': job_dict.pop('final_score'),
                'risk_level': job_dict.pop('risk_level'),
                'risk_factors': json.loads(job_dict.pop('risk_factors', '[]')),
                'recommendations': json.loads(job_dict.pop('recommendations', '[]')),
                'analysis_summary': job_dict.pop('analysis_summary', '')
            }
        else:
            # 필드 제거
            for field in ['base_score', 'combo_multiplier', 'final_score', 'risk_level', 'risk_factors', 'recommendations', 'analysis_summary']:
                job_dict.pop(field, None)

        # 2. 키워드 매칭 결과
        cursor.execute("""
            SELECT tier, keyword, category, weight, match_count
            FROM keyword_matches
            WHERE job_id = ?
            ORDER BY tier, weight DESC
        """, (job_id,))
        keyword_matches = [dict(row) for row in cursor.fetchall()]

        # 3. 패턴 매칭 결과
        cursor.execute("""
            SELECT pattern_name, keywords, weight, description
            FROM pattern_matches
            WHERE job_id = ?
            ORDER BY weight DESC
        """, (job_id,))
        pattern_matches = []
        for row in cursor.fetchall():
            pattern_dict = dict(row)
            pattern_dict['keywords'] = json.loads(pattern_dict['keywords'])
            pattern_matches.append(pattern_dict)

    return {
        "job": job_dict,
        "risk_analysis": risk_data,
        "keyword_matches": keyword_matches,
        "pattern_matches": pattern_matches
    }
