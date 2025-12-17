# Quick Start Guide

## 개발 서버 실행

### 1. 의존성 설치
```bash
cd c:\Users\USER\claude_code\채용시스템\frontend
npm install
```

### 2. 개발 서버 시작
```bash
npm run dev
```

브라우저에서 http://localhost:3000 접속

## 페이지 구성

### 1. 대시보드 (/)
- URL: http://localhost:3000
- 메트릭 카드 4개
- 트렌드 차트
- 위험도 분포 차트
- 최근 고위험 공고 목록

### 2. 채용 정보 (/jobs)
- URL: http://localhost:3000/jobs
- 검색 및 필터 기능
- 채용 공고 테이블
- 페이지네이션

### 3. 관련 뉴스 (/news)
- URL: http://localhost:3000/news
- 카테고리 탭
- 뉴스 카드 그리드

### 4. 분석 리포트 (/reports)
- URL: http://localhost:3000/reports
- 리포트 목록
- 리포트 상세 보기

## 백엔드 연동

### 1. 백엔드 API 서버 실행
```bash
cd c:\Users\USER\claude_code\채용시스템\backend
uvicorn app.main:app --reload
```

### 2. API 엔드포인트 확인
- API 문서: http://127.0.0.1:8000/docs
- 필요한 엔드포인트: API_REQUIREMENTS.md 참조

### 3. CORS 설정 확인
backend/app/main.py에서 CORS 설정 필요:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 트러블슈팅

### API 연결 실패
1. 백엔드 서버가 실행 중인지 확인
2. CORS 설정 확인
3. 브라우저 콘솔에서 에러 확인

### 컴포넌트 에러
1. 의존성 재설치: `npm install`
2. 캐시 삭제: `rm -rf .next`
3. 서버 재시작: `npm run dev`

### 타입 에러
1. types/index.ts 확인
2. API 응답 형식과 타입 정의 일치 확인

## 개발 팁

### Hot Reload
파일 저장 시 자동으로 브라우저에 반영됩니다.

### API 테스트
브라우저 개발자 도구(F12) > Network 탭에서 API 호출 확인 가능.

### 스타일 수정
Tailwind CSS 사용으로 className에서 직접 스타일 수정 가능.

### 다크 모드
기본적으로 다크 모드가 활성화되어 있습니다.
app/layout.tsx의 `<html lang="ko" className="dark">`에서 조정 가능.

## 다음 단계

1. 백엔드 API 구현
2. 실제 데이터로 테스트
3. 에러 처리 개선
4. 로딩 상태 UI 추가
5. 반응형 디자인 개선
