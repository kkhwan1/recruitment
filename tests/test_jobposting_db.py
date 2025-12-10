"""
잡포스팅 크롤러 데이터베이스 저장 테스트
"""
import json
from database.repositories import JobRepository

# 리포지토리 생성
job_repo = JobRepository()

# JSON 파일 로드
json_file = 'data/json_results/jobposting_반도체_20251120_193746.json'

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== 데이터베이스 저장 시작 ===')
print(f'사이트: {data["site"]}')
print(f'키워드: {data["keyword"]}')
print(f'총 공고 수: {len(data["jobs"])}')

# 각 공고를 데이터베이스에 저장
inserted = 0
duplicates = 0
errors = 0

for job in data['jobs']:
    try:
        # source_site와 search_keyword 추가
        job['source_site'] = data['site']
        job['search_keyword'] = data['keyword']

        # 데이터베이스에 저장
        job_id = job_repo.insert_job(job)
        if job_id:
            inserted += 1
            print(f'✓ 저장 완료: {job["title"]} (ID: {job_id})')
        else:
            duplicates += 1
            print(f'⊘ 중복 스킵: {job["title"]}')
    except Exception as e:
        errors += 1
        print(f'✗ 오류: {job["title"]} - {e}')

print('\n=== 저장 결과 ===')
print(f'신규 저장: {inserted}개')
print(f'중복 스킵: {duplicates}개')
print(f'오류: {errors}개')

# 저장된 데이터 확인
print('\n=== 저장된 데이터 확인 ===')
with job_repo.db as conn:
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, source_site, title, company, location, salary
        FROM jobs
        WHERE source_site = ?
        ORDER BY crawled_at DESC
        LIMIT 5
    ''', ('잡포스팅',))

    for row in cursor.fetchall():
        print(f'\nID: {row[0]}')
        print(f'사이트: {row[1]}')
        print(f'제목: {row[2]}')
        print(f'회사: {row[3]}')
        print(f'위치: {row[4]}')
        print(f'급여: {row[5]}')

    cursor.close()
