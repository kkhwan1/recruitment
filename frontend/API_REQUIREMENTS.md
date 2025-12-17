# Backend API Requirements

프론트엔드에서 필요한 백엔드 API 엔드포인트 명세.

## Required Endpoints

### 1. Dashboard Statistics
```http
GET /api/stats/dashboard
```

**Response**:
```json
{
  "total": 150,
  "high": 25,
  "medium": 50,
  "low": 75
}
```

### 2. Trend Data
```http
GET /api/stats/trend?days=7
```

**Response**:
```json
[
  {
    "date": "2024-12-17",
    "total": 20,
    "high": 5,
    "medium": 8,
    "low": 7
  },
  ...
]
```

### 3. All Jobs
```http
GET /api/jobs
```

**Response**:
```json
[
  {
    "id": 1,
    "title": "반도체 공정 엔지니어",
    "company": "글로벌 R&D",
    "location": "중국 상하이",
    "salary": "협의",
    "url": "https://...",
    "posted_date": "2024-12-17",
    "source_site": "JobKorea",
    "crawled_at": "2024-12-17T10:30:00",
    "keyword_matches": [...],
    "pattern_matches": [...],
    "risk_analysis": {
      "id": 1,
      "job_id": 1,
      "base_score": 45.0,
      "combo_multiplier": 1.5,
      "final_score": 67.5,
      "risk_level": "중위험",
      "risk_factors": "...",
      "recommendations": "...",
      "analysis_summary": "..."
    }
  },
  ...
]
```

### 4. High Risk Jobs
```http
GET /api/jobs/high-risk?limit=5
```

**Response**: Same structure as /api/jobs but filtered and limited.

### 5. News
```http
GET /api/news
```

**Response**:
```json
[
  {
    "id": 1,
    "title": "반도체 기술 유출 적발",
    "description": "삼성전자 출신 연구원이...",
    "url": "https://news.example.com/...",
    "published_at": "2024-12-17T09:00:00",
    "source": "연합뉴스",
    "category": "기술유출"
  },
  ...
]
```

### 6. Reports
```http
GET /api/reports
```

**Response**:
```json
[
  {
    "id": 1,
    "date": "2024-12-17",
    "total_jobs": 50,
    "high_risk": 10,
    "medium_risk": 20,
    "low_risk": 20,
    "summary": "오늘 수집된 50개의 채용 공고 중...",
    "top_keywords": ["반도체", "중국어", "해외협업"],
    "recommendations": [
      "고위험 공고 10건에 대한 상세 검토가 필요합니다.",
      "중국어 필수 조건이 있는 공고가 증가 추세입니다."
    ]
  },
  ...
]
```

## Implementation Notes

### CORS Configuration
프론트엔드(http://localhost:3000)에서 백엔드(http://127.0.0.1:8000) 호출을 위해 CORS 설정 필요.

```python
# FastAPI example
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Error Responses
모든 엔드포인트는 에러 시 다음 형식 반환:

```json
{
  "detail": "Error message"
}
```

### Date Format
모든 날짜는 ISO 8601 형식 사용: `2024-12-17T10:30:00`

### Pagination (Optional)
향후 데이터가 많아질 경우 페이지네이션 고려:

```http
GET /api/jobs?page=1&limit=20
```

**Response**:
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "pages": 8
}
```
