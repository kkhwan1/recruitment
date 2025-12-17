# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

**채용 공고 분석 시스템** - 기술 유출 의심 공고 탐지 및 위험도 분석 자동화 시스템

- 10개 채용 사이트 크롤링 (JobKorea, Incruit, Saramin, Hibrain, Alba 등)
- 3단계 키워드 탐지 (기술/의심/위험) + 복합 패턴 매칭
- 위험도 점수 계산 및 등급 분류 (고/중/저위험)

## 개발 환경

```bash
# 백엔드 (FastAPI + SQLite)
cd backend
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload --port 8000

# 프론트엔드 (Next.js 15 + TypeScript + Tailwind)
cd frontend
npm install
npm run dev
```

## 프로젝트 구조

```
채용시스템/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 앱 (CORS, 라우터 등록)
│   │   ├── schemas.py           # Pydantic 스키마
│   │   └── api/
│   │       ├── jobs.py          # GET /api/jobs, /api/jobs/{id}
│   │       ├── stats.py         # GET /api/stats/overview, trends, keywords
│   │       ├── reports.py       # GET /api/reports/daily
│   │       ├── news.py          # GET /api/news
│   │       └── crawlers.py      # POST /api/crawl
│   ├── sites/                   # 10개 사이트별 크롤러
│   ├── analyzers/
│   │   ├── keyword_detector.py  # 3단계 키워드 탐지
│   │   └── risk_scorer.py       # 위험도 점수 계산
│   ├── database/
│   │   ├── connection.py        # SQLite 연결 (Singleton)
│   │   ├── models.py            # dataclass 모델
│   │   └── repositories.py      # Repository 패턴
│   ├── config/
│   │   ├── detection_keywords.csv
│   │   └── complex_patterns.csv
│   └── data/recruitment.db      # SQLite DB
│
└── frontend/
    ├── src/app/
    │   ├── page.tsx             # 대시보드
    │   ├── jobs/page.tsx        # 채용정보 목록
    │   ├── news/page.tsx        # 관련 뉴스
    │   └── reports/page.tsx     # 분석 리포트
    ├── src/components/
    │   ├── dashboard/           # 메트릭카드, 차트
    │   ├── jobs/                # 테이블
    │   └── ui/                  # Card, Badge
    └── src/lib/api.ts           # axios 클라이언트
```

## 핵심 아키텍처

### 3단계 키워드 탐지

| Tier | 분류 | 예시 | 가중치 |
|------|------|------|--------|
| 1차 | 기술 | 반도체, OLED, 이차전지 | 8-10점 |
| 2차 | 의심 | 해외협업, 중국어필수 | 12-25점 |
| 3차 | 위험 | 급구, 비자필요없음 | 20-25점 |

### 위험도 계산

```
final_score = base_score × combo_multiplier
- 고위험: 100점 이상
- 중위험: 50-99점
- 저위험: 50점 미만
```

### 크롤러 패턴

모든 크롤러는 Playwright 기반 + Bot Detection 회피:

- `--disable-blink-features=AutomationControlled`
- navigator.webdriver 제거
- React SPA: 4단계 계층적 대기 전략

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /api/jobs | 공고 목록 (필터, 페이지네이션) |
| GET | /api/jobs/{id} | 공고 상세 (키워드 매칭 포함) |
| GET | /api/stats/overview | 종합 통계 |
| GET | /api/stats/trends | 일별 트렌드 |
| GET | /api/stats/keywords | 상위 키워드 |
| GET | /api/reports/daily | 일일 리포트 목록 |
| GET | /api/news | 뉴스 목록 |
| POST | /api/crawl | 크롤러 실행 |

## 데이터베이스 테이블

- `jobs`: 채용 공고 (title, company, location, url 등)
- `keyword_matches`: 키워드 매칭 결과 (job_id, tier, keyword, weight)
- `pattern_matches`: 복합 패턴 매칭 (job_id, pattern_name, score)
- `risk_analysis`: 위험도 분석 (job_id, final_score, risk_level)
- `daily_reports`: 일일 리포트

## 주요 명령어

```bash
# 크롤링 실행
python backend/cli.py --site jobkorea --keyword "반도체" --max-jobs 50

# 분석 테스트
python backend/test_analysis_system.py

# API 문서
http://localhost:8000/docs
```

## 확장 가이드

### 새 크롤러 추가
1. `backend/sites/[사이트]/` 디렉토리 생성
2. `config.json` + `crawler.py` 작성
3. `backend/cli.py`에 사이트 등록

### 새 키워드 추가

`backend/config/detection_keywords.csv` 편집:

```
tier,category,keyword,weight,description
1,technology,양자컴퓨터,10,양자 컴퓨팅 기술
```

### 새 API 추가

1. `backend/app/api/[이름].py` 생성
2. `backend/app/main.py`에 라우터 등록
