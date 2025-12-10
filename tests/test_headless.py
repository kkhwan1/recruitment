"""
사람인 크롤러 Headless 모드 테스트 스크립트

이 스크립트는 headless 모드와 headed 모드의 동작을 비교 테스트합니다.
"""
import time
from crawler import SaraminCrawler


def test_mode(headless: bool, keyword: str = "데이터분석", max_jobs: int = 3) -> dict:
    """
    특정 모드로 크롤러를 테스트합니다.

    Args:
        headless: True면 headless 모드, False면 headed 모드
        keyword: 검색 키워드
        max_jobs: 최대 수집 공고 수

    Returns:
        테스트 결과 딕셔너리
    """
    mode_name = "HEADLESS" if headless else "HEADED"
    print(f"\n{'='*60}")
    print(f"Testing {mode_name} mode...")
    print(f"{'='*60}")

    crawler = SaraminCrawler(headless=headless)
    result = {
        "mode": mode_name,
        "success": False,
        "jobs_count": 0,
        "elapsed_time": 0,
        "error": None
    }

    try:
        start_time = time.time()

        # 크롤러 시작
        crawler.start()
        print(f"✓ Browser started")

        # 공고 수집
        jobs = crawler.crawl(keyword, max_jobs=max_jobs)

        # 결과 기록
        result["elapsed_time"] = time.time() - start_time
        result["jobs_count"] = len(jobs)
        result["success"] = len(jobs) > 0

        # 결과 출력
        print(f"\n{'─'*60}")
        print(f"RESULTS:")
        print(f"  Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        print(f"  Jobs collected: {result['jobs_count']}/{max_jobs}")
        print(f"  Time elapsed: {result['elapsed_time']:.1f}s")

        if jobs:
            print(f"\n  Collected jobs:")
            for i, job in enumerate(jobs, 1):
                title = job['title'][:50] + "..." if len(job['title']) > 50 else job['title']
                print(f"    {i}. {title}")
                print(f"       Company: {job.get('company', 'N/A')}")

        return result

    except Exception as e:
        result["error"] = str(e)
        print(f"\n❌ ERROR: {e}")
        return result

    finally:
        crawler.close()
        print(f"✓ Browser closed")


def compare_modes(keyword: str = "데이터분석", max_jobs: int = 5):
    """
    Headless와 Headed 모드를 비교 테스트합니다.

    Args:
        keyword: 검색 키워드
        max_jobs: 최대 수집 공고 수
    """
    print("\n" + "="*60)
    print("SARAMIN CRAWLER - HEADLESS vs HEADED COMPARISON TEST")
    print("="*60)
    print(f"Keyword: {keyword}")
    print(f"Max jobs: {max_jobs}")

    # Test headless mode
    result_headless = test_mode(headless=True, keyword=keyword, max_jobs=max_jobs)

    # Test headed mode
    result_headed = test_mode(headless=False, keyword=keyword, max_jobs=max_jobs)

    # Print comparison
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)

    print(f"\nHeadless Mode:")
    print(f"  Status: {'✅ PASS' if result_headless['success'] else '❌ FAIL'}")
    print(f"  Jobs: {result_headless['jobs_count']}/{max_jobs}")
    print(f"  Time: {result_headless['elapsed_time']:.1f}s")
    if result_headless['error']:
        print(f"  Error: {result_headless['error']}")

    print(f"\nHeaded Mode:")
    print(f"  Status: {'✅ PASS' if result_headed['success'] else '❌ FAIL'}")
    print(f"  Jobs: {result_headed['jobs_count']}/{max_jobs}")
    print(f"  Time: {result_headed['elapsed_time']:.1f}s")
    if result_headed['error']:
        print(f"  Error: {result_headed['error']}")

    # Performance comparison
    if result_headless['success'] and result_headed['success']:
        time_diff = result_headed['elapsed_time'] - result_headless['elapsed_time']
        speed_improvement = (time_diff / result_headed['elapsed_time']) * 100

        print(f"\nPerformance:")
        print(f"  Time difference: {abs(time_diff):.1f}s")
        if time_diff > 0:
            print(f"  Headless is {speed_improvement:.1f}% faster")
        else:
            print(f"  Headed is {abs(speed_improvement):.1f}% faster")

    # Overall status
    print("\n" + "="*60)
    both_pass = result_headless['success'] and result_headed['success']
    print(f"Overall: {'✅ ALL TESTS PASSED' if both_pass else '❌ SOME TESTS FAILED'}")
    print("="*60 + "\n")

    return {
        "headless": result_headless,
        "headed": result_headed,
        "all_passed": both_pass
    }


if __name__ == "__main__":
    # Run comparison test
    results = compare_modes(keyword="반도체", max_jobs=3)

    # Exit with appropriate code
    exit(0 if results["all_passed"] else 1)
