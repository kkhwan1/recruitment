# 채용 공고 모니터링 시스템

진행.md 파일의 채용 사이트 목록과 필요 서칭 키워드를 기반으로 채용 공고를 수집하고,
기술유출 위험 및 불법 고용 의심 공고를 자동으로 탐지·분석하는 시스템입니다.

## 주요 기능

### 1. 자동 크롤링
- 잡코리아, 인크루트, 사람인, 하이브레인넷, 알바천국, 알바몬, 잡플래닛, 워크넷 등 주요 채용 사이트에서 공고 수집
- 키워드 기반 검색 및 필터링
- JSON 형식으로 데이터 저장

### 2. 지능형 분석 엔진
- **3단계 키워드 탐지**: 첨단기술, 의심 패턴, 위험 키워드 자동 탐지
- **복합 패턴 매칭**: 2-3개 키워드 조합을 통한 고도화된 위험 탐지
- **위험도 점수화**: 탐지된 키워드와 패턴을 기반으로 위험도 점수 계산
- **자동 등급 분류**: 고위험/중위험/저위험 자동 분류
- **일일 리포트 생성**: 탐지 결과 요약 및 권장 조치사항 제공

## 프로젝트 구조

```
채용시스템/
├── config/
│   ├── keywords.json               # 검색 키워드 설정
│   ├── detection_keywords.csv      # 3단계 탐지 키워드 (75+개)
│   └── complex_patterns.csv        # 복합 패턴 규칙 (25개)
├── analyzers/                      # 분석 엔진
│   ├── keyword_detector.py         # 키워드 탐지 시스템
│   └── risk_scorer.py              # 위험도 점수화 및 분류
├── sites/
│   ├── jobkorea/                   # 잡코리아 크롤러
│   │   ├── crawler.py
│   │   └── config.json
│   └── incruit/                    # 인크루트 크롤러
│       ├── crawler.py
│       └── config.json
├── utils/                          # 공통 유틸리티
│   ├── file_handler.py
│   └── logger.py
├── data/
│   └── json_results/               # 수집된 데이터 저장 디렉토리
├── main.py                         # 메인 실행 스크립트
├── test_analysis_system.py         # 분석 시스템 테스트
└── requirements.txt
```

## 설치

1. Python 3.8 이상 필요
2. 의존성 설치:

```bash
pip install -r requirements.txt
playwright install chromium
```

## 분석 엔진

### 3단계 키워드 탐지 시스템

#### 1차 탐지 (첨단기술 분야)
첨단기술 분야 키워드 탐지 (가중치: 8-10점)

- **반도체**: 반도체, 웨이퍼, 공정, 식각, 증착 등
- **디스플레이**: OLED, LCD, 패널, TFT 등
- **이차전지**: 배터리, 리튬이온, 양극재, 음극재 등
- **조선**: 조선, 선박, 해양플랜트 등
- **원자력**: 원자력, 원전, 핵연료 등
- **우주항공**: 우주항공, 위성, 로켓 등

#### 2차 탐지 (의심 패턴)
해외 협업, 언어 요구사항, 지역, 대기업 경력 등 의심 패턴 탐지 (가중치: 12-25점)

- **협업 패턴**: 해외협업, 기술이전, 파견, 공동개발, 합작회사 등
- **언어 요구**: 중국어필수, 중국어가능, 일본어 등
- **지역**: 중국, UAE, 홍콩, 상하이, 베이징 등
- **회사**: 삼성, LG, SK, 현대 등 대기업 경력 요구

#### 3차 탐지 (위험 키워드)
불법 고용 의심 키워드 탐지 (가중치: 20-25점)

- 급구, 비자필요없음, 현금지급, 여권보관, 숙식제공 등

#### 복합 패턴 매칭
2-3개 키워드를 AND 연산자로 조합한 고위험 패턴 탐지 (가중치: 28-40점)

- `반도체 + 중국 + 기술이전` → 40점 (최고위험)
- `이차전지 + 기술이전 + 파견` → 38점
- `OLED + 해외 + R&D` → 35점
- `반도체 + 중국어필수` → 30점

### 위험도 점수화 시스템

#### 기본 점수 계산
- 각 탐지된 키워드의 가중치를 합산
- 1차(기술) + 2차(의심) + 3차(위험) + 복합패턴

#### 복합 조건 가중치
- **기술 + 언어**: 1.5배
- **기술 + 해외근무**: 1.8배
- **기술 + 대기업**: 1.3배
- **기술 + 언어 + 해외**: 2.0배

#### 위험 등급 분류
- **고위험 (100점 이상)**: 기술유출 가능성 높음, 즉시 정밀 조사 필요
- **중위험 (50-99점)**: 해외 협업 연구소 형태, 모니터링 강화 필요
- **저위험 (50점 미만)**: 일반 모니터링

### 분석 시스템 테스트

```bash
python test_analysis_system.py
```

테스트 결과:
- 4개 샘플 공고 분석 (고위험 2건, 중위험 1건, 저위험 1건)
- 키워드 탐지 현황 출력
- 위험도 점수 및 등급 표시
- 위험 요인 및 권장 조치사항 제공
- 일일 리포트 생성
- JSON 파일로 상세 결과 저장

## 사용법

### 기본 사용 (모든 사이트, 모든 키워드)
```bash
python main.py
```

### 특정 사이트만 크롤링
```bash
python main.py --site jobkorea
python main.py --site incruit
python main.py --site saramin
python main.py --site hibrain
```

### 특정 키워드로 검색
```bash
python main.py --keyword "중국어"
```

### 최대 수집 개수 지정
```bash
python main.py --max-jobs 100
```

### 브라우저 창 표시 (디버깅용)
```bash
python main.py --no-headless
```

### 여러 옵션 조합
```bash
python main.py --site jobkorea --keyword "중국" --max-jobs 30 --no-headless
```

## 분석 엔진 사용 예시

### Python 코드에서 직접 사용

```python
from analyzers.keyword_detector import KeywordDetector
from analyzers.risk_scorer import RiskScorer

# 분석 엔진 초기화
detector = KeywordDetector()
scorer = RiskScorer()

# 채용 공고 데이터
job_info = {
    "title": "반도체 공정 엔지니어 (중국 상하이 근무)",
    "company": "글로벌 R&D 센터",
    "location": "중국 상하이",
    "salary": "협의",
    "conditions": "삼성전자 경력 5년 이상, 중국어 필수",
    "recruit_summary": "해외 기술이전 프로젝트 참여",
    "detail": "OLED 디스플레이 기술 지원",
    "url": "http://example.com/job1"
}

# 키워드 탐지
detection_result = detector.analyze(job_info)
print(f"탐지된 키워드: {len(detection_result['tier1_matches'])}개")
print(f"총점: {detection_result['total_score']}점")

# 위험도 분석
risk_result = scorer.calculate_risk_score(detection_result)
print(f"위험 등급: {risk_result['risk_level']}")
print(f"최종 점수: {risk_result['final_score']}점")
print(f"권장 조치: {risk_result['recommendations'][0]}")
```

### 일일 리포트 생성

```python
# 여러 공고 분석
all_results = []
for job in jobs:
    detection = detector.analyze(job)
    risk = scorer.calculate_risk_score(detection)
    risk['job_info'] = job
    all_results.append(risk)

# 일일 리포트 생성
daily_report = scorer.generate_daily_report(all_results)
print(f"탐지일자: {daily_report['탐지일자']}")
print(f"탐지공고수: {daily_report['탐지공고수']}")
print(f"고위험 공고: {len(daily_report['고위험공고'])}건")
```

## 키워드 설정

### 크롤링 키워드 (config/keywords.json)

검색용 키워드 관리:

- `technology_fields`: 기술 분야 키워드
- `regions`: 지역 키워드
- `languages`: 언어 키워드
- `companies`: 회사명 키워드
- `risk_keywords`: 리스크 키워드

### 탐지 키워드 (config/detection_keywords.csv)

3단계 탐지 시스템용 키워드 75+개:

```csv
tier,category,keyword,weight,description
1,technology,반도체,10,반도체 기술 분야
2,language,중국어필수,25,중국어 필수 조건
3,risk,급구,20,급하게 구함 (의심)
```

**필드 설명:**
- `tier`: 탐지 단계 (1=기술, 2=의심, 3=위험)
- `category`: 카테고리 (technology, collaboration, language, location, company, risk)
- `keyword`: 탐지할 키워드
- `weight`: 가중치 (점수)
- `description`: 설명

### 복합 패턴 (config/complex_patterns.csv)

2-3개 키워드 조합 패턴 25개:

```csv
pattern_id,pattern_name,keyword1,operator1,keyword2,operator2,keyword3,weight,description
P001,반도체_중국어,반도체,AND,중국어필수,"","",30,반도체 + 중국어 필수
P015,반도체_중국_기술이전,반도체,AND,중국,AND,기술이전,40,최고위험
```

**필드 설명:**
- `pattern_id`: 패턴 고유 ID
- `pattern_name`: 패턴 이름
- `keyword1/2/3`: 조합할 키워드
- `operator1/2`: 연산자 (AND, OR)
- `weight`: 패턴 가중치
- `description`: 설명

## 출력 형식

수집된 데이터는 `data/json_results/` 디렉토리에 JSON 파일로 저장됩니다.

파일명 형식: `{사이트명}_{키워드}_{타임스탬프}.json`

예시:
```json
{
  "site": "잡코리아",
  "keyword": "중국어",
  "collected_at": "2024-01-01T12:00:00",
  "jobs": [
    {
      "title": "공고 제목",
      "company": "회사명",
      "location": "근무지",
      "salary": "급여",
      "conditions": "조건",
      "detail": "상세내용",
      "url": "공고 URL",
      "posted_date": "등록일"
    }
  ]
}
```

## 사이트별 크롤러

각 사이트는 독립적인 크롤러로 구성되어 있어, 새로운 사이트를 추가하기 쉽습니다.

### 잡코리아 크롤러
```python
from sites.jobkorea import JobKoreaCrawler

crawler = JobKoreaCrawler(headless=True)
crawler.start()
jobs = crawler.crawl("중국어", max_jobs=50)
crawler.save_results("중국어", jobs)
crawler.close()
```

### 인쿠르트 크롤러
```python
from sites.incruit import IncruitCrawler

crawler = IncruitCrawler(headless=True)
crawler.start()
jobs = crawler.crawl("중국어", max_jobs=50)
crawler.save_results("중국어", jobs)
crawler.close()
```

## 주의사항

### 크롤링 관련
- 각 사이트의 이용약관을 확인하고 준수하세요
- 과도한 요청은 IP 차단을 받을 수 있으므로 적절한 딜레이를 설정하세요
- 수집된 데이터의 사용 목적을 명확히 하세요

### 분석 엔진 관련
- **키워드 정확도**: 탐지 키워드는 지속적으로 업데이트하여 정확도를 높여야 합니다
- **오탐 가능성**: 정상적인 공고도 키워드 조합에 따라 고위험으로 분류될 수 있습니다
- **인적 검증 필수**: 자동 분석 결과는 참고용이며, 최종 판단은 전문가의 검증이 필요합니다
- **법적 근거**: 탐지된 공고에 대한 조치는 산업보안법 등 법적 근거를 확인 후 진행하세요
- **개인정보 보호**: 수집된 데이터에 개인정보가 포함될 수 있으므로 관련 법규를 준수하세요

### 키워드 관리
- `config/detection_keywords.csv`: 새로운 위험 패턴 발견 시 지속적으로 추가
- `config/complex_patterns.csv`: 고위험 패턴 조합을 지속적으로 업데이트
- 가중치 조정: 실제 운영 데이터를 기반으로 키워드 가중치를 미세 조정
- 오탐 감소: 오탐이 많은 키워드는 가중치를 낮추거나 제외 검토

## 향후 개발 계획

- [x] 추가 채용 사이트 크롤러 구현 (사람인, 잡플래닛, 알바천국, 알바몬, 워크넷 완료)
- [ ] 크롤러와 분석 엔진 통합 자동화
- [ ] 웹 대시보드 개발 (분석 결과 시각화)
- [ ] 이메일/슬랙 알림 기능 추가
- [ ] 머신러닝 기반 위험도 예측 모델 개발
- [ ] 기업 정보 자동 조회 (등기부, 외국인투자 등)
- [ ] 히스토리 데이터베이스 구축 및 트렌드 분석

## 라이센스

이 프로젝트는 교육 및 연구 목적으로 개발되었습니다.

