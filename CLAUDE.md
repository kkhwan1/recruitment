# CLAUDE.md - 채용시스템 프로젝트 가이드

이 파일은 Claude Code가 이 저장소의 코드를 작업할 때 참고하는 가이드입니다.

## 프로젝트 개요

**채용 공고 분석 시스템** - 기술 유출 의심 공고 탐지 및 위험도 분석 자동화 시스템

### 핵심 기능
- 🔍 **다중 채용 사이트 크롤링**: JobKorea, Incruit, Saramin, Hibrain 지원
- 🎯 **3단계 키워드 탐지**: 기술/의심/위험 키워드 체계적 분류
- ⚠️ **복합 패턴 매칭**: 2-3개 키워드 조합으로 고위험 패턴 탐지
- 📊 **위험도 점수 산정**: 가중치 기반 자동 점수 계산 및 등급 분류
- 💾 **데이터베이스 저장**: SQLite 기반 지속적 데이터 관리
- 📈 **일일 리포트 생성**: 탐지 결과 자동 요약 및 분석

## 프로젝트 구조

```
채용시스템/
├── config/                      # 설정 파일
│   ├── keywords.csv            # 키워드 데이터베이스 (tier, category, weight)
│   └── patterns.csv            # 복합 패턴 정의
├── sites/                       # 크롤러 구현
│   ├── jobkorea/               # JobKorea 크롤러
│   ├── incruit/                # Incruit 크롤러
│   ├── saramin/                # Saramin 크롤러
│   └── hibrain/                # Hibrain 크롤러
├── analyzers/                   # 분석 엔진
│   ├── keyword_detector.py     # 키워드 탐지 엔진
│   └── risk_scorer.py          # 위험도 점수 계산기
├── database/                    # 데이터베이스 레이어
│   ├── models.py               # 데이터 모델
│   └── repositories.py         # Repository 패턴 구현
├── utils/                       # 유틸리티
│   ├── logger.py               # 로깅 설정
│   └── text_utils.py           # 텍스트 정제
├── data/                        # 데이터 저장소
│   ├── json_results/           # JSON 백업
│   └── recruitment.db          # SQLite 데이터베이스
├── main.py                      # CLI 진입점
├── crawl_and_analyze.py        # 통합 실행 스크립트
└── test_analysis_system.py     # 분석 시스템 테스트
```

## 빠른 시작

### 1. 환경 설정

```bash
# Python 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### 2. 기본 실행

```bash
# 모든 사이트, 모든 키워드로 크롤링 및 분석
python crawl_and_analyze.py

# 특정 사이트만 크롤링
python main.py --site jobkorea

# 특정 키워드로 검색
python main.py --keyword "반도체"

# 최대 수집 개수 제한
python main.py --max-jobs 50

# 브라우저 표시 (디버깅용)
python main.py --no-headless
```

### 3. 산업별 크롤링 (JobKorea)

```bash
# 특정 산업 필터링
python sites/jobkorea/crawler.py --industry "반도체"
python sites/jobkorea/crawler.py --industry "디스플레이"
python sites/jobkorea/crawler.py --industry "이차전지"
```

### 4. 분석 시스템 테스트

```bash
# 키워드 탐지 및 위험도 분석 테스트
python test_analysis_system.py
```

## 아키텍처 패턴

### 1. 크롤러 구현 패턴

모든 사이트 크롤러는 일관된 패턴을 따릅니다:

```python
from playwright.sync_api import sync_playwright
import time

class SiteCrawler:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.config = self._load_config()

    def start(self):
        """브라우저 시작 및 Bot Detection 회피 설정"""
        self.playwright = sync_playwright().start()

        # Bot Detection 회피 설정
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )

        # User-Agent 설정
        self.page = self.browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        # navigator.webdriver 제거
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    def crawl(self, keyword: str, max_jobs: int = 50) -> List[Dict]:
        """키워드로 검색하여 공고 수집"""
        # 구현 로직
        pass
```

### 2. React SPA 크롤링 패턴 (Hibrain)

React 기반 SPA는 특별한 대기 전략이 필요합니다:

```python
def get_job_list_with_preview(self, list_type: str = "ING", max_jobs: int = 50):
    """4단계 계층적 대기 전략"""

    # Level 1: 빠른 DOM 로드
    self.page.goto(url, wait_until="domcontentloaded", timeout=60000)

    # Level 2: 네트워크 안정화 (타임아웃 허용)
    try:
        self.page.wait_for_load_state("networkidle", timeout=10000)
    except:
        pass  # React SPA는 완전한 idle 상태에 도달하지 못할 수 있음

    # Level 3: 실제 콘텐츠 대기
    self.page.wait_for_selector('.recruitTitle', timeout=15000, state="visible")

    # Level 4: React 렌더링 안정화
    time.sleep(3)

    # JavaScript로 데이터 추출
    jobs_data = self.page.evaluate("""
        () => {
            const jobs = [];
            const recruitTitles = document.querySelectorAll('.recruitTitle');

            recruitTitles.forEach(titleEl => {
                let container = titleEl.closest('a[href*="/recruitment/recruits/"]');
                if (container) {
                    jobs.push({
                        title: titleEl.innerText.trim(),
                        company: titleEl.innerText.trim(),
                        content: container.querySelector('.recruitContent')?.innerText.trim() || '',
                        date: container.querySelector('.recruitDate')?.innerText.trim() || '',
                        link: container.href || ''
                    });
                }
            });
            return jobs;
        }
    """)

    return jobs_data
```

### 3. 분석 엔진 패턴

```python
from analyzers.keyword_detector import KeywordDetector
from analyzers.risk_scorer import RiskScorer

# 키워드 탐지
detector = KeywordDetector(
    keywords_csv="config/keywords.csv",
    patterns_csv="config/patterns.csv"
)

# 위험도 점수 계산
scorer = RiskScorer()

# 분석 실행
for job in jobs:
    # 1. 키워드 탐지
    detection_result = detector.analyze(job)

    # 2. 위험도 점수 계산
    risk_result = scorer.calculate_risk_score(detection_result)

    # 3. 결과 확인
    if risk_result['risk_level'] == '고위험':
        print(f"⚠️ 고위험 공고 발견: {job['title']}")
        print(f"   점수: {risk_result['final_score']}")
        print(f"   위험 요인: {risk_result['risk_factors']}")
```

### 4. 데이터베이스 패턴 (Repository)

```python
from database.repositories import JobRepository, AnalysisRepository

# Repository 초기화
job_repo = JobRepository(db_path="data/recruitment.db")
analysis_repo = AnalysisRepository(db_path="data/recruitment.db")

# 공고 저장
job_id = job_repo.insert_job({
    "title": "반도체 공정 엔지니어",
    "company": "글로벌 R&D",
    "location": "중국 상하이",
    # ... 기타 필드
})

# 분석 결과 저장
analysis_repo.save_analysis(job_id, detection_result, risk_result)
```

## 핵심 개념

### 1. 3단계 키워드 탐지 시스템

| Tier | 카테고리 | 예시 키워드 | 가중치 |
|------|---------|------------|-------|
| 1차 | 기술 키워드 | 반도체, OLED, 이차전지, AI | 8-10점 |
| 2차 | 의심 패턴 | 해외협업, 중국어필수, 기술이전 | 12-25점 |
| 3차 | 위험 키워드 | 급구, 비자필요없음, 현금지급 | 20-25점 |

### 2. 복합 패턴 매칭

2-3개 키워드 AND 조합으로 고위험 패턴 탐지:

```python
# 예시: "기술 + 중국 + 급구" 패턴
{
    "pattern_name": "기술유출_중국_급구",
    "keywords": ["반도체", "중국어", "급구"],
    "operator": "AND",
    "score": 35
}
```

### 3. 위험도 점수 계산

```python
# 기본 점수 = Tier1 + Tier2 + Tier3 + Patterns
base_score = sum(tier1_weights) + sum(tier2_weights) + sum(tier3_weights) + sum(pattern_scores)

# 복합 조건 가중치
combo_multiplier = 1.0
if tier1_count >= 2 and tier2_count >= 1:
    combo_multiplier += 0.5  # 1.5x
if tier3_count >= 1:
    combo_multiplier += 0.5  # 2.0x

# 최종 점수
final_score = base_score * combo_multiplier
```

### 4. 위험 등급 분류

- **고위험** (100점 이상): 즉시 검토 필요
- **중위험** (50-99점): 주의 깊게 모니터링
- **저위험** (50점 미만): 일반 공고

## Bot Detection 회피 기법

### 1. 브라우저 설정

```python
args = [
    '--disable-blink-features=AutomationControlled',  # 자동화 제어 기능 비활성화
    '--no-sandbox',                                   # 샌드박스 비활성화
    '--disable-dev-shm-usage',                        # 공유 메모리 사용 비활성화
]
```

### 2. User-Agent 설정

```python
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
```

### 3. WebDriver 속성 제거

```python
page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
""")
```

## 데이터베이스 스키마

### jobs 테이블
```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    company TEXT,
    location TEXT,
    salary TEXT,
    conditions TEXT,
    recruit_summary TEXT,
    detail TEXT,
    url TEXT UNIQUE,
    posted_date TEXT,
    source_site TEXT,
    search_keyword TEXT,
    crawled_at TEXT,
    crawled_date TEXT,
    crawled_weekday TEXT,
    crawled_hour INTEGER
)
```

### keyword_matches 테이블
```sql
CREATE TABLE keyword_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    keyword TEXT,
    tier INTEGER,
    category TEXT,
    weight INTEGER,
    positions TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs (id)
)
```

### pattern_matches 테이블
```sql
CREATE TABLE pattern_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    pattern_name TEXT,
    keywords TEXT,
    score INTEGER,
    FOREIGN KEY (job_id) REFERENCES jobs (id)
)
```

### risk_analysis 테이블
```sql
CREATE TABLE risk_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER UNIQUE,
    base_score REAL,
    combo_multiplier REAL,
    final_score REAL,
    risk_level TEXT,
    risk_factors TEXT,
    recommendations TEXT,
    analysis_summary TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs (id)
)
```

## 일반적인 문제 해결

### 1. Bot Detection 오류
**증상**: 403 Forbidden 또는 빈 페이지
**해결책**:
- `--no-headless` 플래그로 브라우저 표시하여 디버깅
- User-Agent 및 webdriver 속성 확인
- 대기 시간 증가 (time.sleep 값 조정)

### 2. React SPA 콘텐츠 로드 실패
**증상**: 빈 데이터 또는 selector 오류
**해결책**:
- 4단계 계층적 대기 전략 사용
- networkidle 타임아웃 허용 (try-except)
- 최종 sleep 시간 증가 (3초 → 5초)

### 3. 키워드 매칭 실패
**증상**: 예상되는 공고가 탐지되지 않음
**해결책**:
- config/keywords.csv 확인 및 키워드 추가
- 텍스트 정제 로직 확인 (utils/text_utils.py)
- 로그 활성화하여 매칭 과정 추적

## 개발 가이드

### 새로운 크롤러 추가

1. `sites/[사이트명]/` 디렉토리 생성
2. `config.json` 작성 (base_url, selectors 등)
3. `crawler.py` 구현 (기존 패턴 참고)
4. `__init__.py`에 export 추가
5. `main.py`에 사이트 등록

### 새로운 키워드 추가

1. `config/keywords.csv` 편집
2. 형식: `tier,category,keyword,weight`
3. 예시: `1,핵심기술,양자컴퓨터,10`

### 새로운 패턴 추가

1. `config/patterns.csv` 편집
2. 형식: `pattern_name,keyword1,keyword2,keyword3,operator,score,description`
3. 예시: `양자기술_해외_급구,양자컴퓨터,해외협업,급구,AND,40,양자컴퓨터 기술 해외 유출 의심`

## 성능 최적화

### 1. 병렬 크롤링
```python
# 여러 산업 동시 크롤링
industries = ["반도체", "디스플레이", "이차전지"]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(crawler.crawl_industry, ind) for ind in industries]
```

### 2. 데이터베이스 배치 저장
```python
# 한 번에 여러 레코드 저장
job_repo.insert_jobs_batch(jobs_list)
```

### 3. 캐싱
```python
# 중복 URL 방지
visited_urls = set()
if url not in visited_urls:
    visited_urls.add(url)
    process_job(url)
```

## 테스트

### 단위 테스트
```bash
pytest tests/
```

### 통합 테스트
```bash
python test_analysis_system.py
```

### 크롤러 개별 테스트
```bash
python -m sites.jobkorea.crawler --keyword "반도체" --max-jobs 10
python -m sites.hibrain.crawler --keyword "교수" --max-jobs 10
```

## 참고 문서

- [README.md](./README.md) - 프로젝트 전체 개요
- [sites/hibrain/IMPLEMENTATION_NOTES.md](./sites/hibrain/IMPLEMENTATION_NOTES.md) - Hibrain 구현 노트
- [sites/saramin/IMPLEMENTATION_NOTES.md](./sites/saramin/IMPLEMENTATION_NOTES.md) - Saramin 구현 노트

## 기여 가이드

1. 새로운 기능 추가 시 테스트 코드 작성
2. 크롤러 추가 시 IMPLEMENTATION_NOTES.md 작성
3. 코드 스타일: PEP 8 준수
4. 로깅: utils.logger.setup_logger() 사용
5. 에러 처리: try-except로 안전하게 처리

## 라이선스

이 프로젝트는 내부 사용을 위한 것입니다.
