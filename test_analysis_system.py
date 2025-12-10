"""
키워드 탐지 및 위험도 분석 시스템 통합 테스트
"""
from analyzers.keyword_detector import KeywordDetector
from analyzers.risk_scorer import RiskScorer
import json


def test_analysis_system():
    """분석 시스템 통합 테스트"""

    print("=" * 80)
    print("채용 공고 분석 시스템 테스트")
    print("=" * 80)

    # 분석 엔진 초기화
    detector = KeywordDetector()
    scorer = RiskScorer()

    # 테스트 공고 모음
    test_jobs = [
        {
            "name": "고위험 공고 1",
            "data": {
                "title": "반도체 공정 엔지니어 (중국 상하이 근무)",
                "company": "글로벌 R&D 센터",
                "location": "중국 상하이",
                "salary": "협의",
                "conditions": "삼성전자 경력 5년 이상, 중국어 필수",
                "recruit_summary": "해외 기술이전 프로젝트 참여, 파견 근무",
                "detail": "OLED 디스플레이 기술 지원 및 현지화 작업. 글로벌 R&D 센터에서 최신 반도체 기술을 활용한 합작회사 프로젝트",
                "url": "http://example.com/job1"
            }
        },
        {
            "name": "고위험 공고 2",
            "data": {
                "title": "이차전지 연구원 (베이징)",
                "company": "테크놀로지 연구소",
                "location": "중국 베이징",
                "salary": "급구, 현금지급",
                "conditions": "LG화학 또는 삼성SDI 경력, 중국어 가능자 우대",
                "recruit_summary": "리튬이온 배터리 기술 이전 프로젝트",
                "detail": "2차전지 기술 지원 및 공동개발",
                "url": "http://example.com/job2"
            }
        },
        {
            "name": "중위험 공고",
            "data": {
                "title": "디스플레이 연구원",
                "company": "한국 디스플레이",
                "location": "경기도 수원",
                "salary": "4000-5000만원",
                "conditions": "경력 3년 이상, 영어 가능자",
                "recruit_summary": "OLED 디스플레이 연구 개발. 해외 협업 프로젝트 참여 가능",
                "detail": "최신 디스플레이 기술 연구",
                "url": "http://example.com/job3"
            }
        },
        {
            "name": "저위험 공고",
            "data": {
                "title": "일반 사무직",
                "company": "일반 기업",
                "location": "서울 강남구",
                "salary": "3000만원",
                "conditions": "경력 무관, 워드/엑셀 가능자",
                "recruit_summary": "일반 사무 업무",
                "detail": "문서 작성 및 관리",
                "url": "http://example.com/job4"
            }
        }
    ]

    all_results = []

    # 각 공고 분석
    for test_job in test_jobs:
        print(f"\n{'=' * 80}")
        print(f"📋 {test_job['name']}: {test_job['data']['title']}")
        print("=" * 80)

        # 키워드 탐지
        detection_result = detector.analyze(test_job['data'])

        # 위험도 분석
        risk_result = scorer.calculate_risk_score(detection_result)
        risk_result['job_info'] = test_job['data']

        all_results.append(risk_result)

        # 결과 출력
        print(f"\n🎯 분석 결과:")
        print(f"  - 기본 점수: {risk_result['base_score']}")
        print(f"  - 복합 가중치: {risk_result['combo_multiplier']}x")
        print(f"  - 최종 점수: {risk_result['final_score']}")
        print(f"  - 위험 등급: {risk_result['risk_level']}")

        print(f"\n🔍 탐지된 키워드:")
        print(f"  - 1차 (기술): {len(detection_result['tier1_matches'])}개")
        for m in detection_result['tier1_matches']:
            print(f"    • {m['keyword']} (가중치: {m['weight']})")

        print(f"  - 2차 (의심): {len(detection_result['tier2_matches'])}개")
        for m in detection_result['tier2_matches']:
            print(f"    • {m['keyword']} (가중치: {m['weight']})")

        if detection_result['tier3_matches']:
            print(f"  - 3차 (위험): {len(detection_result['tier3_matches'])}개")
            for m in detection_result['tier3_matches']:
                print(f"    • ⚠️ {m['keyword']} (가중치: {m['weight']})")

        if detection_result['pattern_matches']:
            print(f"  - 복합 패턴: {len(detection_result['pattern_matches'])}개")
            for p in detection_result['pattern_matches']:
                print(f"    • {p['pattern_name']}: {' + '.join(p['keywords'])}")

        print(f"\n⚠️ 위험 요인:")
        for factor in risk_result['risk_factors']:
            print(f"  - {factor}")

        print(f"\n💡 권장 조치:")
        for i, rec in enumerate(risk_result['recommendations'][:3], 1):
            print(f"  {i}. {rec}")

        print(f"\n📊 요약: {risk_result['analysis_summary']}")

    # 일일 리포트 생성
    print(f"\n\n{'=' * 80}")
    print("📈 일일 리포트")
    print("=" * 80)

    daily_report = scorer.generate_daily_report(all_results)

    print(f"\n탐지일자: {daily_report['탐지일자']}")
    print(f"탐지대상: {daily_report['탐지대상']}")
    print(f"탐지공고수: {daily_report['탐지공고수']}")
    print(f"주요탐지키워드: {daily_report['주요탐지키워드']}")

    print(f"\n분석결과:")
    for level, count in daily_report['분석결과'].items():
        print(f"  - {level}: {count}")

    print(f"\n추천조치: {daily_report['추천조치']}")

    if daily_report['고위험공고']:
        print(f"\n⚠️ 고위험 공고 목록:")
        for i, job in enumerate(daily_report['고위험공고'], 1):
            print(f"\n  {i}. {job['제목']}")
            print(f"     회사: {job['회사']}")
            print(f"     점수: {job['점수']}점")
            print(f"     위험요인:")
            for factor in job['위험요인'][:3]:
                print(f"       - {factor}")

    # JSON 파일로 저장
    output_file = "test_analysis_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_jobs': test_jobs,
            'analysis_results': [
                {
                    'job_title': r['job_info']['title'],
                    'risk_level': r['risk_level'],
                    'final_score': r['final_score'],
                    'risk_factors': r['risk_factors'],
                    'recommendations': r['recommendations']
                }
                for r in all_results
            ],
            'daily_report': daily_report
        }, f, ensure_ascii=False, indent=2)

    print(f"\n\n✅ 테스트 완료!")
    print(f"📄 상세 결과가 '{output_file}' 파일에 저장되었습니다.")

    return all_results, daily_report


if __name__ == "__main__":
    test_analysis_system()
