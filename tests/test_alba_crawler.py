"""
알바천국 크롤러 테스트 및 DB 저장
"""
import sys
from pathlib import Path
from datetime import datetime
from sites.alba.crawler import AlbaCrawler

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root))


def test_crawler_with_db():
    """크롤러 테스트 후 DB 저장"""
    try:
        # DB 모델 import
        from models.job import JobPosting
        from models.database import get_db

        print("=" * 60)
        print("알바천국 크롤러 테스트 시작")
        print("=" * 60)

        crawler = AlbaCrawler(headless=False)
        crawler.start()

        keyword = "반도체"
        max_jobs = 3

        print(f"\n키워드: {keyword}")
        print(f"최대 수집 개수: {max_jobs}개")
        print("-" * 60)

        # 크롤링 실행
        jobs = crawler.crawl(keyword, max_jobs=max_jobs)

        if not jobs:
            print("\n경고: 수집된 공고가 없습니다!")
            crawler.close()
            return

        print(f"\n수집 완료: {len(jobs)}개 공고")
        print("=" * 60)

        # 결과 출력
        for i, job in enumerate(jobs, 1):
            print(f"\n[{i}] {job['title']}")
            print(f"    회사: {job.get('company', 'N/A')}")
            print(f"    위치: {job.get('location', 'N/A')}")
            print(f"    급여: {job.get('salary', 'N/A')}")
            print(f"    URL: {job['url']}")

        # JSON 파일로 저장
        crawler.save_results(keyword, jobs)
        print("\nJSON 파일 저장 완료")

        # DB 저장
        print("\n" + "=" * 60)
        print("데이터베이스 저장 시작")
        print("=" * 60)

        db = next(get_db())
        saved_count = 0

        for job in jobs:
            try:
                # JobPosting 모델로 변환
                job_posting = JobPosting(
                    title=job['title'],
                    company=job.get('company', ''),
                    location=job.get('location', ''),
                    salary=job.get('salary', ''),
                    job_type='',  # 알바천국은 job_type 정보가 없을 수 있음
                    experience='',  # 알바천국은 경력 정보가 명시적이지 않음
                    education='',  # 알바천국은 학력 정보가 명시적이지 않음
                    employment_type='',  # 고용 형태
                    deadline=job.get('posted_date', ''),
                    url=job['url'],
                    detail=job.get('detail', ''),
                    search_keyword=keyword,
                    source_site='알바천국',
                    crawled_at=datetime.now()
                )

                db.add(job_posting)
                saved_count += 1
                print(f"[{saved_count}] DB 저장: {job['title']}")

            except Exception as e:
                print(f"DB 저장 오류 ({job['title']}): {e}")
                continue

        # 커밋
        db.commit()
        print(f"\n데이터베이스 저장 완료: {saved_count}개")
        print("=" * 60)

        # 저장 확인
        print("\n데이터베이스 확인:")
        recent_jobs = db.query(JobPosting).filter(
            JobPosting.search_keyword == keyword,
            JobPosting.source_site == '알바천국'
        ).order_by(JobPosting.crawled_at.desc()).limit(5).all()

        for job in recent_jobs:
            print(f"- {job.title} ({job.company}) [{job.crawled_at.strftime('%Y-%m-%d %H:%M:%S')}]")

        print("\n테스트 완료!")

    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if 'crawler' in locals():
            crawler.close()
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    test_crawler_with_db()
