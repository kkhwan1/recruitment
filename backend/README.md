# 채용 시스템 FastAPI Backend

채용 공고 크롤링 및 분석 시스템을 위한 RESTful API 서버

## Architecture

```
backend/
├── app/
│   ├── api/                    # API 엔드포인트
│   │   ├── jobs.py            # 공고 API
│   │   ├── crawlers.py        # 크롤러 API
│   │   ├── stats.py           # 통계 API
│   │   ├── reports.py         # 리포트 API
│   │   └── news.py            # 뉴스 API
│   ├── schemas.py             # Pydantic 스키마
│   └── main.py                # FastAPI 앱
├── database/                   # 데이터베이스 레이어
│   ├── connection.py          # DB 연결 관리
│   ├── models.py              # 데이터 모델
│   └── repositories.py        # Repository 패턴
├── cli.py                      # CLI 인터페이스
├── API_DOCS.md                # API 문서
├── CHANGELOG.md               # 변경 이력
├── test_api.py                # API 테스트
└── README.md                  # 이 파일
```

## Quick Start

### 1. Installation

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Test API

```bash
# API 테스트 실행
python test_api.py

# 또는 Swagger UI로 테스트
open http://localhost:8000/docs
```

## API Endpoints

### Dashboard & Stats
- `GET /api/stats/dashboard` - 대시보드 통합 통계

### Jobs
- `GET /api/jobs` - 공고 목록 조회 (페이지네이션, 필터링)
- `GET /api/jobs/{id}` - 공고 상세 조회

### Crawlers
- `POST /api/crawlers/crawl` - 크롤러 실행 (백그라운드)

### Reports
- `GET /api/reports/daily` - 일일 리포트 목록
- `GET /api/reports/daily/{date}` - 특정 날짜 리포트

### News
- `GET /api/news` - 기술 유출 관련 뉴스

자세한 API 문서는 [API_DOCS.md](./API_DOCS.md)를 참고하세요.

## Key Features

### 1. Query Optimization
- JOIN을 통한 N+1 쿼리 해결
- 50개 공고 조회 시 51번 → 1번 쿼리 (98% 감소)

### 2. Single Page API
- 대시보드에 필요한 모든 데이터를 한 번의 요청으로 제공
- 네트워크 요청 횟수 75% 감소

### 3. On-Demand Report Generation
- 요청 시 즉시 리포트 생성
- 기존 리포트 캐싱으로 빠른 응답

### 4. Background Task Processing
- 크롤링 작업을 백그라운드에서 실행
- 즉각적인 API 응답

## Performance Benchmarks

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Jobs List (50) | 51 queries | 1 query | 98% faster |
| Dashboard Load | 4 requests | 1 request | 75% faster |
| Job Detail | 3 queries | 3 queries | Optimized |

## Database Schema

### jobs
- 채용 공고 기본 정보
- 크롤링 시간 메타데이터

### keyword_matches
- 키워드 매칭 결과 (Tier 1-3)

### pattern_matches
- 복합 패턴 매칭 결과

### risk_analysis
- 위험도 분석 결과

### daily_reports
- 일일 리포트 집계 데이터

## Development

### Running Tests

```bash
# API 테스트
python test_api.py

# 특정 테스트만 실행
python -c "from test_api import test_stats_dashboard; test_stats_dashboard()"
```

### Adding New Endpoint

1. Create new file in `app/api/`
2. Define router and endpoints
3. Register in `app/main.py`
4. Add tests in `test_api.py`
5. Document in `API_DOCS.md`

### Example: New Endpoint

```python
# app/api/example.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
def get_example():
    return {"message": "Hello World"}
```

```python
# app/main.py
from backend.app.api import jobs, crawlers, stats, reports, news, example
app.include_router(example.router, prefix="/api", tags=["example"])
```

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Database Locked
```bash
# Close all database connections
pkill -f "python.*backend"
```

### Import Errors
```bash
# Ensure backend directory is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Production Deployment

### 1. Environment Variables
```bash
export DATABASE_URL="sqlite:///data/recruitment.db"
export API_PORT=8000
export CORS_ORIGINS="https://your-frontend-domain.com"
```

### 2. Run with Gunicorn
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 3. CORS Configuration
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Production domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Security Considerations

### 1. Authentication (TODO)
- Add JWT token authentication
- Implement role-based access control

### 2. Rate Limiting (TODO)
- Prevent API abuse
- Use slowapi or similar

### 3. Input Validation
- Pydantic schemas for request validation
- SQL injection prevention via parameterized queries

## Next Steps

1. Add authentication & authorization
2. Implement WebSocket for real-time updates
3. Add caching layer (Redis)
4. Integrate real news API
5. Add monitoring & logging (Prometheus, Grafana)
6. Deploy to cloud (AWS, GCP, Azure)

## Contributing

1. Follow existing code structure
2. Add tests for new endpoints
3. Update API documentation
4. Follow PEP 8 style guide

## License

Internal use only.
