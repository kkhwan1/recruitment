from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add backend directory to path so we can import from sites, database, etc.
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

app = FastAPI(
    title="채용 시스템 API",
    description="채용 공고 크롤링 및 분석 시스템을 위한 API 서버",
    version="1.0.0"
)

# CORS Middleware (Frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.app.api import jobs, crawlers
app.include_router(jobs.router, prefix="/api", tags=["jobs"])
app.include_router(crawlers.router, prefix="/api", tags=["crawlers"])


@app.get("/")
def read_root():
    return {"message": "채용 시스템 API 서버가 정상 작동 중입니다."}

@app.get("/health")
def health_check():
    return {"status": "ok"}
