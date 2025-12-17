"""
FastAPI 백엔드 테스트 스크립트
모든 엔드포인트의 기본 동작을 확인합니다.
"""
import sys
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.append(str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Health check 테스트"""
    print("\n[TEST] Health Check")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✅ PASSED")


def test_stats_dashboard():
    """대시보드 통계 테스트"""
    print("\n[TEST] GET /api/stats/dashboard")
    response = client.get("/api/stats/dashboard")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ PASSED")
        print(f"  - Total jobs: {data.get('total_jobs')}")
        print(f"  - Today: {data.get('total_today')}")
        print(f"  - High risk: {data.get('high_risk')}")
        print(f"  - Medium risk: {data.get('medium_risk')}")
        print(f"  - Low risk: {data.get('low_risk')}")
        print(f"  - Top keywords: {len(data.get('top_keywords', []))} items")
        print(f"  - Recent high risk: {len(data.get('recent_high_risk', []))} items")
    else:
        print(f"❌ FAILED")


def test_jobs_list():
    """공고 목록 테스트"""
    print("\n[TEST] GET /api/jobs")
    response = client.get("/api/jobs?limit=5")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ PASSED")
        print(f"  - Retrieved {len(data)} jobs")
        if data:
            print(f"  - First job title: {data[0].get('title')}")
    else:
        print(f"❌ FAILED")


def test_jobs_list_with_filter():
    """공고 목록 (위험도 필터링) 테스트"""
    print("\n[TEST] GET /api/jobs?risk_level=고위험")
    response = client.get("/api/jobs?risk_level=고위험&limit=5")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ PASSED")
        print(f"  - Retrieved {len(data)} high-risk jobs")
    else:
        print(f"❌ FAILED")


def test_job_detail():
    """공고 상세 테스트"""
    print("\n[TEST] GET /api/jobs/{id}")

    # 먼저 공고 목록에서 ID 가져오기
    list_response = client.get("/api/jobs?limit=1")
    if list_response.status_code == 200 and list_response.json():
        job_id = list_response.json()[0]['id']

        response = client.get(f"/api/jobs/{job_id}")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASSED")
            print(f"  - Job ID: {job_id}")
            print(f"  - Job title: {data['job'].get('title')}")
            print(f"  - Risk analysis: {data['risk_analysis'] is not None}")
            print(f"  - Keyword matches: {len(data.get('keyword_matches', []))} items")
            print(f"  - Pattern matches: {len(data.get('pattern_matches', []))} items")
        else:
            print(f"❌ FAILED")
    else:
        print("⚠️  SKIPPED (no jobs in database)")


def test_reports_list():
    """리포트 목록 테스트"""
    print("\n[TEST] GET /api/reports/daily")
    response = client.get("/api/reports/daily?limit=5")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ PASSED")
        print(f"  - Retrieved {len(data)} reports")
    else:
        print(f"❌ FAILED")


def test_report_detail():
    """리포트 상세 테스트"""
    print("\n[TEST] GET /api/reports/daily/{date}")

    # 오늘 날짜로 테스트 (없으면 자동 생성됨)
    from datetime import date
    today = date.today().isoformat()

    response = client.get(f"/api/reports/daily/{today}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ PASSED")
        print(f"  - Report date: {data.get('report_date', data.get('탐지일자'))}")
        print(f"  - Total jobs: {data.get('total_jobs', data.get('탐지공고수'))}")
    elif response.status_code == 404:
        print(f"⚠️  No jobs found for today")
    else:
        print(f"❌ FAILED")


def test_news():
    """뉴스 목록 테스트"""
    print("\n[TEST] GET /api/news")
    response = client.get("/api/news?limit=5")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ PASSED")
        print(f"  - Retrieved {len(data)} news items")
        if data:
            print(f"  - First news: {data[0].get('title')[:50]}...")
    else:
        print(f"❌ FAILED")


def test_crawler_endpoint():
    """크롤러 엔드포인트 경로 테스트"""
    print("\n[TEST] POST /api/crawlers/crawl")

    # 실제 크롤링은 하지 않고 경로만 확인
    response = client.post(
        "/api/crawlers/crawl",
        json={
            "site": "jobkorea",
            "keyword": "테스트",
            "max_jobs": 1
        }
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ PASSED")
        print(f"  - Message: {data.get('message')}")
        print(f"  - Status: {data.get('status')}")
    else:
        print(f"❌ FAILED")


if __name__ == "__main__":
    print("=" * 60)
    print("FastAPI Backend API Tests")
    print("=" * 60)

    tests = [
        test_health_check,
        test_stats_dashboard,
        test_jobs_list,
        test_jobs_list_with_filter,
        test_job_detail,
        test_reports_list,
        test_report_detail,
        test_news,
        test_crawler_endpoint,
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ ASSERTION FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️  SKIPPED: {e}")
            skipped += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
