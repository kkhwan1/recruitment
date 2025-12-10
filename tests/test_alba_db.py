"""
Alba 크롤러 데이터베이스 통합 테스트
"""
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent))

from sites.alba.crawler import AlbaCrawler
from database import JobRepository
from utils.logger import setup_logger
from datetime import datetime

logger = setup_logger("AlbaDBTest")


def test_alba_crawler_with_db():
    """Alba 크롤러 + 데이터베이스 통합 테스트"""

    # 1. 크롤러 실행
    logger.info("=== 알바천국 크롤러 시작 ===")
    crawler = AlbaCrawler(headless=True)

    try:
        crawler.start()
        jobs = crawler.crawl("반도체", max_jobs=3)

        if not jobs:
            logger.error("수집된 공고가 없습니다")
            return

        logger.info(f"수집 완료: {len(jobs)}개 공고")

        # 2. JSON 저장
        crawler.save_results("반도체", jobs)

        # 3. 데이터베이스 저장
        logger.info("\n=== 데이터베이스 저장 시작 ===")
        job_repo = JobRepository()

        saved_count = 0
        for job_data in jobs:
            try:
                # 시간 정보 추가
                crawled_at = datetime.now()

                # 데이터베이스 저장용 딕셔너리 준비
                db_job_data = {
                    'title': job_data['title'],
                    'company': job_data.get('company', ''),
                    'location': job_data.get('location', ''),
                    'salary': job_data.get('salary', ''),
                    'conditions': job_data.get('conditions', ''),
                    'recruit_summary': job_data.get('recruit_summary', ''),
                    'detail': job_data.get('detail', ''),
                    'url': job_data['url'],
                    'posted_date': job_data.get('posted_date', ''),
                    'source_site': '알바천국',
                    'search_keyword': '반도체',
                    'crawled_at': crawled_at
                }

                # 저장
                job_id = job_repo.insert_job(db_job_data)

                if job_id:
                    saved_count += 1
                    logger.info(f"저장 성공 (ID: {job_id}): {db_job_data['title'][:50]}")

            except Exception as e:
                logger.error(f"저장 실패 ({job_data['title'][:50]}): {e}", exc_info=True)

        # 4. 결과 출력
        logger.info(f"\n=== 테스트 완료 ===")
        logger.info(f"수집 공고: {len(jobs)}개")
        logger.info(f"저장 성공: {saved_count}개")
        logger.info(f"저장 실패: {len(jobs) - saved_count}개")

        # 5. 공고 목록 출력
        logger.info("\n=== 수집된 공고 목록 ===")
        for i, job in enumerate(jobs, 1):
            logger.info(f"{i}. {job['title']}")
            logger.info(f"   회사: {job.get('company', 'N/A')}")
            logger.info(f"   위치: {job.get('location', 'N/A')}")
            logger.info(f"   급여: {job.get('salary', 'N/A')}")
            logger.info(f"   마감: {job.get('posted_date', 'N/A')}")
            logger.info(f"   URL: {job['url']}\n")

    finally:
        crawler.close()


if __name__ == "__main__":
    test_alba_crawler_with_db()
