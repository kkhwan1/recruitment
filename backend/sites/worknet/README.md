# 워크넷 크롤러

워크넷(www.work.go.kr → www.work24.go.kr) 채용 공고 크롤러

## 현재 상태

⚠️ **개발 중** - 워크넷 사이트 구조 분석 필요

### 확인된 사항

1. **URL 리다이렉트**
   - www.work.go.kr → www.work24.go.kr 자동 리다이렉트
   - base_url: `https://www.work24.go.kr`

2. **검색 페이지 구조**
   - 복잡한 검색 조건 필요
   - 직접 검색 URL로 이동 시 "검색된 내용이 없습니다" 표시
   - 실제 검색 흐름: 메인 페이지 → 검색창 입력 → 검색 버튼 클릭

3. **공고 목록 구조**
   - 테이블 기반 레이아웃 (`#contentArea`)
   - 동적 로딩 가능성 (Ajax/API 기반)
   - iframe 사용하지 않음 (확인됨)

### 구현된 기능

- ✅ 기본 크롤러 구조 (BaseCrawler 패턴 참고)
- ✅ 브라우저 자동화 (Playwright)
- ✅ 검색 URL 접근
- ✅ 공고 상세 파싱 로직
- ✅ JSON 저장 기능

### 미완성 부분

- ❌ 정확한 search_url 파라미터
- ❌ 공고 링크 수집 (get_job_list)
- ❌ 실제 데이터 수집 테스트

## 사용 방법

### 기본 사용

```python
from sites.worknet.crawler import WorknetCrawler

crawler = WorknetCrawler(headless=False)
try:
    crawler.start()
    jobs = crawler.crawl("반도체", max_jobs=3)
    if jobs:
        crawler.save_results("반도체", jobs)
finally:
    crawler.close()
```

### 테스트 스크립트

```bash
# 크롤러 테스트
python sites/worknet/crawler.py

# 사이트 구조 분석
python test_worknet_structure.py
python test_worknet_search.py
python test_worknet_iframe.py
```

## 개선 필요사항

### 1. 정확한 검색 URL 파악

현재 설정된 URL이 작동하지 않음. 다음 방법으로 정확한 URL 확인 필요:

1. 워크넷 메인 페이지에서 수동 검색
2. 개발자 도구 Network 탭에서 실제 요청 URL 확인
3. 파라미터 분석 및 config.json 업데이트

### 2. 공고 링크 패턴 분석

```javascript
// 현재 시도한 패턴들 (작동 안함)
- onclick="goDetail('...')"
- href="...empDetailAuthView.do..."
- href="...wantedAuthNo=..."

// 추가로 확인 필요한 패턴
- API 호출 방식
- 동적 로딩 대기 시간
- 페이징 처리 방식
```

### 3. 동적 콘텐츠 로딩 대응

- 검색 버튼 클릭 후 대기 시간 조정
- Ajax 요청 완료 대기
- 로딩 인디케이터 확인

## 설정 파일 (config.json)

```json
{
  "site_name": "워크넷",
  "base_url": "https://www.work24.go.kr",
  "search_url": "https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?keyword={keyword}&empTpGbcd=1&dtlEmpSrchMode=0&sortField=RECRT_DATE&sortOrderBy=DESC",
  "wait_time": 5,
  "max_retries": 3,
  "request_delay": 2
}
```

## 디버깅 가이드

### 1. 실제 검색 흐름 확인

```bash
# headless=False로 실행하여 브라우저 확인
python -c "
from sites.worknet.crawler import WorknetCrawler
c = WorknetCrawler(headless=False)
c.start()
c.search('반도체')
input('엔터를 누르면 종료...')
c.close()
"
```

### 2. 페이지 구조 분석

- 개발자 도구(F12) → Elements 탭에서 공고 목록 구조 확인
- onclick 이벤트 확인
- href 속성 확인
- 클래스명/ID 확인

### 3. Network 분석

- 개발자 도구 → Network 탭
- 검색 실행
- XHR/Fetch 요청 확인
- 응답 데이터 구조 파악

## 참고사항

- 정부 사이트 특성상 복잡한 인증/보안 시스템 가능성
- 로봇 방지 메커니즘 존재 가능성
- API 기반일 경우 직접 API 호출 고려
- 인크루트 크롤러 (sites/incruit/crawler.py) 참고

## 다음 단계

1. 워크넷 실제 사용하여 검색 흐름 파악
2. 개발자 도구로 정확한 URL 및 파라미터 확인
3. get_job_list() 함수 업데이트
4. 실제 데이터 수집 테스트
5. DB 저장 통합 테스트
