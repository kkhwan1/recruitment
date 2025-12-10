"""
잡포스팅 채용 공고 크롤러
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


class JobPostingCrawler:
    """잡포스팅 채용 공고 크롤러"""

    def __init__(self, headless: bool = True):
        """
        Args:
            headless: 브라우저를 헤드리스 모드로 실행할지 여부
        """
        self.logger = setup_logger("JobPostingCrawler")
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
            # 검색 URL 구성 (employ.php에 keyword 파라미터 사용)
            search_url = f"{self.config['base_url']}/job/employ.php?keyword={keyword}"
            self.logger.info(f"검색 페이지 접속: {search_url}")

            self.page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(self.config.get("wait_time", 3))

            # employ_detail.php 패턴의 링크 수집 (테이블 내부 h3 태그 안)
            links_data = self.page.evaluate("""
                () => {
                    const links = [];
                    const baseUrl = 'http://jobposting.co.kr';

                    // 테이블 내부의 h3 > a 링크 (채용공고 제목 링크)
                    const jobLinks = document.querySelectorAll('table h3 a[href*="employ_detail.php"]');

                    jobLinks.forEach(link => {
                        const href = link.getAttribute('href');
                        if (!href) return;

                        // 상대 경로를 절대 경로로 변환
                        let fullUrl;
                        if (href.startsWith('http://') || href.startsWith('https://')) {
                            fullUrl = href;
                        } else if (href.startsWith('/')) {
                            fullUrl = baseUrl + href;
                        } else {
                            fullUrl = baseUrl + '/job/' + href;
                        }

                        // 중복 방지
                        if (!links.includes(fullUrl)) {
                            links.push(fullUrl);
                        }
                    });

                    return links;
                }
            """)

            job_links = links_data if links_data else []

            # 링크가 없는 경우 페이지 상태 확인
            if not job_links:
                self.logger.warning("공고 링크를 찾지 못했습니다. 페이지 상태 확인 중...")
                page_text = self.page.evaluate('() => document.body.innerText.substring(0, 500)')
                self.logger.debug(f"페이지 내용 샘플: {page_text}")

            # 최대 개수만큼만 반환
            if len(job_links) > max_jobs:
                job_links = job_links[:max_jobs]

            self.logger.info(f"총 {len(job_links)}개의 공고 링크 수집")
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
        max_retries = self.config.get("max_retries", 3)
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"공고 상세 페이지 접속: {job_url} (시도 {attempt + 1}/{max_retries})")
                self.page.goto(job_url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(self.config.get("wait_time", 3))

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

                    // 제목 추출 (h2 태그 - 공고 제목 패턴)
                    const h2Tags = document.querySelectorAll('h2');
                    for (const h2 of h2Tags) {
                        const text = h2.innerText.trim();
                        // 공고 제목 패턴: 지역이나 회사명을 포함하는 긴 텍스트
                        if (text && !text.includes('주요업무') && !text.includes('자격요건') &&
                            !text.includes('추가사항') && !text.includes('Job Description') &&
                            !text.includes('Job Requirements') && !text.includes('Additional Information')) {
                            // 제목은 보통 [지역] 형태를 포함하거나 길이가 15자 이상
                            if (text.includes('[') || text.length > 15) {
                                result.title = text;
                                break;
                            }
                        }
                    }

                    // 제목이 없으면 첫 번째 h2 사용 (섹션 제목이 아닌 경우)
                    if (!result.title && h2Tags.length > 0) {
                        const firstH2 = h2Tags[0].innerText.trim();
                        if (firstH2 && !firstH2.includes('주요업무') && !firstH2.includes('자격요건')) {
                            result.title = firstH2;
                        }
                    }

                    // 회사명 추출 (h3 태그)
                    const h3 = document.querySelector('h3');
                    if (h3) result.company = h3.innerText.trim();

                    // 전체 페이지 텍스트
                    const bodyText = document.body.innerText;
                    result.detail = bodyText;

                    // 테이블에서 정보 추출
                    const tables = document.querySelectorAll('table');
                    tables.forEach(table => {
                        const rows = table.querySelectorAll('tr');
                        rows.forEach(row => {
                            const cells = row.querySelectorAll('td, th');
                            if (cells.length >= 2) {
                                const label = cells[0].innerText.trim();
                                const value = cells[1].innerText.trim();

                                // 근무지
                                if (label.includes('근무지') || label.includes('위치')) {
                                    result.location = value;
                                }
                                // 급여
                                if (label.includes('급여') || label.includes('연봉')) {
                                    result.salary = value;
                                }
                            }
                        });
                    });

                    // 주요업무, 자격요건 추출
                    const sections = [];
                    const allH2 = document.querySelectorAll('h2');
                    allH2.forEach(h2 => {
                        const sectionTitle = h2.innerText.trim();
                        if (sectionTitle.includes('주요업무') || sectionTitle.includes('자격요건') ||
                            sectionTitle.includes('추가사항')) {
                            // 다음 형제 요소들의 텍스트 수집
                            let content = sectionTitle + '\\n';
                            let sibling = h2.nextElementSibling;
                            while (sibling && sibling.tagName !== 'H2') {
                                content += sibling.innerText.trim() + '\\n';
                                sibling = sibling.nextElementSibling;
                            }
                            sections.push(content);
                        }
                    });

                    if (sections.length > 0) {
                        result.conditions = sections.join('\\n\\n');
                        result.recruit_summary = sections.join('\\n\\n');
                    }

                    return result;
                }
            """)

                job_info = {
                    "url": job_url,
                    "title": parsed_data.get("title", ""),
                    "company": parsed_data.get("company", ""),
                    "location": self._clean_text(parsed_data.get("location", ""), max_length=200),
                    "salary": self._clean_text(parsed_data.get("salary", ""), max_length=100),
                    "conditions": self._clean_text(parsed_data.get("conditions", ""), max_length=1000),
                    "detail": parsed_data.get("detail", ""),
                    "recruit_summary": self._clean_text(parsed_data.get("recruit_summary", ""), max_length=2000),
                    "posted_date": self._clean_text(parsed_data.get("posted_date", ""), max_length=50)
                }

                # 제목이 없으면 스킵
                if not job_info["title"]:
                    self.logger.warning(f"제목을 찾을 수 없어 스킵: {job_url}")
                    return None

                # 정규표현식으로 추가 정보 추출 (fallback)
                if job_info["detail"]:
                    job_info = self._extract_fields_from_detail(job_info)

                self.logger.info(f"공고 파싱 완료: {job_info['title']} - {job_info.get('company', 'N/A')}")
                return job_info

            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"공고 상세 파싱 시도 {attempt + 1} 실패, 재시도 중: {e}")
                    time.sleep(2)
                    continue
                else:
                    self.logger.error(f"공고 상세 파싱 최종 실패 ({job_url}): {e}", exc_info=True)
                    return None
        
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

        # 급여 추출 (없는 경우)
        if not job_info.get("salary"):
            salary_patterns = [
                r'급여[\s:]*([^\n]{10,100})',
                r'연봉[\s:]*([^\n]{10,100})',
            ]
            for pattern in salary_patterns:
                match = re.search(pattern, detail)
                if match:
                    job_info["salary"] = match.group(1).strip()
                    break

        # 근무지 추출 (없는 경우)
        if not job_info.get("location"):
            location_patterns = [
                r'근무지[\s:]*([^\n]{10,150})',
                r'위치[\s:]*([^\n]{10,150})',
                r'(서울|경기|인천|부산|대구|광주|대전|울산|세종)[^\n]{0,100}',
            ]
            for pattern in location_patterns:
                match = re.search(pattern, detail)
                if match:
                    location = match.group(1) if match.groups() else match.group(0)
                    job_info["location"] = location.strip()
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
        self.logger.info(f"'{keyword}' 키워드로 크롤링 시작 (최대 {max_jobs}개)")

        # 1. 공고 링크 목록 수집
        job_links = self.get_job_list(keyword, max_jobs)

        if not job_links:
            self.logger.warning("공고 링크를 찾을 수 없습니다")
            return []

        # 2. 각 공고 상세 정보 파싱
        jobs = []
        for i, job_url in enumerate(job_links, 1):
            try:
                self.logger.info(f"공고 수집 중: {i}/{len(job_links)}")
                job_info = self.parse_job_detail(job_url)

                if job_info:
                    jobs.append(job_info)

                # 요청 간 대기
                time.sleep(self.config.get("request_delay", 2))

            except Exception as e:
                self.logger.error(f"공고 처리 중 오류 ({job_url}): {e}")
                continue

        self.logger.info(f"총 {len(jobs)}개의 공고 수집 완료")
        return jobs

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
        filename = f"jobposting_{safe_keyword}_{timestamp}.json"

        filepath = save_json(data, filename)
        self.logger.info(f"결과 저장 완료: {filepath}")


if __name__ == "__main__":
    # 테스트 실행
    crawler = JobPostingCrawler(headless=False)
    try:
        crawler.start()
        jobs = crawler.crawl("반도체", max_jobs=3)
        if jobs:
            crawler.save_results("반도체", jobs)
            print(f"\n수집 완료: {len(jobs)}개 공고")
            for job in jobs:
                print(f"- {job['title']} ({job['company']})")
    finally:
        crawler.close()
