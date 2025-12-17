# Frontend Implementation Summary

## Overview
채용 공고 분석 시스템의 프론트엔드 페이지와 컴포넌트 구현 완료.

## Tech Stack
- Next.js 15 (App Router)
- React 19
- TypeScript
- Tailwind CSS (Dark Mode)
- Recharts (차트 라이브러리)
- Lucide React (아이콘)
- Axios (API 클라이언트)

## Implemented Pages (4개)

### 1. Dashboard (/)
**파일**: `src/app/page.tsx`
**기능**:
- 4개 메트릭 카드 (총 공고, 고위험, 중위험, 저위험)
- 7일 트렌드 라인 차트
- 위험도 분포 파이 차트
- 최근 고위험 공고 목록

**API 호출**:
- GET /api/stats/dashboard
- GET /api/stats/trend?days=7
- GET /api/jobs/high-risk?limit=5

### 2. Jobs (/jobs)
**파일**: `src/app/jobs/page.tsx`
**기능**:
- 검색 필터 (제목, 회사명)
- 위험도 필터
- 사이트 필터
- 채용 공고 테이블
- 페이지네이션 (20개씩)

**API 호출**:
- GET /api/jobs

### 3. News (/news)
**파일**: `src/app/news/page.tsx`
**기능**:
- 카테고리 탭 필터
- 뉴스 카드 그리드 (3열)
- 외부 링크
- 발행일 표시

**API 호출**:
- GET /api/news

### 4. Reports (/reports)
**파일**: `src/app/reports/page.tsx`
**기능**:
- 리포트 목록 (사이드바)
- 리포트 상세 보기
- 수집 통계
- 요약
- 주요 키워드
- 권장사항

**API 호출**:
- GET /api/reports

## Components

### UI Components
- `components/ui/Card.tsx` - 카드 컴포넌트 및 하위 컴포넌트
- `components/ui/Badge.tsx` - 위험도 배지 (고/중/저 색상)

### Dashboard Components
- `components/dashboard/MetricCard.tsx` - 메트릭 카드
- `components/dashboard/TrendChart.tsx` - 트렌드 라인 차트
- `components/dashboard/RiskDistributionChart.tsx` - 위험도 분포 파이 차트
- `components/dashboard/HighRiskJobsList.tsx` - 고위험 공고 목록

### Jobs Components
- `components/jobs/JobTable.tsx` - 채용 공고 테이블

### Layout Components
- `components/layout/Sidebar.tsx` - 사이드바 네비게이션 (업데이트)

## API Integration

### Base Configuration
**파일**: `src/lib/api.ts`
```typescript
baseURL: "http://127.0.0.1:8000/api"
```

### Expected API Endpoints
- GET /api/stats/dashboard - 대시보드 통계
- GET /api/stats/trend?days=7 - 트렌드 데이터
- GET /api/jobs - 전체 공고 목록
- GET /api/jobs/high-risk?limit=5 - 고위험 공고
- GET /api/news - 뉴스 목록
- GET /api/reports - 리포트 목록

## Type Definitions

**파일**: `src/types/index.ts`
- RiskLevel: "고위험" | "중위험" | "저위험"
- Job: 기본 공고 정보
- KeywordMatch: 키워드 매칭 결과
- PatternMatch: 패턴 매칭 결과
- RiskAnalysis: 위험도 분석 결과
- JobDetail: 공고 상세 정보 (extends Job)

## Design System

### Color Scheme (Dark Mode)
- Primary: 파란색
- Red: 고위험 (#ef4444)
- Yellow: 중위험 (#eab308)
- Green: 저위험 (#22c55e)

### Typography
- Heading 1: 3xl, bold
- Heading 2: 2xl, semibold
- Card Title: 2xl, semibold
- Body: sm, regular

### Layout
- Sidebar: 64 (256px) 고정 너비
- Main Content: flex-1, 8 (32px) 패딩
- Card: 6 (24px) 패딩

## Running the Application

### Development
```bash
cd frontend
npm run dev
```

### Build
```bash
npm run build
npm run start
```

### Access
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000

## Next Steps

1. Backend API 엔드포인트 구현 필요:
   - /api/stats/dashboard
   - /api/stats/trend
   - /api/jobs
   - /api/jobs/high-risk
   - /api/news
   - /api/reports

2. 에러 처리 개선
3. 로딩 스켈레톤 추가
4. 반응형 디자인 개선 (모바일)
5. 접근성 향상 (ARIA labels)

## File Structure
```
frontend/
├── src/
│   ├── app/
│   │   ├── jobs/
│   │   │   └── page.tsx
│   │   ├── news/
│   │   │   └── page.tsx
│   │   ├── reports/
│   │   │   └── page.tsx
│   │   ├── layout.tsx
│   │   ├── page.tsx (Dashboard)
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Card.tsx
│   │   │   └── Badge.tsx
│   │   ├── dashboard/
│   │   │   ├── MetricCard.tsx
│   │   │   ├── TrendChart.tsx
│   │   │   ├── RiskDistributionChart.tsx
│   │   │   └── HighRiskJobsList.tsx
│   │   ├── jobs/
│   │   │   └── JobTable.tsx
│   │   └── layout/
│   │       └── Sidebar.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   └── types/
│       └── index.ts
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.ts
```

## Notes
- 모든 페이지는 "use client" 지시문 사용 (클라이언트 컴포넌트)
- API 에러 처리는 콘솔 로그 기본 제공
- Tailwind CSS 다크 모드 기본 활성화
- Recharts 사용으로 인터랙티브 차트 구현
