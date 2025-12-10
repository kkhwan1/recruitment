# 크롤러 완성 가이드

## 개요

이 문서는 채용시스템 프로젝트의 미완성 크롤러 6개를 완성하기 위한 상세 가이드입니다.

### 현재 상태 요약

| 크롤러 | 사이트 | 구현 상태 | 우선순위 | 주요 작업 |
|--------|--------|----------|---------|----------|
| alba | 알바천국 | 90% | 높음 | Bot Detection 회피, 테스트 |
| albamon | 알바몬 | 90% | 높음 | Bot Detection 회피, 테스트 |
| jobplanet | 잡플래닛 | 95% | 중간 | Bot Detection 회피, 테스트 |
| jobposting | 잡포스팅 | 95% | 중간 | Bot Detection 회피, 테스트 |
| worknet | 워크넷 | 95% | 높음 | Bot Detection 회피, 테스트 |
| blind | 블라인드 | 95% | 낮음 | Bot Detection 회피, 테스트 (영문 사이트) |

> **중요 발견**: 초기 분석과 달리 모든 6개 크롤러가 이미 **거의 완전한 구현**을 갖추고 있습니다.
> 주요 작업은 Bot Detection 회피 적용과 실제 사이트 테스트입니다.

---

## 1단계: 공통 패턴 적용 (Bot Detection 회피)

### 1.1 Saramin 프로덕션 패턴 (참조 기준)

모든 크롤러에 다음 패턴을 적용해야 합니다:

```python
def start(self):
    """브라우저 시작 - Bot Detection 회피 적용"""
    self.playwright = sync_playwright().start()

    # ✅ Bot Detection 회피 설정
    self.browser = self.playwright.chromium.launch(
        headless=self.headless,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage',
        ]
    )

    # ✅ 실제 브라우저처럼 보이는 User-Agent 설정
    self.page = self.browser.new_page(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    # ✅ Viewport 설정
    self.page.set_viewport_size({"width": 1920, "height": 1080})

    # ✅ navigator.webdriver 속성 제거
    self.page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    self.logger.info("브라우저 시작 완료 (Bot Detection 회피 적용)")
```

### 1.2 각 크롤러에 적용해야 할 코드 변경

#### alba/crawler.py (알바천국)

**현재 코드** (Line 44-50):
```python
def start(self):
    """브라우저 시작"""
    self.playwright = sync_playwright().start()
    self.browser = self.playwright.chromium.launch(headless=self.headless)
    self.page = self.browser.new_page()
    self.page.set_viewport_size({"width": 1920, "height": 1080})
    self.logger.info("브라우저 시작 완료")
```

**변경할 코드**:
```python
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
```

#### albamon/crawler.py, jobplanet/crawler.py, jobposting/crawler.py, worknet/crawler.py, blind/crawler.py

동일한 패턴을 각 크롤러의 `start()` 메서드에 적용합니다.

---

## 2단계: 크롤러별 상세 작업

### 2.1 alba/crawler.py (알바천국)

**파일 위치**: `sites/alba/crawler.py` (549 lines)

**현재 구현 상태**:
- ✅ 기본 클래스 구조 완성
- ✅ 검색 기능 (`search()`) - 다중 셀렉터 패턴
- ✅ 공고 목록 수집 (`get_job_list()`) - JavaScript 추출
- ✅ 상세 페이지 파싱 (`parse_job_detail()`)
- ✅ 팝업 닫기 (`_close_popups()`)
- ✅ 필드 추출 (`_extract_fields_from_detail()`)
- ❌ Bot Detection 회피 미적용

**테스트 명령어**:
```bash
cd c:\Users\USER\claude_code\채용시스템
python -m sites.alba.crawler --keyword "편의점" --max-jobs 5 --no-headless
```

**주의사항**:
- 알바천국은 팝업이 많아 `_close_popups()` 메서드가 중요
- 검색 결과 페이지 구조가 자주 변경될 수 있음
- 여러 셀렉터 패턴이 이미 구현되어 있음

---

### 2.2 albamon/crawler.py (알바몬)

**파일 위치**: `sites/albamon/crawler.py` (362 lines)

**현재 구현 상태**:
- ✅ 기본 클래스 구조 완성
- ✅ 공고 목록 수집 (`get_job_list()`)
- ✅ 상세 페이지 파싱 (`parse_job_detail()`)
- ✅ 텍스트 정리 (`_clean_text()`)
- ❌ Bot Detection 회피 미적용

**URL 패턴**:
```
검색: https://www.albamon.com/search?kwd={keyword}
상세: https://www.albamon.com/jobs/detail/[숫자]
```

**테스트 명령어**:
```bash
python -m sites.albamon.crawler --keyword "카페" --max-jobs 5 --no-headless
```

---

### 2.3 jobplanet/crawler.py (잡플래닛)

**파일 위치**: `sites/jobplanet/crawler.py` (359 lines)

**현재 구현 상태**:
- ✅ 기본 클래스 구조 완성
- ✅ 공고 목록 수집 - 2가지 URL 패턴 지원
- ✅ 상세 페이지 파싱
- ❌ Bot Detection 회피 미적용

**URL 패턴**:
```
패턴1: posting_ids[]=숫자
패턴2: /companies/[회사]/job_postings/[공고ID]
```

**테스트 명령어**:
```bash
python -m sites.jobplanet.crawler --keyword "개발자" --max-jobs 5 --no-headless
```

**주의사항**:
- 잡플래닛은 로그인 요구 페이지가 있을 수 있음
- 상세 페이지 접근 시 쿠키/세션 관리 필요할 수 있음

---

### 2.4 jobposting/crawler.py (잡포스팅)

**파일 위치**: `sites/jobposting/crawler.py` (397 lines)

**현재 구현 상태**:
- ✅ 기본 클래스 구조 완성
- ✅ 공고 목록 수집
- ✅ 상세 페이지 파싱
- ❌ Bot Detection 회피 미적용

**URL 패턴**:
```
검색: https://www.jobposting.co.kr/employ/employ_list.php?keyword={keyword}
상세: employ_detail.php?idx=[숫자]
```

**테스트 명령어**:
```bash
python -m sites.jobposting.crawler --keyword "사무직" --max-jobs 5 --no-headless
```

---

### 2.5 worknet/crawler.py (워크넷) ⭐ 우선순위 높음

**파일 위치**: `sites/worknet/crawler.py` (469 lines)

**현재 구현 상태**:
- ✅ 기본 클래스 구조 완성
- ✅ 검색 기능 (`search()`)
- ✅ 공고 목록 수집 (`get_job_list()`) - goDetail() onclick 및 empDetailAuthView.do 패턴
- ✅ 상세 페이지 파싱 (`parse_job_detail()`)
- ❌ Bot Detection 회피 미적용

**URL 패턴**:
```
검색: https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?keyword={keyword}
상세: empDetailAuthView.do 또는 goDetail() JavaScript 호출
```

**테스트 명령어**:
```bash
python -m sites.worknet.crawler --keyword "반도체" --max-jobs 5 --no-headless
```

**주의사항**:
- 정부 사이트로 비교적 안정적인 구조
- JavaScript onclick 이벤트로 상세 페이지 이동하는 패턴 있음
- 공공기관 공고가 많아 기술유출 분석에 중요

---

### 2.6 blind/crawler.py (블라인드)

**파일 위치**: `sites/blind/crawler.py` (418 lines)

**현재 구현 상태**:
- ✅ 기본 클래스 구조 완성
- ✅ 검색 기능 - URL 인코딩 처리
- ✅ 공고 목록 수집 - 스크롤하여 더 로드
- ✅ 상세 페이지 파싱
- ❌ Bot Detection 회피 미적용

**URL 패턴**:
```
검색: https://www.teamblind.com/job/search?keyword={keyword}
상세: /job/ 또는 /jobs/ 경로 포함
```

**테스트 명령어**:
```bash
python -m sites.blind.crawler --keyword "semiconductor" --max-jobs 5 --no-headless
```

**주의사항**:
- **영문 사이트** - 키워드도 영문으로 사용
- 미국 채용 시장 중심 (Remote, Hybrid, USD 급여)
- 스크롤하여 더 많은 공고 로드하는 패턴 사용
- 국내 기술유출 분석보다는 해외 채용 동향 파악에 유용

---

## 3단계: 테스트 절차

### 3.1 개별 크롤러 테스트

각 크롤러를 다음 순서로 테스트합니다:

```bash
# 1. 브라우저 표시 모드로 동작 확인
python -m sites.[사이트명].crawler --keyword "[테스트키워드]" --max-jobs 3 --no-headless

# 2. Headless 모드로 테스트
python -m sites.[사이트명].crawler --keyword "[테스트키워드]" --max-jobs 5

# 3. 결과 파일 확인
ls data/json_results/
cat data/json_results/[사이트명]_[키워드]_*.json
```

### 3.2 통합 테스트

```bash
# 분석 시스템 전체 테스트
python test_analysis_system.py

# 전체 크롤링 및 분석
python crawl_and_analyze.py --sites alba,albamon,jobplanet,jobposting,worknet --max-jobs 10
```

### 3.3 테스트 체크리스트

각 크롤러에 대해 다음 항목을 확인합니다:

| 항목 | 설명 | 확인 |
|------|------|------|
| 브라우저 시작 | Bot Detection 없이 정상 로드 | ☐ |
| 검색 실행 | 키워드 검색 후 결과 페이지 로드 | ☐ |
| 공고 목록 수집 | 최소 1개 이상의 공고 링크 수집 | ☐ |
| 상세 페이지 파싱 | 제목, 회사명, 상세내용 추출 | ☐ |
| JSON 저장 | 결과 파일 정상 생성 | ☐ |
| 키워드 분석 | 분석 엔진과 연동 확인 | ☐ |

---

## 4단계: 문제 해결 가이드

### 4.1 Bot Detection 차단

**증상**: 403 Forbidden, 빈 페이지, CAPTCHA

**해결책**:
1. `--no-headless` 플래그로 브라우저 표시하여 확인
2. Bot Detection 회피 설정 재확인
3. 대기 시간 증가: `time.sleep(5)`
4. 랜덤 지연 추가:
```python
import random
time.sleep(random.uniform(2, 5))
```

### 4.2 셀렉터 오류

**증상**: `TimeoutError: waiting for selector`

**해결책**:
1. 브라우저에서 실제 페이지 구조 확인 (F12 개발자 도구)
2. 셀렉터 업데이트:
```python
# 기존 셀렉터가 작동하지 않으면 새로운 셀렉터 추가
selectors = [
    '.old-selector',
    '.new-selector',
    '[data-testid="job-item"]',
]
for selector in selectors:
    try:
        self.page.wait_for_selector(selector, timeout=5000)
        break
    except:
        continue
```

### 4.3 JavaScript 렌더링 문제 (React/SPA)

**증상**: 빈 데이터, 요소 없음

**해결책**:
```python
# 4단계 계층적 대기 전략
# Level 1: DOM 로드
self.page.goto(url, wait_until="domcontentloaded", timeout=60000)

# Level 2: 네트워크 안정화 (타임아웃 허용)
try:
    self.page.wait_for_load_state("networkidle", timeout=10000)
except:
    pass

# Level 3: 실제 콘텐츠 대기
self.page.wait_for_selector('.job-item', timeout=15000, state="visible")

# Level 4: 렌더링 안정화
time.sleep(3)
```

### 4.4 인코딩 문제

**증상**: 한글 깨짐, UnicodeDecodeError

**해결책**:
```python
# URL 인코딩
import urllib.parse
encoded_keyword = urllib.parse.quote(keyword)

# 파일 저장 시 인코딩 지정
with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

---

## 5단계: main.py 통합

모든 크롤러 테스트 완료 후 `main.py`에 등록합니다:

```python
# main.py에 크롤러 등록
AVAILABLE_CRAWLERS = {
    'jobkorea': JobKoreaCrawler,
    'incruit': IncruitCrawler,
    'saramin': SaraminCrawler,
    'hibrain': HibrainCrawler,
    'alba': AlbaCrawler,           # 추가
    'albamon': AlbamonCrawler,     # 추가
    'jobplanet': JobplanetCrawler, # 추가
    'jobposting': JobPostingCrawler, # 추가
    'worknet': WorknetCrawler,     # 추가
    'blind': BlindCrawler,         # 추가
}
```

---

## 부록: 작업 우선순위

### 높음 (즉시 작업)
1. **worknet** - 정부 사이트, 공공기관 채용 정보
2. **alba** - 대형 알바 사이트
3. **albamon** - 주요 알바 사이트

### 중간 (2순위)
4. **jobplanet** - 기업 리뷰와 함께 채용 정보
5. **jobposting** - 추가 채용 정보 소스

### 낮음 (3순위)
6. **blind** - 영문 사이트, 해외 시장 분석용

---

## 예상 작업 시간

| 작업 | 예상 시간 |
|------|----------|
| Bot Detection 회피 적용 (6개 크롤러) | 30분 |
| 개별 테스트 (크롤러당 10분) | 1시간 |
| 셀렉터 수정 (필요시) | 크롤러당 20분 |
| main.py 통합 | 15분 |
| 통합 테스트 | 30분 |
| **총 예상 시간** | **3-4시간** |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2024-12-06 | 1.0 | 초기 문서 작성 |
