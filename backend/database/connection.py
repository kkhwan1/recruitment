"""
데이터베이스 연결 관리자
Singleton 패턴 + Context Manager
"""
import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseConnection:
    """싱글톤 데이터베이스 연결 관리자"""

    _instance: Optional['DatabaseConnection'] = None
    _db_path: Path = Path(__file__).parent.parent.parent / "data" / "recruitment.db"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._ensure_db_directory()
            self._initialize_schema()

    def _ensure_db_directory(self):
        """데이터 디렉토리 생성"""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    def _initialize_schema(self):
        """스키마 초기화"""
        schema_file = Path(__file__).parent / "migrations" / "init_schema.sql"

        if not schema_file.exists():
            print(f"⚠️ 스키마 파일을 찾을 수 없습니다: {schema_file}")
            return

        with sqlite3.connect(self._db_path) as conn:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                conn.executescript(schema_sql)
            conn.commit()

        print(f"✅ 데이터베이스 초기화 완료: {self._db_path}")

    def get_connection(self) -> sqlite3.Connection:
        """데이터베이스 연결 반환"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def __enter__(self):
        """Context Manager 진입"""
        self.conn = self.get_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager 종료"""
        if self.conn:
            if exc_type:
                self.conn.rollback()
                print(f"❌ 트랜잭션 롤백: {exc_val}")
            else:
                self.conn.commit()
            self.conn.close()
        return False


def get_db_connection():
    """편의 함수: 데이터베이스 연결 반환"""
    return DatabaseConnection().get_connection()


if __name__ == "__main__":
    # 테스트
    print("데이터베이스 연결 테스트...")

    db = DatabaseConnection()

    # Context Manager 사용 예시
    with db as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print("\n📊 생성된 테이블:")
        for table in tables:
            print(f"  - {table['name']}")

    print("\n✅ 데이터베이스 연결 테스트 완료!")
