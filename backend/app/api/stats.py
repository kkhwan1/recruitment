"""
통계 API 엔드포인트
대시보드 통합 통계 제공
"""
from fastapi import APIRouter
from typing import Dict, List, Any
from datetime import date
from backend.database.repositories import JobRepository, AnalysisRepository

router = APIRouter()
job_repo = JobRepository()
analysis_repo = AnalysisRepository()


@router.get("/stats/overview")
def get_stats_overview() -> Dict[str, Any]:
    """
    종합 통계 조회

    Returns:
        {
            "total_jobs": int,              # 전체 공고 수
            "high_risk_count": int,         # 고위험 공고 수
            "medium_risk_count": int,       # 중위험 공고 수
            "low_risk_count": int,          # 저위험 공고 수
            "top_sources": List[Dict],      # 상위 수집 사이트
            "avg_risk_score": float         # 평균 위험도 점수
        }
    """
    with job_repo.db as conn:
        cursor = conn.cursor()

        # 전체 공고 수
        cursor.execute("SELECT COUNT(*) as total FROM jobs")
        total_jobs = cursor.fetchone()['total']

        # 위험도별 집계
        cursor.execute("""
            SELECT
                risk_level,
                COUNT(*) as count
            FROM risk_analysis
            GROUP BY risk_level
        """)
        risk_counts = {row['risk_level']: row['count'] for row in cursor.fetchall()}

        # 상위 수집 사이트
        cursor.execute("""
            SELECT
                source_site,
                COUNT(*) as count
            FROM jobs
            GROUP BY source_site
            ORDER BY count DESC
            LIMIT 5
        """)
        top_sources = [{"site": row['source_site'], "count": row['count']} for row in cursor.fetchall()]

        # 평균 위험도 점수
        cursor.execute("SELECT AVG(final_score) as avg_score FROM risk_analysis")
        avg_result = cursor.fetchone()
        avg_risk_score = round(avg_result['avg_score'], 2) if avg_result['avg_score'] else 0

    return {
        "total_jobs": total_jobs,
        "high_risk_count": risk_counts.get('고위험', 0),
        "medium_risk_count": risk_counts.get('중위험', 0),
        "low_risk_count": risk_counts.get('저위험', 0),
        "top_sources": top_sources,
        "avg_risk_score": avg_risk_score
    }


@router.get("/stats/trends")
def get_stats_trends(days: int = 7) -> List[Dict[str, Any]]:
    """
    일별 트렌드 조회

    Args:
        days: 조회할 일수 (기본값: 7, 최대: 30)

    Returns:
        [
            {
                "date": str,                # 날짜 (YYYY-MM-DD)
                "total_jobs": int,          # 해당 날짜 수집 공고 수
                "high_risk_count": int,     # 고위험 공고 수
                "medium_risk_count": int,   # 중위험 공고 수
                "low_risk_count": int       # 저위험 공고 수
            },
            ...
        ]
    """
    with job_repo.db as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                j.crawled_date as date,
                COUNT(j.id) as total_jobs,
                SUM(CASE WHEN r.risk_level = '고위험' THEN 1 ELSE 0 END) as high_risk_count,
                SUM(CASE WHEN r.risk_level = '중위험' THEN 1 ELSE 0 END) as medium_risk_count,
                SUM(CASE WHEN r.risk_level = '저위험' THEN 1 ELSE 0 END) as low_risk_count
            FROM jobs j
            LEFT JOIN risk_analysis r ON j.id = r.job_id
            WHERE j.crawled_date >= date('now', '-' || ? || ' days')
            GROUP BY j.crawled_date
            ORDER BY j.crawled_date DESC
        """, (days,))

        trends = []
        for row in cursor.fetchall():
            trends.append({
                "date": row['date'],
                "total_jobs": row['total_jobs'],
                "high_risk_count": row['high_risk_count'] or 0,
                "medium_risk_count": row['medium_risk_count'] or 0,
                "low_risk_count": row['low_risk_count'] or 0
            })

    return trends


@router.get("/stats/keywords")
def get_top_keywords(limit: int = 10) -> List[Dict[str, Any]]:
    """
    상위 키워드 조회

    Args:
        limit: 조회할 키워드 개수 (기본값: 10, 최대: 50)

    Returns:
        [
            {
                "keyword": str,         # 키워드
                "tier": int,            # Tier (1, 2, 3)
                "category": str,        # 카테고리
                "count": int,           # 탐지 횟수
                "avg_weight": float     # 평균 가중치
            },
            ...
        ]
    """
    with job_repo.db as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                keyword,
                tier,
                category,
                COUNT(*) as count,
                AVG(weight) as avg_weight
            FROM keyword_matches
            GROUP BY keyword, tier, category
            ORDER BY count DESC, avg_weight DESC
            LIMIT ?
        """, (limit,))

        keywords = []
        for row in cursor.fetchall():
            keywords.append({
                "keyword": row['keyword'],
                "tier": row['tier'],
                "category": row['category'],
                "count": row['count'],
                "avg_weight": round(row['avg_weight'], 2)
            })

    return keywords


@router.get("/stats/dashboard")
def get_dashboard_stats() -> Dict[str, Any]:
    """
    대시보드 통합 통계 조회

    Returns:
        {
            "total_jobs": int,              # 전체 공고 수
            "total_today": int,             # 오늘 수집된 공고 수
            "high_risk": int,               # 고위험 공고 수
            "medium_risk": int,             # 중위험 공고 수
            "low_risk": int,                # 저위험 공고 수
            "top_keywords": List[Dict],     # 상위 키워드 (keyword, count, tier)
            "recent_high_risk": List[Dict]  # 최근 고위험 공고 5건
        }
    """
    today = date.today().isoformat()

    with job_repo.db as conn:
        cursor = conn.cursor()

        # 전체 공고 수
        cursor.execute("SELECT COUNT(*) as count FROM jobs")
        total_jobs = cursor.fetchone()['count']

        # 오늘 수집된 공고 수
        cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE crawled_date = ?", (today,))
        total_today = cursor.fetchone()['count']

        # 위험도별 통계
        risk_stats = analysis_repo.get_risk_statistics()

        # 상위 키워드 (Tier별 상위 3개씩)
        cursor.execute("""
            SELECT tier, keyword, COUNT(*) as count
            FROM keyword_matches
            GROUP BY tier, keyword
            ORDER BY tier, count DESC
        """)
        all_keywords = cursor.fetchall()

        # Tier별로 상위 3개씩 선택
        top_keywords = []
        tier_counts = {1: 0, 2: 0, 3: 0}
        for row in all_keywords:
            tier = row['tier']
            if tier_counts[tier] < 3:
                top_keywords.append({
                    "tier": tier,
                    "keyword": row['keyword'],
                    "count": row['count']
                })
                tier_counts[tier] += 1
            if all(c >= 3 for c in tier_counts.values()):
                break

        # 최근 고위험 공고 5건 (JOIN으로 한번에)
        cursor.execute("""
            SELECT
                j.id,
                j.title,
                j.company,
                j.location,
                j.url,
                j.crawled_at,
                r.final_score,
                r.risk_level
            FROM jobs j
            JOIN risk_analysis r ON j.id = r.job_id
            WHERE r.risk_level = '고위험'
            ORDER BY j.crawled_at DESC
            LIMIT 5
        """)
        recent_high_risk = [dict(row) for row in cursor.fetchall()]

    return {
        "total_jobs": total_jobs,
        "total_today": total_today,
        "high_risk": risk_stats.get('고위험', 0),
        "medium_risk": risk_stats.get('중위험', 0),
        "low_risk": risk_stats.get('저위험', 0),
        "top_keywords": top_keywords,
        "recent_high_risk": recent_high_risk
    }
