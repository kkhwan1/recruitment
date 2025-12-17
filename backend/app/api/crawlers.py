from fastapi import APIRouter, BackgroundTasks, HTTPException
from backend.app.schemas import CrawlRequest
from backend.cli import run_crawler, load_keywords

router = APIRouter()

def background_crawl_task(site: str, keyword: str, max_jobs: int):
    print(f"Starting background crawl for {site}...")
    keywords = [keyword] if keyword else []
    
    if not keywords:
         # Load defaults
        keywords_data = load_keywords()
        all_keywords = []
        for category, kw_list in keywords_data.items():
            all_keywords.extend(kw_list)
        keywords = list(set(all_keywords))

    # Determine industries
    keywords_data = load_keywords()
    industries = keywords_data.get("technology_fields", [])
    
    # Run
    # Using a smaller max_companies logic for web triggers to be faster?
    # Or respect user input.
    max_companies = max(1, max_jobs // 10)
    
    run_crawler(site, keywords, industries, max_companies=max_companies, max_jobs_per_company=10, headless=True)
    print(f"Background crawl for {site} finished.")

@router.post("/crawlers/crawl")
def trigger_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    크롤러 실행 (백그라운드)

    Args:
        request: {
            "site": str,          # 크롤링할 사이트 (jobkorea, incruit, saramin, hibrain, all)
            "keyword": str,       # 검색 키워드 (optional)
            "max_jobs": int       # 최대 수집 개수 (기본값: 10)
        }

    Returns:
        {"message": str, "status": str}
    """
    if request.site not in ["jobkorea", "incruit", "alba", "albamon", "jobplanet", "jobposting", "worknet", "saramin", "hibrain", "blind", "all"]:
        raise HTTPException(status_code=400, detail="Invalid site")

    background_tasks.add_task(background_crawl_task, request.site, request.keyword, request.max_jobs)
    return {"message": f"Crawler for {request.site} started in background", "status": "processing"}
