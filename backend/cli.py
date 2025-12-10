"""
채용 사이트 크롤러 메인 실행 스크립트
"""
import json
import argparse
from pathlib import Path
from typing import List

from sites.jobkorea.crawler import JobKoreaCrawler
from sites.incruit.crawler import IncruitCrawler
from sites.alba.crawler import AlbaCrawler
from sites.albamon.crawler import AlbamonCrawler
from sites.jobplanet.crawler import JobplanetCrawler
from sites.jobposting.crawler import JobPostingCrawler
from sites.worknet.crawler import WorknetCrawler
from sites.saramin.crawler import SaraminCrawler
from sites.hibrain.crawler import HibrainCrawler
from sites.blind.crawler import BlindCrawler
from utils.logger import setup_logger


def load_keywords() -> dict:
    """키워드 파일에서 모든 키워드 로드 (카테고리별로 반환)"""
    keywords_path = Path(__file__).parent / "config" / "keywords.json"
    
    if not keywords_path.exists():
        logger = setup_logger()
        logger.warning("키워드 파일을 찾을 수 없습니다. 기본 키워드를 사용합니다.")
        return {
            "technology_fields": ["반도체", "디스플레이"],
            "regions": ["중국", "UAE", "홍콩"],
            "languages": ["중국어"],
            "companies": ["삼성", "LG"],
            "risk_keywords": ["급구"]
        }
    
    with open(keywords_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_crawler(site: str, keywords: List[str], industries: List[str] = None, max_companies: int = 50, max_jobs_per_company: int = 10, headless: bool = True):
    """
    특정 사이트의 크롤러 실행
    
    Args:
        site: 사이트명
        keywords: 검색 키워드 리스트
        industries: 산업 필터 리스트 (None이면 기술 분야 사용)
        max_companies: 최대 수집할 기업 수
        max_jobs_per_company: 기업당 최대 수집할 공고 수
        headless: 헤드리스 모드 여부
    """
    logger = setup_logger()
    
    # 크롤러 인스턴스 생성
    crawler_map = {
        "jobkorea": JobKoreaCrawler,
        "incruit": IncruitCrawler,
        "alba": AlbaCrawler,
        "albamon": AlbamonCrawler,
        "jobplanet": JobplanetCrawler,
        "jobposting": JobPostingCrawler,
        "worknet": WorknetCrawler,
        "saramin": SaraminCrawler,
        "hibrain": HibrainCrawler,
        "blind": BlindCrawler,
    }
    
    if site not in crawler_map:
        logger.error(f"지원하지 않는 사이트: {site}")
        return
    
    crawler_class = crawler_map[site]
    crawler = crawler_class(headless=headless)
    
    try:
        crawler.start()
        
        if site == "jobkorea":
            # 잡코리아는 산업별 크롤링 방식 사용
            jobs = crawler.crawl_by_industry(keywords, industries, max_companies, max_jobs_per_company)
        elif site == "blind":
            # 블라인드는 영문 키워드만 사용 (첫 번째 키워드만 사용)
            keyword = keywords[0] if keywords else "semiconductor"
            jobs = crawler.crawl(keyword, max_jobs=max_jobs_per_company * max_companies)
        else:
            # 나머지 크롤러는 키워드별로 순회하며 수집
            all_jobs = []
            for keyword in keywords:
                keyword_jobs = crawler.crawl(keyword, max_jobs=max_jobs_per_company * max_companies)
                all_jobs.extend(keyword_jobs)
            jobs = all_jobs
        
        if jobs:
            keyword_str = ", ".join(keywords[:3])  # 처음 3개만 표시
            if len(keywords) > 3:
                keyword_str += f" 외 {len(keywords) - 3}개"
            crawler.save_results(keyword_str, jobs)
            logger.info(f"{site} - 키워드({keyword_str}): {len(jobs)}개 공고 수집 완료")
        else:
            logger.warning(f"{site} - 키워드({', '.join(keywords[:3])}): 수집된 공고가 없습니다")
    except Exception as e:
        logger.error(f"{site} 크롤링 중 오류: {e}", exc_info=True)
    finally:
        crawler.close()


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="채용 사이트 크롤러")
    parser.add_argument(
        "--site",
        type=str,
        choices=["jobkorea", "incruit", "alba", "albamon", "jobplanet", "jobposting", "worknet", "saramin", "hibrain", "blind", "all"],
        default="all",
        help="크롤링할 사이트 선택 (기본값: all)"
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default=None,
        help="검색 키워드 (지정하지 않으면 config/keywords.json의 모든 키워드 사용)"
    )
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=50,
        help="사이트당 최대 수집할 공고 수 (기본값: 50)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="헤드리스 모드로 실행"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="헤드리스 모드 비활성화 (브라우저 창 표시)"
    )
    
    args = parser.parse_args()
    
    logger = setup_logger()
    logger.info("=" * 50)
    logger.info("채용 사이트 크롤러 시작")
    logger.info("=" * 50)
    
    # 키워드 결정
    if args.keyword:
        keywords = [args.keyword]
    else:
        # keywords.json에서 모든 키워드 로드
        keywords_data = load_keywords()
        # 모든 카테고리의 키워드를 하나의 리스트로 합치기
        all_keywords = []
        for category, kw_list in keywords_data.items():
            all_keywords.extend(kw_list)
        keywords = list(set(all_keywords))
        logger.info(f"총 {len(keywords)}개의 키워드 로드: {keywords}")
    
    # 산업 필터 결정 (기술 분야 사용)
    keywords_data = load_keywords()
    industries = keywords_data.get("technology_fields", [])
    logger.info(f"산업 필터: {industries}")
    
    # 헤드리스 모드 결정
    headless = args.headless
    if args.no_headless:
        headless = False
    
    # 사이트 결정
    sites = []
    if args.site == "all":
        sites = ["jobkorea", "incruit", "alba", "albamon", "jobplanet", "jobposting", "worknet", "saramin", "hibrain"]
        # blind는 영문 사이트이므로 기본적으로 제외
    else:
        sites = [args.site]
    
    # 크롤링 실행
    for site in sites:
        logger.info(f"\n{'='*50}")
        logger.info(f"{site.upper()} 크롤링 시작")
        logger.info(f"{'='*50}")
        
        # 산업별 기업 크롤링 방식 사용
        max_companies = max(1, args.max_jobs // 10)  # 기업당 평균 10개 공고 가정, 최소 1개
        run_crawler(site, keywords, industries, max_companies=max_companies, max_jobs_per_company=10, headless=headless)
    
    logger.info("\n" + "=" * 50)
    logger.info("모든 크롤링 완료")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()

