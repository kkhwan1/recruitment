# JobPosting 크롤러 셀렉터 수정 보고서

## 문제 상황
- **현상**: 공고 링크를 0개 수집
- **원인**: 단일 셀렉터 전략의 한계
- **영향**: 크롤러가 전혀 작동하지 않음

## 수정 내용

### 1. 다중 셀렉터 전략 적용

기존 단일 셀렉터:
```javascript
const jobLinks = document.querySelectorAll('a[href*="employ_detail.php"]');
```

수정된 다중 전략:
```javascript
// 전략 1: employ_detail.php 패턴
const strategy1 = document.querySelectorAll('a[href*="employ_detail.php"]');

// 전략 2: employ_detail (확장자 없이)
const strategy2 = document.querySelectorAll('a[href*="employ_detail"]');

// 전략 3: no= 파라미터가 있는 모든 링크
const strategy3 = document.querySelectorAll('a[href*="no="]');

// 전략 4: 테이블 내부의 모든 링크
const strategy4 = document.querySelectorAll('table a[href]');

// 전략 5: tr 내부의 모든 링크
const strategy5 = document.querySelectorAll('tr a[href]');
```

### 2. 링크 필터링 강화

```javascript
// employ 또는 detail 또는 no= 가 포함된 링크만 처리
if (!href.includes('employ') && !href.includes('detail') && !href.includes('no=')) {
    return;
}
```

### 3. URL 정규화 개선

```javascript
// 상대 경로를 절대 경로로 변환
let fullUrl;
if (href.startsWith('http://') || href.startsWith('https://')) {
    fullUrl = href;
} else if (href.startsWith('/')) {
    fullUrl = baseUrl + href;
} else if (href.startsWith('employ_detail')) {
    fullUrl = baseUrl + '/job/' + href;
} else {
    fullUrl = baseUrl + '/job/' + href;
}
```

### 4. 디버깅 정보 추가

```javascript
console.log('전략 1 (employ_detail.php):', strategy1.length);
console.log('전략 2 (employ_detail):', strategy2.length);
console.log('전략 3 (no=):', strategy3.length);
console.log('전략 4 (table a):', strategy4.length);
console.log('전략 5 (tr a):', strategy5.length);
console.log('최종 링크 수:', links.length);
```

### 5. 오류 처리 강화

```python
# 링크가 없는 경우 페이지 상태 확인
if not job_links:
    self.logger.warning("공고 링크를 찾지 못했습니다. 페이지 상태 확인 중...")
    page_text = self.page.evaluate('() => document.body.innerText.substring(0, 500)')
    self.logger.debug(f"페이지 내용 샘플: {page_text}")
```

## 테스트 방법

### 방법 1: 빠른 테스트
```bash
cd c:\Users\USER\claude_code\채용시스템
python test_jobposting_fixed.py
```

### 방법 2: 셀렉터 분석
```bash
python test_jobposting_selectors.py
```

### 방법 3: 기본 실행
```bash
python sites/jobposting/crawler.py
```

## 기대 효과

1. **다중 전략**: 5가지 셀렉터 전략으로 링크 수집 성공률 향상
2. **유연성**: 사이트 구조 변경에 대한 내구성 증가
3. **디버깅**: 각 전략별 성공 개수 확인 가능
4. **안정성**: 오류 상황에서도 페이지 상태 확인

## 주의사항

- 브라우저 창이 표시되므로(`headless=False`) 실제 페이지 상태를 확인할 수 있습니다
- 콘솔 로그에서 각 전략별 링크 수를 확인하세요
- 링크가 여전히 0개라면 사이트 접근 제한이나 구조 변경을 의심해야 합니다

## 다음 단계

1. 테스트 스크립트 실행하여 수정 효과 확인
2. 브라우저 콘솔에서 각 전략별 성공 개수 확인
3. 실패 시 페이지 HTML 구조 직접 확인
4. 필요시 추가 셀렉터 전략 개발

## 파일 위치

- **수정된 크롤러**: `c:\Users\USER\claude_code\채용시스템\sites\jobposting\crawler.py`
- **테스트 스크립트**: `c:\Users\USER\claude_code\채용시스템\test_jobposting_fixed.py`
- **셀렉터 분석**: `c:\Users\USER\claude_code\채용시스템\test_jobposting_selectors.py`
- **이 보고서**: `c:\Users\USER\claude_code\채용시스템\sites\jobposting\SELECTOR_FIX.md`
