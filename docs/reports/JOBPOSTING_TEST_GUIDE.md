# JobPosting 크롤러 수정 및 테스트 가이드

## 수정 완료 사항

JobPosting 크롤러의 셀렉터를 분석하고 수정했습니다.

### 주요 변경 사항

1. **다중 셀렉터 전략**: 5가지 셀렉터 전략을 동시에 사용하여 링크 수집 성공률 향상
2. **링크 필터링**: employ, detail, no= 키워드로 공고 링크만 선별
3. **URL 정규화**: 다양한 형태의 상대/절대 경로를 올바르게 처리
4. **디버깅 강화**: 각 전략별 성공 개수를 콘솔에 출력
5. **오류 처리**: 링크 수집 실패 시 페이지 상태 확인

## 테스트 방법

### 1단계: 빠른 테스트 (추천)

```bash
cd c:\Users\USER\claude_code\채용시스템
python test_jobposting_fixed.py
```

이 스크립트는:
- 브라우저를 표시 모드로 실행
- "반도체" 키워드로 최대 3개 공고 수집
- 결과를 화면에 출력하고 파일로 저장
- Enter 키를 눌러 종료할 때까지 대기

### 2단계: 상세 분석 (문제 발생 시)

```bash
python test_jobposting_selectors.py
```

이 스크립트는:
- 각 셀렉터 전략별 성공 개수 출력
- 샘플 링크 5개 표시
- 페이지 내용 일부 출력
- 실제 크롤링 테스트 수행

### 3단계: 직접 실행

```bash
python sites/jobposting/crawler.py
```

기본 크롤러를 직접 실행하여 동작 확인

## 기대 결과

### 성공 케이스
```
수집된 공고 수: 3개

수집된 공고 목록:

   [1] 반도체 공정 엔지니어
       회사: ABC 주식회사
       위치: 경기도 화성시
       URL: http://jobposting.co.kr/job/employ_detail.php?no=12345

   [2] 반도체 설비 엔지니어
       회사: XYZ 테크
       위치: 서울특별시
       URL: http://jobposting.co.kr/job/employ_detail.php?no=12346
```

### 실패 케이스 (여전히 0개 수집)

가능한 원인:
1. **사이트 구조 변경**: JobPosting 사이트가 최근에 HTML 구조를 변경했을 수 있음
2. **접근 제한**: 자동화 탐지로 인한 접근 차단
3. **검색 결과 없음**: "반도체" 키워드로 검색 결과가 실제로 없을 수 있음
4. **JavaScript 렌더링**: 페이지가 완전히 로드되지 않았을 수 있음

## 문제 해결 가이드

### 브라우저에서 직접 확인

1. 테스트 스크립트 실행 시 브라우저가 자동으로 열립니다
2. 브라우저에서 페이지 구조를 육안으로 확인하세요:
   - 검색 결과가 표시되는가?
   - 공고 링크가 보이는가?
   - 오류 메시지가 있는가?

### 콘솔 로그 확인

브라우저의 개발자 도구(F12)를 열고 Console 탭에서:
```
전략 1 (employ_detail.php): X개
전략 2 (employ_detail): Y개
전략 3 (no=): Z개
...
최종 링크 수: N개
```

각 전략별 결과를 확인하세요.

### 대기 시간 조정

`sites/jobposting/config.json` 파일 수정:
```json
{
  "wait_time": 5,  // 3에서 5로 증가
  "request_delay": 3  // 2에서 3으로 증가
}
```

### 추가 셀렉터 전략

크롤러 코드에 새로운 전략 추가 가능:
```javascript
// 전략 6: 특정 클래스명
const strategy6 = document.querySelectorAll('.job-link a');
```

## 수정된 파일

- `c:\Users\USER\claude_code\채용시스템\sites\jobposting\crawler.py` - 메인 크롤러 (수정됨)
- `c:\Users\USER\claude_code\채용시스템\test_jobposting_fixed.py` - 빠른 테스트 스크립트 (신규)
- `c:\Users\USER\claude_code\채용시스템\test_jobposting_selectors.py` - 상세 분석 스크립트 (신규)
- `c:\Users\USER\claude_code\채용시스템\sites\jobposting\SELECTOR_FIX.md` - 기술 문서 (신규)

## 다음 단계

1. **테스트 실행**: `test_jobposting_fixed.py` 실행하여 결과 확인
2. **결과 보고**: 수집된 공고 개수와 샘플 확인
3. **문제 진단**: 실패 시 브라우저 화면과 콘솔 로그 확인
4. **추가 조치**: 필요시 추가 셀렉터 전략 개발 또는 사이트 구조 재분석

## 지원

문제가 계속되면 다음 정보를 제공해주세요:
- 테스트 스크립트 실행 결과 (콘솔 출력)
- 브라우저에서 보이는 페이지 상태
- 개발자 도구 Console 탭의 로그
- 스크린샷 (`jobposting_debug.png`)
