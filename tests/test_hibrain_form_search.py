"""
하이브레인넷 검색 폼 사용 테스트 (직접 URL 대신 폼 제출)
"""
import time
from playwright.sync_api import sync_playwright

def test_form_search():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )

        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={"width": 1920, "height": 1080},
            locale='ko-KR',
            timezone_id='Asia/Seoul'
        )

        page = context.new_page()

        # Stealth mode
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ko-KR', 'ko']
            });
        """)

        # Step 1: Visit main page
        print("단계 1: 메인 페이지 방문...")
        page.goto("https://www.hibrain.net", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        print(f"✓ 메인 페이지: {page.title()}")

        # Step 2: Navigate to recruit section
        print("\n단계 2: 채용정보 섹션으로 이동...")
        try:
            # Try to find and click recruit menu
            recruit_link = page.locator('a[href*="recruit"]').first
            if recruit_link.is_visible(timeout=5000):
                recruit_link.click()
                time.sleep(2)
                print(f"✓ 채용정보 페이지: {page.title()}")
        except:
            # Or navigate directly
            print("  메뉴 클릭 실패, 직접 이동...")
            page.goto("https://www.hibrain.net/recruit/", wait_until="domcontentloaded", timeout=60000)
            time.sleep(2)

        # Step 3: Use search form
        print("\n단계 3: 검색 폼 사용...")
        try:
            # Find search input
            search_input = page.locator('input[name="strSrchWord"]').first
            if search_input.is_visible(timeout=5000):
                print("  검색창 발견!")
                search_input.fill("반도체")
                time.sleep(1)

                # Click search button
                search_btn = page.locator('button[type="submit"], input[type="submit"]').first
                search_btn.click()

                print("  ✓ 검색 버튼 클릭")
                time.sleep(3)

                # Check result
                page_title = page.title()
                print(f"\n검색 결과 페이지: {page_title}")

                if "403" in page.content() or "ERROR" in page.content():
                    print("❌ 여전히 403 에러")
                else:
                    print("✓ 검색 성공!")

                    # Analyze
                    analysis = page.evaluate("""
                        () => {
                            const items = document.querySelectorAll('.item_recruit, tr[onclick], table tr');
                            return {
                                item_count: document.querySelectorAll('.item_recruit').length,
                                tr_count: document.querySelectorAll('tr').length,
                                table_count: document.querySelectorAll('table').length,
                                sample_text: document.body.innerText.substring(0, 500)
                            };
                        }
                    """)

                    print(f"\n결과:")
                    print(f"  - .item_recruit: {analysis['item_count']}개")
                    print(f"  - TR: {analysis['tr_count']}개")
                    print(f"  - TABLE: {analysis['table_count']}개")
                    print(f"\n페이지 샘플:\n{analysis['sample_text']}")

        except Exception as e:
            print(f"❌ 검색 폼 사용 실패: {e}")

        # Screenshot
        try:
            page.screenshot(path="hibrain_form_search.png")
            print("\n✓ 스크린샷 저장")
        except:
            pass

        print("\n5초 후 종료...")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    test_form_search()
