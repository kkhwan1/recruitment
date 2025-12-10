"""
모든 크롤러 개별 테스트 스크립트
"""
import sys
import argparse
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.append(str(Path(__file__).parent))

from sites.alba.crawler import AlbaCrawler
from sites.albamon.crawler import AlbamonCrawler
from sites.jobplanet.crawler import JobplanetCrawler
from sites.jobposting.crawler import JobPostingCrawler
from sites.worknet.crawler import WorknetCrawler
from sites.blind.crawler import BlindCrawler
from utils.logger import setup_logger


def test_alba(keyword="편의점", max_jobs=3, headless=False):
    """알바천국 크롤러 테스트"""
    logger = setup_logger("TestAlba")
    logger.info("=" * 80)
    logger.info("알바천국 크롤러 테스트 시작")
    logger.info("=" * 80)
    
    crawler = AlbaCrawler(headless=headless)
    try:
        crawler.start()
        jobs = crawler.crawl(keyword, max_jobs=max_jobs)
        if jobs:
            crawler.save_results(keyword, jobs)
            logger.info(f"✅ 테스트 성공: {len(jobs)}개 공고 수집")
            for i, job in enumerate(jobs[:3], 1):
                logger.info(f"  {i}. {job.get('title', 'N/A')[:50]} - {job.get('company', 'N/A')}")
            return True
        else:
            logger.warning("⚠️  수집된 공고가 없습니다")
            return False
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}", exc_info=True)
        return False
    finally:
        crawler.close()


def test_albamon(keyword="카페", max_jobs=3, headless=False):
    """알바몬 크롤러 테스트"""
    logger = setup_logger("TestAlbamon")
    logger.info("=" * 80)
    logger.info("알바몬 크롤러 테스트 시작")
    logger.info("=" * 80)
    
    crawler = AlbamonCrawler(headless=headless)
    try:
        crawler.start()
        jobs = crawler.crawl(keyword, max_jobs=max_jobs)
        if jobs:
            crawler.save_results(keyword, jobs)
            logger.info(f"✅ 테스트 성공: {len(jobs)}개 공고 수집")
            for i, job in enumerate(jobs[:3], 1):
                logger.info(f"  {i}. {job.get('title', 'N/A')[:50]} - {job.get('company', 'N/A')}")
            return True
        else:
            logger.warning("⚠️  수집된 공고가 없습니다")
            return False
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}", exc_info=True)
        return False
    finally:
        crawler.close()


def test_jobplanet(keyword="개발자", max_jobs=3, headless=False):
    """잡플래닛 크롤러 테스트"""
    logger = setup_logger("TestJobplanet")
    logger.info("=" * 80)
    logger.info("잡플래닛 크롤러 테스트 시작")
    logger.info("=" * 80)
    
    crawler = JobplanetCrawler(headless=headless)
    try:
        crawler.start()
        jobs = crawler.crawl(keyword, max_jobs=max_jobs)
        if jobs:
            crawler.save_results(keyword, jobs)
            logger.info(f"✅ 테스트 성공: {len(jobs)}개 공고 수집")
            for i, job in enumerate(jobs[:3], 1):
                logger.info(f"  {i}. {job.get('title', 'N/A')[:50]} - {job.get('company', 'N/A')}")
            return True
        else:
            logger.warning("⚠️  수집된 공고가 없습니다")
            return False
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}", exc_info=True)
        return False
    finally:
        crawler.close()


def test_jobposting(keyword="사무직", max_jobs=3, headless=False):
    """잡포스팅 크롤러 테스트"""
    logger = setup_logger("TestJobposting")
    logger.info("=" * 80)
    logger.info("잡포스팅 크롤러 테스트 시작")
    logger.info("=" * 80)
    
    crawler = JobPostingCrawler(headless=headless)
    try:
        crawler.start()
        jobs = crawler.crawl(keyword, max_jobs=max_jobs)
        if jobs:
            crawler.save_results(keyword, jobs)
            logger.info(f"✅ 테스트 성공: {len(jobs)}개 공고 수집")
            for i, job in enumerate(jobs[:3], 1):
                logger.info(f"  {i}. {job.get('title', 'N/A')[:50]} - {job.get('company', 'N/A')}")
            return True
        else:
            logger.warning("⚠️  수집된 공고가 없습니다")
            return False
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}", exc_info=True)
        return False
    finally:
        crawler.close()


def test_worknet(keyword="반도체", max_jobs=3, headless=False):
    """워크넷 크롤러 테스트"""
    logger = setup_logger("TestWorknet")
    logger.info("=" * 80)
    logger.info("워크넷 크롤러 테스트 시작")
    logger.info("=" * 80)
    
    crawler = WorknetCrawler(headless=headless)
    try:
        crawler.start()
        jobs = crawler.crawl(keyword, max_jobs=max_jobs)
        if jobs:
            crawler.save_results(keyword, jobs)
            logger.info(f"✅ 테스트 성공: {len(jobs)}개 공고 수집")
            for i, job in enumerate(jobs[:3], 1):
                logger.info(f"  {i}. {job.get('title', 'N/A')[:50]} - {job.get('company', 'N/A')}")
            return True
        else:
            logger.warning("⚠️  수집된 공고가 없습니다")
            return False
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}", exc_info=True)
        return False
    finally:
        crawler.close()


def test_blind(keyword="semiconductor", max_jobs=3, headless=False):
    """블라인드 크롤러 테스트"""
    logger = setup_logger("TestBlind")
    logger.info("=" * 80)
    logger.info("블라인드 크롤러 테스트 시작")
    logger.info("=" * 80)
    
    crawler = BlindCrawler(headless=headless)
    try:
        crawler.start()
        jobs = crawler.crawl(keyword, max_jobs=max_jobs)
        if jobs:
            crawler.save_results(keyword, jobs)
            logger.info(f"✅ 테스트 성공: {len(jobs)}개 공고 수집")
            for i, job in enumerate(jobs[:3], 1):
                logger.info(f"  {i}. {job.get('title', 'N/A')[:50]} - {job.get('company', 'N/A')}")
            return True
        else:
            logger.warning("⚠️  수집된 공고가 없습니다")
            return False
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}", exc_info=True)
        return False
    finally:
        crawler.close()


def main():
    parser = argparse.ArgumentParser(description="모든 크롤러 개별 테스트")
    parser.add_argument(
        "--crawler",
        type=str,
        choices=["alba", "albamon", "jobplanet", "jobposting", "worknet", "blind", "all"],
        default="all",
        help="테스트할 크롤러 선택"
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default=None,
        help="검색 키워드 (기본값: 각 크롤러별 기본 키워드)"
    )
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=3,
        help="최대 수집할 공고 수 (기본값: 3)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="헤드리스 모드로 실행"
    )
    
    args = parser.parse_args()
    
    results = {}
    
    # 알바천국
    if args.crawler in ["alba", "all"]:
        keyword = args.keyword if args.keyword else "편의점"
        results["alba"] = test_alba(keyword, args.max_jobs, args.headless)
    
    # 알바몬
    if args.crawler in ["albamon", "all"]:
        keyword = args.keyword if args.keyword else "카페"
        results["albamon"] = test_albamon(keyword, args.max_jobs, args.headless)
    
    # 잡플래닛
    if args.crawler in ["jobplanet", "all"]:
        keyword = args.keyword if args.keyword else "개발자"
        results["jobplanet"] = test_jobplanet(keyword, args.max_jobs, args.headless)
    
    # 잡포스팅
    if args.crawler in ["jobposting", "all"]:
        keyword = args.keyword if args.keyword else "사무직"
        results["jobposting"] = test_jobposting(keyword, args.max_jobs, args.headless)
    
    # 워크넷
    if args.crawler in ["worknet", "all"]:
        keyword = args.keyword if args.keyword else "반도체"
        results["worknet"] = test_worknet(keyword, args.max_jobs, args.headless)
    
    # 블라인드
    if args.crawler in ["blind", "all"]:
        keyword = args.keyword if args.keyword else "semiconductor"
        results["blind"] = test_blind(keyword, args.max_jobs, args.headless)
    
    # 결과 요약
    logger = setup_logger("TestSummary")
    logger.info("\n" + "=" * 80)
    logger.info("테스트 결과 요약")
    logger.info("=" * 80)
    for crawler_name, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        logger.info(f"{crawler_name:15} : {status}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()

