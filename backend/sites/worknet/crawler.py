"""
워크넷 채용 공고 크롤러
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


class WorknetCrawler:
    """워크넷 채용 공고 크롤러"""

    def __init__(self, headless: bool = True):
        """
        Args:
            headless: 브라우저를 헤드리스 모드로 실행할지 여부
        """
        self.logger = setup_logger("WorknetCrawler")
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
        키워드로 검색 - URL 직접 접속

        Args:
            keyword: 검색 키워드

        Returns:
            검색 성공 여부
        """
        try:
            # 검색 URL로 직접 이동
            search_url = self.config["search_url"].format(keyword=keyword)
            self.logger.info(f"검색 URL로 이동: {search_url}")
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(self.config.get("wait_time", 5))
            
            # 검색 결과 페이지 로딩 대기
            self.page.wait_for_load_state("networkidle", timeout=10000)

            # 5. 결과 개수 확인
            result_count = self.page.evaluate("""
                () => {
                    const countElements = document.querySelectorAll('[id*="Cnt"], [id*="cnt"], .count, [class*="count"]');
                    for (const el of countElements) {
                        const text = el.innerText || el.textContent;
                        if (text && text.match(/\d+/)) {
                            return text.trim();
                        }
                    }
                    return '0';
                }
            """)

            self.logger.info(f"'{keyword}' 검색 완료 - 결과: {result_count}")
            return True

        except Exception as e:
            self.logger.error(f"검색 중 오류 발생: {e}", exc_info=True)
            return False

    def get_job_list(self) -> List[str]:
        """
        현재 페이지의 공고 목록에서 공고 링크 수집
        워크넷은 동적으로 로드되므로 여러 패턴 시도

        Returns:
            공고 링크 리스트
        """
        job_links = []
        try:
            # 페이지가 완전히 로드될 때까지 대기
            self.logger.info("공고 목록 로딩 대기...")
            time.sleep(3)

            # JavaScript로 공고 링크 수집
            links_data = self.page.evaluate("""
                () => {
                    const links = new Set();
                    const baseUrl = 'https://www.work24.go.kr';

                    // 패턴 1: onclick 속성에서 추출
                    document.querySelectorAll('a[onclick]').forEach(el => {
                        const onclick = el.getAttribute('onclick');
                        const text = el.innerText.trim();

                        // 공고 상세보기 함수 패턴 (goDetail, openDetail, viewDetail 등)
                        const patterns = [
                            /goDetail.*?['"]([^'"]+)['"]/,
                            /openDetail.*?['"]([^'"]+)['"]/,
                            /viewDetail.*?['"]([^'"]+)['"]/,
                            /fn_goEmpDetail.*?['"]([^'"]+)['"]/,
                            /wantedAuthNo.*?['"]([^'"]+)['"]/,
                            /empId.*?['"]([^'"]+)['"]/
                        ];

                        for (const pattern of patterns) {
                            const match = onclick.match(pattern);
                            if (match && text && text.length > 5) {
                                const param = match[1];
                                // URL 구성 (여러 가능한 패턴 시도)
                                const urls = [
                                    `${baseUrl}/empInfo/empInfoSrch/detail/empDetailAuthView.do?wantedAuthNo=${param}`,
                                    `${baseUrl}/wk/a/b/1200/empDetailAuthView.do?wantedAuthNo=${param}`,
                                    `${baseUrl}/empDetail?id=${param}`
                                ];
                                urls.forEach(url => links.add(url));
                                break;
                            }
                        }
                    });

                    // 패턴 2: href 속성에서 추출
                    document.querySelectorAll('a[href]').forEach(el => {
                        const href = el.getAttribute('href');
                        const text = el.innerText.trim();

                        if (href && text && text.length > 5) {
                            // 공고 상세 페이지 URL 패턴
                            if (href.includes('empDetail') ||
                                href.includes('wantedAuthNo') ||
                                href.includes('/detail/') ||
                                href.includes('jobDetail')) {

                                let fullUrl = href;
                                if (href.startsWith('http')) {
                                    fullUrl = href;
                                } else if (href.startsWith('/')) {
                                    fullUrl = baseUrl + href;
                                } else if (!href.startsWith('javascript')) {
                                    fullUrl = baseUrl + '/' + href;
                                }

                                if (fullUrl.startsWith('http')) {
                                    links.add(fullUrl);
                                }
                            }
                        }
                    });

                    // 패턴 3: data 속성에서 추출
                    document.querySelectorAll('[data-wanted-no], [data-emp-id], [data-job-id]').forEach(el => {
                        const wantedNo = el.getAttribute('data-wanted-no') ||
                                       el.getAttribute('data-emp-id') ||
                                       el.getAttribute('data-job-id');
                        if (wantedNo) {
                            const url = `${baseUrl}/empInfo/empInfoSrch/detail/empDetailAuthView.do?wantedAuthNo=${wantedNo}`;
                            links.add(url);
                        }
                    });

                    // 패턴 4: 리스트 아이템에서 추출
                    const listSelectors = [
                        '.list_result li a',
                        '.result_list li a',
                        '.job_list li a',
                        'ul.list li a',
                        'table tbody tr a',
                        '[class*="list"] [class*="item"] a',
                        '[id*="list"] a'
                    ];

                    for (const selector of listSelectors) {
                        try {
                            document.querySelectorAll(selector).forEach(el => {
                                const href = el.getAttribute('href');
                                const onclick = el.getAttribute('onclick');
                                const text = el.innerText.trim();

                                if (text && text.length > 5) {
                                    if (onclick && onclick.includes('Detail')) {
                                        // onclick 처리는 위에서 했음
                                    } else if (href && href.includes('empDetail')) {
                                        let fullUrl = href;
                                        if (!href.startsWith('http')) {
                                            fullUrl = href.startsWith('/') ? baseUrl + href : baseUrl + '/' + href;
                                        }
                                        links.add(fullUrl);
                                    }
                                }
                            });
                        } catch (e) {
                            // selector 오류 무시
                        }
                    }

                    return Array.from(links);
                }
            """)

            job_links = links_data if links_data else []

            # 중복 제거 및 정리
            job_links = list(set(job_links))

            self.logger.info(f"총 {len(job_links)}개의 공고 링크 수집")

            # 디버깅: 처음 3개 링크 출력
            if job_links:
                self.logger.debug("수집된 링크 샘플:")
                for i, link in enumerate(job_links[:3], 1):
                    self.logger.debug(f"  {i}. {link}")

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

            # JavaScript로 정확한 정보 추출
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
                        'h3.tit',
                        'h2.tit',
                        '.employ-tit',
                        '.detail-tit',
                        'h1'
                    ];
                    for (const selector of titleSelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.innerText.trim()) {
                            result.title = el.innerText.trim();
                            break;
                        }
                    }

                    // 회사명 추출
                    const companySelectors = [
                        '.cp-name',
                        '.company-name',
                        'h2.name',
                        '.employ-info .name'
                    ];
                    for (const selector of companySelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.innerText.trim()) {
                            result.company = el.innerText.trim();
                            break;
                        }
                    }

                    // 근무지 추출
                    const locationSelectors = [
                        '.work-place',
                        '.location',
                        'dd:has(> span:contains("근무지"))',
                    ];
                    for (const selector of locationSelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.innerText.trim()) {
                            result.location = el.innerText.trim();
                            break;
                        }
                    }

                    // 급여 추출
                    const salarySelectors = [
                        '.pay',
                        '.salary',
                        'dd:has(> span:contains("급여"))',
                    ];
                    for (const selector of salarySelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.innerText.trim()) {
                            result.salary = el.innerText.trim();
                            break;
                        }
                    }

                    // 상세 내용 추출
                    const detailSelectors = [
                        '.detail-view',
                        '.employ-detail',
                        '.contents-area',
                        'main',
                        'body'
                    ];
                    for (const selector of detailSelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.innerText.trim()) {
                            result.detail = el.innerText.trim();
                            break;
                        }
                    }

                    // 등록일/마감일 추출
                    const dateSelectors = [
                        '.date',
                        '.employ-date',
                        'dd:has(> span:contains("등록일"))',
                        'dd:has(> span:contains("마감일"))'
                    ];
                    for (const selector of dateSelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.innerText.trim()) {
                            result.posted_date = el.innerText.trim();
                            break;
                        }
                    }

                    return result;
                }
            """)

            # 파싱된 데이터를 job_info에 반영
            job_info.update(parsed_data)

            # detail에서 정보 추출 (fallback)
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
                r'(?:급여|연봉|시급|월급)[\s\n]*:?[\s\n]*([^\n]{0,100}?)(?=\n|근무시간|모집인원|$)',
                r'(?:급여|연봉)[\s\n]*([\d,~만원]+[^\n]{0,50})',
            ]
            for pattern in salary_patterns:
                match = re.search(pattern, detail, re.IGNORECASE)
                if match:
                    salary = match.group(1).strip()
                    salary = re.sub(r'근무시간.*|모집인원.*|지원자격.*', '', salary).strip()
                    if salary:
                        job_info["salary"] = salary
                        break

        # 근무지 추출
        if not job_info.get("location"):
            location_patterns = [
                r'(?:근무지|근무지역|지역|주소)[\s\n]*:?[\s\n]*([^\n]{0,150}?)(?=\n|지원자격|$)',
                r'(서울|경기|인천|부산|대구|광주|대전|울산|세종|강원|충북|충남|전북|전남|경북|경남|제주)[^\n]{0,100}',
            ]
            for pattern in location_patterns:
                match = re.search(pattern, detail, re.IGNORECASE)
                if match:
                    location = match.group(1).strip() if match.groups() else match.group(0).strip()
                    if location:
                        job_info["location"] = location.split('\n')[0]
                        break

        # 지원자격 추출
        if not job_info.get("conditions"):
            conditions_match = re.search(r'(?:지원자격|자격요건|모집조건|우대사항)[\s\S]{0,800}(?=전형절차|접수기간|기업정보|$)', detail, re.IGNORECASE)
            if conditions_match:
                job_info["conditions"] = conditions_match.group(0).strip()

        # 모집요강 요약 추출
        if not job_info.get("recruit_summary"):
            recruit_match = re.search(r'(?:모집요강|채용내용|모집내용|상세내용)[\s\S]{0,1500}(?=접수기간|기업정보|$)', detail, re.IGNORECASE)
            if recruit_match:
                job_info["recruit_summary"] = recruit_match.group(0).strip()

        # 마감일 추출
        if not job_info.get("posted_date"):
            date_patterns = [
                r'(?:마감일|등록일|접수기간|채용기간)[\s\n]*:?[\s\n]*(\d{4}[\s\-./]\d{1,2}[\s\-./]\d{1,2}[^\n]{0,30})',
                r'(\d{4}[\s\-./]\d{1,2}[\s\-./]\d{1,2}[^\n]{0,30})(?=.*마감|채용 시 마감)',
            ]
            for pattern in date_patterns:
                match = re.search(pattern, detail)
                if match:
                    job_info["posted_date"] = match.group(1).strip() if match.groups() else match.group(0).strip()
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
                time.sleep(self.config.get("request_delay", 2))  # 요청 간 대기
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

        # 파일명 생성 (사이트명_키워드_타임스탬프.json)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 파일명에 특수문자 제거
        safe_keyword = re.sub(r'[<>:"/\\|?*]', '_', keyword)
        filename = f"worknet_{safe_keyword}_{timestamp}.json"

        filepath = save_json(data, filename)
        self.logger.info(f"결과 저장 완료: {filepath}")


if __name__ == "__main__":
    # 테스트 실행
    crawler = WorknetCrawler(headless=False)
    try:
        crawler.start()
        jobs = crawler.crawl("반도체", max_jobs=3)
        if jobs:
            crawler.save_results("반도체", jobs)
            print(f"\n수집된 공고 수: {len(jobs)}")
            for job in jobs:
                print(f"- {job['title']} ({job['company']})")
    finally:
        crawler.close()
