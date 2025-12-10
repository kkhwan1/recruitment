"""
하이브레인넷 향상된 Bot Detection 우회 테스트
"""
import time
from playwright.sync_api import sync_playwright

def test_enhanced_bypass():
    with sync_playwright() as p:
        # Enhanced browser launch args
        browser = p.chromium.launch(
            headless=False,  # Start with visible for debugging
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials'
            ]
        )

        # Enhanced context with more realistic browser fingerprint
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={"width": 1920, "height": 1080},
            locale='ko-KR',
            timezone_id='Asia/Seoul',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            }
        )

        page = context.new_page()

        # Enhanced stealth scripts
        page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Add more realistic properties
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['ko-KR', 'ko', 'en-US', 'en']
            });

            // Spoof Chrome runtime
            window.chrome = {
                runtime: {}
            };

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        # Visit main page first (may help with cookies/session)
        print("단계 1: 메인 페이지 방문...")
        page.goto("https://www.hibrain.net", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        print(f"✓ 메인 페이지 응답: {page.title()}")

        # Now visit search page
        search_url = "https://www.hibrain.net/recruit/List.asp?strSrchWord=반도체"
        print(f"\n단계 2: 검색 페이지 방문...")
        print(f"URL: {search_url}")

        page.goto(search_url, wait_until="domcontentloaded", timeout=60000)

        # Wait for stabilization
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
            print("✓ 네트워크 안정화")
        except:
            print("⚠ 네트워크 idle 타임아웃")

        time.sleep(3)

        # Check response
        page_title = page.title()
        print(f"\n페이지 제목: {page_title}")

        # Get page content
        content = page.content()

        if "403" in content or "ERROR" in content:
            print("\n❌ 여전히 403 에러 발생")
            print("첫 500자:")
            print(content[:500])
        else:
            print("\n✓ 성공적으로 페이지 로드됨!")

            # Analyze structure
            analysis = page.evaluate("""
                () => {
                    return {
                        item_count: document.querySelectorAll('.item_recruit').length,
                        tr_count: document.querySelectorAll('tr').length,
                        table_count: document.querySelectorAll('table').length,
                        link_count: document.querySelectorAll('a[href]').length,
                        sample_links: Array.from(document.querySelectorAll('a[href]'))
                            .slice(0, 10)
                            .map(a => ({ href: a.href, text: a.innerText.trim().substring(0, 30) }))
                    };
                }
            """)

            print(f"\n구조 분석:")
            print(f"  - .item_recruit: {analysis['item_count']}개")
            print(f"  - TR 요소: {analysis['tr_count']}개")
            print(f"  - TABLE 요소: {analysis['table_count']}개")
            print(f"  - 링크: {analysis['link_count']}개")

            print(f"\n샘플 링크:")
            for i, link in enumerate(analysis['sample_links'], 1):
                print(f"  {i}. {link['href']}")
                if link['text']:
                    print(f"     {link['text']}")

        # Take screenshot
        try:
            page.screenshot(path="hibrain_enhanced_test.png", full_page=False)
            print("\n✓ 스크린샷 저장: hibrain_enhanced_test.png")
        except:
            print("\n⚠ 스크린샷 저장 실패")

        print("\n테스트 완료. 브라우저를 5초 후 종료합니다...")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    test_enhanced_bypass()
