# 크롤러 완성 체크리스트

## 빠른 참조: Bot Detection 회피 코드

다음 코드를 각 크롤러의 `start()` 메서드에 적용하세요:

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

---

## 크롤러별 체크리스트

### ☐ 1. worknet (워크넷) - 우선순위 높음

**파일**: `sites/worknet/crawler.py`

| 단계 | 작업 | 완료 |
|------|------|------|
| 1 | Bot Detection 회피 코드 적용 | ☐ |
| 2 | 테스트: `python -m sites.worknet.crawler --keyword "반도체" --max-jobs 3 --no-headless` | ☐ |
| 3 | 브라우저에서 정상 로드 확인 | ☐ |
| 4 | 공고 목록 수집 확인 | ☐ |
| 5 | 상세 페이지 파싱 확인 | ☐ |
| 6 | Headless 모드 테스트 | ☐ |
| 7 | JSON 파일 저장 확인 | ☐ |

**테스트 키워드**: `반도체`, `연구원`, `엔지니어`

---

### ☐ 2. alba (알바천국) - 우선순위 높음

**파일**: `sites/alba/crawler.py`

| 단계 | 작업 | 완료 |
|------|------|------|
| 1 | Bot Detection 회피 코드 적용 | ☐ |
| 2 | 테스트: `python -m sites.alba.crawler --keyword "편의점" --max-jobs 3 --no-headless` | ☐ |
| 3 | 팝업 닫기 기능 동작 확인 | ☐ |
| 4 | 공고 목록 수집 확인 | ☐ |
| 5 | 상세 페이지 파싱 확인 | ☐ |
| 6 | Headless 모드 테스트 | ☐ |
| 7 | JSON 파일 저장 확인 | ☐ |

**테스트 키워드**: `편의점`, `카페`, `음식점`

---

### ☐ 3. albamon (알바몬) - 우선순위 높음

**파일**: `sites/albamon/crawler.py`

| 단계 | 작업 | 완료 |
|------|------|------|
| 1 | Bot Detection 회피 코드 적용 | ☐ |
| 2 | 테스트: `python -m sites.albamon.crawler --keyword "카페" --max-jobs 3 --no-headless` | ☐ |
| 3 | 공고 목록 수집 확인 | ☐ |
| 4 | 상세 페이지 파싱 확인 | ☐ |
| 5 | Headless 모드 테스트 | ☐ |
| 6 | JSON 파일 저장 확인 | ☐ |

**테스트 키워드**: `카페`, `마트`, `배달`

---

### ☐ 4. jobplanet (잡플래닛) - 우선순위 중간

**파일**: `sites/jobplanet/crawler.py`

| 단계 | 작업 | 완료 |
|------|------|------|
| 1 | Bot Detection 회피 코드 적용 | ☐ |
| 2 | 테스트: `python -m sites.jobplanet.crawler --keyword "개발자" --max-jobs 3 --no-headless` | ☐ |
| 3 | 로그인 요구 페이지 처리 확인 | ☐ |
| 4 | 공고 목록 수집 확인 | ☐ |
| 5 | 상세 페이지 파싱 확인 | ☐ |
| 6 | Headless 모드 테스트 | ☐ |
| 7 | JSON 파일 저장 확인 | ☐ |

**테스트 키워드**: `개발자`, `디자이너`, `마케팅`

---

### ☐ 5. jobposting (잡포스팅) - 우선순위 중간

**파일**: `sites/jobposting/crawler.py`

| 단계 | 작업 | 완료 |
|------|------|------|
| 1 | Bot Detection 회피 코드 적용 | ☐ |
| 2 | 테스트: `python -m sites.jobposting.crawler --keyword "사무직" --max-jobs 3 --no-headless` | ☐ |
| 3 | 공고 목록 수집 확인 | ☐ |
| 4 | 상세 페이지 파싱 확인 | ☐ |
| 5 | Headless 모드 테스트 | ☐ |
| 6 | JSON 파일 저장 확인 | ☐ |

**테스트 키워드**: `사무직`, `경리`, `총무`

---

### ☐ 6. blind (블라인드) - 우선순위 낮음

**파일**: `sites/blind/crawler.py`

| 단계 | 작업 | 완료 |
|------|------|------|
| 1 | Bot Detection 회피 코드 적용 | ☐ |
| 2 | 테스트: `python -m sites.blind.crawler --keyword "semiconductor" --max-jobs 3 --no-headless` | ☐ |
| 3 | 스크롤 로드 기능 확인 | ☐ |
| 4 | 공고 목록 수집 확인 | ☐ |
| 5 | 상세 페이지 파싱 확인 | ☐ |
| 6 | Headless 모드 테스트 | ☐ |
| 7 | JSON 파일 저장 확인 | ☐ |

**테스트 키워드** (영문): `semiconductor`, `engineer`, `developer`

---

## 통합 테스트 체크리스트

| 단계 | 작업 | 완료 |
|------|------|------|
| 1 | main.py에 모든 크롤러 등록 | ☐ |
| 2 | `python test_analysis_system.py` 실행 | ☐ |
| 3 | 키워드 탐지 정상 동작 확인 | ☐ |
| 4 | 위험도 점수 계산 확인 | ☐ |
| 5 | 데이터베이스 저장 확인 | ☐ |
| 6 | 전체 크롤링 테스트: `python crawl_and_analyze.py --max-jobs 5` | ☐ |

---

## 문제 발생 시 빠른 해결

### 403 Forbidden / 차단됨
```bash
# 브라우저 표시 모드로 확인
python -m sites.[사이트].crawler --keyword "테스트" --max-jobs 1 --no-headless
```

### 셀렉터 오류
1. 브라우저에서 F12 → Elements 탭
2. 실제 요소 구조 확인
3. `crawler.py`에서 셀렉터 업데이트

### 빈 데이터
```python
# 대기 시간 증가
time.sleep(5)  # 기존 2-3초에서 증가

# 또는 명시적 대기
self.page.wait_for_selector('.job-item', timeout=15000, state="visible")
```

---

## 완료 확인

모든 체크리스트 완료 후:

```bash
# 최종 통합 테스트
python crawl_and_analyze.py --sites worknet,alba,albamon,jobplanet,jobposting --max-jobs 10

# 결과 확인
python -c "import sqlite3; conn = sqlite3.connect('data/recruitment.db'); print(conn.execute('SELECT COUNT(*) FROM jobs').fetchone())"
```
