"""
크롤러 테스트 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.append(str(Path(__file__).parent))

from sites.jobkorea import JobKoreaCrawler
from sites.incruit import IncruitCrawler
from utils.logger import setup_logger

def test_jobkorea():
    """잡코리아 크롤러 테스트 (산업별 기업 크롤링 방식)"""
    logger = setup_logger("Test")
    logger.info("=" * 60)
    logger.info("잡코리아 크롤러 테스트 시작 (산업별 기업 크롤링)")
    logger.info("=" * 60)
    
    crawler = JobKoreaCrawler(headless=False)  # 브라우저 창 표시
    try:
        crawler.start()
        # 산업별 기업 크롤링 방식 테스트
        keywords = ["중국어", "중국"]
        industries = ["반도체"]  # 테스트용으로 하나만
        jobs = crawler.crawl_by_industry(keywords, industries, max_companies=3, max_jobs_per_company=2)
        
        if jobs:
            logger.info(f"\n수집된 공고 수: {len(jobs)}")
            for i, job in enumerate(jobs, 1):
                logger.info(f"\n--- 공고 {i} ---")
                logger.info(f"제목: {job.get('title', 'N/A')}")
                logger.info(f"회사: {job.get('company', 'N/A')}")
                logger.info(f"근무지: {job.get('location', 'N/A')[:50] if job.get('location') else 'N/A'}")
                logger.info(f"급여: {job.get('salary', 'N/A')[:50] if job.get('salary') else 'N/A'}")
                logger.info(f"URL: {job.get('url', 'N/A')}")
            crawler.save_results("중국어", jobs)
        else:
            logger.warning("수집된 공고가 없습니다")
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}", exc_info=True)
    finally:
        crawler.close()
    
    logger.info("=" * 60)
    logger.info("잡코리아 크롤러 테스트 완료")
    logger.info("=" * 60)

def test_incruit():
    """인쿠르트 크롤러 테스트"""
    logger = setup_logger("Test")
    logger.info("=" * 60)
    logger.info("인쿠르트 크롤러 테스트 시작")
    logger.info("=" * 60)
    
    crawler = IncruitCrawler(headless=False)  # 브라우저 창 표시
    try:
        crawler.start()
        jobs = crawler.crawl("중국어", max_jobs=3)  # 3개만 테스트
        if jobs:
            logger.info(f"\n수집된 공고 수: {len(jobs)}")
            for i, job in enumerate(jobs, 1):
                logger.info(f"\n--- 공고 {i} ---")
                logger.info(f"제목: {job.get('title', 'N/A')}")
                logger.info(f"회사: {job.get('company', 'N/A')}")
                logger.info(f"근무지: {job.get('location', 'N/A')}")
                logger.info(f"URL: {job.get('url', 'N/A')}")
            crawler.save_results("중국어", jobs)
        else:
            logger.warning("수집된 공고가 없습니다")
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}", exc_info=True)
    finally:
        crawler.close()
    
    logger.info("=" * 60)
    logger.info("인쿠르트 크롤러 테스트 완료")
    logger.info("=" * 60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="크롤러 테스트")
    parser.add_argument("--site", choices=["jobkorea", "incruit", "all"], default="all")
    args = parser.parse_args()
    
    if args.site == "jobkorea":
        test_jobkorea()
    elif args.site == "incruit":
        test_incruit()
    else:
        test_jobkorea()
        print("\n")
        test_incruit()

