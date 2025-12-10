"""
사람인 채용 공고 크롤러
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


class SaraminCrawler:
    """사람인 채용 공고 크롤러"""

    def __init__(self, headless: bool = True):
        """
        Args:
            headless: 브라우저를 헤드리스 모드로 실행할지 여부
        """
        self.logger = setup_logger("SaraminCrawler")
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
        """브라우저 시작"""
        self.playwright = sync_playwright().start()

        # Bot detection 회피를 위한 설정
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',  # automation detection 비활성화
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )

        # 일반 브라우저처럼 보이도록 user agent 설정
        self.page = self.browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # navigator.webdriver 제거 (bot detection 회피)
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        self.page.set_viewport_size({"width": 1920, "height": 1080})
        self.logger.info("브라우저 시작 완료 (bot detection 회피 설정 적용)")

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

    def get_job_list(self, keyword: str, max_jobs: int = 50) -> List[str]:
        """
        키워드로 검색하여 공고 링크 목록 수집

        Args:
            keyword: 검색 키워드
            max_jobs: 최대 수집할 공고 수

        Returns:
            공고 링크 리스트
        """
        job_links = []
        try:
            search_url = self.config["search_url"].format(keyword=keyword)
            self.logger.info(f"검색 페이지로 이동: {search_url}")

            # 1. 기본 DOM 로드까지만 대기 (networkidle은 사람인에서 너무 오래 걸림)
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            self.logger.info("초기 페이지 로드 완료 (domcontentloaded)")

            # 2. 추가 네트워크 요청 완료 대기 (최대 10초, 실패해도 계속 진행)
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
                self.logger.info("네트워크 안정화 완료")
            except:
                self.logger.warning("네트워크 idle 타임아웃 (계속 진행)")

            # 3. 공고 컨테이너가 실제로 렌더링될 때까지 대기
            # 여러 셀렉터 중 하나라도 나타날 때까지 대기
            selectors_to_wait = [
                'a[href*="/zf_user/jobs/relay/view"]',
                'a[href*="/zf_user/"]',
                '.item_recruit a',
                'a.job_tit'
            ]

            element_found = False
            for selector in selectors_to_wait:
                try:
                    self.page.wait_for_selector(selector, timeout=5000, state="visible")
                    self.logger.info(f"공고 링크 요소 발견: {selector}")
                    element_found = True
                    break
                except:
                    continue

            if not element_found:
                self.logger.warning("공고 링크 요소를 찾지 못함 - 페이지 구조 변경 가능성")

            # 4. JavaScript 실행이 완료될 때까지 추가 대기
            try:
                self.page.wait_for_load_state("load", timeout=10000)
                self.logger.info("페이지 load 상태 완료")
            except:
                self.logger.warning("페이지 load 타임아웃 (계속 진행)")

            # 5. 동적 콘텐츠 렌더링을 위한 대기 (DOM 안정화)
            time.sleep(2)

            self.logger.info("페이지 로드 완료, 공고 링크 수집 시작")

            # 7. 안정적인 상태에서 JavaScript 실행
            job_links_data = self.page.evaluate("""
                () => {
                    const links = [];

                    // 사람인 공고 링크 패턴들을 시도
                    const selectors = [
                        'a[href*="/zf_user/jobs/relay/view"]',  // 사람인 상세 페이지 패턴
                        'a[href*="/zf_user/"]',                  // zf_user 포함 링크
                        '.item_recruit a',                       // 공고 아이템 링크
                        'a.job_tit',                            // 공고 제목 링크
                        'a[class*="tit"]'                       // tit 클래스 링크
                    ];

                    // 각 셀렉터로 링크 수집 시도
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(link => {
                            const href = link.getAttribute('href');
                            if (href) {
                                // rec_idx 파라미터가 있는 링크만 수집
                                if (href.includes('rec_idx=') || href.includes('/view/')) {
                                    const fullUrl = href.startsWith('http') ? href : 'https://www.saramin.co.kr' + href;
                                    if (!links.includes(fullUrl)) {
                                        links.push(fullUrl);
                                    }
                                }
                            }
                        });

                        if (links.length > 0) {
                            console.log(`Found ${links.length} links with selector: ${selector}`);
                            break;
                        }
                    }

                    // 발견된 모든 링크 출력 (디버깅용)
                    if (links.length === 0) {
                        console.log('No links found. Sample href patterns:');
                        const allLinks = document.querySelectorAll('a[href]');
                        const samples = [];
                        allLinks.forEach((link, idx) => {
                            const href = link.getAttribute('href');
                            if (href && (href.includes('zf_user') || href.includes('recruit') || href.includes('job'))) {
                                samples.push(href);
                            }
                        });
                        // 중복 제거 후 처음 10개 출력
                        const uniqueSamples = [...new Set(samples)].slice(0, 10);
                        uniqueSamples.forEach(href => console.log(href));
                    }

                    return links;
                }
            """)

            job_links = job_links_data[:max_jobs] if job_links_data else []
            self.logger.info(f"총 {len(job_links)}개의 공고 링크 발견")

            # 링크가 없으면 페이지 HTML 구조 로깅
            if not job_links:
                self.logger.warning("공고 링크를 찾을 수 없습니다. HTML 구조를 확인하세요.")
                # 페이지의 일부 HTML 출력
                try:
                    sample_html = self.page.evaluate("() => document.body.innerHTML.substring(0, 2000)")
                    self.logger.debug(f"페이지 HTML 샘플: {sample_html}")
                except:
                    self.logger.warning("HTML 샘플 수집 실패 - 페이지가 불안정함")

            return job_links

        except Exception as e:
            self.logger.error(f"공고 목록 수집 중 오류: {e}", exc_info=True)
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
                    const titleSelectors = [
                        '.tit_job',
                        '.recruit_tit',
                        'h1',
                        '.job_tit',
                        '.wrap_jv_cont h1'
                    ];
                    for (const selector of titleSelectors) {
                        const titleEl = document.querySelector(selector);
                        if (titleEl && titleEl.innerText.trim()) {
                            result.title = titleEl.innerText.trim();
                            break;
                        }
                    }

                    // 회사명 추출
                    const companySelectors = [
                        '.company',
                        '.corp_name',
                        'a.str_tit',
                        '.company_nm',
                        '.wrap_jv_cont .company'
                    ];
                    for (const selector of companySelectors) {
                        const companyEl = document.querySelector(selector);
                        if (companyEl && companyEl.innerText.trim()) {
                            result.company = companyEl.innerText.trim();
                            break;
                        }
                    }

                    // 모든 dd, dt 요소에서 정보 추출
                    const dts = document.querySelectorAll('dt');
                    dts.forEach(dt => {
                        const label = dt.innerText.trim();
                        const dd = dt.nextElementSibling;
                        if (!dd) return;
                        const value = dd.innerText.trim();

                        if (label.includes('근무지역') || label.includes('근무 지역')) {
                            result.location = value;
                        } else if (label.includes('급여') || label.includes('연봉')) {
                            result.salary = value;
                        } else if (label.includes('마감일') || label.includes('접수기간')) {
                            result.posted_date = value;
                        }
                    });

                    // 지원자격 추출
                    const qualificationSelectors = [
                        '.jv_cont.jv_summary',
                        '.content'
                    ];
                    for (const selector of qualificationSelectors) {
                        const qualEl = document.querySelector(selector);
                        if (qualEl) {
                            const text = qualEl.innerText.trim();
                            if (text.includes('자격') || text.includes('요건')) {
                                result.conditions = text.substring(0, 500);
                                break;
                            }
                        }
                    }

                    // 상세 내용 (전체 페이지 내용)
                    const detailSelectors = [
                        '#content',
                        '.wrap_jv_cont',
                        '.jv_cont',
                        'main',
                        'article'
                    ];
                    for (const selector of detailSelectors) {
                        const detailEl = document.querySelector(selector);
                        if (detailEl && detailEl.innerText.trim()) {
                            result.detail = detailEl.innerText.trim();
                            break;
                        }
                    }

                    // 모집요강 요약
                    const summarySelectors = [
                        '.jv_cont.jv_summary',
                        '.wrap_jv_summary',
                        '.summary'
                    ];
                    for (const selector of summarySelectors) {
                        const summaryEl = document.querySelector(selector);
                        if (summaryEl) {
                            result.recruit_summary = summaryEl.innerText.trim();
                            break;
                        }
                    }

                    return result;
                }
            """)

            # 파싱된 데이터를 job_info에 반영
            job_info.update(parsed_data)

            # 텍스트 정리
            job_info["title"] = self._clean_text(job_info["title"])
            job_info["company"] = self._clean_text(job_info["company"])
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

    def crawl(self, keyword: str, max_jobs: int = 50) -> List[Dict]:
        """
        키워드로 검색하여 공고 수집

        Args:
            keyword: 검색 키워드
            max_jobs: 최대 수집할 공고 수

        Returns:
            수집된 공고 정보 리스트
        """
        self.logger.info(f"사람인 크롤링 시작 (키워드: {keyword}, 최대: {max_jobs}개)")

        # 1. 공고 링크 목록 수집
        job_links = self.get_job_list(keyword, max_jobs)

        if not job_links:
            self.logger.warning("수집된 공고 링크가 없습니다")
            return []

        # 2. 각 공고 상세 정보 파싱
        all_jobs = []
        for i, job_url in enumerate(job_links, 1):
            try:
                self.logger.info(f"공고 처리 중: {i}/{len(job_links)}")
                job_info = self.parse_job_detail(job_url)

                if job_info:
                    all_jobs.append(job_info)

                # 요청 간 대기
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
        filename = f"saramin_{safe_keyword}_{timestamp}.json"

        filepath = save_json(data, filename)
        self.logger.info(f"결과 저장 완료: {filepath}")


if __name__ == "__main__":
    # 테스트 실행
    crawler = SaraminCrawler(headless=False)
    try:
        crawler.start()
        jobs = crawler.crawl("반도체", max_jobs=3)
        if jobs:
            crawler.save_results("반도체", jobs)
            print(f"\n수집 완료: {len(jobs)}개 공고")
            for job in jobs:
                print(f"- {job['title']} ({job.get('company', 'N/A')})")
    finally:
        crawler.close()
