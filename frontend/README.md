# 채용 공고 분석 시스템 Frontend

Next.js 15 + TypeScript + Tailwind CSS로 구성된 채용 공고 분석 시스템 대시보드

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui 준비
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Getting Started

### 1. 의존성 설치

```bash
npm install
```

### 2. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000) 접속

### 3. 빌드

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # 루트 레이아웃 (사이드바 포함)
│   │   ├── page.tsx           # 메인 페이지 (대시보드)
│   │   └── globals.css        # 글로벌 스타일 (다크 테마)
│   ├── components/
│   │   └── layout/
│   │       └── Sidebar.tsx    # 네비게이션 사이드바
│   ├── lib/
│   │   ├── api.ts             # Axios API 클라이언트
│   │   └── utils.ts           # cn() 유틸리티
│   └── types/
│       └── index.ts           # TypeScript 타입 정의
├── public/                     # 정적 파일
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
└── postcss.config.mjs
```

## API Integration

백엔드 API는 `http://127.0.0.1:8000/api`를 기본 URL로 사용합니다.

```typescript
// src/lib/api.ts
import api from "@/lib/api";

const response = await api.get("/jobs");
```

## Navigation

- **대시보드** (`/`): 통계 요약 및 주요 지표
- **고위험 공고** (`/high-risk`): 고위험 등급 공고 목록
- **공고 검색** (`/search`): 키워드/필터 기반 검색
- **통계 및 분석** (`/analytics`): 데이터 분석 및 차트
- **리포트** (`/reports`): 일일/주간 리포트
- **설정** (`/settings`): 시스템 설정

## Dark Theme

기본적으로 다크 테마가 활성화되어 있습니다.

CSS 변수 기반 테마 시스템을 사용하며, `globals.css`에서 색상을 커스터마이징할 수 있습니다.

## Development Notes

- **Turbopack**: 빠른 개발 서버 (Next.js 15 기본)
- **Type Safety**: 모든 컴포넌트는 TypeScript로 작성
- **Responsive**: 모바일 반응형 지원 (Tailwind 사용)
- **Accessibility**: 시맨틱 HTML 및 ARIA 레이블 준수
