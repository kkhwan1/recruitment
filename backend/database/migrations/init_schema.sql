-- 채용 공고 모니터링 시스템 데이터베이스 스키마
-- SQLite 데이터베이스 초기화 스크립트

-- 1. 채용 공고 기본 정보 테이블
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    salary TEXT,
    conditions TEXT,
    recruit_summary TEXT,
    detail TEXT,
    url TEXT UNIQUE NOT NULL,
    posted_date TEXT,
    source_site TEXT NOT NULL,
    search_keyword TEXT NOT NULL,
    crawled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    crawled_date DATE NOT NULL,
    crawled_weekday INTEGER NOT NULL,  -- 0=월요일, 6=일요일
    crawled_hour INTEGER NOT NULL,     -- 0-23
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. 키워드 매칭 결과 테이블
CREATE TABLE IF NOT EXISTS keyword_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    tier INTEGER NOT NULL,             -- 1, 2, 3
    keyword TEXT NOT NULL,
    category TEXT NOT NULL,
    weight INTEGER NOT NULL,
    match_count INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- 3. 복합 패턴 매칭 결과 테이블
CREATE TABLE IF NOT EXISTS pattern_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    pattern_id TEXT NOT NULL,
    pattern_name TEXT NOT NULL,
    keywords TEXT NOT NULL,            -- JSON 배열 형태로 저장
    weight INTEGER NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- 4. 위험도 분석 결과 테이블
CREATE TABLE IF NOT EXISTS risk_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    base_score INTEGER NOT NULL,
    combo_multiplier REAL NOT NULL,
    final_score INTEGER NOT NULL,
    risk_level TEXT NOT NULL,          -- 고위험, 중위험, 저위험
    risk_factors TEXT NOT NULL,        -- JSON 배열 형태로 저장
    recommendations TEXT NOT NULL,     -- JSON 배열 형태로 저장
    analysis_summary TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- 5. 일일 리포트 테이블
CREATE TABLE IF NOT EXISTS daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date DATE NOT NULL UNIQUE,
    detection_target TEXT NOT NULL,
    total_jobs INTEGER NOT NULL,
    high_risk_count INTEGER NOT NULL,
    medium_risk_count INTEGER NOT NULL,
    low_risk_count INTEGER NOT NULL,
    main_keywords TEXT NOT NULL,       -- JSON 배열 형태로 저장
    recommended_action TEXT NOT NULL,
    high_risk_jobs TEXT NOT NULL,      -- JSON 배열 형태로 저장
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성 (검색 성능 향상)

-- 시간별 분석을 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_jobs_crawled_weekday ON jobs(crawled_weekday);
CREATE INDEX IF NOT EXISTS idx_jobs_crawled_hour ON jobs(crawled_hour);
CREATE INDEX IF NOT EXISTS idx_jobs_crawled_date ON jobs(crawled_date);

-- 검색 키워드 인덱스
CREATE INDEX IF NOT EXISTS idx_jobs_search_keyword ON jobs(search_keyword);

-- 위험도 레벨 인덱스
CREATE INDEX IF NOT EXISTS idx_risk_analysis_risk_level ON risk_analysis(risk_level);
CREATE INDEX IF NOT EXISTS idx_risk_analysis_final_score ON risk_analysis(final_score);

-- 키워드 티어 인덱스
CREATE INDEX IF NOT EXISTS idx_keyword_matches_tier ON keyword_matches(tier);
CREATE INDEX IF NOT EXISTS idx_keyword_matches_keyword ON keyword_matches(keyword);

-- 외래 키 인덱스
CREATE INDEX IF NOT EXISTS idx_keyword_matches_job_id ON keyword_matches(job_id);
CREATE INDEX IF NOT EXISTS idx_pattern_matches_job_id ON pattern_matches(job_id);
CREATE INDEX IF NOT EXISTS idx_risk_analysis_job_id ON risk_analysis(job_id);
