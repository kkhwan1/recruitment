# Backend Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│                    http://localhost:3000                     │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/REST
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend Server                     │
│                    http://localhost:8000                     │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Layer (app/api/)                     │  │
│  │                                                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │  jobs.py │  │stats.py  │  │reports.py│           │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  │  ┌──────────┐  ┌──────────┐                          │  │
│  │  │crawlers  │  │ news.py  │                          │  │
│  │  │  .py     │  └──────────┘                          │  │
│  │  └──────────┘                                         │  │
│  └────────────┬───────────────────────────────────────────┘  │
│               │                                               │
│  ┌────────────▼───────────────────────────────────────────┐  │
│  │         Repository Layer (database/)                   │  │
│  │                                                         │  │
│  │  ┌──────────────┐  ┌──────────────┐                   │  │
│  │  │    Job       │  │   Analysis   │                   │  │
│  │  │  Repository  │  │  Repository  │                   │  │
│  │  └──────────────┘  └──────────────┘                   │  │
│  │  ┌──────────────┐                                     │  │
│  │  │   Report     │                                     │  │
│  │  │  Repository  │                                     │  │
│  │  └──────────────┘                                     │  │
│  └────────────┬────────────────────────────────────────────┘  │
│               │                                               │
│  ┌────────────▼────────────────────────────────────────────┐  │
│  │         Database Connection (SQLite)                    │  │
│  │              data/recruitment.db                        │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## API Routing Structure

```
/api
├── /jobs
│   ├── GET /jobs                    # 공고 목록 (페이지네이션, 필터링)
│   └── GET /jobs/{id}               # 공고 상세 (키워드, 패턴 포함)
│
├── /crawlers
│   └── POST /crawlers/crawl         # 크롤러 실행 (백그라운드)
│
├── /stats
│   └── GET /stats/dashboard         # 대시보드 통합 통계
│
├── /reports
│   ├── GET /reports/daily           # 리포트 목록
│   └── GET /reports/daily/{date}    # 특정 날짜 리포트
│
└── /news
    └── GET /news                     # 뉴스 목록 (MVP: 샘플 데이터)
```

## Request Flow

### Example: Dashboard Loading

```
┌──────────┐
│ Frontend │
└────┬─────┘
     │
     │ GET /api/stats/dashboard
     │
     ▼
┌──────────────┐
│  stats.py    │
│ (API Layer)  │
└──────┬───────┘
       │
       │ Query database
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Database Queries (Optimized with JOINs)                  │
│                                                           │
│ 1. SELECT COUNT(*) FROM jobs                             │
│ 2. SELECT COUNT(*) FROM jobs WHERE crawled_date = ?      │
│ 3. SELECT risk_level, COUNT(*) ... GROUP BY ...          │
│ 4. SELECT tier, keyword, COUNT(*) ... GROUP BY ...       │
│ 5. SELECT j.*, r.* FROM jobs j JOIN risk_analysis r ...  │
│                                                           │
└──────────────────────────┬───────────────────────────────┘
                           │
                           │ Return aggregated data
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│ Response JSON                                             │
│ {                                                         │
│   "total_jobs": 1250,                                     │
│   "total_today": 45,                                      │
│   "high_risk": 12,                                        │
│   "medium_risk": 23,                                      │
│   "low_risk": 10,                                         │
│   "top_keywords": [...],                                  │
│   "recent_high_risk": [...]                               │
│ }                                                         │
└──────────────────────────────────────────────────────────┘
```

### Example: Jobs List with N+1 Query Optimization

#### Before (N+1 Problem)
```
Frontend Request
     │
     ▼
GET /api/jobs?limit=50
     │
     ▼
┌─────────────────────────────────────────┐
│ Query 1: SELECT * FROM jobs LIMIT 50    │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ For each job (50 iterations):           │
│   Query N: SELECT * FROM risk_analysis  │
│            WHERE job_id = ?             │
└─────────────────────────────────────────┘

Total: 51 queries ❌
```

#### After (JOIN Optimization)
```
Frontend Request
     │
     ▼
GET /api/jobs?limit=50
     │
     ▼
┌──────────────────────────────────────────┐
│ Query 1:                                 │
│ SELECT j.*, r.*                          │
│ FROM jobs j                              │
│ LEFT JOIN risk_analysis r                │
│   ON j.id = r.job_id                     │
│ LIMIT 50                                 │
└──────────────────────────────────────────┘

Total: 1 query ✅
Performance: 98% faster
```

## Database Schema Relationships

```
┌──────────────────┐
│      jobs        │
│──────────────────│
│ id (PK)          │◄────┐
│ title            │     │
│ company          │     │
│ location         │     │
│ salary           │     │
│ conditions       │     │
│ recruit_summary  │     │
│ detail           │     │
│ url              │     │
│ posted_date      │     │
│ source_site      │     │
│ search_keyword   │     │
│ crawled_at       │     │
│ crawled_date     │     │
│ crawled_weekday  │     │
│ crawled_hour     │     │
└──────────────────┘     │
                         │
        ┌────────────────┼────────────────┬────────────────┐
        │                │                │                │
        │                │                │                │
        ▼                ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ keyword_     │  │ pattern_     │  │ risk_        │  │ daily_       │
│ matches      │  │ matches      │  │ analysis     │  │ reports      │
│──────────────│  │──────────────│  │──────────────│  │──────────────│
│ id (PK)      │  │ id (PK)      │  │ id (PK)      │  │ id (PK)      │
│ job_id (FK)  │  │ job_id (FK)  │  │ job_id (FK)  │  │ report_date  │
│ tier         │  │ pattern_id   │  │ base_score   │  │ detection_   │
│ keyword      │  │ pattern_name │  │ combo_mult.  │  │   target     │
│ category     │  │ keywords     │  │ final_score  │  │ total_jobs   │
│ weight       │  │ weight       │  │ risk_level   │  │ high_risk_   │
│ match_count  │  │ description  │  │ risk_factors │  │   count      │
└──────────────┘  └──────────────┘  │ recommend.   │  │ medium_risk_ │
                                    │ analysis_    │  │   count      │
                                    │   summary    │  │ low_risk_    │
                                    └──────────────┘  │   count      │
                                                      │ main_        │
                                                      │   keywords   │
                                                      │ recommended_ │
                                                      │   action     │
                                                      │ high_risk_   │
                                                      │   jobs       │
                                                      └──────────────┘
```

## Repository Pattern

```
┌──────────────────────────────────────────────────────┐
│                   API Layer                          │
│  - Handles HTTP requests/responses                   │
│  - Validates input via Pydantic schemas              │
│  - Orchestrates business logic                       │
└─────────────────┬────────────────────────────────────┘
                  │
                  │ Calls repository methods
                  │
                  ▼
┌──────────────────────────────────────────────────────┐
│              Repository Layer                        │
│  - Abstracts database operations                     │
│  - Provides clean interface for data access          │
│  - Handles SQL queries and data transformation       │
│                                                       │
│  JobRepository:                                       │
│    - insert_job(job_data)                            │
│    - get_job_by_id(job_id)                           │
│    - get_jobs_by_weekday(weekday)                    │
│    - get_jobs_by_date_range(start, end)              │
│                                                       │
│  AnalysisRepository:                                  │
│    - save_analysis(job_id, detection, risk)          │
│    - get_high_risk_jobs(limit)                       │
│    - get_risk_statistics()                           │
│    - get_keyword_statistics(tier)                    │
│                                                       │
│  ReportRepository:                                    │
│    - save_daily_report(report_data)                  │
│    - get_daily_report(date)                          │
│    - get_recent_reports(limit)                       │
└─────────────────┬────────────────────────────────────┘
                  │
                  │ Executes SQL queries
                  │
                  ▼
┌──────────────────────────────────────────────────────┐
│               Database Layer                         │
│  - SQLite database connection                        │
│  - Transaction management                            │
│  - Connection pooling                                │
└──────────────────────────────────────────────────────┘
```

## Error Handling Strategy

```
┌──────────────┐
│ API Request  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────┐
│ Pydantic Schema Validation       │
│ - Type checking                  │
│ - Required fields validation     │
│ - Format validation              │
└──────┬───────────────────────────┘
       │
       │ ✅ Valid
       │
       ▼
┌──────────────────────────────────┐
│ Business Logic                   │
│ - Authorization checks           │
│ - Data existence validation      │
│ - Business rule enforcement      │
└──────┬───────────────────────────┘
       │
       │ ✅ Valid
       │
       ▼
┌──────────────────────────────────┐
│ Database Operation               │
│ - Execute query                  │
│ - Handle DB errors               │
│ - Transaction management         │
└──────┬───────────────────────────┘
       │
       │ ✅ Success
       │
       ▼
┌──────────────────────────────────┐
│ Response Formatting              │
│ - Serialize data                 │
│ - Apply response schema          │
│ - Return JSON                    │
└──────────────────────────────────┘

Error Handling at Each Layer:

1. Schema Validation Error → 422 Unprocessable Entity
2. Not Found → 404 Not Found
3. Business Logic Error → 400 Bad Request
4. Database Error → 500 Internal Server Error
5. Unauthorized → 401 Unauthorized (TODO)
```

## Performance Optimizations

### 1. Query Optimization
```
Technique: JOIN instead of N+1 queries
Impact: 98% reduction in database queries
Example:
  - Before: 51 queries for 50 jobs
  - After: 1 query for 50 jobs
```

### 2. Single Page API
```
Technique: Aggregate related data in one endpoint
Impact: 75% reduction in HTTP requests
Example:
  - Before: 4 API calls for dashboard
  - After: 1 API call for dashboard
```

### 3. Lazy Loading
```
Technique: Load detailed data only when needed
Impact: Reduced initial payload size
Example:
  - Jobs list: Basic info only
  - Job detail: Full info + keywords + patterns
```

### 4. Background Tasks
```
Technique: Async processing for long operations
Impact: Instant API response
Example:
  - Crawler execution runs in background
  - User gets immediate confirmation
```

## Scalability Considerations

### Horizontal Scaling
```
┌──────────┐
│ Frontend │
└────┬─────┘
     │
     ▼
┌─────────────┐
│Load Balancer│
└──────┬──────┘
       │
       ├──────────┬──────────┬──────────┐
       │          │          │          │
       ▼          ▼          ▼          ▼
┌──────────┐┌──────────┐┌──────────┐┌──────────┐
│ FastAPI  ││ FastAPI  ││ FastAPI  ││ FastAPI  │
│ Server 1 ││ Server 2 ││ Server 3 ││ Server 4 │
└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘
     │           │           │           │
     └───────────┴───────────┴───────────┘
                     │
                     ▼
           ┌─────────────────┐
           │ Database Server │
           │   (PostgreSQL)  │
           └─────────────────┘
```

### Caching Strategy (TODO)
```
┌──────────┐
│ Frontend │
└────┬─────┘
     │
     ▼
┌──────────┐
│  Redis   │  ◄── Cache Layer
│  Cache   │      - Dashboard stats (TTL: 5 min)
└────┬─────┘      - News list (TTL: 30 min)
     │            - Top keywords (TTL: 10 min)
     │ Cache Miss
     ▼
┌──────────┐
│ FastAPI  │
│  Server  │
└────┬─────┘
     │
     ▼
┌──────────┐
│ Database │
└──────────┘
```

## Security Architecture (TODO)

```
┌──────────┐
│ Frontend │
└────┬─────┘
     │
     │ Include: Authorization: Bearer <JWT>
     │
     ▼
┌─────────────────────┐
│ API Gateway         │
│ - Rate limiting     │
│ - JWT validation    │
│ - Request logging   │
└────┬────────────────┘
     │
     │ Validated request
     │
     ▼
┌─────────────────────┐
│ FastAPI Backend     │
│ - Role-based access │
│ - Input validation  │
│ - SQL injection     │
│   prevention        │
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ Database            │
│ - Encrypted at rest │
│ - Connection pooling│
└─────────────────────┘
```

## Monitoring & Logging (TODO)

```
┌──────────────────────────────────────────┐
│          Application Metrics             │
│  - Request rate                          │
│  - Response time                         │
│  - Error rate                            │
│  - Active connections                    │
└────┬─────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│          Prometheus                      │
│  - Metric collection                     │
│  - Time-series database                  │
└────┬─────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│          Grafana                         │
│  - Dashboard visualization               │
│  - Alerting rules                        │
│  - Real-time monitoring                  │
└──────────────────────────────────────────┘
```
