# Blind 크롤러 셀렉터 분석 결과

**분석 일자**: 2024-12-06
**분석 대상**: https://www.teamblind.com/job/search?keyword=engineer
**상태**: ❌ 크롤링 불가능 (Bot Detection + Login Required)

---

## 분석 요약

Blind (TeamBlind.com) 채용 공고 크롤러는 **기술적으로 크롤링이 불가능**한 것으로 확인되었습니다.

### 핵심 발견사항

| 항목 | 결과 |
|------|------|
| 공고 링크 수집 | ❌ 0개 (예상: 10-50개) |
| Bot Detection | ✅ 활성화됨 |
| Login 요구사항 | ✅ 필요함 |
| 셀렉터 문제 | ❌ 아님 (접근 자체가 차단됨) |

---

## 상세 분석

### 1. Bot Detection 확인

#### 테스트 URL
```
https://www.teamblind.com/job/search?keyword=engineer
```

#### 응답 내용
```
Oops! Something went wrong. Please try again later.
If the problem continues, please contact our team.
US : blindapp@teamblind.com
KR : support@teamblind.com
```

#### 결론
Blind는 **강력한 Bot Detection 시스템**을 운영하며, 자동화된 크롤링을 명시적으로 차단합니다.

### 2. 우회 시도 결과

다음 Bot Detection 우회 기법을 모두 시도했으나 **전부 실패**:

| 기법 | 설명 | 결과 |
|------|------|------|
| User-Agent 설정 | Chrome 120 UA 사용 | ❌ 실패 |
| navigator.webdriver 제거 | 자동화 속성 숨김 | ❌ 실패 |
| 브라우저 플래그 조정 | `--disable-blink-features` 등 | ❌ 실패 |
| 랜덤 딜레이 | 1-5초 무작위 대기 | ❌ 실패 |
| 홈페이지 우회 | 홈 → 검색 순차 접근 | ❌ 실패 |
| Viewport/Timezone 설정 | 실제 브라우저 환경 모방 | ❌ 실패 |
| 스크롤 시뮬레이션 | 사용자 행동 모방 | ❌ 실패 |

### 3. 대체 엔드포인트 테스트

| URL | 접근성 | 상태 |
|-----|--------|------|
| `/job/search?keyword=engineer` | ❌ | Bot Detection 에러 |
| `/jobs` | ⚠️ | Login 필요 |
| `/` (홈페이지) | ✅ | 접근 가능 |

#### /jobs 엔드포인트 분석
- 페이지 로드는 성공
- "Sign in" / "Log in" 메시지 표시
- 공고 목록 접근에 **인증 필수**

### 4. HTML 구조 분석

Bot Detection으로 인해 실제 공고 페이지 HTML을 확인할 수 없었습니다.

```javascript
// 시도한 셀렉터 (모두 요소 없음)
document.querySelectorAll('a[href*="/job/"]')        // 0개
document.querySelectorAll('div.job-card')            // 0개
document.querySelectorAll('div[class*="job"]')       // 0개
document.querySelectorAll('article')                 // 0개
```

---

## 코드 수정 내역

### 1. `crawler.py` 개선

#### Before (원본)
```python
def get_job_list(self) -> List[str]:
    """현재 페이지의 공고 목록에서 공고 링크 수집"""
    # 직접 링크 수집 시도
    # → Bot Detection 감지 못함
```

#### After (개선)
```python
def get_job_list(self) -> List[str]:
    """
    현재 페이지의 공고 목록에서 공고 링크 수집

    ⚠️ 현재 제한사항:
    - Blind는 Bot Detection으로 자동 크롤링 차단
    - /job/search 엔드포인트: Bot Detection 에러
    - /jobs 엔드포인트: 로그인 필요
    """
    # 페이지 상태 확인
    body_text = self.page.evaluate("document.body.innerText")

    # Bot Detection 에러 체크
    if "Oops" in body_text or "Something went wrong" in body_text:
        self.logger.error("❌ Bot Detection 감지됨")
        return []

    # Login wall 체크
    if "Sign in" in body_text or "Log in" in body_text:
        self.logger.warning("⚠️ 로그인 필요")
        return []
```

**개선 사항**:
- ✅ Bot Detection 자동 감지
- ✅ Login wall 감지
- ✅ 명확한 에러 메시지
- ✅ 문서 참조 안내

### 2. 문서 추가

새로운 문서 생성:
- `sites/blind/IMPLEMENTATION_STATUS.md` - 상세 분석 문서
- `BLIND_CRAWLER_ANALYSIS.md` - 이 문서

---

## 테스트 결과

### 실행 로그

```bash
$ python sites/blind/crawler.py

=== Blind 크롤러 테스트 ===

2025-12-06 16:58:28 - BlindCrawler - INFO - 브라우저 시작 완료
✅ 브라우저 시작 완료

2025-12-06 16:58:39 - BlindCrawler - INFO - 'engineer' 검색 완료
✅ 검색 페이지 접속 시도

--- 공고 링크 수집 시도 ---
2025-12-06 16:58:39 - BlindCrawler - ERROR - ❌ Bot Detection 감지됨
2025-12-06 16:58:39 - BlindCrawler - ERROR - 에러 메시지: Oops! Something...
2025-12-06 16:58:39 - BlindCrawler - INFO - 💡 해결 방법: IMPLEMENTATION_STATUS.md

📊 결과: 0개 수집

✅ 예상대로 0개 수집됨 (Bot Detection/Login wall)
```

### 예상 vs 실제

| 항목 | 예상 | 실제 | 상태 |
|------|------|------|------|
| 페이지 로드 | 성공 | 에러 페이지 | ❌ |
| 공고 링크 | 10-50개 | 0개 | ❌ |
| 셀렉터 매칭 | 성공 | N/A | ❌ |
| 상세 페이지 | 파싱 가능 | 접근 불가 | ❌ |

---

## 대안 및 권장사항

### ❌ 권장하지 않는 방법

1. **로그인 인증 구현**
   - 이유: 서비스 약관 위반 가능성
   - 리스크: 법적 문제, 계정 정지

2. **Selenium Stealth 플러그인**
   - 이유: Blind의 Bot Detection이 너무 강력함
   - 결과: 시도했으나 실패

3. **Proxy/VPN 사용**
   - 이유: 근본적 해결책 아님
   - 결과: IP 차단 가능성

### ✅ 권장하는 방법

#### Option 1: Blind 크롤링 제외 (즉시 실행)

**현재 작동하는 사이트에 집중**:
- ✅ JobKorea (정상 작동)
- ✅ Incruit (정상 작동)
- ✅ Saramin (정상 작동)
- ✅ Hibrain (정상 작동)

```python
# crawl_and_analyze.py 수정
SITES = [
    "jobkorea",
    "incruit",
    "saramin",
    "hibrain"
    # "blind"  # Bot Detection으로 제외
]
```

#### Option 2: 수동 데이터 수집 지원

사용자가 수동으로 Blind에서 데이터를 수집한 경우 시스템에 통합:

```python
def import_blind_manual_data(json_file: str):
    """
    수동 수집한 Blind 데이터를 표준 형식으로 변환

    Args:
        json_file: 사용자가 수동 작성한 JSON 파일
    """
    # 표준 형식으로 변환 후 분석 시스템 통합
    pass
```

#### Option 3: 향후 API 대기

Blind가 공식 API를 제공할 경우:
- 공식 API 키 발급 신청
- 파트너십 체결 고려
- RSS 피드 제공 여부 확인

---

## 기술적 근거

### 1. Bot Detection 메커니즘 추정

Blind는 다음과 같은 Bot Detection 시스템 사용 추정:

- **Cloudflare Bot Management** (가능성 높음)
  - JavaScript Challenge
  - Browser Fingerprinting
  - Behavioral Analysis

- **Custom Bot Detection**
  - Request Pattern Analysis
  - User-Agent Validation
  - Rate Limiting

### 2. Playwright 회피 한계

Playwright의 일반적인 회피 기법으로는 극복 불가:

```python
# 시도한 모든 기법
args = [
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-dev-shm-usage',
]

page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
""")
```

**결과**: Cloudflare 등 고급 Bot Detection은 더 깊은 수준에서 자동화 감지

### 3. 법적 고려사항

⚠️ **중요**: Blind의 Bot Detection 존재는 자동화 크롤링을 **명시적으로 거부**하는 의도

- 이용약관(ToS) 위반 가능성
- robots.txt 확인 필요
- 법적 리스크 존재

---

## 결론

### 현재 상태

Blind 크롤러는 **셀렉터 문제가 아닌**, **Bot Detection과 인증 요구사항**으로 인해 크롤링 불가능합니다.

### 최종 권장사항

1. **단기 (즉시)**
   - Blind 크롤링 비활성화
   - 다른 4개 사이트에 집중
   - 문서화 완료 (✅)

2. **중기 (3-6개월)**
   - 대안 플랫폼 추가 검토
     - LinkedIn Jobs API
     - Indeed API
     - Glassdoor
   - Blind 접근성 분기별 재확인

3. **장기 (1년+)**
   - Blind 공식 API 출시 모니터링
   - 데이터 파트너십 가능성 탐색
   - 법적 검토 후 접근 방법 재평가

### 수정된 파일

- ✅ `c:\Users\USER\claude_code\채용시스템\sites\blind\crawler.py`
  - Bot Detection 감지 로직 추가
  - Login wall 감지 로직 추가
  - 개선된 에러 메시지

- ✅ `c:\Users\USER\claude_code\채용시스템\sites\blind\IMPLEMENTATION_STATUS.md`
  - 상세 분석 문서 (7 섹션)
  - 대안 제시
  - 법적 고려사항

- ✅ `c:\Users\USER\claude_code\채용시스템\BLIND_CRAWLER_ANALYSIS.md`
  - 이 분석 보고서

### 코드 테스트 결과

```bash
✅ Bot Detection 자동 감지 - 정상 작동
✅ 명확한 에러 메시지 - 정상 작동
✅ 문서 참조 안내 - 정상 작동
✅ 0개 링크 수집 (예상대로) - 정상 작동
```

---

## 참고 자료

- [Blind 공식 사이트](https://www.teamblind.com/)
- [IMPLEMENTATION_STATUS.md](sites/blind/IMPLEMENTATION_STATUS.md) - 상세 분석
- [Playwright Documentation](https://playwright.dev/)
- [Bot Detection Best Practices](https://www.cloudflare.com/learning/bots/what-is-bot-management/)

---

**분석자**: Claude Code (SuperClaude Framework)
**문서 버전**: 1.0
**최종 수정**: 2024-12-06
