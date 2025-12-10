"""
위험도 분석 엔진 - 고/중/저 위험 분류
"""
from typing import Dict, List
from enum import Enum


class RiskLevel(Enum):
    """위험 등급"""
    LOW = "저위험"
    MEDIUM = "중위험"
    HIGH = "고위험"


class RiskScorer:
    """위험도 점수화 및 분류 시스템"""

    def __init__(self):
        """위험도 임계값 설정"""
        # 위험도 임계값
        self.THRESHOLD_HIGH = 100  # 100점 이상: 고위험
        self.THRESHOLD_MEDIUM = 50  # 50-99점: 중위험
        # 50점 미만: 저위험

        # 복합 조건 가중치
        self.COMBO_TECH_LANGUAGE = 1.5  # 기술 + 언어 조합
        self.COMBO_TECH_LOCATION = 1.8  # 기술 + 해외근무 조합
        self.COMBO_TECH_COMPANY = 1.3  # 기술 + 대기업 조합
        self.COMBO_FULL_RISK = 2.0  # 기술 + 언어 + 해외 조합

    def calculate_risk_score(self, analysis_result: Dict) -> Dict:
        """
        종합 위험도 점수 계산

        Args:
            analysis_result: KeywordDetector의 분석 결과

        Returns:
            위험도 분석 결과 딕셔너리
        """
        base_score = analysis_result['total_score']

        # 카테고리별 집계
        categories = self._aggregate_categories(analysis_result)

        # 복합 조건 보너스
        combo_multiplier = self._calculate_combo_multiplier(categories)

        # 최종 점수
        final_score = int(base_score * combo_multiplier)

        # 위험 등급 분류
        risk_level = self._classify_risk_level(final_score, categories)

        # 위험 요인 분석
        risk_factors = self._identify_risk_factors(analysis_result, categories)

        # 권장 조치
        recommendations = self._get_recommendations(risk_level, risk_factors)

        return {
            'base_score': base_score,
            'combo_multiplier': combo_multiplier,
            'final_score': final_score,
            'risk_level': risk_level.value,
            'risk_level_enum': risk_level,
            'categories': categories,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'analysis_summary': self._generate_summary(
                risk_level, final_score, risk_factors, categories
            )
        }

    def _aggregate_categories(self, analysis_result: Dict) -> Dict:
        """카테고리별 집계"""
        categories = {
            'technology': [],
            'collaboration': [],
            'language': [],
            'location': [],
            'company': [],
            'risk': []
        }

        # Tier 1 (기술)
        for match in analysis_result['tier1_matches']:
            categories['technology'].append(match)

        # Tier 2 (협업, 언어, 위치, 회사)
        for match in analysis_result['tier2_matches']:
            category = match['category']
            if category in categories:
                categories[category].append(match)

        # Tier 3 (위험)
        for match in analysis_result['tier3_matches']:
            categories['risk'].append(match)

        return categories

    def _calculate_combo_multiplier(self, categories: Dict) -> float:
        """복합 조건 가중치 계산"""
        multiplier = 1.0

        has_tech = len(categories['technology']) > 0
        has_language = len(categories['language']) > 0
        has_location = len(categories['location']) > 0
        has_company = len(categories['company']) > 0

        # 기술 + 언어
        if has_tech and has_language:
            multiplier *= self.COMBO_TECH_LANGUAGE

        # 기술 + 해외위치
        if has_tech and has_location:
            multiplier *= self.COMBO_TECH_LOCATION

        # 기술 + 대기업
        if has_tech and has_company:
            multiplier *= self.COMBO_TECH_COMPANY

        # 완전 조합 (기술 + 언어 + 해외)
        if has_tech and has_language and has_location:
            multiplier *= self.COMBO_FULL_RISK

        return round(multiplier, 2)

    def _classify_risk_level(self, score: int, categories: Dict) -> RiskLevel:
        """위험 등급 분류"""
        # Tier 3 (위험 키워드)가 있으면 무조건 고위험
        if len(categories['risk']) > 0:
            return RiskLevel.HIGH

        # 복합 패턴이 있고 점수가 높으면 고위험
        if score >= self.THRESHOLD_HIGH:
            return RiskLevel.HIGH

        # 중위험
        if score >= self.THRESHOLD_MEDIUM:
            return RiskLevel.MEDIUM

        # 저위험
        return RiskLevel.LOW

    def _identify_risk_factors(self, analysis_result: Dict, categories: Dict) -> List[str]:
        """위험 요인 식별"""
        factors = []

        # 1. 첨단기술 분야
        if categories['technology']:
            tech_keywords = [m['keyword'] for m in categories['technology']]
            factors.append(f"첨단기술 분야: {', '.join(tech_keywords)}")

        # 2. 해외 관련
        if categories['location']:
            loc_keywords = [m['keyword'] for m in categories['location']]
            factors.append(f"해외 근무: {', '.join(loc_keywords)}")

        # 3. 언어 요구사항
        if categories['language']:
            lang_keywords = [m['keyword'] for m in categories['language']]
            factors.append(f"언어 요구: {', '.join(lang_keywords)}")

        # 4. 대기업 경력
        if categories['company']:
            comp_keywords = [m['keyword'] for m in categories['company']]
            factors.append(f"대기업 대상: {', '.join(comp_keywords)}")

        # 5. 의심 패턴
        if categories['collaboration']:
            collab_keywords = [m['keyword'] for m in categories['collaboration']]
            factors.append(f"의심 패턴: {', '.join(collab_keywords)}")

        # 6. 위험 키워드
        if categories['risk']:
            risk_keywords = [m['keyword'] for m in categories['risk']]
            factors.append(f"⚠️ 위험 키워드: {', '.join(risk_keywords)}")

        # 7. 복합 패턴
        if analysis_result['pattern_matches']:
            pattern_names = [p['pattern_name'] for p in analysis_result['pattern_matches']]
            factors.append(f"복합 패턴 탐지: {', '.join(pattern_names)}")

        return factors

    def _get_recommendations(self, risk_level: RiskLevel, risk_factors: List[str]) -> List[str]:
        """위험도에 따른 권장 조치"""
        recommendations = []

        if risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "🚨 즉시 정밀 조사 필요",
                "산업보안법 위반 여부 확인",
                "기업 등기부등본 및 실소유주 확인",
                "외국인투자신고 내역 확인",
                "해당 기업 공고 전수 조사",
                "관련 당국에 신고 검토"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "⚠️ 모니터링 강화 필요",
                "기업 배경 조사",
                "유사 공고 패턴 분석",
                "정기적인 추적 관찰"
            ])
        else:
            recommendations.extend([
                "ℹ️ 일반 모니터링",
                "정기 리뷰 대상"
            ])

        return recommendations

    def _generate_summary(
        self,
        risk_level: RiskLevel,
        score: int,
        risk_factors: List[str],
        categories: Dict
    ) -> str:
        """분석 요약 생성"""
        summary_parts = []

        # 위험 등급
        if risk_level == RiskLevel.HIGH:
            summary_parts.append(f"🚨 {risk_level.value} (점수: {score})")
        elif risk_level == RiskLevel.MEDIUM:
            summary_parts.append(f"⚠️ {risk_level.value} (점수: {score})")
        else:
            summary_parts.append(f"ℹ️ {risk_level.value} (점수: {score})")

        # 주요 위험 요인
        if risk_factors:
            summary_parts.append(f"주요 요인: {len(risk_factors)}개")

        # 카테고리별 매칭
        tech_count = len(categories['technology'])
        lang_count = len(categories['language'])
        loc_count = len(categories['location'])
        risk_count = len(categories['risk'])

        if tech_count > 0:
            summary_parts.append(f"기술키워드 {tech_count}개")
        if lang_count > 0:
            summary_parts.append(f"언어요구 {lang_count}개")
        if loc_count > 0:
            summary_parts.append(f"해외근무 {loc_count}개")
        if risk_count > 0:
            summary_parts.append(f"⚠️위험키워드 {risk_count}개")

        return " | ".join(summary_parts)

    def generate_daily_report(self, all_results: List[Dict]) -> Dict:
        """
        일일 리포트 생성 (참고 문서의 예시 형식)

        Args:
            all_results: 모든 분석 결과 리스트

        Returns:
            일일 리포트 딕셔너리
        """
        from datetime import datetime

        high_risk = [r for r in all_results if r['risk_level_enum'] == RiskLevel.HIGH]
        medium_risk = [r for r in all_results if r['risk_level_enum'] == RiskLevel.MEDIUM]
        low_risk = [r for r in all_results if r['risk_level_enum'] == RiskLevel.LOW]

        # 주요 키워드 집계
        all_keywords = set()
        for result in all_results:
            for category, matches in result['categories'].items():
                for match in matches:
                    all_keywords.add(match['keyword'])

        report = {
            '탐지일자': datetime.now().strftime('%Y-%m-%d'),
            '탐지대상': '잡코리아, 인크루트 등',  # 실제로는 동적으로
            '탐지공고수': f"{len(all_results)}건",
            '주요탐지키워드': ', '.join(list(all_keywords)[:10]),  # 상위 10개
            '분석결과': {
                '고위험': f"{len(high_risk)}건 (기술유출 가능성 높음)",
                '중위험': f"{len(medium_risk)}건 (해외 협업 연구소 형태)",
                '저위험': f"{len(low_risk)}건 (일반 모니터링)"
            },
            '추천조치': "산업보안법 모니터링 및 등기부 실소유주 확인 요청" if high_risk else "정기 모니터링",
            '고위험공고': [
                {
                    '제목': r['job_info']['title'],
                    '회사': r['job_info']['company'],
                    '위험요인': r['risk_factors'],
                    '점수': r['final_score']
                }
                for r in high_risk[:5]  # 상위 5개
            ]
        }

        return report


if __name__ == "__main__":
    # 테스트
    from keyword_detector import KeywordDetector

    detector = KeywordDetector()
    scorer = RiskScorer()

    # 테스트 공고 1: 고위험
    test_job_high = {
        "title": "반도체 공정 엔지니어 (중국 상하이 근무)",
        "company": "글로벌 R&D 센터",
        "location": "중국 상하이",
        "salary": "협의",
        "conditions": "삼성전자 경력 5년 이상, 중국어 필수",
        "recruit_summary": "해외 기술이전 프로젝트 참여, 파견 근무",
        "detail": "OLED 디스플레이 기술 지원 및 현지화 작업",
        "url": "http://example.com/1"
    }

    # 테스트 공고 2: 중위험
    test_job_medium = {
        "title": "디스플레이 연구원",
        "company": "중소기업",
        "location": "서울",
        "salary": "면접 후 결정",
        "conditions": "경력 3년 이상",
        "recruit_summary": "OLED 연구 개발",
        "detail": "디스플레이 기술 연구",
        "url": "http://example.com/2"
    }

    # 테스트 공고 3: 저위험
    test_job_low = {
        "title": "일반 사무직",
        "company": "일반기업",
        "location": "서울",
        "salary": "3000만원",
        "conditions": "경력 무관",
        "recruit_summary": "일반 사무 업무",
        "detail": "사무 보조",
        "url": "http://example.com/3"
    }

    print("=== 위험도 분석 테스트 ===\n")

    for i, test_job in enumerate([test_job_high, test_job_medium, test_job_low], 1):
        print(f"\n📋 테스트 공고 {i}: {test_job['title']}")
        print("-" * 60)

        # 키워드 탐지
        detection_result = detector.analyze(test_job)

        # 위험도 분석
        risk_result = scorer.calculate_risk_score(detection_result)

        print(f"✓ 기본 점수: {risk_result['base_score']}")
        print(f"✓ 복합 가중치: {risk_result['combo_multiplier']}x")
        print(f"✓ 최종 점수: {risk_result['final_score']}")
        print(f"✓ 위험 등급: {risk_result['risk_level']}")
        print(f"\n위험 요인:")
        for factor in risk_result['risk_factors']:
            print(f"  - {factor}")
        print(f"\n권장 조치:")
        for rec in risk_result['recommendations']:
            print(f"  - {rec}")
        print(f"\n요약: {risk_result['analysis_summary']}")
