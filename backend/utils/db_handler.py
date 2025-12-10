"""
데이터베이스 저장 유틸리티
채용 공고를 데이터베이스에 저장하는 헬퍼 함수
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from database.repositories import JobRepository
from utils.logger import setup_logger

logger = setup_logger("DBHandler")


def save_jobs_to_db(jobs: List[Dict], site: str, keyword: str) -> int:
    """
    채용 공고 목록을 데이터베이스에 저장

    Args:
        jobs: 채용 공고 목록 (딕셔너리 리스트)
        site: 출처 사이트명 (예: '알바몬', '인크루트')
        keyword: 검색 키워드

    Returns:
        저장된 공고 개수
    """
    if not jobs:
        logger.warning("저장할 공고가 없습니다")
        return 0

    job_repo = JobRepository()
    saved_count = 0

    logger.info(f"데이터베이스 저장 시작: {len(jobs)}개 공고")

    for i, job in enumerate(jobs, 1):
        try:
            # 필수 필드 추가
            job_data = job.copy()
            job_data['source_site'] = site
            job_data['search_keyword'] = keyword
            job_data['crawled_at'] = datetime.now()

            # DB 저장
            job_id = job_repo.insert_job(job_data)
            saved_count += 1

            logger.debug(f"  [{i}/{len(jobs)}] DB 저장 완료 (ID: {job_id}) - {job.get('title', 'N/A')[:50]}")

        except Exception as e:
            logger.error(f"  [{i}/{len(jobs)}] DB 저장 실패: {e}")
            continue

    logger.info(f"✅ DB 저장 완료: {saved_count}/{len(jobs)}개 성공")
    return saved_count


def get_jobs_from_db(keyword: str = None, site: str = None, limit: int = 100) -> List[Dict]:
    """
    데이터베이스에서 채용 공고 조회

    Args:
        keyword: 검색 키워드 (None이면 전체)
        site: 출처 사이트명 (None이면 전체)
        limit: 최대 조회 개수

    Returns:
        채용 공고 목록
    """
    job_repo = JobRepository()

    if keyword:
        jobs = job_repo.get_jobs_by_keyword(keyword)
        logger.info(f"'{keyword}' 키워드 공고 {len(jobs)}개 조회")
    else:
        # 전체 조회는 추가 구현 필요
        jobs = []
        logger.warning("전체 조회는 아직 미구현")

    return jobs[:limit]


if __name__ == "__main__":
    # 테스트
    print("DB Handler 테스트...")

    # 샘플 데이터
    sample_jobs = [
        {
            "title": "테스트 공고 1",
            "company": "테스트 회사",
            "location": "서울",
            "salary": "협의",
            "conditions": "",
            "recruit_summary": "",
            "detail": "테스트 상세 내용",
            "url": "https://test.com/1",
            "posted_date": "2025-11-20"
        }
    ]

    # 저장 테스트
    count = save_jobs_to_db(sample_jobs, site="테스트", keyword="테스트")
    print(f"저장 완료: {count}개")

    # 조회 테스트
    jobs = get_jobs_from_db(keyword="테스트")
    print(f"조회 완료: {len(jobs)}개")
