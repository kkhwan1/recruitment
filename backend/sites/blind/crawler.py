"""
블라인드(Blind) 채용 공고 크롤러
"""
import json
import re
import time
import urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, Browser
from typing import List, Dict, Optional
import sys

# 프로젝트 루트를 경로에 추가
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.logger import setup_logger
from utils.file_handler import save_json, create_job_data


class BlindCrawler:
    """블라인드 채용 공고 크롤러"""

    def __init__(self, headless: bool = True):
        """
        Args:
            headless: 브라우저를 헤드리스 모드로 실행할지 여부
        """
        self.logger = setup_logger("BlindCrawler")
        self.headless = headless
        self.config = self._load_config()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def _load_config(self) -> dict:
        """설정 파일 로드"""
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def start(self):
        """브라우저 시작 - Bot Detection 회피 적용"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        self.page = self.browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        self.logger.info("브라우저 시작 완료 (Bot Detection 회피 적용)")

    def close(self):
        """브라우저 종료"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        self.logger.info("브라우저 종료 완료")

    def _clean_text(self, text: str, max_length: int = None) -> str:
        """
        텍스트 정리 (불필요한 공백, 개행 제거)

        Args:
            text: 정리할 텍스트
            max_length: 최대 길이 (None이면 제한 없음)

        Returns:
            정리된 텍스트
        """
        if not text:
            return ""

        # 여러 공백을 하나로, 개행 정리
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()

        if max_length and len(text) > max_length:
            text = text[:max_length] + "..."

        return text

    def search(self, keyword: str) -> bool:
        """
        키워드로 검색 - /jobs 페이지에서 검색창 이용

        Args:
            keyword: 검색 키워드

        Returns:
            검색 성공 여부
        """
        try:
            # /jobs 페이지로 이동
            self.logger.info(f"블라인드 Jobs 페이지로 이동")
            self.page.goto(self.config["jobs_url"], wait_until="domcontentloaded", timeout=60000)
            time.sleep(3)

            # 검색창 찾기 및 입력
            search_input = self.page.query_selector('input[placeholder*="Search by job title or company"], input[type="search"], input[aria-label*="Search"]')
            if search_input:
                search_input.fill(keyword)
                time.sleep(1)
                
                # Enter 키로 검색
                search_input.press("Enter")
                time.sleep(3)
                
                self.page.wait_for_load_state("networkidle", timeout=15000)
                self.logger.info(f"'{keyword}' 검색 완료")
                return True
            else:
                self.logger.warning("검색창을 찾을 수 없습니다")
                return False

        except Exception as e:
            self.logger.error(f"검색 중 오류 발생: {e}", exc_info=True)
            return False

    def get_job_list(self) -> List[str]:
        """
        현재 페이지의 공고 목록에서 공고 링크 수집

        ⚠️ 현재 제한사항:
        - Blind는 Bot Detection으로 자동 크롤링 차단
        - /job/search 엔드포인트: Bot Detection 에러
        - /jobs 엔드포인트: 로그인 필요
        - 현재 버전에서는 공고 수집 불가능

        자세한 내용은 IMPLEMENTATION_STATUS.md 참조

        Returns:
            공고 링크 리스트 (현재는 항상 빈 리스트 또는 에러)
        """
        job_links = []
        try:
            # 페이지 상태 확인
            body_text = self.page.evaluate("document.body.innerText")

            # Bot Detection 에러 체크
            if "Oops" in body_text or "Something went wrong" in body_text:
                self.logger.error("❌ Bot Detection 감지됨 - Blind는 자동 크롤링을 차단합니다")
                self.logger.error("에러 메시지: " + body_text[:200])
                self.logger.info("💡 해결 방법: IMPLEMENTATION_STATUS.md 참조")
                return []

            # Login wall 체크
            if "Sign in" in body_text or "Log in" in body_text:
                self.logger.warning("⚠️ 로그인 필요 - Blind 채용 공고는 로그인 후 접근 가능합니다")
                self.logger.info("💡 현재 버전에서는 Blind 크롤링을 지원하지 않습니다")
                return []

            # 페이지가 완전히 로드될 때까지 대기
            time.sleep(3)

            # 스크롤하여 더 많은 공고 로드
            for i in range(3):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)

            # JavaScript로 링크 수집 - 실제 페이지 구조에 맞게
            links_data = self.page.evaluate("""
                () => {
                    const links = [];
                    const baseUrl = 'https://www.teamblind.com';
                    
                    // 블라인드 Jobs 페이지의 실제 구조 분석
                    // 이미지 링크나 클릭 가능한 요소들을 찾아서 부모 링크 추출
                    const jobCards = document.querySelectorAll('[class*="job"], [class*="Job"], img[alt*="company"], [data-testid*="job"]');
                    
                    jobCards.forEach(card => {
                        // 부모 요소에서 링크 찾기
                        let parent = card;
                        for (let i = 0; i < 5; i++) {
                            if (parent && parent.tagName === 'A' && parent.href) {
                                const href = parent.href;
                                if (href.includes('/jobs/') || href.includes('/job/')) {
                                    if (!links.includes(href) && !href.includes('/jobs?') && !href.includes('/job/search')) {
                                        links.push(href);
                                    }
                                    break;
                                }
                            }
                            parent = parent.parentElement;
                            if (!parent) break;
                        }
                    });
                    
                    // 일반 링크에서도 찾기
                    document.querySelectorAll('a[href]').forEach(link => {
                        const href = link.getAttribute('href');
                        if (href && (href.includes('/jobs/') || href.includes('/job/'))) {
                            if (!href.includes('/jobs?') && !href.includes('/job/search') && !href.match(/\\/jobs?\\/?(\\?|#|$)/)) {
                                let fullUrl = href.startsWith('http') ? href : baseUrl + href;
                                if (!links.includes(fullUrl)) {
                                    links.push(fullUrl);
                                }
                            }
                        }
                    });
                    
                    return [...new Set(links)];
                }
            """)

            job_links = links_data if links_data else []

            if len(job_links) == 0:
                self.logger.warning("⚠️ 공고 링크를 찾을 수 없습니다")
                self.logger.info("💡 Blind는 Bot Detection 또는 Login wall로 크롤링이 제한됩니다")
                self.logger.info("📖 자세한 내용: sites/blind/IMPLEMENTATION_STATUS.md")
            else:
                self.logger.info(f"총 {len(job_links)}개의 공고 링크 수집")
                self.logger.debug(f"샘플 링크: {job_links[:3]}")

            return job_links

        except Exception as e:
            self.logger.error(f"공고 목록 수집 중 오류: {e}", exc_info=True)
            self.logger.info("💡 Blind 크롤링 제한사항: sites/blind/IMPLEMENTATION_STATUS.md")
            return []

    def parse_job_detail(self, job_url: str) -> Optional[Dict]:
        """
        공고 상세 페이지에서 정보 파싱

        Args:
            job_url: 공고 상세 페이지 URL

        Returns:
            파싱된 공고 정보 딕셔너리
        """
        try:
            self.logger.debug(f"공고 상세 페이지 접속: {job_url}")
            self.page.goto(job_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(self.config.get("wait_time", 5))

            # 네트워크 안정화 대기
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass

            job_info = {
                "url": job_url,
                "title": "",
                "company": "",
                "location": "",
                "salary": "",
                "conditions": "",
                "detail": "",
                "recruit_summary": "",
                "posted_date": ""
            }

            # JavaScript로 정보 추출
            parsed_data = self.page.evaluate("""
                () => {
                    const result = {
                        title: '',
                        company: '',
                        location: '',
                        salary: '',
                        conditions: '',
                        detail: '',
                        recruit_summary: '',
                        posted_date: ''
                    };

                    // 제목 추출 (h1)
                    const h1 = document.querySelector('h1');
                    if (h1) {
                        result.title = h1.innerText.trim();
                    }

                    // 전체 텍스트
                    const bodyText = document.body.innerText;
                    const lines = bodyText.split('\\n').map(l => l.trim()).filter(l => l);

                    // 회사명 (평점 앞에 있음)
                    for (let i = 0; i < lines.length; i++) {
                        if (lines[i].match(/^[0-9]\\.[0-9]$/)) {
                            if (i > 0) {
                                result.company = lines[i - 1];
                            }
                        }
                    }

                    // 상세 내용
                    const main = document.querySelector('main, article, [role="main"]');
                    result.detail = main ? main.innerText.trim() : bodyText;

                    // 근무지 패턴
                    const locMatch = result.detail.match(/(?:Remote|Hybrid|On-site|USA|United States)[^\\n]{0,100}/i);
                    if (locMatch) {
                        result.location = locMatch[0];
                    }

                    // 급여 패턴
                    const salMatch = result.detail.match(/\\$[\\d,]+[^\\n]{0,100}/);
                    if (salMatch) {
                        result.salary = salMatch[0];
                    }

                    // 자격요건
                    const condMatch = result.detail.match(/(?:Requirements?|Qualifications?|Skills?)[\\s\\S]{0,800}/i);
                    if (condMatch) {
                        result.conditions = condMatch[0];
                    }

                    // 모집요강
                    const recruitMatch = result.detail.match(/(?:About|Description|Responsibilities)[\\s\\S]{0,1500}/i);
                    if (recruitMatch) {
                        result.recruit_summary = recruitMatch[0];
                    } else {
                        result.recruit_summary = result.detail.substring(0, 1000);
                    }

                    return result;
                }
            """)

            # 파싱된 데이터 반영
            job_info.update(parsed_data)

            # 정규표현식으로 재추출 (fallback)
            if job_info["detail"]:
                job_info = self._extract_fields_from_detail(job_info)

            # 텍스트 정리
            job_info["location"] = self._clean_text(job_info["location"], max_length=200)
            job_info["salary"] = self._clean_text(job_info["salary"], max_length=100)
            job_info["conditions"] = self._clean_text(job_info["conditions"], max_length=500)
            job_info["recruit_summary"] = self._clean_text(job_info["recruit_summary"], max_length=2000)
            job_info["posted_date"] = self._clean_text(job_info["posted_date"], max_length=50)

            # 제목이 없으면 스킵
            if not job_info["title"]:
                self.logger.warning(f"제목을 찾을 수 없어 스킵: {job_url}")
                return None

            self.logger.info(f"공고 파싱 완료: {job_info['title']} - {job_info.get('company', 'N/A')}")
            return job_info

        except Exception as e:
            self.logger.error(f"공고 상세 파싱 중 오류 ({job_url}): {e}", exc_info=True)
            return None

    def _extract_fields_from_detail(self, job_info: Dict) -> Dict:
        """
        detail 필드에서 정규표현식으로 필드 재추출 (fallback)

        Args:
            job_info: 공고 정보 딕셔너리

        Returns:
            업데이트된 공고 정보
        """
        detail = job_info.get("detail", "")
        if not detail:
            return job_info

        # 급여 추출
        if not job_info.get("salary"):
            salary_patterns = [
                r'\$[\d,]+[\s\-~]*(?:to|-)?\s*\$?[\d,]+',
                r'[\d,]+K[\s\-~]*(?:to|-)?\s*[\d,]+K',
            ]
            for pattern in salary_patterns:
                match = re.search(pattern, detail, re.IGNORECASE)
                if match:
                    job_info["salary"] = match.group(0).strip()
                    break

        # 근무지 추출
        if not job_info.get("location"):
            location_patterns = [
                r'(?:Remote|Hybrid|On-site)[^\n]{0,100}',
                r'(?:USA|United States)[^\n]{0,100}',
            ]
            for pattern in location_patterns:
                match = re.search(pattern, detail, re.IGNORECASE)
                if match:
                    job_info["location"] = match.group(0).strip()
                    break

        return job_info

    def crawl(self, keyword: str, max_jobs: int = 50) -> List[Dict]:
        """
        키워드로 검색하여 공고 수집

        Args:
            keyword: 검색 키워드
            max_jobs: 최대 수집할 공고 수

        Returns:
            수집된 공고 정보 리스트
        """
        self.logger.info(f"'{keyword}' 키워드로 크롤링 시작")

        if not self.search(keyword):
            return []

        all_jobs = []
        job_links = self.get_job_list()

        if not job_links:
            self.logger.warning("공고 링크를 찾을 수 없습니다")
            return []

        # 최대 개수만큼만 수집
        job_links = job_links[:max_jobs]

        for i, job_url in enumerate(job_links, 1):
            try:
                self.logger.info(f"진행 중: {i}/{len(job_links)}")
                job_info = self.parse_job_detail(job_url)
                if job_info:
                    all_jobs.append(job_info)
                time.sleep(self.config.get("request_delay", 2))
            except Exception as e:
                self.logger.error(f"공고 처리 중 오류 ({job_url}): {e}")
                continue

        self.logger.info(f"총 {len(all_jobs)}개의 공고 수집 완료")
        return all_jobs

    def save_results(self, keyword: str, jobs: List[Dict]):
        """
        수집 결과를 JSON 파일로 저장

        Args:
            keyword: 검색 키워드
            jobs: 수집된 공고 리스트
        """
        data = create_job_data(
            site=self.config["site_name"],
            keyword=keyword,
            jobs=jobs
        )

        # 파일명 생성
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = re.sub(r'[<>:"/\\|?*]', '_', keyword)
        filename = f"blind_{safe_keyword}_{timestamp}.json"

        filepath = save_json(data, filename)
        self.logger.info(f"결과 저장 완료: {filepath}")


if __name__ == "__main__":
    # 테스트 실행
    crawler = BlindCrawler(headless=False)
    try:
        crawler.start()
        # "semiconductor" 키워드로 검색 (블라인드는 영문 사이트)
        jobs = crawler.crawl("semiconductor", max_jobs=3)
        if jobs:
            crawler.save_results("semiconductor", jobs)
            print(f"\n수집된 공고 수: {len(jobs)}")
            for job in jobs:
                print(f"- {job['title']} at {job.get('company', 'N/A')}")
    finally:
        crawler.close()
