"""
알바몬 채용 공고 크롤러
"""
import json
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, Browser
from typing import List, Dict, Optional
import sys

# 프로젝트 루트를 경로에 추가
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.logger import setup_logger
from utils.file_handler import save_json, create_job_data


class AlbamonCrawler:
    """알바몬 채용 공고 크롤러"""

    def __init__(self, headless: bool = True):
        """
        Args:
            headless: 브라우저를 헤드리스 모드로 실행할지 여부
        """
        self.logger = setup_logger("AlbamonCrawler")
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

    def get_job_list(self, keyword: str) -> List[str]:
        """
        검색 결과에서 공고 링크 수집

        Args:
            keyword: 검색 키워드

        Returns:
            공고 링크 리스트
        """
        job_links = []
        try:
            # 검색 URL로 이동
            search_url = self.config["search_url"].format(keyword=keyword)
            self.logger.info(f"검색 페이지로 이동: {search_url}")
            self.page.goto(search_url, wait_until="networkidle", timeout=60000)
            time.sleep(self.config.get("wait_time", 3))

            # 공고 링크 수집 (JavaScript 사용)
            links_data = self.page.evaluate("""
                () => {
                    const links = [];
                    // 알바몬의 공고 링크 패턴: /jobs/detail/[숫자]
                    const jobLinks = document.querySelectorAll('a[href*="/jobs/detail/"]');

                    jobLinks.forEach(link => {
                        const href = link.getAttribute('href');
                        if (href && !links.includes(href)) {
                            const fullUrl = href.startsWith('http') ? href : 'https://www.albamon.com' + href;
                            // searchRow, logpath 등 쿼리 파라미터 제거 (고유 URL만 유지)
                            const cleanUrl = fullUrl.split('?')[0];
                            if (!links.includes(cleanUrl)) {
                                links.push(cleanUrl);
                            }
                        }
                    });

                    return [...new Set(links)]; // 중복 제거
                }
            """)

            job_links = links_data if links_data else []
            self.logger.info(f"총 {len(job_links)}개의 공고 링크 발견")

        except Exception as e:
            self.logger.error(f"공고 목록 수집 중 오류: {e}", exc_info=True)

        return job_links

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
            time.sleep(self.config.get("wait_time", 3))

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

                    // 제목 추출
                    const titleEl = document.querySelector('h1');
                    if (titleEl) result.title = titleEl.innerText.trim();

                    // 회사명 추출
                    const companySelectors = [
                        'a[href*="/jobs/company/"]',
                        'span[class*="company"]',
                        'div[class*="company"]'
                    ];
                    for (const selector of companySelectors) {
                        const companyEl = document.querySelector(selector);
                        if (companyEl && companyEl.innerText.trim()) {
                            result.company = companyEl.innerText.trim();
                            break;
                        }
                    }

                    // 근무지 추출
                    const locationElements = Array.from(document.querySelectorAll('*')).filter(el =>
                        el.innerText && (el.innerText.includes('근무지') || el.innerText.includes('주소'))
                    );
                    if (locationElements.length > 0) {
                        const text = locationElements[0].innerText;
                        const addressMatch = text.match(/(서울|경기|인천|부산|대구|광주|대전|울산|세종|강원|충북|충남|전북|전남|경북|경남|제주)[^\\n]{0,150}/);
                        if (addressMatch) {
                            result.location = addressMatch[0].trim().split('\\n')[0];
                        }
                    }

                    // 급여 추출
                    const salaryElements = Array.from(document.querySelectorAll('*')).filter(el =>
                        el.innerText && (el.innerText.includes('급여') || el.innerText.includes('시급') || el.innerText.includes('월급'))
                    );
                    if (salaryElements.length > 0) {
                        const text = salaryElements[0].innerText;
                        const lines = text.split('\\n').map(l => l.trim()).filter(l => l);
                        for (let i = 0; i < lines.length; i++) {
                            if (lines[i].includes('급여') || lines[i].includes('시급') || lines[i].includes('월급')) {
                                if (i + 1 < lines.length) {
                                    const value = lines[i + 1];
                                    if (value && !value.includes('급여') && value.match(/\\d/)) {
                                        result.salary = value;
                                        break;
                                    }
                                }
                            }
                        }
                    }

                    // 전체 본문 내용
                    const mainEl = document.querySelector('main') || document.querySelector('div[class*="content"]');
                    if (mainEl) {
                        result.detail = mainEl.innerText.trim();
                    }

                    // 지원자격 추출
                    const qualificationEl = Array.from(document.querySelectorAll('*')).find(el =>
                        el.innerText && el.innerText.includes('지원자격')
                    );
                    if (qualificationEl) {
                        const qualParent = qualificationEl.closest('div');
                        if (qualParent) {
                            result.conditions = qualParent.innerText.trim();
                        }
                    }

                    // 마감일 추출
                    const dateElements = Array.from(document.querySelectorAll('*')).filter(el =>
                        el.innerText && (el.innerText.includes('마감') || el.innerText.includes('기간'))
                    );
                    if (dateElements.length > 0) {
                        const text = dateElements[0].innerText;
                        const dateMatch = text.match(/(\\d{4}[\\s\\-./]\\d{1,2}[\\s\\-./]\\d{1,2})/);
                        if (dateMatch) {
                            result.posted_date = dateMatch[1].trim();
                        } else if (text.includes('상시')) {
                            result.posted_date = '상시채용';
                        } else if (text.includes('채용시')) {
                            result.posted_date = '채용시 마감';
                        }
                    }

                    return result;
                }
            """)

            # 파싱된 데이터를 job_info에 반영
            job_info.update(parsed_data)

            # 텍스트 정리
            job_info["title"] = self._clean_text(job_info["title"])
            job_info["company"] = self._clean_text(job_info["company"], max_length=100)
            job_info["location"] = self._clean_text(job_info["location"], max_length=200)
            job_info["salary"] = self._clean_text(job_info["salary"], max_length=100)
            job_info["conditions"] = self._clean_text(job_info["conditions"], max_length=500)
            job_info["detail"] = self._clean_text(job_info["detail"], max_length=5000)
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

    def crawl(self, keyword: str, max_jobs: int = 50) -> List[Dict]:
        """
        키워드로 검색하여 공고 수집

        Args:
            keyword: 검색 키워드
            max_jobs: 최대 수집할 공고 수

        Returns:
            수집된 공고 정보 리스트
        """
        self.logger.info(f"알바몬 크롤링 시작 (키워드: {keyword}, 최대: {max_jobs}개)")

        # 공고 링크 수집
        job_links = self.get_job_list(keyword)

        if not job_links:
            self.logger.warning(f"'{keyword}' 검색 결과가 없습니다")
            return []

        # 최대 개수만큼만 처리
        job_links = job_links[:max_jobs]
        self.logger.info(f"{len(job_links)}개 공고 상세 정보 수집 시작")

        # 각 공고 상세 정보 수집
        all_jobs = []
        for i, job_url in enumerate(job_links, 1):
            try:
                self.logger.info(f"[{i}/{len(job_links)}] 공고 처리 중...")
                job_info = self.parse_job_detail(job_url)

                if job_info:
                    all_jobs.append(job_info)
                    self.logger.info(f"✓ 수집 완료: {job_info['title'][:50]}")

                # 요청 간 대기
                time.sleep(1)

            except Exception as e:
                self.logger.error(f"공고 처리 중 오류 ({job_url}): {e}")
                continue

        self.logger.info(f"총 {len(all_jobs)}개 공고 수집 완료")
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

        # 파일명 생성 (사이트명_키워드_타임스탬프.json)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 파일명에 특수문자 제거
        safe_keyword = re.sub(r'[<>:"/\\|?*]', '_', keyword)
        filename = f"albamon_{safe_keyword}_{timestamp}.json"

        filepath = save_json(data, filename)
        self.logger.info(f"결과 저장 완료: {filepath}")


if __name__ == "__main__":
    # 테스트 실행
    crawler = AlbamonCrawler(headless=False)
    try:
        crawler.start()
        jobs = crawler.crawl("반도체", max_jobs=3)
        if jobs:
            crawler.save_results("반도체", jobs)
            print(f"\n✅ 테스트 완료: {len(jobs)}개 공고 수집")
        else:
            print("\n⚠️  수집된 공고가 없습니다")
    finally:
        crawler.close()
