# 채용 공고 데이터베이스 시스템

## 개요

요일 및 시간별 채용 공고 수집 데이터를 저장하고 관리하는 SQLite 기반 데이터베이스 시스템입니다.

## 데이터베이스 구조

### 📍 위치
```
data/recruitment.db
```

### 📊 테이블 구조 (5개 테이블)

#### 1. jobs (채용 공고 기본 정보)
- 채용 공고의 기본 정보 저장
- **핵심 시간 추적 필드**:
  - `crawled_date`: 수집 날짜 (YYYY-MM-DD)
  - `crawled_weekday`: 수집 요일 (0=월요일 ~ 6=일요일)
  - `crawled_hour`: 수집 시간대 (0~23)
  - `crawled_at`: 정확한 수집 시각 (datetime)

#### 2. keyword_matches (키워드 매칭 결과)
- 3-tier 키워드 탐지 결과 저장
- Tier 1: 기술 분야 키워드 (weight 8-10)
- Tier 2: 의심 패턴 키워드 (weight 12-25)
- Tier 3: 고위험 키워드 (weight 20-25)

#### 3. pattern_matches (복합 패턴 매칭)
- 2-3개 키워드 AND 조합 패턴 매칭 결과
- 가중치: 28-40점

#### 4. risk_analysis (위험도 분석)
- 최종 위험도 점수 및 등급
- 위험 요인 및 권장 조치사항
- 분석 요약

#### 5. daily_reports (일일 리포트)
- 일자별 종합 분석 리포트
- 주요 키워드 통계
- 고위험 공고 목록

## 시간별 데이터 분석 기능

### 요일별 조회
```python
from database.repositories import JobRepository

job_repo = JobRepository()

# 월요일(0)에 수집된 공고 조회
monday_jobs = job_repo.get_jobs_by_weekday(0)

# 목요일(3)에 수집된 공고 조회
thursday_jobs = job_repo.get_jobs_by_weekday(3)
```

### 시간대별 조회
```python
# 오전 9시에 수집된 공고 조회
morning_jobs = job_repo.get_jobs_by_hour(9)

# 오후 6시에 수집된 공고 조회
evening_jobs = job_repo.get_jobs_by_hour(18)
```

### 기간별 조회
```python
# 특정 기간 동안 수집된 공고 조회
jobs = job_repo.get_jobs_by_date_range('2024-01-01', '2024-01-31')
```

## 데이터 저장 흐름

```
크롤러 수집
    ↓
키워드 탐지 (3-tier)
    ↓
위험도 분석
    ↓
데이터베이스 저장 (temporal tracking)
    ↓
JSON 백업 (data/analysis_results/)
```

## 통계 및 분석

### 위험도 통계
```python
from database.repositories import AnalysisRepository

analysis_repo = AnalysisRepository()

# 위험도별 통계
stats = analysis_repo.get_risk_statistics()
# {'고위험': 15, '중위험': 32, '저위험': 8}
```

### 키워드 통계
```python
# 전체 키워드 통계
keyword_stats = analysis_repo.get_keyword_statistics()

# Tier별 키워드 통계
tier1_stats = analysis_repo.get_keyword_statistics(tier=1)
```

### 고위험 공고 조회
```python
# 고위험 공고 상위 100개 조회
high_risk_jobs = analysis_repo.get_high_risk_jobs(limit=100)
```

## 실시간 수집 현황

현재 백그라운드에서 크롤링이 진행 중입니다:
- 키워드: "반도체"
- 수집 방식: 산업별 기업 → 기업별 공고 → 키워드 매칭
- 진행 산업: 반도체, 디스플레이, 이차전지 (완료), 조선, 원자력, 우주항공 (대기중)
- 상태: 자동으로 데이터베이스에 저장 진행 중

## 데이터베이스 인덱스

성능 최적화를 위한 인덱스:
- `idx_jobs_crawled_weekday`: 요일별 조회 최적화
- `idx_jobs_crawled_hour`: 시간대별 조회 최적화
- `idx_jobs_crawled_date`: 날짜별 조회 최적화
- `idx_risk_analysis_risk_level`: 위험도별 조회 최적화
- `idx_keyword_matches_keyword`: 키워드별 통계 최적화

## Repository 패턴

### JobRepository
- `insert_job()`: 채용 공고 저장 (자동 시간 추적)
- `get_job_by_id()`: ID로 조회
- `get_jobs_by_weekday()`: 요일별 조회
- `get_jobs_by_hour()`: 시간대별 조회
- `get_jobs_by_date_range()`: 기간별 조회
- `get_jobs_by_keyword()`: 검색 키워드별 조회

### AnalysisRepository
- `save_analysis()`: 분석 결과 저장 (키워드, 패턴, 위험도)
- `get_high_risk_jobs()`: 고위험 공고 조회
- `get_risk_statistics()`: 위험도 통계
- `get_keyword_statistics()`: 키워드 통계

### ReportRepository
- `save_daily_report()`: 일일 리포트 저장
- `get_daily_report()`: 특정 날짜 리포트 조회
- `get_recent_reports()`: 최근 리포트 목록 조회

## 향후 활용 가능한 분석

수집된 시간 데이터를 활용하여 다음과 같은 분석이 가능합니다:

1. **시간대별 패턴 분석**
   - 어느 시간대에 위험 공고가 많이 게시되는지
   - 출근 시간(9-10시) vs 퇴근 시간(18-19시) 비교

2. **요일별 패턴 분석**
   - 주중 vs 주말 게시 패턴
   - 월요일 vs 금요일 비교

3. **시계열 트렌드 분석**
   - 일별/주별/월별 위험 공고 증감 추세
   - 특정 키워드의 시간 경과에 따른 변화

4. **조합 분석**
   - 특정 요일 + 특정 시간대 고위험 패턴
   - 산업별 × 시간대별 교차 분석

## 테스트

```bash
python test_database.py
```

모든 기능 (연결, 저장, 조회, 시간별 조회, 통계)을 테스트합니다.
