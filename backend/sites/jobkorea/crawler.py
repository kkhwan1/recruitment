"""
잡코리아 채용 공고 크롤러
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


class JobKoreaCrawler:
    """잡코리아 채용 공고 크롤러"""
    
    def __init__(self, headless: bool = True):
        """
        Args:
            headless: 브라우저를 헤드리스 모드로 실행할지 여부
        """
        self.logger = setup_logger("JobKoreaCrawler")
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
        
        # 불필요한 키워드 제거
        remove_keywords = ['지도보기', '인근지하철', '채용정보에 잘못된 내용이 있을 경우 문의해주세요']
        for keyword in remove_keywords:
            text = text.replace(keyword, '')
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        if max_length and len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    def get_companies_by_industry(self, industry_filter: str = None) -> List[Dict]:
        """
        산업별로 기업 목록 수집
        
        Args:
            industry_filter: 산업 필터 (예: "반도체", "이차전지" 등)
            
        Returns:
            기업 정보 리스트 [{"name": "기업명", "url": "기업URL", "company_id": "기업ID"}]
        """
        companies = []
        try:
            industry_url = self.config.get("industry_search_url", "https://www.jobkorea.co.kr/recruit/joblist?menucode=industry")
            self.logger.info(f"산업별 검색 페이지로 이동: {industry_url}")
            self.page.goto(industry_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(self.config.get("wait_time", 3))
            
            # 산업 필터 적용 (있는 경우)
            if industry_filter:
                try:
                    # 산업 필터 찾기 및 선택
                    industry_labels = self.page.query_selector_all('dl.dev-industry label')
                    for label in industry_labels:
                        label_text = label.inner_text().strip()
                        # 산업명이 라벨 텍스트에 포함되어 있는지 확인
                        if industry_filter in label_text and label_text != "산업, 키워드 입력":
                            input_elem = label.query_selector('input[type="checkbox"], input[type="radio"]')
                            if input_elem:
                                # 체크박스가 체크되어 있지 않으면 클릭
                                if not input_elem.is_checked():
                                    label.click()
                                    time.sleep(2)
                                    self.logger.info(f"산업 필터 적용: {industry_filter} (라벨: {label_text})")
                                    # 검색 버튼 클릭하여 필터 적용
                                    search_btn = self.page.query_selector('button[type="submit"], button.search')
                                    if search_btn:
                                        search_btn.click()
                                        time.sleep(3)
                                    break
                except Exception as e:
                    self.logger.warning(f"산업 필터 적용 실패: {e}")
            
            # 기업 목록 수집 (페이지네이션 고려)
            companies_data = self.page.evaluate("""
                () => {
                    const companies = [];
                    const companyLinks = document.querySelectorAll('a[href*="/Recruit/Co_Read/C/"]');
                    
                    companyLinks.forEach(link => {
                        const href = link.getAttribute('href');
                        const companyId = href.match(/\\/Co_Read\\/C\\/(\\d+)/)?.[1];
                        const name = link.innerText.trim();
                        
                        if (companyId && name && !companies.find(c => c.company_id === companyId)) {
                            companies.push({
                                name: name,
                                url: href.startsWith('http') ? href : 'https://www.jobkorea.co.kr' + href,
                                company_id: companyId
                            });
                        }
                    });
                    
                    return companies;
                }
            """)
            
            companies = companies_data if companies_data else []
            self.logger.info(f"총 {len(companies)}개의 기업 수집")
            return companies
            
        except Exception as e:
            self.logger.error(f"기업 목록 수집 중 오류: {e}", exc_info=True)
            return []
    
    def get_company_jobs(self, company_url: str) -> List[str]:
        """
        특정 기업의 공고 목록 수집
        
        Args:
            company_url: 기업 상세 페이지 URL
            
        Returns:
            공고 링크 리스트
        """
        job_links = []
        try:
            self.logger.debug(f"기업 페이지 접속: {company_url}")
            self.page.goto(company_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(self.config.get("wait_time", 2))
            
            # 기업의 공고 링크 수집
            links_data = self.page.evaluate("""
                () => {
                    const links = [];
                    const jobLinks = document.querySelectorAll('a[href*="/Recruit/GI_Read/"]');
                    
                    jobLinks.forEach(link => {
                        const href = link.getAttribute('href');
                        if (href && !links.includes(href)) {
                            const fullUrl = href.startsWith('http') ? href : 'https://www.jobkorea.co.kr' + href;
                            links.push(fullUrl);
                        }
                    });
                    
                    return [...new Set(links)]; // 중복 제거
                }
            """)
            
            job_links = links_data if links_data else []
            self.logger.debug(f"기업 공고 {len(job_links)}개 발견")
            return job_links
            
        except Exception as e:
            self.logger.error(f"기업 공고 수집 중 오류 ({company_url}): {e}")
            return []
    
    def parse_job_detail(self, job_url: str) -> Optional[Dict]:
        """
        공고 상세 페이지에서 정보 파싱 (모집요강 섹션 중심, 정확도 향상)
        
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
                    
                    // 회사명 추출 (h2 또는 h2 a)
                    const companyEl = document.querySelector('h2 a, h2');
                    if (companyEl) result.company = companyEl.innerText.trim();
                    
                    // 모집요강 섹션 찾기
                    const recruitSection = Array.from(document.querySelectorAll('*')).find(el => 
                        el.innerText && el.innerText.includes('모집요강')
                    );
                    
                    if (recruitSection) {
                        const section = recruitSection.closest('div') || recruitSection.parentElement;
                        if (section) {
                            // 모집요강 전체 텍스트 (요약용)
                            result.recruit_summary = section.innerText.trim();
                            
                            // 급여/연봉 추출
                            const salaryLabels = Array.from(section.querySelectorAll('*')).filter(el => 
                                el.innerText && (el.innerText.includes('급여') || el.innerText.includes('연봉'))
                            );
                            if (salaryLabels.length > 0) {
                                const salaryParent = salaryLabels[0].closest('div');
                                if (salaryParent) {
                                    // 급여 다음 형제 요소 찾기
                                    const allText = salaryParent.innerText;
                                    const lines = allText.split('\\n').map(l => l.trim()).filter(l => l);
                                    for (let i = 0; i < lines.length; i++) {
                                        if (lines[i].includes('급여') || lines[i].includes('연봉')) {
                                            // 다음 줄이 값인 경우
                                            if (i + 1 < lines.length && !lines[i + 1].includes('근무시간')) {
                                                result.salary = lines[i + 1];
                                                break;
                                            }
                                        }
                                    }
                                    // 구조적으로 찾기 (div 구조)
                                    if (!result.salary) {
                                        const salaryDivs = salaryParent.querySelectorAll('div');
                                        for (let i = 0; i < salaryDivs.length; i++) {
                                            const div = salaryDivs[i];
                                            if (div.innerText.includes('급여') || div.innerText.includes('연봉')) {
                                                if (i + 1 < salaryDivs.length) {
                                                    const valueDiv = salaryDivs[i + 1];
                                                    const value = valueDiv.innerText.trim();
                                                    if (value && !value.includes('급여') && !value.includes('연봉')) {
                                                        result.salary = value;
                                                        break;
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            
                            // 근무지주소 추출
                            const locationLabels = Array.from(section.querySelectorAll('*')).filter(el => 
                                el.innerText && (el.innerText.includes('근무지주소') || el.innerText.includes('근무지'))
                            );
                            if (locationLabels.length > 0) {
                                const locationParent = locationLabels[0].closest('div');
                                if (locationParent) {
                                    const allText = locationParent.innerText;
                                    // 주소 패턴 찾기 (시/도로 시작하는 패턴)
                                    const addressMatch = allText.match(/(서울|경기|인천|부산|대구|광주|대전|울산|세종|강원|충북|충남|전북|전남|경북|경남|제주|중국|홍콩|UAE|상하이|베이징|광저우|심천|대만|싱가포르|일본|미국|유럽)[^\\n]{0,150}/);
                                    if (addressMatch) {
                                        let location = addressMatch[0].trim();
                                        // 불필요한 텍스트 제거
                                        location = location.split('\\n')[0];
                                        location = location.replace(/지도보기|인근지하철|지원자격.*/g, '').trim();
                                        if (location) result.location = location;
                                    }
                                    // 구조적으로 찾기
                                    if (!result.location) {
                                        const locationDivs = locationParent.querySelectorAll('div');
                                        for (let i = 0; i < locationDivs.length; i++) {
                                            const div = locationDivs[i];
                                            if (div.innerText.includes('근무지') || div.innerText.includes('주소')) {
                                                if (i + 1 < locationDivs.length) {
                                                    const valueDiv = locationDivs[i + 1];
                                                    const value = valueDiv.innerText.trim();
                                                    if (value && !value.includes('근무지') && !value.includes('지도보기')) {
                                                        result.location = value.split('\\n')[0];
                                                        break;
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            
                            // 지원자격 추출
                            const qualificationSection = Array.from(document.querySelectorAll('*')).find(el => 
                                el.innerText && el.innerText.includes('지원자격')
                            );
                            if (qualificationSection) {
                                const qualParent = qualificationSection.closest('div');
                                if (qualParent) {
                                    // 지원자격 섹션의 핵심 정보만 추출
                                    const qualText = qualParent.innerText;
                                    // 지원자격부터 다음 섹션(접수기간, 기업정보 등) 전까지 추출
                                    const qualMatch = qualText.match(/지원자격[\\s\\S]{0,1000}(?=접수기간|기업정보|이 기업과|$)/);
                                    if (qualMatch) {
                                        result.conditions = qualMatch[0].trim();
                                    } else {
                                        // 전체 텍스트에서 지원자격 부분만 추출
                                        result.conditions = qualText.trim();
                                    }
                                }
                            }
                            
                            // 모집요강 요약 (모집요강 섹션 전체)
                            if (section && !result.recruit_summary) {
                                result.recruit_summary = section.innerText.trim();
                            }
                        }
                    }
                    
                    // 상세 내용 (main 섹션)
                    const mainEl = document.querySelector('main');
                    if (mainEl) {
                        result.detail = mainEl.innerText.trim();
                    }
                    
                    // 접수기간에서 마감일 추출
                    const deadlineLabel = Array.from(document.querySelectorAll('*')).find(el => 
                        el.innerText && (el.innerText.includes('마감일') || el.innerText.includes('접수기간'))
                    );
                    if (deadlineLabel) {
                        const deadlineParent = deadlineLabel.closest('div');
                        if (deadlineParent) {
                            const deadlineText = deadlineParent.innerText;
                            // 날짜 패턴 찾기 (YYYY.MM.DD 형식)
                            const dateMatch = deadlineText.match(/(\\d{4}\\.\\d{1,2}\\.\\d{1,2}[^\\n]{0,30})/);
                            if (dateMatch) {
                                result.posted_date = dateMatch[1].trim();
                            } else {
                                // 다른 형식 시도 (YYYY-MM-DD, YYYY/MM/DD)
                                const altDateMatch = deadlineText.match(/(\\d{4}[\\s\\-./]\\d{1,2}[\\s\\-./]\\d{1,2}[^\\n]{0,30})/);
                                if (altDateMatch) {
                                    result.posted_date = altDateMatch[1].trim();
                                }
                            }
                        }
                    }
                    
                    return result;
                }
            """)
            
            # 파싱된 데이터를 job_info에 반영
            job_info.update(parsed_data)
            
            # 정규표현식으로 재추출 및 정리 (fallback)
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
                try:
                    match = re.search(pattern, detail, re.IGNORECASE)
                    if match:
                        salary = match.group(1).strip()
                        # 불필요한 텍스트 제거
                        salary = re.sub(r'근무시간.*|모집인원.*|지원자격.*', '', salary).strip()
                        if salary:
                            job_info["salary"] = salary
                            break
                except re.error:
                    continue
        
        # 근무지 추출
        if not job_info.get("location"):
            location_patterns = [
                r'근무지주소[\s\n]*:?[\s\n]*([^\n]{0,150}?)(?=\n|지도보기|인근지하철|지원자격|$)',
                r'근무지[\s\n]*:?[\s\n]*([^\n]{0,150}?)(?=\n|지도보기|인근지하철|지원자격|$)',
                r'(서울|경기|인천|부산|대구|광주|대전|울산|세종|강원|충북|충남|전북|전남|경북|경남|제주|중국|홍콩|UAE|상하이|베이징)[^\n]{0,100}',
            ]
            for pattern in location_patterns:
                try:
                    match = re.search(pattern, detail, re.IGNORECASE)
                    if match:
                        location = match.group(1).strip() if match.groups() else match.group(0).strip()
                        location = re.sub(r'지도보기|인근지하철|지원자격.*', '', location).strip()
                        if location:
                            job_info["location"] = location.split('\n')[0]
                            break
                except re.error:
                    continue
        
        # 지원자격 추출
        if not job_info.get("conditions"):
            try:
                conditions_match = re.search(r'지원자격[\s\S]{0,1000}(?=접수기간|기업정보|이 기업과|$)', detail)
                if conditions_match:
                    conditions = conditions_match.group(0).strip()
                    # 불필요한 섹션 제거
                    conditions = re.sub(r'이 기업과 나의 적합도.*|접수기간.*|기업정보.*', '', conditions, flags=re.DOTALL).strip()
                    if conditions:
                        job_info["conditions"] = conditions
            except re.error:
                pass
        
        # 모집요강 요약 추출
        if not job_info.get("recruit_summary"):
            try:
                # 모집요강 섹션 찾기
                recruit_match = re.search(r'모집요강[\s\S]{0,2000}(?=접수기간|기업정보|이 기업과|$)', detail)
                if recruit_match:
                    recruit_summary = recruit_match.group(0).strip()
                    # 불필요한 섹션 제거
                    recruit_summary = re.sub(r'이 기업과 나의 적합도.*|접수기간.*|기업정보.*', '', recruit_summary, flags=re.DOTALL).strip()
                    if recruit_summary:
                        job_info["recruit_summary"] = recruit_summary
            except re.error:
                pass
        
        # 마감일 추출
        if not job_info.get("posted_date"):
            date_patterns = [
                r'마감일[\s\n]*:?[\s\n]*(\d{4}\.\d{1,2}\.\d{1,2}[^\n]{0,30})',
                r'접수기간[\s\S]{0,200}마감일[\s\n]*:?[\s\n]*(\d{4}\.\d{1,2}\.\d{1,2}[^\n]{0,30})',
                r'(\d{4}\.\d{1,2}\.\d{1,2}[^\n]{0,30})(?=.*마감|채용 시 마감)',
                r'(\d{4}[\s\-./]\d{1,2}[\s\-./]\d{1,2}[^\n]{0,30})(?=.*마감)',
            ]
            for pattern in date_patterns:
                try:
                    match = re.search(pattern, detail)
                    if match:
                        date_str = match.group(1).strip() if match.groups() else match.group(0).strip()
                        if date_str:
                            job_info["posted_date"] = date_str
                            break
                except re.error:
                    continue
        
        return job_info
    
    def _matches_keywords(self, job_info: Dict, keywords: List[str]) -> bool:
        """
        공고가 키워드와 매칭되는지 확인
        
        Args:
            job_info: 공고 정보
            keywords: 검색 키워드 리스트
            
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
        
        # detail에서도 키워드 검색 (하지만 너무 길면 일부만)
        detail = job_info.get('detail', '')
        if detail:
            # detail의 앞부분과 모집요강 부분만 검색
            detail_sample = detail[:1000] + (detail[detail.find('모집요강'):detail.find('모집요강')+500] if '모집요강' in detail else '')
            search_fields.append(detail_sample)
        
        text_to_search = ' '.join(search_fields).lower()
        
        # 키워드 매칭
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in text_to_search:
                return True
        
        return False
    
    def crawl_by_industry(self, keywords: List[str], industries: List[str] = None, max_companies: int = 50, max_jobs_per_company: int = 10) -> List[Dict]:
        """
        산업별로 기업을 먼저 수집하고, 각 기업의 공고를 확인하여 키워드와 매칭
        
        Args:
            keywords: 검색 키워드 리스트
            industries: 산업 필터 리스트 (None이면 기술 분야 사용)
            max_companies: 최대 수집할 기업 수
            max_jobs_per_company: 기업당 최대 수집할 공고 수
            
        Returns:
            수집된 공고 정보 리스트
        """
        self.logger.info(f"산업별 기업 크롤링 시작 (키워드: {keywords})")
        
        all_jobs = []
        
        # 산업별로 기업 수집
        if industries:
            industry_list = industries
        else:
            # 진행.md의 기술 분야를 산업으로 사용
            industry_list = ["반도체", "디스플레이", "이차전지", "조선", "원자력", "우주항공"]
        
        for industry in industry_list:
            self.logger.info(f"산업 '{industry}' 기업 수집 시작")
            companies = self.get_companies_by_industry(industry)
            
            if not companies:
                self.logger.warning(f"'{industry}' 산업의 기업을 찾을 수 없습니다")
                continue
            
            # 최대 개수만큼만 수집
            companies = companies[:max_companies]
            self.logger.info(f"'{industry}' 산업: {len(companies)}개 기업 처리 예정")
            
            for i, company in enumerate(companies, 1):
                try:
                    self.logger.info(f"[{industry}] 기업 진행 중: {i}/{len(companies)} - {company['name']}")
                    
                    # 기업의 공고 목록 가져오기
                    job_links = self.get_company_jobs(company['url'])
                    
                    if not job_links:
                        self.logger.debug(f"기업 '{company['name']}'의 공고가 없습니다")
                        continue
                    
                    # 기업당 최대 개수만큼만 수집
                    job_links = job_links[:max_jobs_per_company]
                    
                    # 각 공고 상세 정보 파싱
                    for job_url in job_links:
                        try:
                            job_info = self.parse_job_detail(job_url)
                            if not job_info:
                                continue
                            
                            # 키워드 필터링
                            if self._matches_keywords(job_info, keywords):
                                all_jobs.append(job_info)
                                self.logger.info(f"✓ 키워드 매칭: {job_info['title']} - {job_info.get('company', 'N/A')}")
                            else:
                                self.logger.debug(f"✗ 키워드 미매칭: {job_info['title']}")
                            
                            time.sleep(1)  # 요청 간 대기
                        except Exception as e:
                            self.logger.error(f"공고 파싱 중 오류 ({job_url}): {e}")
                            continue
                    
                    time.sleep(2)  # 기업 간 대기
                except Exception as e:
                    self.logger.error(f"기업 처리 중 오류 ({company['name']}): {e}")
                    continue
        
        self.logger.info(f"총 {len(all_jobs)}개의 키워드 매칭 공고 수집 완료")
        return all_jobs
    
    def crawl(self, keyword: str, max_jobs: int = 50) -> List[Dict]:
        """
        키워드로 검색하여 공고 수집 (기존 방식 - 호환성 유지)
        
        Args:
            keyword: 검색 키워드
            max_jobs: 최대 수집할 공고 수
            
        Returns:
            수집된 공고 정보 리스트
        """
        # 새로운 방식으로 전환
        return self.crawl_by_industry([keyword], max_companies=50, max_jobs_per_company=10)
    
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
        filename = f"jobkorea_{safe_keyword}_{timestamp}.json"
        
        filepath = save_json(data, filename)
        self.logger.info(f"결과 저장 완료: {filepath}")


if __name__ == "__main__":
    # 테스트 실행
    crawler = JobKoreaCrawler(headless=False)
    try:
        crawler.start()
        jobs = crawler.crawl_by_industry(["중국어", "중국"], ["반도체"], max_companies=3, max_jobs_per_company=2)
        if jobs:
            crawler.save_results("중국어", jobs)
    finally:
        crawler.close()
