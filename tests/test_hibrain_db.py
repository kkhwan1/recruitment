"""
하이브레인넷 크롤러 테스트 및 DB 저장
"""
import sys
from pathlib import Path
from datetime import datetime
import sqlite3
import json

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parent))

from sites.hibrain.crawler import HibrainCrawler
from utils.logger import setup_logger

logger = setup_logger("HibrainTest")


def create_database():
    """데이터베이스 테이블 생성"""
    db_path = Path(__file__).parent / "data" / "jobs.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # jobs 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            salary TEXT,
            conditions TEXT,
            recruit_summary TEXT,
            detail TEXT,
            url TEXT UNIQUE,
            posted_date TEXT,
            source_site TEXT NOT NULL,
            search_keyword TEXT,
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    logger.info(f"데이터베이스 생성 완료: {db_path}")
    return db_path


def save_jobs_to_db(jobs, keyword, db_path):
    """공고 데이터를 DB에 저장"""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    saved_count = 0
    for job in jobs:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO jobs (
                    title, company, location, salary, conditions,
                    recruit_summary, detail, url, posted_date,
                    source_site, search_keyword, crawled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.get('title', ''),
                job.get('company', ''),
                job.get('location', ''),
                job.get('salary', ''),
                job.get('conditions', ''),
                job.get('recruit_summary', ''),
                job.get('detail', ''),
                job.get('url', ''),
                job.get('posted_date', ''),
                '하이브레인넷',
                keyword,
                datetime.now()
            ))
            if cursor.rowcount > 0:
                saved_count += 1
        except Exception as e:
            logger.error(f"DB 저장 중 오류: {e}")
            continue

    conn.commit()
    conn.close()
    logger.info(f"DB 저장 완료: {saved_count}개 공고")
    return saved_count


def verify_db_data(db_path, keyword):
    """DB에 저장된 데이터 확인"""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # 전체 개수 확인
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE search_keyword = ?", (keyword,))
    total_count = cursor.fetchone()[0]
    logger.info(f"DB에 저장된 '{keyword}' 공고 개수: {total_count}")

    # 최근 3개 공고 확인
    cursor.execute("""
        SELECT id, title, company, url, crawled_at
        FROM jobs
        WHERE search_keyword = ?
        ORDER BY id DESC
        LIMIT 3
    """, (keyword,))

    rows = cursor.fetchall()
    logger.info("\n최근 저장된 공고 3개:")
    for row in rows:
        job_id, title, company, url, crawled_at = row
        logger.info(f"  [{job_id}] {title} - {company}")
        logger.info(f"      URL: {url}")
        logger.info(f"      수집시간: {crawled_at}\n")

    conn.close()
    return total_count


def main():
    """메인 테스트 함수"""
    logger.info("=== 하이브레인넷 크롤러 테스트 시작 ===\n")

    # 1. DB 생성
    db_path = create_database()

    # 2. 크롤러 실행
    crawler = HibrainCrawler(headless=False)
    keyword = "반도체"
    max_jobs = 3

    try:
        logger.info(f"크롤링 시작: 키워드='{keyword}', 최대={max_jobs}개\n")
        crawler.start()

        # 공고 수집
        jobs = crawler.crawl(keyword, max_jobs=max_jobs)

        if not jobs:
            logger.warning("수집된 공고가 없습니다")
            return

        logger.info(f"\n수집 완료: {len(jobs)}개 공고")

        # 수집된 공고 출력
        logger.info("\n수집된 공고 목록:")
        for i, job in enumerate(jobs, 1):
            logger.info(f"{i}. {job.get('title', 'N/A')}")
            logger.info(f"   회사: {job.get('company', 'N/A')}")
            logger.info(f"   위치: {job.get('location', 'N/A')}")
            logger.info(f"   급여: {job.get('salary', 'N/A')}")
            logger.info(f"   URL: {job.get('url', 'N/A')}\n")

        # 3. DB 저장
        logger.info("DB 저장 시작...")
        saved_count = save_jobs_to_db(jobs, keyword, db_path)

        # 4. DB 데이터 확인
        logger.info("\nDB 데이터 검증...")
        total_count = verify_db_data(db_path, keyword)

        # 5. JSON 파일로도 저장
        crawler.save_results(keyword, jobs)

        # 결과 요약
        logger.info("\n" + "="*60)
        logger.info("테스트 완료!")
        logger.info(f"수집된 공고: {len(jobs)}개")
        logger.info(f"DB 저장: {saved_count}개")
        logger.info(f"DB 총 개수: {total_count}개")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}", exc_info=True)
    finally:
        crawler.close()


if __name__ == "__main__":
    main()
