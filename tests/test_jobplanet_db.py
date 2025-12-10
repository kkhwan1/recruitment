"""
잡플래닛 크롤러 데이터베이스 저장 테스트
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from sites.jobplanet.crawler import JobplanetCrawler
from database.repositories import JobRepository
from database.connection import get_db_connection
from datetime import datetime

def test_crawl_and_save():
    """크롤링 후 데이터베이스 저장 테스트"""
    print("=" * 80)
    print("잡플래닛 크롤러 데이터베이스 저장 테스트")
    print("=" * 80)

    crawler = JobplanetCrawler(headless=False)

    try:
        # 1. 크롤링
        print("\n[1단계] 크롤링 시작...")
        crawler.start()
        keyword = "반도체"
        jobs = crawler.crawl(keyword, max_jobs=3)

        print(f"\n✅ 수집 완료: {len(jobs)}개의 공고")

        if not jobs:
            print("❌ 수집된 공고가 없습니다.")
            return

        # 2. JSON 저장
        print("\n[2단계] JSON 파일 저장...")
        crawler.save_results(keyword, jobs)

        # 3. 데이터베이스 저장
        print("\n[3단계] 데이터베이스 저장...")
        repo = JobRepository()

        saved_count = 0
        error_count = 0

        for i, job in enumerate(jobs, 1):
            try:
                # 시간 정보 추가
                now = datetime.now()
                job['source_site'] = "잡플래닛"
                job['search_keyword'] = keyword
                job['crawled_at'] = now

                # 저장 (insert_job 메서드는 딕셔너리를 받음)
                job_id = repo.insert_job(job)
                print(f"  ✓ [{i}/{len(jobs)}] 저장 성공 (ID: {job_id}): {job.get('title', '')[:50]}")
                saved_count += 1

            except Exception as e:
                print(f"  ✗ [{i}/{len(jobs)}] 저장 실패: {str(e)}")
                error_count += 1
                import traceback
                traceback.print_exc()

        # 4. 결과 요약
        print("\n" + "=" * 80)
        print("최종 결과")
        print("=" * 80)
        print(f"📊 수집된 공고: {len(jobs)}개")
        print(f"✅ 저장 성공: {saved_count}개")
        print(f"❌ 저장 실패: {error_count}개")

        if saved_count > 0:
            print(f"\n✅ 데이터베이스 저장 테스트 성공!")
        else:
            print(f"\n❌ 데이터베이스 저장 실패!")

    finally:
        crawler.close()


if __name__ == "__main__":
    test_crawl_and_save()
