"""
알바몬 크롤러 데이터베이스 저장 테스트
"""
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent))

from sites.albamon.crawler import AlbamonCrawler
from utils.db_handler import save_jobs_to_db
from utils.logger import setup_logger

def main():
    """메인 테스트 함수"""
    logger = setup_logger("AlbamonDBTest")

    logger.info("=" * 50)
    logger.info("알바몬 크롤러 데이터베이스 저장 테스트 시작")
    logger.info("=" * 50)

    # 크롤러 실행
    crawler = AlbamonCrawler(headless=False)
    try:
        crawler.start()

        # 3개 공고 수집
        logger.info("\n1단계: 공고 수집...")
        jobs = crawler.crawl("반도체", max_jobs=3)

        if not jobs:
            logger.warning("수집된 공고가 없습니다.")
            return

        logger.info(f"✓ {len(jobs)}개 공고 수집 완료")

        # JSON 파일 저장
        logger.info("\n2단계: JSON 파일 저장...")
        crawler.save_results("반도체", jobs)

        # 데이터베이스 저장
        logger.info("\n3단계: 데이터베이스 저장...")
        save_jobs_to_db(jobs, site="알바몬", keyword="반도체")

        # 결과 요약
        logger.info("\n" + "=" * 50)
        logger.info("테스트 결과 요약")
        logger.info("=" * 50)
        logger.info(f"수집된 공고 개수: {len(jobs)}개")
        logger.info(f"JSON 저장: ✓ 완료")
        logger.info(f"데이터베이스 저장: ✓ 완료")

        # 수집된 공고 상세 정보
        logger.info("\n수집된 공고 목록:")
        for i, job in enumerate(jobs, 1):
            logger.info(f"\n{i}. {job['title'][:60]}")
            logger.info(f"   회사: {job.get('company', 'N/A')}")
            logger.info(f"   위치: {job.get('location', 'N/A')}")
            logger.info(f"   급여: {job.get('salary', 'N/A')}")
            logger.info(f"   URL: {job.get('url', 'N/A')}")

    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}", exc_info=True)
    finally:
        crawler.close()

    logger.info("\n" + "=" * 50)
    logger.info("테스트 완료")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
