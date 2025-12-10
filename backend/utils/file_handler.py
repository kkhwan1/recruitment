"""
파일 처리 유틸리티
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def save_json(data: dict, filename: str, directory: str = "data/json_results") -> Path:
    """
    JSON 데이터를 파일로 저장

    Args:
        data: 저장할 데이터
        filename: 파일명
        directory: 저장 디렉토리

    Returns:
        저장된 파일 경로
    """
    # 디렉토리 생성
    save_dir = Path(directory)
    save_dir.mkdir(parents=True, exist_ok=True)

    # 파일 경로
    filepath = save_dir / filename

    # JSON 저장
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath


def create_job_data(site: str, keyword: str, jobs: List[Dict]) -> dict:
    """
    공고 데이터 구조 생성

    Args:
        site: 사이트명
        keyword: 검색 키워드
        jobs: 공고 리스트

    Returns:
        구조화된 공고 데이터
    """
    return {
        "site": site,
        "keyword": keyword,
        "collected_at": datetime.now().isoformat(),
        "jobs": jobs
    }
