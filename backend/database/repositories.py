"""
데이터 접근 계층 (Repository Pattern)
데이터베이스 CRUD 작업 추상화
"""
import json
from datetime import datetime
from typing import List, Dict, Optional
from .connection import DatabaseConnection
from .models import Job, KeywordMatch, PatternMatch, RiskAnalysis, DailyReport


class JobRepository:
    """채용 공고 데이터 저장소"""

    def __init__(self):
        self.db = DatabaseConnection()

    def insert_job(self, job_data: dict) -> int:
        """
        채용 공고 저장

        Args:
            job_data: 채용 공고 정보 딕셔너리

        Returns:
            저장된 job_id
        """
        with self.db as conn:
            cursor = conn.cursor()

            # 시간 정보 추가
            now = datetime.now()
            crawled_at = job_data.get('crawled_at', now)
            crawled_date = crawled_at.date().isoformat()
            crawled_weekday = crawled_at.weekday()  # 0=월요일
            crawled_hour = crawled_at.hour

            cursor.execute("""
                INSERT INTO jobs (
                    title, company, location, salary, conditions,
                    recruit_summary, detail, url, posted_date,
                    source_site, search_keyword,
                    crawled_at, crawled_date, crawled_weekday, crawled_hour
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_data.get('title', ''),
                job_data.get('company', ''),
                job_data.get('location', ''),
                job_data.get('salary', ''),
                job_data.get('conditions', ''),
                job_data.get('recruit_summary', ''),
                job_data.get('detail', ''),
                job_data.get('url', ''),
                job_data.get('posted_date', ''),
                job_data.get('source_site', '잡코리아'),
                job_data.get('search_keyword', ''),
                crawled_at,
                crawled_date,
                crawled_weekday,
                crawled_hour
            ))

            return cursor.lastrowid

    def get_job_by_id(self, job_id: int) -> Optional[dict]:
        """ID로 채용 공고 조회"""
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_jobs_by_weekday(self, weekday: int) -> List[dict]:
        """요일별 채용 공고 조회 (0=월요일, 6=일요일)"""
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM jobs WHERE crawled_weekday = ?
                ORDER BY crawled_at DESC
            """, (weekday,))
            return [dict(row) for row in cursor.fetchall()]

    def get_jobs_by_hour(self, hour: int) -> List[dict]:
        """시간대별 채용 공고 조회 (0-23)"""
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM jobs WHERE crawled_hour = ?
                ORDER BY crawled_at DESC
            """, (hour,))
            return [dict(row) for row in cursor.fetchall()]

    def get_jobs_by_date_range(self, start_date: str, end_date: str) -> List[dict]:
        """기간별 채용 공고 조회"""
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM jobs
                WHERE crawled_date BETWEEN ? AND ?
                ORDER BY crawled_at DESC
            """, (start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]

    def get_jobs_by_keyword(self, keyword: str) -> List[dict]:
        """검색 키워드별 채용 공고 조회"""
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM jobs WHERE search_keyword = ?
                ORDER BY crawled_at DESC
            """, (keyword,))
            return [dict(row) for row in cursor.fetchall()]


class AnalysisRepository:
    """분석 결과 저장소"""

    def __init__(self):
        self.db = DatabaseConnection()

    def save_analysis(self, job_id: int, detection_result: dict, risk_result: dict):
        """
        분석 결과 저장 (키워드 매칭, 패턴 매칭, 위험도 분석)

        Args:
            job_id: 채용 공고 ID
            detection_result: 키워드 탐지 결과
            risk_result: 위험도 분석 결과
        """
        with self.db as conn:
            cursor = conn.cursor()

            # 1. 키워드 매칭 결과 저장
            for tier in [1, 2, 3]:
                key = f'tier{tier}_matches'
                if key in detection_result:
                    for match in detection_result[key]:
                        cursor.execute("""
                            INSERT INTO keyword_matches (
                                job_id, tier, keyword, category, weight, match_count
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            job_id,
                            tier,
                            match['keyword'],
                            match['category'],
                            match['weight'],
                            match['count']
                        ))

            # 2. 복합 패턴 매칭 결과 저장
            if 'pattern_matches' in detection_result:
                for pattern in detection_result['pattern_matches']:
                    cursor.execute("""
                        INSERT INTO pattern_matches (
                            job_id, pattern_id, pattern_name, keywords, weight, description
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        job_id,
                        pattern['pattern_id'],
                        pattern['pattern_name'],
                        json.dumps(pattern['keywords'], ensure_ascii=False),
                        pattern['weight'],
                        pattern['description']
                    ))

            # 3. 위험도 분석 결과 저장
            cursor.execute("""
                INSERT INTO risk_analysis (
                    job_id, base_score, combo_multiplier, final_score, risk_level,
                    risk_factors, recommendations, analysis_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id,
                risk_result['base_score'],
                risk_result['combo_multiplier'],
                risk_result['final_score'],
                risk_result['risk_level'],
                json.dumps(risk_result['risk_factors'], ensure_ascii=False),
                json.dumps(risk_result['recommendations'], ensure_ascii=False),
                risk_result['analysis_summary']
            ))

    def get_high_risk_jobs(self, limit: int = 100) -> List[dict]:
        """고위험 공고 조회"""
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT j.*, r.final_score, r.risk_level, r.risk_factors
                FROM jobs j
                JOIN risk_analysis r ON j.id = r.job_id
                WHERE r.risk_level = '고위험'
                ORDER BY r.final_score DESC, j.crawled_at DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_risk_statistics(self) -> dict:
        """위험도 통계"""
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT risk_level, COUNT(*) as count
                FROM risk_analysis
                GROUP BY risk_level
            """)
            stats = {row['risk_level']: row['count'] for row in cursor.fetchall()}
            return stats

    def get_keyword_statistics(self, tier: Optional[int] = None) -> List[dict]:
        """키워드 통계"""
        with self.db as conn:
            cursor = conn.cursor()
            if tier:
                cursor.execute("""
                    SELECT keyword, category, COUNT(*) as count, SUM(match_count) as total_matches
                    FROM keyword_matches
                    WHERE tier = ?
                    GROUP BY keyword, category
                    ORDER BY count DESC, total_matches DESC
                """, (tier,))
            else:
                cursor.execute("""
                    SELECT tier, keyword, category, COUNT(*) as count, SUM(match_count) as total_matches
                    FROM keyword_matches
                    GROUP BY tier, keyword, category
                    ORDER BY tier, count DESC, total_matches DESC
                """)
            return [dict(row) for row in cursor.fetchall()]


class ReportRepository:
    """리포트 저장소"""

    def __init__(self):
        self.db = DatabaseConnection()

    def save_daily_report(self, report_data: dict):
        """일일 리포트 저장"""
        with self.db as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO daily_reports (
                    report_date, detection_target, total_jobs,
                    high_risk_count, medium_risk_count, low_risk_count,
                    main_keywords, recommended_action, high_risk_jobs
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report_data['탐지일자'],
                report_data['탐지대상'],
                report_data['탐지공고수'],
                report_data['분석결과']['고위험'],
                report_data['분석결과']['중위험'],
                report_data['분석결과']['저위험'],
                json.dumps(report_data['주요탐지키워드'], ensure_ascii=False),
                report_data['추천조치'],
                json.dumps(report_data['고위험공고'], ensure_ascii=False)
            ))

    def get_daily_report(self, report_date: str) -> Optional[dict]:
        """일일 리포트 조회"""
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM daily_reports WHERE report_date = ?
            """, (report_date,))
            row = cursor.fetchone()
            if row:
                report = dict(row)
                report['main_keywords'] = json.loads(report['main_keywords'])
                report['high_risk_jobs'] = json.loads(report['high_risk_jobs'])
                return report
            return None

    def get_recent_reports(self, limit: int = 30) -> List[dict]:
        """최근 리포트 조회"""
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM daily_reports
                ORDER BY report_date DESC
                LIMIT ?
            """, (limit,))
            reports = []
            for row in cursor.fetchall():
                report = dict(row)
                report['main_keywords'] = json.loads(report['main_keywords'])
                report['high_risk_jobs'] = json.loads(report['high_risk_jobs'])
                reports.append(report)
            return reports


if __name__ == "__main__":
    # 테스트
    print("Repository 테스트...")

    job_repo = JobRepository()
    analysis_repo = AnalysisRepository()

    print("\n✅ Repository 초기화 완료!")
