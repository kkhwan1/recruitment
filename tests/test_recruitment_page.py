"""
하이브레인넷 /recruitment 페이지 탐색 (React SPA)
"""
import time
import json
from playwright.sync_api import sync_playwright

def test_recruitment_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )

        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={"width": 1920, "height": 1080}
        )

        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

        # Visit recruitment page (React SPA)
        url = "https://www.hibrain.net/recruitment"
        print(f"채용정보 페이지 방문: {url}")

        # Hierarchical wait strategy for React SPA
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        print("✓ DOM 로드 완료")

        # Try network idle (may timeout, that's ok for SPAs)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
            print("✓ 네트워크 안정화")
        except:
            print("⚠ 네트워크 idle 타임아웃 (정상 - React SPA)")

        # Wait for React to render - try different selectors
        print("\nReact 렌더링 대기 중...")
        react_selectors = [
            '.item_recruit',
            'div[class*="recruit"]',
            'div[class*="job"]',
            'article',
            'div[data-react]',
            '#root',
            '.list',
            '.card'
        ]

        rendered = False
        for selector in react_selectors:
            try:
                page.wait_for_selector(selector, timeout=5000, state="visible")
                print(f"✓ React 요소 발견: {selector}")
                rendered = True
                break
            except:
                print(f"  시도: {selector} (없음)")

        # Final stabilization wait
        time.sleep(3)
        print("\n페이지 안정화 완료\n")

        # Analyze React structure
        analysis = page.evaluate("""
            () => {
                const result = {
                    title: document.title,
                    root_element: '',
                    react_root: '',
                    job_items: [],
                    search_form: null,
                    api_calls: [],
                    structure: {
                        divs_with_classes: 0,
                        articles: 0,
                        links: 0
                    }
                };

                // Check for React root
                const root = document.getElementById('root') || document.querySelector('[data-react]') || document.querySelector('[data-reactroot]');
                if (root) {
                    result.root_element = root.tagName;
                    result.react_root = root.innerHTML.substring(0, 500);
                }

                // Find job-like elements
                const jobPatterns = [
                    '.item_recruit',
                    '[class*="recruit"]',
                    '[class*="job"]',
                    '[class*="card"]',
                    'article',
                    '[class*="list-item"]',
                    '[data-id]'
                ];

                for (const pattern of jobPatterns) {
                    const elements = document.querySelectorAll(pattern);
                    if (elements.length > 0) {
                        elements.forEach((el, idx) => {
                            if (idx < 10) {  // First 10 only
                                const text = el.innerText.trim().substring(0, 100);
                                const classes = el.className;
                                const href = el.querySelector('a')?.href || '';
                                if (text) {
                                    result.job_items.push({
                                        pattern,
                                        classes,
                                        text,
                                        href
                                    });
                                }
                            }
                        });
                    }
                }

                // Find search form
                const searchInputs = document.querySelectorAll('input[type="text"], input[type="search"], input[name*="search"], input[name*="keyword"]');
                if (searchInputs.length > 0) {
                    const input = searchInputs[0];
                    result.search_form = {
                        name: input.name,
                        id: input.id,
                        placeholder: input.placeholder,
                        type: input.type
                    };
                }

                // Get all links
                result.structure.links = document.querySelectorAll('a[href]').length;
                result.structure.divs_with_classes = document.querySelectorAll('div[class]').length;
                result.structure.articles = document.querySelectorAll('article').length;

                return result;
            }
        """)

        # Print results
        print("=" * 80)
        print("React SPA 구조 분석 결과")
        print("=" * 80)

        print(f"\n페이지 제목: {analysis['title']}")
        print(f"React Root 요소: {analysis['root_element']}")

        if analysis['search_form']:
            print(f"\n검색 폼 발견:")
            print(f"  - 이름: {analysis['search_form']['name']}")
            print(f"  - ID: {analysis['search_form']['id']}")
            print(f"  - Placeholder: {analysis['search_form']['placeholder']}")

        print(f"\n페이지 구조:")
        print(f"  - DIV (with classes): {analysis['structure']['divs_with_classes']}개")
        print(f"  - Article 요소: {analysis['structure']['articles']}개")
        print(f"  - 링크: {analysis['structure']['links']}개")

        print(f"\n채용 아이템 발견: {len(analysis['job_items'])}개")
        for i, item in enumerate(analysis['job_items'][:5], 1):
            print(f"\n  {i}. [패턴: {item['pattern']}]")
            print(f"     클래스: {item['classes']}")
            print(f"     텍스트: {item['text']}")
            if item['href']:
                print(f"     링크: {item['href']}")

        # Save page content for inspection
        with open("hibrain_recruitment_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"\n✓ HTML 저장: hibrain_recruitment_page.html")

        # Save analysis as JSON
        with open("hibrain_recruitment_analysis.json", "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"✓ 분석 결과 저장: hibrain_recruitment_analysis.json")

        # Screenshot
        try:
            page.screenshot(path="hibrain_recruitment_page.png", full_page=True)
            print(f"✓ 스크린샷 저장: hibrain_recruitment_page.png")
        except:
            print("⚠ 스크린샷 저장 실패")

        print("\n10초 후 종료 (수동 확인 시간)...")
        time.sleep(10)
        browser.close()

if __name__ == "__main__":
    test_recruitment_page()
