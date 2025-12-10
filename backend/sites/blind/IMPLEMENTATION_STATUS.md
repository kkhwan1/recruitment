# Blind (TeamBlind.com) 크롤러 구현 현황

## 현재 상태: 제한적 접근 (Login Required)

### 발견 사항

#### 1. 접근 가능성 분석 (2024년 기준)

| URL | 상태 | 설명 |
|-----|------|------|
| `https://www.teamblind.com/job/search?keyword=engineer` | ❌ 차단됨 | Bot Detection 에러 페이지 표시 |
| `https://www.teamblind.com/jobs` | ⚠️ 제한적 | 로그인 필요 (Login wall) |
| `https://www.teamblind.com/` | ✅ 접근 가능 | 홈페이지는 접근 가능 |

#### 2. Bot Detection 메커니즘

Blind는 강력한 Bot Detection 시스템을 운영 중:

```
에러 메시지:
"Oops! Something went wrong. Please try again later.
If the problem continues, please contact our team.
US : blindapp@teamblind.com
KR : support@teamblind.com"
```

**시도한 회피 기법 (모두 실패)**:
- ✗ User-Agent 설정
- ✗ navigator.webdriver 속성 제거
- ✗ 브라우저 자동화 플래그 비활성화
- ✗ 랜덤 딜레이 및 스크롤
- ✗ 홈페이지 방문 후 검색 페이지 이동
- ✗ Viewport 및 Timezone 설정

#### 3. 인증 요구사항

`/jobs` 엔드포인트는 다음을 요구:
- 사용자 로그인 (이메일/비밀번호 또는 소셜 로그인)
- 회사 이메일 인증 (Blind의 핵심 정책)

### 기술적 제약사항

1. **Bot Detection 우회 불가**
   - Cloudflare 또는 유사한 서비스 사용 추정
   - 일반적인 Playwright 회피 기법으로 해결 불가

2. **인증 필요**
   - 채용 공고 접근에 로그인 필수
   - 회사 이메일 인증이 Blind 사용의 전제 조건

3. **API 미제공**
   - 공개 API 없음
   - 비공식 API도 접근 제한 예상

## 대안 및 해결 방안

### Option 1: 로그인 인증 구현 (권장하지 않음)

```python
# 이론적으로 가능하지만 권장하지 않음
def login_to_blind(email: str, password: str):
    """
    ⚠️ 주의사항:
    - Blind 서비스 약관 위반 가능성
    - 회사 이메일 사용 시 보안 리스크
    - Bot Detection으로 차단될 가능성 높음
    """
    pass  # 구현하지 않음
```

**권장하지 않는 이유**:
- 서비스 약관(ToS) 위반 우려
- 회사 계정 사용 시 컴플라이언스 리스크
- 로그인 세션 유지 복잡성

### Option 2: 수동 데이터 수집

```python
# 수동으로 Blind에서 데이터 수집 후 파일 import
def import_blind_data(json_file: str):
    """
    사용자가 수동으로 수집한 Blind 데이터를 시스템에 통합

    Args:
        json_file: 수동 수집한 JSON 파일 경로
    """
    # 표준 형식으로 변환하여 분석 시스템 통합
    pass
```

### Option 3: Blind 크롤링 제외 (현재 권장)

다른 채용 사이트에 집중:
- ✅ JobKorea (정상 작동)
- ✅ Incruit (정상 작동)
- ✅ Saramin (정상 작동)
- ✅ Hibrain (정상 작동)

## 크롤러 코드 현황

### 구현된 기능

현재 `sites/blind/crawler.py`는 다음 기능을 포함:

1. **Bot Detection 회피 설정**
   ```python
   - --disable-blink-features=AutomationControlled
   - User-Agent 설정
   - navigator.webdriver 제거
   ```

2. **검색 기능**
   - URL 인코딩
   - 동적 대기 전략

3. **공고 파싱 로직**
   - JavaScript 기반 데이터 추출
   - 정규표현식 fallback
   - 필드 정제

### 제한사항

```python
# sites/blind/crawler.py의 get_job_list() 메서드
def get_job_list(self) -> List[str]:
    """
    ⚠️ 현재 작동하지 않음

    이유:
    1. Bot Detection으로 검색 페이지 차단
    2. /jobs 엔드포인트는 로그인 필요
    3. 공고 링크 수집 불가 (0개 반환)
    """
    pass
```

## 향후 가능성

### 1. Blind API 출시 대기

Blind가 공식 API를 제공할 경우:
```python
# 미래 구현 예시
import blind_api

client = blind_api.Client(api_key="...")
jobs = client.jobs.search(keyword="engineer")
```

### 2. 파트너십 체결

Blind와 데이터 파트너십 협의:
- 공식 데이터 제공 협약
- API 키 발급
- 정기 데이터 수출

### 3. RSS/Feed 제공 여부 확인

일부 채용 사이트는 RSS 피드 제공:
```python
# 만약 Blind가 RSS를 제공한다면
import feedparser
feed = feedparser.parse("https://www.teamblind.com/jobs.rss")
```

## 테스트 결과

### 테스트 실행 기록

```bash
# 2024년 테스트 결과
python sites/blind/crawler.py

결과:
- 검색 페이지 접근: ❌ Bot Detection 에러
- /jobs 페이지 접근: ⚠️ 로그인 필요
- 공고 링크 수집: 0개
- 공고 파싱: 테스트 불가 (링크 없음)
```

### 에러 로그

```
ERROR: 공고 링크를 찾을 수 없습니다
WARNING: 공고 링크를 찾을 수 없습니다
INFO: 총 0개의 공고 링크 수집
```

## 결론 및 권장사항

### 단기 대응 (즉시)

1. **Blind 크롤링 비활성화**
   - `crawl_and_analyze.py`에서 Blind 제외
   - 다른 4개 사이트에 집중

2. **문서화**
   - 이 문서를 프로젝트 문서에 포함
   - README에 Blind 제외 이유 명시

### 중장기 대응 (6개월~1년)

1. **대안 플랫폼 추가**
   - LinkedIn Jobs API (공식 API 제공)
   - Indeed API (파트너십 가능)
   - Glassdoor (조건부 접근)

2. **Blind 상황 모니터링**
   - 분기별 접근성 재확인
   - API 출시 여부 추적
   - 정책 변경 모니터링

### 법적 고려사항

⚠️ **중요**: 크롤링 시 항상 고려해야 할 사항
- 웹사이트 이용약관(ToS) 준수
- 로봇 배제 표준(robots.txt) 확인
- 과도한 요청으로 인한 서비스 방해 금지
- 개인정보 처리 시 법률 준수 (GDPR, CCPA 등)

Blind의 경우:
- Bot Detection 존재 = 자동화 크롤링 명시적 차단 의도
- Login wall = 비인증 접근 불허 정책
- **결론**: 크롤링 시도 자체가 이용약관 위반 가능성

## 참고 자료

- [Blind 공식 사이트](https://www.teamblind.com/)
- [Blind 앱 다운로드](https://www.teamblind.com/download)
- Blind Support: blindapp@teamblind.com (US), support@teamblind.com (KR)

## 문서 이력

- 2024-12-06: 초기 분석 및 문서 작성
  - Bot Detection 확인
  - Login 요구사항 확인
  - 대안 제시
