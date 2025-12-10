"""
인쿠르트 채용 공고 크롤러
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


class IncruitCrawler:
    """인쿠르트 채용 공고 크롤러"""
    
    def __init__(self, headless: bool = True):
        """
        Args:
            headless: 브라우저를 헤드리스 모드로 실행할지 여부
        """
        self.logger = setup_logger("IncruitCrawler")
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
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
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
        키워드로 검색
        
        Args:
            keyword: 검색 키워드
            
        Returns:
            검색 성공 여부
        """
        try:
            search_url = self.config["search_url"].format(keyword=keyword)
            self.logger.info(f"검색 URL로 이동: {search_url}")
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(self.config.get("wait_time", 3))
            
            # 검색 결과 페이지가 로드될 때까지 대기
            self.page.wait_for_load_state("domcontentloaded")
            self.logger.info(f"'{keyword}' 검색 완료")
            return True
        except Exception as e:
            self.logger.error(f"검색 중 오류 발생: {e}", exc_info=True)
            return False
    
    def get_job_list(self) -> List[str]:
        """
        현재 페이지의 공고 목록에서 공고 링크 수집

        Returns:
            공고 링크 리스트
        """
        job_links = []
        try:
            # JavaScript로 더 정확하게 링크 수집
            links_data = self.page.evaluate("""
                () => {
                    const links = [];
                    // 인크루트의 실제 공고 링크 패턴: job.incruit.com/jobdb_info/jobpost.asp
                    document.querySelectorAll('a').forEach(el => {
                        const href = el.getAttribute('href');
                        if (href && (href.includes('job.incruit.com/jobdb_info/jobpost.asp') ||
                                   href.includes('/jobdb_info/jobpost.asp'))) {
                            if (!links.includes(href)) {
                                links.push(href);
                            }
                        }
                    });

                    return [...new Set(links)].map(link => {
                        if (link.startsWith('http')) {
                            return link;
                        } else if (link.startsWith('/')) {
                            return 'https://job.incruit.com' + link;
                        } else {
                            return 'https://job.incruit.com/' + link;
                        }
                    });
                }
            """)

            job_links = links_data if links_data else []
            self.logger.info(f"총 {len(job_links)}개의 공고 링크 수집")
            return job_links

        except Exception as e:
            self.logger.error(f"공고 목록 수집 중 오류: {e}")
            return []
    
    def parse_job_detail(self, job_url: str) -> Optional[Dict]:
        """
        공고 상세 페이지에서 정보 파싱 (정확도 향상)
        
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
                    
                    // 제목 추출 (h1)
                    const titleEl = document.querySelector('h1');
                    if (titleEl) result.title = titleEl.innerText.trim();
                    
                    // 회사명 추출
                    const companySelectors = ['h2', 'h3', '[class*="company"]', '[class*="corp"]'];
                    for (const selector of companySelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.innerText.trim()) {
                            result.company = el.innerText.trim();
                            break;
                        }
                    }
                    
                    // 상세 내용 (main 또는 body)
                    const mainEl = document.querySelector('main') || document.body;
                    if (mainEl) {
                        result.detail = mainEl.innerText.trim();
                    }
                    
                    // detail에서 정보 추출
                    const detail = result.detail;
                    
                    // 급여 패턴 찾기
                    const salaryMatch = detail.match(/(?:급여|연봉|시급|월급)[\\s\\n]*:?[\\s\\n]*([^\\n]{0,100})/i);
                    if (salaryMatch) {
                        result.salary = salaryMatch[1].trim();
                    }
                    
                    // 근무지 패턴 찾기
                    const locationMatch = detail.match(/(?:근무지|근무지역|지역|주소)[\\s\\n]*:?[\\s\\n]*([^\\n]{0,150})/i);
                    if (locationMatch) {
                        result.location = locationMatch[1].trim();
                    } else {
                        // 지역 패턴으로 찾기
                        const regionMatch = detail.match(/(서울|경기|인천|부산|대구|광주|대전|울산|세종|강원|충북|충남|전북|전남|경북|경남|제주|중국|홍콩|UAE)[^\\n]{0,100}/);
                        if (regionMatch) {
                            result.location = regionMatch[0].trim();
                        }
                    }
                    
                    // 지원자격 패턴 찾기
                    const conditionsMatch = detail.match(/(?:지원자격|자격요건|모집조건)[\\s\\S]{0,800}/i);
                    if (conditionsMatch) {
                        result.conditions = conditionsMatch[0].trim();
                    }
                    
                    // 모집요강 패턴 찾기
                    const recruitMatch = detail.match(/(?:모집요강|채용내용|상세내용)[\\s\\S]{0,1500}/i);
                    if (recruitMatch) {
                        result.recruit_summary = recruitMatch[0].trim();
                    }
                    
                    // 등록일/마감일 패턴 찾기
                    const dateMatch = detail.match(/(?:마감일|등록일|접수기간)[\\s\\n]*:?[\\s\\n]*(\\d{4}[\\s\\-./]\\d{1,2}[\\s\\-./]\\d{1,2}[^\\n]{0,30})/);
                    if (dateMatch) {
                        result.posted_date = dateMatch[1].trim();
                    }
                    
                    return result;
                }
            """)
            
            # 파싱된 데이터를 job_info에 반영
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
                r'(서울|경기|인천|부산|대구|광주|대전|울산|세종|강원|충북|충남|전북|전남|경북|경남|제주|중국|홍콩|UAE|상하이|베이징)[^\n]{0,100}',
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
            conditions_match = re.search(r'(?:지원자격|자격요건|모집조건)[\s\S]{0,800}(?=접수기간|기업정보|$)', detail, re.IGNORECASE)
            if conditions_match:
                job_info["conditions"] = conditions_match.group(0).strip()
        
        # 모집요강 요약 추출
        if not job_info.get("recruit_summary"):
            recruit_match = re.search(r'(?:모집요강|채용내용|상세내용)[\s\S]{0,1500}(?=접수기간|기업정보|$)', detail, re.IGNORECASE)
            if recruit_match:
                job_info["recruit_summary"] = recruit_match.group(0).strip()
        
        # 마감일 추출
        if not job_info.get("posted_date"):
            date_patterns = [
                r'(?:마감일|등록일|접수기간)[\s\n]*:?[\s\n]*(\d{4}[\s\-./]\d{1,2}[\s\-./]\d{1,2}[^\n]{0,30})',
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
                time.sleep(1)  # 요청 간 대기
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
        filename = f"incruit_{safe_keyword}_{timestamp}.json"
        
        filepath = save_json(data, filename)
        self.logger.info(f"결과 저장 완료: {filepath}")


if __name__ == "__main__":
    # 테스트 실행
    crawler = IncruitCrawler(headless=False)
    try:
        crawler.start()
        jobs = crawler.crawl("중국어", max_jobs=5)
        if jobs:
            crawler.save_results("중국어", jobs)
    finally:
        crawler.close()
