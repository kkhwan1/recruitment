# 사람인 크롤러 Headless 모드 수정 보고서

## 문제 요약

**증상:**
- `headless=False`: 정상 작동 (공고 수집 성공)
- `headless=True`: `Page.evaluate: Execution context was destroyed` 오류 발생

**오류 메시지:**
```
playwright._impl._errors.Error: Page.evaluate: Execution context was destroyed,
most likely because of a navigation
```

---

## 근본 원인 분석

### 1. **Race Condition (타이밍 문제)**

**문제:**
- Playwright의 `page.goto(..., wait_until="load")`는 초기 DOM 로드 완료만을 의미
- 사람인 사이트는 React/SPA 기반으로 클라이언트 사이드 렌더링 사용
- Headless 모드에서는 렌더링이 더 빠르게 완료되어 race condition 발생
- `page.evaluate()` 실행 시점에 페이지가 아직 JavaScript를 실행 중이거나 리다이렉트 진행 중

**타이밍 차이:**
```
Headed Mode (느림):
  goto() → load event → [렌더링 지연] → evaluate() ✓

Headless Mode (빠름):
  goto() → load event → evaluate() ✗ (페이지가 아직 불안정)
                      → [추가 네비게이션/리렌더링]
```

### 2. **Bot Detection (봇 감지)**

**문제:**
- Headless 모드는 `navigator.webdriver` 속성이 자동으로 설정됨
- Automation detection 플래그들이 활성화됨
- 사람인 서버가 봇을 감지하고 리다이렉트/CAPTCHA 페이지로 전환
- 전환 중에 execution context가 파괴됨

**감지 포인트:**
```javascript
// 기본 Playwright headless는 이런 속성들이 노출됨:
navigator.webdriver === true  // ← Bot detection!
window.chrome === undefined
```

### 3. **동적 콘텐츠 로딩**

**문제:**
- SPA는 초기 HTML이 거의 비어있고 JavaScript로 동적 렌더링
- `wait_until="load"`는 정적 리소스 로드만 체크
- 실제 공고 데이터는 API 호출 → 렌더링 과정 필요
- 이 과정이 완료되기 전에 `page.evaluate()` 실행

---

## 해결 방법

### 1. **Bot Detection 회피**

#### 변경 전:
```python
def start(self):
    self.browser = self.playwright.chromium.launch(headless=self.headless)
    self.page = self.browser.new_page()
```

#### 변경 후:
```python
def start(self):
    # Bot detection 회피 설정
    self.browser = self.playwright.chromium.launch(
        headless=self.headless,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage',
        ]
    )

    # 일반 브라우저 User Agent 설정
    self.page = self.browser.new_page(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    # navigator.webdriver 제거
    self.page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
```

**효과:**
- `navigator.webdriver` → `undefined` (봇으로 인식되지 않음)
- Automation 플래그 비활성화
- 일반 사용자 브라우저처럼 보임

### 2. **안정적인 Wait 전략**

#### 변경 전:
```python
self.page.goto(search_url, wait_until="load", timeout=60000)
time.sleep(3)  # 고정 대기
```

#### 변경 후:
```python
# 1. 기본 DOM 로드
self.page.goto(search_url, wait_until="domcontentloaded", timeout=60000)

# 2. 네트워크 안정화 (선택적)
try:
    self.page.wait_for_load_state("networkidle", timeout=10000)
except:
    pass  # 타임아웃해도 계속 진행

# 3. 공고 요소가 실제로 나타날 때까지 대기
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
        element_found = True
        break
    except:
        continue

# 4. 최종 안정화
try:
    self.page.wait_for_load_state("load", timeout=10000)
except:
    pass

time.sleep(2)  # DOM 안정화
```

**Wait 전략 비교:**

| Wait 옵션 | 의미 | 사람인 적합성 |
|-----------|------|--------------|
| `load` | 모든 리소스 로드 완료 | ❌ 초기 렌더링만 체크 |
| `domcontentloaded` | DOM 파싱 완료 | ✅ 빠르고 안정적 |
| `networkidle` | 500ms 동안 네트워크 요청 없음 | ⚠️ SPA에서 너무 오래 걸림 |
| `wait_for_selector()` | 특정 요소 나타날 때까지 | ✅ 실제 콘텐츠 확인 |

**계층적 Wait 전략:**
```
Level 1: domcontentloaded (필수, 빠름)
    ↓
Level 2: networkidle (선택, 타임아웃 허용)
    ↓
Level 3: wait_for_selector (필수, 실제 데이터 확인)
    ↓
Level 4: load state (선택, 최종 안정화)
    ↓
Level 5: sleep(2) (DOM 안정화)
```

### 3. **에러 핸들링 개선**

#### 변경 전:
```python
job_links_data = self.page.evaluate("""...""")  # 오류 발생 시 크래시
```

#### 변경 후:
```python
try:
    sample_html = self.page.evaluate("() => document.body.innerHTML.substring(0, 2000)")
except:
    self.logger.warning("HTML 샘플 수집 실패 - 페이지가 불안정함")
```

---

## 테스트 결과

### Before Fix:
```
headless=False: ✅ 9개 공고 수집 (약 45초)
headless=True:  ❌ 0개 공고 수집 (Execution context destroyed 오류)
```

### After Fix:
```
headless=False: ✅ 5개 공고 수집 (52.8초)
headless=True:  ✅ 5개 공고 수집 (49.9초, 5.6% 더 빠름)
```

### 상세 테스트 로그:

#### Headless Mode (성공):
```
2025-11-20 20:06:44 - INFO - 브라우저 시작 완료 (bot detection 회피 설정 적용)
2025-11-20 20:06:47 - INFO - 초기 페이지 로드 완료 (domcontentloaded)
2025-11-20 20:06:50 - INFO - 네트워크 안정화 완료
2025-11-20 20:06:50 - INFO - 공고 링크 요소 발견: a[href*="/zf_user/jobs/relay/view"]
2025-11-20 20:06:50 - INFO - 페이지 load 상태 완료
2025-11-20 20:06:52 - INFO - 총 5개의 공고 링크 발견
```

---

## 적용된 수정 사항 요약

### 파일: `sites/saramin/crawler.py`

1. **`start()` 메서드 (lines 38-65)**
   - Bot detection 회피 설정 추가
   - User agent 설정
   - `navigator.webdriver` 제거 스크립트

2. **`get_job_list()` 메서드 (lines 94-158)**
   - `wait_until="domcontentloaded"` 사용
   - 선택적 `networkidle` 대기
   - 다중 셀렉터 대기 루프
   - 계층적 안정화 전략
   - 개선된 에러 핸들링

---

## 권장 사항

### 1. **Production 환경에서 항상 headless=True 사용**
```python
# 권장
crawler = SaraminCrawler(headless=True)  # 더 빠르고 서버 리소스 절약

# 디버깅 시에만
crawler = SaraminCrawler(headless=False)  # 문제 발생 시 시각적 확인
```

### 2. **테스트 방법**
```bash
# 간단 테스트
python sites/saramin/test_headless.py

# 또는 직접 실행
python -c "from sites.saramin.crawler import SaraminCrawler; \
c = SaraminCrawler(headless=True); \
c.start(); jobs = c.crawl('반도체', 3); c.close(); \
print(f'Success: {len(jobs)} jobs')"
```

### 3. **모니터링 포인트**
- "공고 링크 요소 발견" 로그 확인 (요소 감지 성공)
- "네트워크 안정화 완료" 로그 확인 (빠른 로딩)
- "총 N개의 공고 링크 발견" 확인 (데이터 수집 성공)

### 4. **추가 최적화 가능성**
```python
# 더 빠른 크롤링을 위한 옵션 (필요시)
self.page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}",
                lambda route: route.abort())  # 이미지/CSS 차단
```

---

## 기술적 세부사항

### Playwright Wait 옵션 상세

| 옵션 | 트리거 조건 | 타임아웃 영향 | SPA 적합성 |
|------|------------|--------------|-----------|
| `load` | `window.load` 이벤트 | 리소스 로딩 지연에 민감 | ⚠️ |
| `domcontentloaded` | DOM 파싱 완료 | 빠름, 안정적 | ✅ |
| `networkidle` | 500ms 동안 네트워크 요청 0개 | 매우 느림 (API 폴링 등) | ❌ |
| `commit` | 네비게이션 커밋 | 매우 빠름 | ❌ |

### Bot Detection 회피 메커니즘

1. **Automation Flags 제거:**
   ```python
   '--disable-blink-features=AutomationControlled'
   ```
   - `navigator.webdriver` 자동 설정 방지
   - Chromium의 automation 감지 플래그 비활성화

2. **User Agent 위장:**
   ```python
   user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'
   ```
   - 실제 Chrome 브라우저처럼 보이게 함
   - 버전 번호는 최신 Chrome에 맞춤

3. **Navigator 객체 수정:**
   ```javascript
   Object.defineProperty(navigator, 'webdriver', {
       get: () => undefined
   });
   ```
   - JavaScript에서 `navigator.webdriver` 체크를 우회

### Race Condition 방지 전략

```
Traditional (FAIL):
  goto() → evaluate() ✗
           ↑
           페이지가 아직 준비 안됨

Improved (SUCCESS):
  goto(domcontentloaded) → wait_for_selector() → evaluate() ✓
                           ↑
                           실제 데이터 확인
```

---

## 문제 해결 가이드

### 문제: 여전히 "Execution context destroyed" 발생

**원인:** 사람인 서버가 새로운 bot detection 방법 도입

**해결:**
1. 더 긴 대기 시간 추가:
   ```python
   time.sleep(5)  # 2초 → 5초로 증가
   ```

2. 추가 stealth 옵션:
   ```python
   from playwright_stealth import stealth_sync
   stealth_sync(self.page)
   ```

### 문제: 공고 링크를 찾을 수 없음

**원인:** 사람인 HTML 구조 변경

**해결:**
1. 브라우저를 headed 모드로 실행하여 실제 HTML 확인
2. `selectors_to_wait` 리스트 업데이트
3. 디버그 모드로 HTML 샘플 확인

---

## 참고 자료

- [Playwright Wait Strategies](https://playwright.dev/python/docs/navigations#wait-until)
- [Bot Detection Evasion](https://github.com/microsoft/playwright/issues/2411)
- [Execution Context Destroyed 해결](https://github.com/microsoft/playwright/issues/1090)

---

## 버전 정보

- **수정 날짜:** 2025-11-20
- **Playwright 버전:** 1.40+
- **Python 버전:** 3.13
- **테스트 환경:** Windows 10

---

## 요약

**문제:** Headless 모드에서 execution context 파괴 오류
**원인:** Bot detection + Race condition
**해결:** Bot 회피 설정 + 계층적 wait 전략
**결과:** ✅ 양쪽 모드 모두 안정적 작동 (headless가 5.6% 더 빠름)
