"""
하이브레인넷 채용 공고 크롤러 (React SPA 버전)
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


class HibrainCrawler:
    """하이브레인넷 채용 공고 크롤러 (React SPA)"""

    def __init__(self, headless: bool = True):
        """
        Args:
            headless: 브라우저를 헤드리스 모드로 실행할지 여부
        """
        self.logger = setup_logger("HibrainCrawler")
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
        """브라우저 시작 (Bot detection 회피 포함)"""
        self.playwright = sync_playwright().start()

        # Bot detection 회피 설정
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )

        # User Agent 설정 (일반 브라우저로 위장)
        self.page = self.browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # navigator.webdriver 제거 (봇 감지 회피)
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        self.page.set_viewport_size({"width": 1920, "height": 1080})
        self.logger.info("브라우저 시작 완료")

    def close(self):
        """브라우저 종료"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        self.logger.info("브라우저 종료 완료")

    def _clean_text(self, text: str, max_length: int = None) -> str:
        """텍스트 정리"""
        if not text:
            return ""

        text = re.sub(r'\s+', ' ', text).strip()

        if max_length and len(text) > max_length:
            text = text[:max_length] + "..."

        return text

    def get_job_list_with_preview(self, list_type: str = "ING", max_jobs: int = 50) -> List[Dict]:
        """
        React SPA에서 공고 목록과 미리보기 정보를 함께 수집
        (상세 페이지 접근 불필요 - 리스트 페이지에서 충분한 정보 확보)

        Args:
            list_type: "RECOMM"(추천), "D3NEW"(신규), "ING"(진행), "D0END"(오늘마감), "DEND"(마감)
            max_jobs: 최대 수집할 공고 수

        Returns:
            공고 정보 리스트 (title, company, date, content, link 포함)
        """
        jobs = []
        try:
            # React SPA 메인 페이지로 이동
            recruitment_url = f"{self.config['recruitment_url']}/recruits?listType={list_type}"
            self.logger.info(f"React SPA 페이지로 이동: {recruitment_url}")

            # Level 1: domcontentloaded (빠르고 안정적)
            self.page.goto(recruitment_url, wait_until="domcontentloaded", timeout=60000)

            # Level 2: networkidle (선택적, 타임아웃 허용)
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except:
                self.logger.debug("networkidle 타임아웃 (정상 - React SPA는 계속 로딩)")
                pass

            # Level 3: 실제 요소 확인 (필수) - React 렌더링 대기
            try:
                self.page.wait_for_selector('.recruitTitle', timeout=15000, state="visible")
                self.logger.info("React 컴포넌트 렌더링 완료")
            except:
                self.logger.warning("공고 요소를 찾지 못함 - React 렌더링 실패 가능성")

            # Level 4: React 안정화 대기 (중요!)
            time.sleep(3)

            # JavaScript로 공고 정보 수집 (리스트 페이지에서 모든 정보 추출)
            jobs_data = self.page.evaluate("""
                () => {
                    const jobs = [];
                    const recruitTitles = document.querySelectorAll('.recruitTitle');

                    recruitTitles.forEach(titleEl => {
                        // 부모 컨테이너에서 모든 정보 추출
                        let container = titleEl.closest('a[href*="/recruitment/recruits/"]');

                        if (container) {
                            const job = {
                                title: titleEl.innerText.trim(),
                                company: titleEl.innerText.trim(),  // 회사명이 제목
                                content: '',
                                date: '',
                                link: ''
                            };

                            // 내용 추출
                            const contentEl = container.querySelector('.recruitContent');
                            if (contentEl) {
                                job.content = contentEl.innerText.trim();
                            }

                            // 날짜 추출
                            const dateEl = container.querySelector('.recruitDate');
                            if (dateEl) {
                                job.date = dateEl.innerText.trim();
                            }

                            // 링크 추출
                            const href = container.getAttribute('href');
                            if (href) {
                                job.link = href.startsWith('http') ? href : 'https://www.hibrain.net' + href;
                            }

                            jobs.push(job);
                        }
                    });

                    return jobs;
                }
            """)

            jobs = jobs_data[:max_jobs] if jobs_data else []
            self.logger.info(f"총 {len(jobs)}개의 공고 정보 수집")

            return jobs

        except Exception as e:
            self.logger.error(f"공고 목록 수집 중 오류: {e}", exc_info=True)
            return []

    def parse_job_detail(self, job_url: str) -> Optional[Dict]:
        """
        공고 상세 페이지에서 정보 파싱 (React SPA)

        Args:
            job_url: 공고 상세 페이지 URL

        Returns:
            파싱된 공고 정보 딕셔너리
        """
        try:
            self.logger.debug(f"공고 상세 페이지 접속: {job_url}")

            # Level 1: domcontentloaded
            self.page.goto(job_url, wait_until="domcontentloaded", timeout=60000)

            # Level 2: networkidle (선택적)
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass

            # Level 3: 실제 콘텐츠 대기
            try:
                self.page.wait_for_selector('.recruitTitle, h1, .title', timeout=10000, state="visible")
            except:
                self.logger.warning("제목 요소를 찾지 못함")

            # Level 4: React 렌더링 안정화
            time.sleep(3)

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

            # JavaScript로 정보 추출 (React SPA 구조)
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
                    const titleEl = document.querySelector('.recruitTitle, h1, h2, .title');
                    if (titleEl) {
                        result.title = titleEl.innerText.trim();
                    }

                    // 전체 텍스트에서 정보 추출
                    const bodyText = document.body.innerText;

                    // 회사명 패턴 매칭
                    const companyMatch = bodyText.match(/기업명[:\\s]*(.*?)(?=\\n|접수|모집|$)/i);
                    if (companyMatch) {
                        result.company = companyMatch[1].trim();
                    }

                    // 근무지 패턴 매칭
                    const locationMatch = bodyText.match(/근무지[:\\s]*(.*?)(?=\\n|접수|모집|$)/i);
                    if (locationMatch) {
                        result.location = locationMatch[1].trim();
                    }

                    // 급여 패턴 매칭
                    const salaryMatch = bodyText.match(/급여|연봉[:\\s]*(.*?)(?=\\n|접수|모집|$)/i);
                    if (salaryMatch) {
                        result.salary = salaryMatch[1].trim();
                    }

                    // 지원자격 추출
                    const conditionsMatch = bodyText.match(/지원자격[\\s\\S]{0,1000}(?=접수기간|모집요강|$)/i);
                    if (conditionsMatch) {
                        result.conditions = conditionsMatch[0].trim();
                    }

                    // 마감일 추출
                    const dateMatch = bodyText.match(/(\\d{4}\\.\\d{1,2}\\.\\d{1,2}[^\\n]{0,30})(?=.*마감|$)/);
                    if (dateMatch) {
                        result.posted_date = dateMatch[1].trim();
                    }

                    // 상세 내용 (전체 텍스트)
                    result.detail = bodyText.trim();

                    // 모집요강 요약
                    result.recruit_summary = bodyText.substring(0, 2000);

                    return result;
                }
            """)

            job_info.update(parsed_data)

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

    def _matches_keyword(self, job_info: Dict, keyword: str) -> bool:
        """
        공고가 키워드와 매칭되는지 확인 (상세 정보 기반)

        Args:
            job_info: 공고 정보
            keyword: 검색 키워드

        Returns:
            매칭 여부
        """
        # 검색할 텍스트 구성
        search_fields = [
            job_info.get('title', ''),
            job_info.get('company', ''),
            job_info.get('location', ''),
            job_info.get('conditions', ''),
            job_info.get('recruit_summary', ''),
        ]

        text_to_search = ' '.join(search_fields).lower()
        keyword_lower = keyword.lower()

        return keyword_lower in text_to_search

    def _matches_keyword_preview(self, job: Dict, keyword: str) -> bool:
        """
        공고가 키워드와 매칭되는지 확인 (미리보기 정보 기반)

        Args:
            job: 리스트 페이지에서 추출한 공고 미리보기 정보
            keyword: 검색 키워드

        Returns:
            매칭 여부
        """
        # 검색할 텍스트 구성 (리스트 페이지에서 사용 가능한 필드만)
        search_fields = [
            job.get('title', ''),
            job.get('company', ''),
            job.get('content', ''),
            job.get('date', ''),
        ]

        text_to_search = ' '.join(search_fields).lower()
        keyword_lower = keyword.lower()

        return keyword_lower in text_to_search

    def crawl(self, keyword: str, max_jobs: int = 50) -> List[Dict]:
        """
        키워드로 검색하여 공고 수집 (클라이언트 사이드 필터링)

        Args:
            keyword: 검색 키워드
            max_jobs: 최대 수집할 공고 수

        Returns:
            수집된 공고 정보 리스트
        """
        self.logger.info(f"'{keyword}' 키워드로 크롤링 시작 (React SPA)")

        # React SPA에서 진행 중인 공고 목록과 미리보기 정보를 함께 수집
        all_jobs = self.get_job_list_with_preview(list_type="ING", max_jobs=max_jobs * 3)

        if not all_jobs:
            self.logger.warning("수집된 공고가 없습니다")
            return []

        # 키워드 필터링
        matching_jobs = []
        for i, job in enumerate(all_jobs, 1):
            try:
                # 키워드 매칭 확인 (리스트 페이지의 미리보기 정보로 필터링)
                if self._matches_keyword_preview(job, keyword):
                    # 데이터베이스 스키마에 맞게 변환
                    formatted_job = {
                        "url": job.get("link", ""),
                        "title": job.get("title", ""),
                        "company": job.get("company", ""),
                        "location": "",  # 리스트 페이지에 없음
                        "salary": "",  # 리스트 페이지에 없음
                        "conditions": "",  # 리스트 페이지에 없음
                        "detail": job.get("content", ""),
                        "recruit_summary": job.get("content", ""),
                        "posted_date": job.get("date", "")
                    }

                    matching_jobs.append(formatted_job)
                    self.logger.info(f"✓ 키워드 매칭 ({i}/{len(all_jobs)}): {job.get('title', 'N/A')}")

                    # 목표 개수 달성 시 중단
                    if len(matching_jobs) >= max_jobs:
                        break
                else:
                    self.logger.debug(f"✗ 키워드 미매칭 ({i}/{len(all_jobs)}): {job.get('title', 'N/A')}")

            except Exception as e:
                self.logger.error(f"공고 처리 중 오류: {e}")
                continue

        self.logger.info(f"총 {len(matching_jobs)}개의 키워드 매칭 공고 수집 완료")
        return matching_jobs

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
        filename = f"hibrain_{safe_keyword}_{timestamp}.json"

        filepath = save_json(data, filename)
        self.logger.info(f"결과 저장 완료: {filepath}")


if __name__ == "__main__":
    # 테스트 실행
    crawler = HibrainCrawler(headless=False)
    try:
        crawler.start()
        jobs = crawler.crawl("반도체", max_jobs=3)
        if jobs:
            crawler.save_results("반도체", jobs)
            print(f"\n수집된 공고 개수: {len(jobs)}")
            for i, job in enumerate(jobs, 1):
                print(f"{i}. {job.get('title', 'N/A')} - {job.get('company', 'N/A')}")
    finally:
        crawler.close()
