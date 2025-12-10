# 워크넷(Work24.go.kr) 크롤러 구현 노트

## 문제점 및 해결 방법

### 문제 1: 공고 링크 0개 수집

**원인**:
- 직접 검색 URL로 접근 시 검색 결과가 0건으로 표시됨
- 워크넷은 동적 검색 시스템을 사용하며, 직접 URL 접근이 제한될 수 있음

**해결**:
- 메인 페이지에서 검색창을 통한 검색 방식으로 변경
- 여러 검색창 selector를 시도하여 호환성 확보
- Enter 키 입력 fallback 추가

### 문제 2: 검색 결과 페이지 구조 불명확

**원인**:
- 워크넷은 동적으로 콘텐츠를 로드
- 공고 링크가 onclick 이벤트, href, data 속성 등 다양한 방식으로 존재

**해결**:
- 4가지 패턴으로 공고 링크 추출:
  1. onclick 속성에서 함수 파라미터 추출
  2. href 속성에서 직접 URL 추출
  3. data-* 속성에서 공고 ID 추출
  4. 리스트 컨테이너 내 링크 탐색

## 구현 상세

### 1. search() 메서드 개선

```python
def search(self, keyword: str) -> bool:
    # 1. 메인 페이지 접속
    self.page.goto(self.config["base_url"], ...)

    # 2. 검색창 찾기 (여러 selector 시도)
    search_input_selectors = [
        '#content_keyword',  # 통합검색
        '#schWord',          # 상세검색
        'input[name="keyword"]',
        'input[placeholder*="검색"]'
    ]

    # 3. 검색 버튼 클릭 (여러 selector 시도)
    button_selectors = [
        'button.btn_search',
        'button:has-text("검색")',
        '#btnSubmit',
        '.search_btn',
        'button[onclick*="goSubmit"]'
    ]

    # 4. Enter 키 fallback
    self.page.keyboard.press('Enter')

    # 5. 결과 개수 확인
    ```

### 2. get_job_list() 메서드 개선

**4단계 링크 추출 전략**:

1. **onclick 속성 패턴 매칭**
   ```javascript
   const patterns = [
       /goDetail.*?['"]([^'"]+)['"]/,
       /openDetail.*?['"]([^'"]+)['"]/,
       /viewDetail.*?['"]([^'"]+)['"]/,
       /fn_goEmpDetail.*?['"]([^'"]+)['"]/,
       /wantedAuthNo.*?['"]([^'"]+)['"]/,
       /empId.*?['"]([^'"]+)['"]/
   ];
   ```

2. **href 속성 분석**
   - empDetail, wantedAuthNo, /detail/, jobDetail 포함 URL 탐지
   - 상대 경로를 절대 경로로 변환

3. **data 속성 추출**
   ```javascript
   document.querySelectorAll('[data-wanted-no], [data-emp-id], [data-job-id]')
   ```

4. **리스트 컨테이너 탐색**
   ```javascript
   const listSelectors = [
       '.list_result li a',
       '.result_list li a',
       '.job_list li a',
       'ul.list li a',
       'table tbody tr a',
       '[class*="list"] [class*="item"] a',
       '[id*="list"] a'
   ];
   ```

### 3. Bot Detection 회피

워크넷 특화 설정:
```python
self.browser = self.playwright.chromium.launch(
    headless=self.headless,
    args=[
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-dev-shm-usage',
    ]
)

# User-Agent 설정
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# navigator.webdriver 제거
page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
""")
```

## 테스트

### 테스트 스크립트 실행

```bash
# 수정된 크롤러 테스트
python test_worknet_fixed.py

# 기존 테스트 (메인에서 실행)
python -m sites.worknet.crawler
```

### 예상 결과

1. 메인 페이지 접속 성공
2. 검색창 입력 성공
3. 검색 실행 성공
4. 공고 링크 10개 이상 수집
5. 첫 번째 공고 상세 정보 파싱 성공

### 실패 시 디버깅

1. **스크린샷 확인**: `worknet_test_error.png`
2. **HTML 저장**: `worknet_test_error.html`
3. **로그 확인**: 콘솔 출력에서 어느 단계에서 실패했는지 확인

## 주요 변경 사항

### crawler.py

1. `search()` 메서드:
   - 직접 URL 접근 → 메인 페이지에서 검색창 이용
   - 여러 selector 패턴 시도
   - Enter 키 fallback 추가
   - 결과 개수 확인 로직 추가

2. `get_job_list()` 메서드:
   - 단순 링크 추출 → 4단계 패턴 매칭
   - onclick 이벤트 파싱 강화
   - data 속성 지원 추가
   - 디버깅 로그 추가

### config.json

- `request_delay`: 2 → 3초 (안정성 향상)
- comment 추가 (search_url 미사용 설명)

## 참고 사항

### 워크넷 URL 패턴

- 메인: `https://www.work24.go.kr`
- 공고 상세 (추정):
  - `https://www.work24.go.kr/empInfo/empInfoSrch/detail/empDetailAuthView.do?wantedAuthNo={id}`
  - `https://www.work24.go.kr/wk/a/b/1200/empDetailAuthView.do?wantedAuthNo={id}`

### 대기 시간

- 페이지 로드: 5초 (config.wait_time)
- 공고 목록 로드: 3초 추가
- 요청 간 대기: 3초 (config.request_delay)

### 알려진 제약

1. 워크넷은 동적 로딩을 사용하므로 headless 모드에서 제대로 작동하지 않을 수 있음
2. 검색 결과가 0건일 경우 원인 파악 필요 (captcha, 로그인 요구 등)
3. 공고 상세 페이지 URL 형식이 변경될 수 있음

## 트러블슈팅

### 검색 결과 0건

1. 브라우저를 headless=False로 실행하여 직접 확인
2. 스크린샷으로 페이지 상태 확인
3. captcha 또는 로그인 요구 여부 확인
4. 다른 키워드로 시도

### 공고 링크 0개

1. HTML 저장하여 구조 분석
2. JavaScript 콘솔에서 selector 테스트
3. onclick 함수 패턴 변경 확인
4. 네트워크 탭에서 AJAX 요청 확인

## 다음 단계

1. 실제 테스트로 검증
2. 공고 상세 페이지 파싱 selector 최적화
3. 페이지네이션 지원 추가
4. 에러 핸들링 강화
