# FastAPI Backend - API Documentation

## Base URL
```
http://localhost:8000
```

## API Endpoints

### 1. Jobs (공고)

#### GET /api/jobs
공고 목록 조회 (페이지네이션, 위험도 필터링 지원)

**Query Parameters:**
- `limit` (int, default: 50): 조회할 공고 개수
- `skip` (int, default: 0): 건너뛸 공고 개수
- `risk_level` (string, optional): 위험도 필터 (고위험, 중위험, 저위험)

**Response:**
```json
[
  {
    "id": 1,
    "title": "반도체 공정 엔지니어",
    "company": "글로벌 R&D",
    "location": "중국 상하이",
    "salary": "연봉 1억원 이상",
    "conditions": "경력 5년 이상",
    "recruit_summary": "반도체 공정 개발",
    "detail": "...",
    "url": "https://...",
    "posted_date": "2024-01-15",
    "source_site": "잡코리아",
    "search_keyword": "반도체",
    "crawled_at": "2024-01-15T10:30:00",
    "crawled_date": "2024-01-15",
    "crawled_weekday": 0,
    "crawled_hour": 10,
    "risk_analysis": {
      "base_score": 80.0,
      "combo_multiplier": 1.5,
      "final_score": 120.0,
      "risk_level": "고위험",
      "risk_factors": ["기술키워드+해외", "중국어필수"],
      "recommendations": ["즉시 검토 필요"],
      "analysis_summary": "기술 유출 의심 패턴 탐지"
    }
  }
]
```

**Optimizations:**
- JOIN으로 N+1 쿼리 해결
- 한 번의 쿼리로 공고 + 위험도 분석 조회

---

#### GET /api/jobs/{job_id}
공고 상세 조회 (키워드 매칭, 패턴 매칭 포함)

**Path Parameters:**
- `job_id` (int): 공고 ID

**Response:**
```json
{
  "job": {
    "id": 1,
    "title": "반도체 공정 엔지니어",
    "company": "글로벌 R&D",
    "location": "중국 상하이",
    "salary": "연봉 1억원 이상",
    "conditions": "경력 5년 이상",
    "recruit_summary": "반도체 공정 개발",
    "detail": "...",
    "url": "https://...",
    "posted_date": "2024-01-15",
    "source_site": "잡코리아",
    "search_keyword": "반도체",
    "crawled_at": "2024-01-15T10:30:00",
    "crawled_date": "2024-01-15",
    "crawled_weekday": 0,
    "crawled_hour": 10
  },
  "risk_analysis": {
    "base_score": 80.0,
    "combo_multiplier": 1.5,
    "final_score": 120.0,
    "risk_level": "고위험",
    "risk_factors": ["기술키워드+해외", "중국어필수"],
    "recommendations": ["즉시 검토 필요"],
    "analysis_summary": "기술 유출 의심 패턴 탐지"
  },
  "keyword_matches": [
    {
      "tier": 1,
      "keyword": "반도체",
      "category": "핵심기술",
      "weight": 10,
      "match_count": 3
    }
  ],
  "pattern_matches": [
    {
      "pattern_name": "기술유출_중국_급구",
      "keywords": ["반도체", "중국어", "급구"],
      "weight": 35,
      "description": "반도체 기술 해외 유출 의심"
    }
  ]
}
```

---

### 2. Crawlers (크롤러)

#### POST /api/crawlers/crawl
크롤러 실행 (백그라운드)

**Request Body:**
```json
{
  "site": "jobkorea",      // 크롤링할 사이트 (jobkorea, incruit, saramin, hibrain, all)
  "keyword": "반도체",      // 검색 키워드 (optional)
  "max_jobs": 10           // 최대 수집 개수 (default: 10)
}
```

**Response:**
```json
{
  "message": "Crawler for jobkorea started in background",
  "status": "processing"
}
```

**Routing Fix:**
- `/api/crawl` → `/api/crawlers/crawl`로 통일
- 페이지당 1개 API 원칙 준수

---

### 3. Stats (통계)

#### GET /api/stats/overview
종합 통계 조회

**Response:**
```json
{
  "total_jobs": 1234,
  "high_risk_count": 45,
  "medium_risk_count": 123,
  "low_risk_count": 1066,
  "top_sources": [
    {"site": "jobkorea", "count": 567},
    {"site": "saramin", "count": 432}
  ],
  "avg_risk_score": 42.5
}
```

---

#### GET /api/stats/trends
일별 트렌드 조회

**Query Parameters:**
- `days` (int, default: 7): 조회할 일수 (최대 30)

**Response:**
```json
[
  {
    "date": "2024-01-15",
    "total_jobs": 150,
    "high_risk_count": 12,
    "medium_risk_count": 38,
    "low_risk_count": 100
  }
]
```

---

#### GET /api/stats/keywords
상위 키워드 조회

**Query Parameters:**
- `limit` (int, default: 10): 조회할 키워드 개수 (최대 50)

**Response:**
```json
[
  {
    "keyword": "반도체",
    "tier": 1,
    "category": "핵심기술",
    "count": 234,
    "avg_weight": 9.5
  }
]
```

---

#### GET /api/stats/dashboard
대시보드 통합 통계 조회

**Response:**
```json
{
  "total_jobs": 1250,           // 전체 공고 수
  "total_today": 45,            // 오늘 수집된 공고 수
  "high_risk": 12,              // 고위험 공고 수
  "medium_risk": 23,            // 중위험 공고 수
  "low_risk": 10,               // 저위험 공고 수
  "top_keywords": [             // 상위 키워드 (Tier별 상위 3개)
    {
      "tier": 1,
      "keyword": "반도체",
      "count": 45
    },
    {
      "tier": 1,
      "keyword": "OLED",
      "count": 32
    },
    {
      "tier": 1,
      "keyword": "이차전지",
      "count": 28
    },
    {
      "tier": 2,
      "keyword": "중국어필수",
      "count": 15
    },
    {
      "tier": 2,
      "keyword": "해외협업",
      "count": 12
    },
    {
      "tier": 2,
      "keyword": "기술이전",
      "count": 8
    },
    {
      "tier": 3,
      "keyword": "급구",
      "count": 10
    },
    {
      "tier": 3,
      "keyword": "비자필요없음",
      "count": 5
    },
    {
      "tier": 3,
      "keyword": "현금지급",
      "count": 3
    }
  ],
  "recent_high_risk": [         // 최근 고위험 공고 5건
    {
      "id": 123,
      "title": "반도체 공정 엔지니어",
      "company": "글로벌 R&D",
      "location": "중국 상하이",
      "url": "https://...",
      "crawled_at": "2024-01-15T10:30:00",
      "final_score": 135.0,
      "risk_level": "고위험"
    }
  ]
}
```

**Optimizations:**
- 단일 페이지에 필요한 모든 통계 한번에 제공
- JOIN으로 최적화된 쿼리

---

### 4. Reports (리포트)

#### GET /api/reports/daily
일일 리포트 목록 조회

**Query Parameters:**
- `limit` (int, default: 30): 조회할 리포트 개수
- `skip` (int, default: 0): 건너뛸 리포트 개수

**Response:**
```json
[
  {
    "id": 1,
    "report_date": "2024-01-15",
    "detection_target": "반도체, OLED, 이차전지",
    "total_jobs": 45,
    "high_risk_count": 12,
    "medium_risk_count": 23,
    "low_risk_count": 10,
    "main_keywords": ["반도체", "중국어", "급구"],
    "recommended_action": "주의: 고위험 공고가 탐지되었습니다. 검토를 권장합니다."
  }
]
```

**Notes:**
- `high_risk_jobs` 필드는 크기가 크므로 목록 조회에서는 제외
- 페이지네이션 지원 (limit, skip)

---

#### GET /api/reports/daily/{report_date}
특정 날짜의 일일 리포트 상세 조회

**Path Parameters:**
- `report_date` (string): 리포트 날짜 (YYYY-MM-DD)

**Response:**
```json
{
  "id": 1,
  "report_date": "2024-01-15",
  "detection_target": "반도체, OLED, 이차전지",
  "total_jobs": 45,
  "high_risk_count": 12,
  "medium_risk_count": 23,
  "low_risk_count": 10,
  "main_keywords": ["반도체", "중국어", "급구"],
  "recommended_action": "주의: 고위험 공고가 탐지되었습니다. 검토를 권장합니다.",
  "high_risk_jobs": [
    {
      "id": 123,
      "title": "반도체 공정 엔지니어",
      "company": "글로벌 R&D",
      "location": "중국 상하이",
      "url": "https://...",
      "final_score": 135.0,
      "risk_level": "고위험",
      "risk_factors": ["기술키워드+해외", "중국어필수"]
    }
  ]
}
```

**Features:**
- 고위험 공고 상세 정보 포함
- 리포트가 없을 경우 404 반환

---

#### GET /api/reports/summary
리포트 요약 통계

**Response:**
```json
{
  "total_reports": 45,
  "latest_report_date": "2024-01-15",
  "avg_high_risk_count": 8.5,
  "total_jobs_analyzed": 6750
}
```

---

### 5. News (뉴스)

#### GET /api/news
기술 유출 관련 뉴스 조회

**Query Parameters:**
- `limit` (int, default: 10): 조회할 뉴스 개수

**Response:**
```json
[
  {
    "id": 1,
    "title": "중국 기업, 한국 반도체 기술자 스카우트 시도 적발",
    "summary": "중국 소재 반도체 기업이 한국 대기업 출신 엔지니어를 대상으로 고액 연봉을 제시하며 기술 유출을 시도한 정황이 포착됐다.",
    "url": "#",
    "source": "전자신문",
    "published_at": "2024-01-15T08:30:00",
    "category": "반도체",
    "thumbnail": null
  }
]
```

**Notes:**
- MVP: 하드코딩된 샘플 데이터 (10개)
- TODO: 실제 뉴스 API 연동 (네이버 뉴스 API, Google News API 등)

---

## Architecture Improvements

### 1. Routing Consistency
- **Before**: `/api/crawl` (불일치)
- **After**: `/api/crawlers/crawl` (일관성)
- **Principle**: 페이지당 1개 API, 명확한 리소스 그룹화

### 2. N+1 Query Optimization
- **Before**: 공고 목록 조회 후 각 공고마다 위험도 분석 쿼리 (N+1)
- **After**: JOIN으로 한 번에 조회
- **Performance**: 50개 공고 조회 시 51번 쿼리 → 1번 쿼리

### 3. Single Page API
- **Before**: 대시보드에 필요한 데이터를 여러 API로 나눔
- **After**: `/api/stats/dashboard`에서 한 번에 제공
- **Benefit**: 클라이언트 요청 횟수 감소, 로딩 속도 향상

### 4. On-Demand Report Generation
- **Before**: 미리 생성된 리포트만 조회 가능
- **After**: 요청 시 즉시 집계하여 생성
- **Benefit**: 유연한 리포트 조회, 저장소 관리 간소화

---

## Running the Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## API Documentation (Swagger UI)
```
http://localhost:8000/docs
```

## Testing
```bash
# Health check
curl http://localhost:8000/health

# Get dashboard stats
curl http://localhost:8000/api/stats/dashboard

# Get jobs
curl "http://localhost:8000/api/jobs?limit=10&risk_level=고위험"

# Get job detail
curl http://localhost:8000/api/jobs/1

# Trigger crawler
curl -X POST http://localhost:8000/api/crawlers/crawl \
  -H "Content-Type: application/json" \
  -d '{"site": "jobkorea", "keyword": "반도체", "max_jobs": 10}'

# Get daily reports
curl http://localhost:8000/api/reports/daily

# Get specific date report
curl http://localhost:8000/api/reports/daily/2024-01-15

# Get news
curl http://localhost:8000/api/news?limit=5
```
