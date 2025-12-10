"""
키워드 탐지 시스템 - 3단계 키워드 매칭
"""
import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass


@dataclass
class KeywordMatch:
    """키워드 매칭 결과"""
    keyword: str
    tier: int
    category: str
    weight: int
    positions: List[int]  # 텍스트 내 위치


@dataclass
class PatternMatch:
    """복합 패턴 매칭 결과"""
    pattern_id: str
    pattern_name: str
    keywords: List[str]
    weight: int
    description: str


class KeywordDetector:
    """3단계 키워드 탐지 시스템"""

    def __init__(self, keywords_csv: str = None, patterns_csv: str = None):
        """
        Args:
            keywords_csv: 키워드 CSV 파일 경로
            patterns_csv: 복합 패턴 CSV 파일 경로
        """
        if keywords_csv is None:
            keywords_csv = Path(__file__).parent.parent / "config" / "detection_keywords.csv"
        if patterns_csv is None:
            patterns_csv = Path(__file__).parent.parent / "config" / "complex_patterns.csv"

        self.keywords = self._load_keywords(keywords_csv)
        self.patterns = self._load_patterns(patterns_csv)

        # 티어별 키워드 인덱스
        self.tier1_keywords = [k for k in self.keywords if k['tier'] == '1']
        self.tier2_keywords = [k for k in self.keywords if k['tier'] == '2']
        self.tier3_keywords = [k for k in self.keywords if k['tier'] == '3']

    def _load_keywords(self, csv_path: Path) -> List[Dict]:
        """CSV에서 키워드 로드"""
        keywords = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                keywords.append(row)
        return keywords

    def _load_patterns(self, csv_path: Path) -> List[Dict]:
        """CSV에서 복합 패턴 로드"""
        patterns = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                patterns.append(row)
        return patterns

    def _find_keyword_positions(self, text: str, keyword: str) -> List[int]:
        """텍스트에서 키워드 위치 찾기"""
        positions = []
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        start = 0

        while True:
            pos = text_lower.find(keyword_lower, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1

        return positions

    def detect_tier1(self, text: str) -> List[KeywordMatch]:
        """1차 키워드 탐지 (기술 분야)"""
        matches = []

        for kw in self.tier1_keywords:
            keyword = kw['keyword']
            positions = self._find_keyword_positions(text, keyword)

            if positions:
                matches.append(KeywordMatch(
                    keyword=keyword,
                    tier=1,
                    category=kw['category'],
                    weight=int(kw['weight']),
                    positions=positions
                ))

        return matches

    def detect_tier2(self, text: str) -> List[KeywordMatch]:
        """2차 키워드 탐지 (의심 패턴)"""
        matches = []

        for kw in self.tier2_keywords:
            keyword = kw['keyword']
            positions = self._find_keyword_positions(text, keyword)

            if positions:
                matches.append(KeywordMatch(
                    keyword=keyword,
                    tier=2,
                    category=kw['category'],
                    weight=int(kw['weight']),
                    positions=positions
                ))

        return matches

    def detect_tier3(self, text: str) -> List[KeywordMatch]:
        """3차 키워드 탐지 (위험 키워드)"""
        matches = []

        for kw in self.tier3_keywords:
            keyword = kw['keyword']
            positions = self._find_keyword_positions(text, keyword)

            if positions:
                matches.append(KeywordMatch(
                    keyword=keyword,
                    tier=3,
                    category=kw['category'],
                    weight=int(kw['weight']),
                    positions=positions
                ))

        return matches

    def detect_complex_patterns(self, text: str) -> List[PatternMatch]:
        """복합 패턴 탐지 (AND/OR 조합)"""
        matches = []
        text_lower = text.lower()

        for pattern in self.patterns:
            kw1 = pattern['keyword1']
            kw2 = pattern['keyword2']
            kw3 = pattern.get('keyword3', '')
            op1 = pattern['operator1']
            op2 = pattern.get('operator2', '')

            # 기본 2-키워드 패턴
            if kw1.lower() in text_lower and kw2.lower() in text_lower:
                if op1 == 'AND':
                    # 3-키워드 패턴 확인
                    if kw3 and op2 == 'AND':
                        if kw3.lower() in text_lower:
                            matches.append(PatternMatch(
                                pattern_id=pattern['pattern_id'],
                                pattern_name=pattern['pattern_name'],
                                keywords=[kw1, kw2, kw3],
                                weight=int(pattern['weight']),
                                description=pattern['description']
                            ))
                    else:
                        # 2-키워드 매칭
                        keywords = [kw1, kw2]
                        if kw3:
                            keywords.append(kw3)

                        matches.append(PatternMatch(
                            pattern_id=pattern['pattern_id'],
                            pattern_name=pattern['pattern_name'],
                            keywords=keywords,
                            weight=int(pattern['weight']),
                            description=pattern['description']
                        ))

        return matches

    def analyze(self, job_info: Dict) -> Dict:
        """
        채용 공고 전체 분석

        Args:
            job_info: 채용 공고 정보 딕셔너리

        Returns:
            분석 결과 딕셔너리
        """
        # 분석할 텍스트 구성
        text_parts = [
            job_info.get('title', ''),
            job_info.get('company', ''),
            job_info.get('location', ''),
            job_info.get('salary', ''),
            job_info.get('conditions', ''),
            job_info.get('recruit_summary', ''),
            job_info.get('detail', '')[:2000]  # detail은 앞부분만
        ]
        full_text = ' '.join([t for t in text_parts if t])

        # 각 티어별 탐지
        tier1_matches = self.detect_tier1(full_text)
        tier2_matches = self.detect_tier2(full_text)
        tier3_matches = self.detect_tier3(full_text)
        pattern_matches = self.detect_complex_patterns(full_text)

        # 결과 구성
        result = {
            'job_info': job_info,
            'tier1_matches': [
                {
                    'keyword': m.keyword,
                    'category': m.category,
                    'weight': m.weight,
                    'count': len(m.positions)
                }
                for m in tier1_matches
            ],
            'tier2_matches': [
                {
                    'keyword': m.keyword,
                    'category': m.category,
                    'weight': m.weight,
                    'count': len(m.positions)
                }
                for m in tier2_matches
            ],
            'tier3_matches': [
                {
                    'keyword': m.keyword,
                    'category': m.category,
                    'weight': m.weight,
                    'count': len(m.positions)
                }
                for m in tier3_matches
            ],
            'pattern_matches': [
                {
                    'pattern_id': p.pattern_id,
                    'pattern_name': p.pattern_name,
                    'keywords': p.keywords,
                    'weight': p.weight,
                    'description': p.description
                }
                for p in pattern_matches
            ],
            'total_score': self._calculate_total_score(
                tier1_matches, tier2_matches, tier3_matches, pattern_matches
            ),
            'has_tech_keyword': len(tier1_matches) > 0,
            'has_suspicious_pattern': len(tier2_matches) > 0 or len(pattern_matches) > 0,
            'has_risk_keyword': len(tier3_matches) > 0
        }

        return result

    def _calculate_total_score(
        self,
        tier1: List[KeywordMatch],
        tier2: List[KeywordMatch],
        tier3: List[KeywordMatch],
        patterns: List[PatternMatch]
    ) -> int:
        """총 위험 점수 계산"""
        score = 0

        # 티어별 점수 합산
        for match in tier1:
            score += match.weight * len(match.positions)

        for match in tier2:
            score += match.weight * len(match.positions)

        for match in tier3:
            score += match.weight * len(match.positions)

        # 복합 패턴 점수 (높은 가중치)
        for pattern in patterns:
            score += pattern.weight

        return score

    def get_matched_keywords_summary(self, analysis_result: Dict) -> str:
        """매칭된 키워드 요약 생성"""
        summary_parts = []

        # 1차 키워드
        if analysis_result['tier1_matches']:
            keywords = [m['keyword'] for m in analysis_result['tier1_matches']]
            summary_parts.append(f"기술분야: {', '.join(keywords)}")

        # 2차 키워드
        if analysis_result['tier2_matches']:
            keywords = [m['keyword'] for m in analysis_result['tier2_matches']]
            summary_parts.append(f"의심패턴: {', '.join(keywords)}")

        # 3차 키워드
        if analysis_result['tier3_matches']:
            keywords = [m['keyword'] for m in analysis_result['tier3_matches']]
            summary_parts.append(f"위험키워드: {', '.join(keywords)}")

        # 복합 패턴
        if analysis_result['pattern_matches']:
            patterns = [p['pattern_name'] for p in analysis_result['pattern_matches']]
            summary_parts.append(f"복합패턴: {', '.join(patterns)}")

        return " | ".join(summary_parts) if summary_parts else "매칭 없음"


if __name__ == "__main__":
    # 테스트
    detector = KeywordDetector()

    # 테스트 채용 공고
    test_job = {
        "title": "반도체 공정 엔지니어 (중국 상하이 근무)",
        "company": "글로벌 R&D 센터",
        "location": "중국 상하이",
        "salary": "협의",
        "conditions": "삼성전자 경력 5년 이상, 중국어 필수",
        "recruit_summary": "해외 기술이전 프로젝트 참여, 파견 근무",
        "detail": "OLED 디스플레이 기술 지원 및 현지화 작업"
    }

    result = detector.analyze(test_job)
    print("=== 키워드 탐지 결과 ===")
    print(f"총 위험 점수: {result['total_score']}")
    print(f"\n1차 키워드 (기술): {len(result['tier1_matches'])}개")
    for m in result['tier1_matches']:
        print(f"  - {m['keyword']} (가중치: {m['weight']}, 출현: {m['count']}회)")

    print(f"\n2차 키워드 (의심): {len(result['tier2_matches'])}개")
    for m in result['tier2_matches']:
        print(f"  - {m['keyword']} (가중치: {m['weight']}, 출현: {m['count']}회)")

    print(f"\n3차 키워드 (위험): {len(result['tier3_matches'])}개")
    for m in result['tier3_matches']:
        print(f"  - {m['keyword']} (가중치: {m['weight']}, 출현: {m['count']}회)")

    print(f"\n복합 패턴: {len(result['pattern_matches'])}개")
    for p in result['pattern_matches']:
        print(f"  - {p['pattern_name']}: {' + '.join(p['keywords'])} (가중치: {p['weight']})")

    print(f"\n요약: {detector.get_matched_keywords_summary(result)}")
