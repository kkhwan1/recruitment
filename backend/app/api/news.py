"""
뉴스 API 엔드포인트
기술 유출 관련 뉴스 제공 (MVP: 하드코딩된 샘플 데이터)
"""
from fastapi import APIRouter
from typing import List, Dict, Any
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/news")
def get_news(limit: int = 10) -> List[Dict[str, Any]]:
    """
    기술 유출 관련 뉴스 조회

    Args:
        limit: 조회할 뉴스 개수 (기본값: 10)

    Returns:
        [{
            "id": int,
            "title": str,
            "summary": str,
            "url": str,
            "source": str,
            "published_at": str,
            "category": str,
            "thumbnail": str (optional)
        }]
    """
    # MVP: 하드코딩된 샘플 데이터
    # TODO: 실제 뉴스 API 연동 (네이버 뉴스 API, Google News API 등)

    base_date = datetime.now()

    sample_news = [
        {
            "id": 1,
            "title": "중국 기업, 한국 반도체 기술자 스카우트 시도 적발",
            "summary": "중국 소재 반도체 기업이 한국 대기업 출신 엔지니어를 대상으로 고액 연봉을 제시하며 기술 유출을 시도한 정황이 포착됐다.",
            "url": "#",
            "source": "전자신문",
            "published_at": (base_date - timedelta(hours=2)).isoformat(),
            "category": "반도체",
            "thumbnail": None
        },
        {
            "id": 2,
            "title": "디스플레이 핵심 기술 해외 유출 방지 대책 마련",
            "summary": "정부가 OLED 등 디스플레이 핵심 기술의 해외 유출을 막기 위한 종합 대책을 발표했다. 특히 퇴직자 관리 강화에 집중한다.",
            "url": "#",
            "source": "아시아경제",
            "published_at": (base_date - timedelta(hours=5)).isoformat(),
            "category": "디스플레이",
            "thumbnail": None
        },
        {
            "id": 3,
            "title": "이차전지 기술 유출 사건, 전직 연구원 구속",
            "summary": "국내 이차전지 기업의 핵심 기술을 중국 기업에 넘긴 혐의로 전직 연구원이 구속됐다. 피해 규모는 수천억원으로 추정된다.",
            "url": "#",
            "source": "한국경제",
            "published_at": (base_date - timedelta(hours=8)).isoformat(),
            "category": "이차전지",
            "thumbnail": None
        },
        {
            "id": 4,
            "title": "AI 기술 해외 유출 급증... 정부 대응 나서",
            "summary": "인공지능 분야의 핵심 기술이 해외로 유출되는 사례가 급증하고 있어 정부가 긴급 대책 마련에 나섰다.",
            "url": "#",
            "source": "ZDNet Korea",
            "published_at": (base_date - timedelta(days=1)).isoformat(),
            "category": "AI",
            "thumbnail": None
        },
        {
            "id": 5,
            "title": "국가 핵심기술 지정 확대... 반도체·바이오 포함",
            "summary": "정부가 국가 핵심기술 지정을 확대하며 반도체, 바이오 등 첨단 산업 기술 보호에 나선다.",
            "url": "#",
            "source": "매일경제",
            "published_at": (base_date - timedelta(days=1, hours=3)).isoformat(),
            "category": "정책",
            "thumbnail": None
        },
        {
            "id": 6,
            "title": "중국 헤드헌터, 한국 기술자 대상 '밀접촉' 활발",
            "summary": "중국 헤드헌터들이 한국 기술자들을 대상으로 고액 연봉을 제시하며 적극적인 스카우트를 벌이고 있는 것으로 파악됐다.",
            "url": "#",
            "source": "서울경제",
            "published_at": (base_date - timedelta(days=2)).isoformat(),
            "category": "인력",
            "thumbnail": None
        },
        {
            "id": 7,
            "title": "퇴직자 기술 유출 방지 법안 통과",
            "summary": "퇴직 후 일정 기간 경쟁사 취업을 제한하는 내용의 법안이 국회를 통과했다. 핵심 기술 보호가 목적이다.",
            "url": "#",
            "source": "연합뉴스",
            "published_at": (base_date - timedelta(days=2, hours=5)).isoformat(),
            "category": "정책",
            "thumbnail": None
        },
        {
            "id": 8,
            "title": "반도체 장비 기술 유출 시도 적발... 3명 입건",
            "summary": "국내 반도체 장비 제조사의 핵심 기술을 해외로 유출하려던 전직 직원 등 3명이 검찰에 입건됐다.",
            "url": "#",
            "source": "뉴시스",
            "published_at": (base_date - timedelta(days=3)).isoformat(),
            "category": "반도체",
            "thumbnail": None
        },
        {
            "id": 9,
            "title": "바이오 신약 개발 정보 해외 유출 의혹",
            "summary": "국내 바이오 기업의 신약 개발 정보가 해외로 유출됐을 가능성이 제기되며 조사가 진행 중이다.",
            "url": "#",
            "source": "팜뉴스",
            "published_at": (base_date - timedelta(days=3, hours=7)).isoformat(),
            "category": "바이오",
            "thumbnail": None
        },
        {
            "id": 10,
            "title": "기술 유출 방지 시스템 도입 기업 늘어",
            "summary": "최근 기술 유출 사건이 잇따르면서 기업들이 내부 정보 보안 시스템 도입에 적극 나서고 있다.",
            "url": "#",
            "source": "IT조선",
            "published_at": (base_date - timedelta(days=4)).isoformat(),
            "category": "보안",
            "thumbnail": None
        }
    ]

    return sample_news[:limit]
