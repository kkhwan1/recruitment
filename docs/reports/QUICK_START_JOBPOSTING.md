# JobPosting 크롤러 빠른 시작 가이드

## 🚀 즉시 실행

```bash
cd c:\Users\USER\claude_code\채용시스템
python test_jobposting_fixed.py
```

**결과**: 브라우저가 열리고 "반도체" 키워드로 3개 공고를 수집합니다.

---

## ✅ 수정 완료 항목

- [x] 셀렉터 전략 5가지로 확장
- [x] 링크 필터링 강화
- [x] URL 정규화 개선
- [x] 디버깅 기능 추가
- [x] 오류 처리 강화
- [x] 테스트 스크립트 3개 작성
- [x] 문서 4개 작성

---

## 📊 주요 변경 사항

### Before
```javascript
// 단일 셀렉터
document.querySelectorAll('a[href*="employ_detail.php"]')
```

### After
```javascript
// 5가지 셀렉터 전략
1. 'a[href*="employ_detail.php"]'
2. 'a[href*="employ_detail"]'
3. 'a[href*="no="]'
4. 'table a[href]'
5. 'tr a[href]'
```

---

## 📂 파일 구조

```
채용시스템/
│
├── test_jobposting_fixed.py          ⭐ 빠른 테스트 (추천)
├── test_jobposting_selectors.py      🔍 상세 분석
├── analyze_jobposting.py             🔬 HTML 구조 분석
│
├── JOBPOSTING_TEST_GUIDE.md          📖 사용 가이드
├── JOBPOSTING_FIX_SUMMARY.md         📋 완료 보고서
├── QUICK_START_JOBPOSTING.md         ⚡ 이 파일
│
└── sites/jobposting/
    ├── crawler.py                     ✅ 수정됨 (메인)
    ├── config.json                    (기존)
    └── SELECTOR_FIX.md                📄 기술 문서
```

---

## 🎯 테스트 옵션

### 1️⃣ 빠른 테스트 (추천)
```bash
python test_jobposting_fixed.py
```
- 3개 공고 수집
- 결과 화면 출력
- 파일로 저장

### 2️⃣ 상세 분석
```bash
python test_jobposting_selectors.py
```
- 셀렉터별 성공 개수
- 샘플 링크 출력
- 페이지 내용 확인

### 3️⃣ HTML 구조 분석
```bash
python analyze_jobposting.py
```
- 전체 HTML 구조 분석
- JSON 파일로 저장
- 스크린샷 저장

---

## 📈 기대 결과

### ✅ 성공 케이스
```
수집된 공고 수: 3개

[1] 반도체 공정 엔지니어
    회사: ABC 주식회사
    위치: 경기도 화성시

[2] 반도체 설비 엔지니어
    ...
```

### ❌ 실패 케이스
```
수집된 공고 수: 0개

→ 브라우저 화면 확인
→ 콘솔 로그 확인
→ 사이트 접근 가능 여부 확인
```

---

## 🔧 문제 해결

### 공고가 0개인 경우

1. **브라우저 확인**: 검색 결과가 보이는가?
2. **콘솔 확인**: F12 → Console → 각 전략별 개수 확인
3. **대기 시간 증가**: `config.json`에서 `wait_time: 5`로 변경
4. **페이지 소스 확인**: 실제 HTML 구조 점검

### 네트워크 오류

```json
// config.json 수정
{
  "wait_time": 5,        // 3 → 5초
  "request_delay": 3,    // 2 → 3초
  "max_retries": 5       // 3 → 5회
}
```

---

## 🎓 상세 문서

- **JOBPOSTING_TEST_GUIDE.md**: 전체 사용 가이드
- **JOBPOSTING_FIX_SUMMARY.md**: 완료 보고서
- **sites/jobposting/SELECTOR_FIX.md**: 기술 상세 문서

---

## 💡 팁

### 디버깅 모드
```python
# crawler.py 실행 시
crawler = JobPostingCrawler(headless=False)  # 브라우저 표시
```

### 로그 레벨 조정
```python
import logging
logging.basicConfig(level=logging.DEBUG)  # 상세 로그
```

### 수집 개수 조정
```python
jobs = crawler.crawl("반도체", max_jobs=10)  # 3 → 10개
```

---

## ⏭️ 다음 단계

1. ✅ 테스트 실행: `python test_jobposting_fixed.py`
2. ⏳ 결과 확인: 수집된 공고 개수 및 내용
3. ⏳ 피드백: 성공/실패 여부 보고
4. ⏳ 최적화: 필요시 추가 조정

---

**마지막 업데이트**: 2025-12-06
**상태**: ✅ 수정 완료, 테스트 준비됨
