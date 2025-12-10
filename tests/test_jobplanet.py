"""
잡플래닛 사이트 구조 분석 테스트
"""
from playwright.sync_api import sync_playwright
import time

def analyze_jobplanet():
    """잡플래닛 사이트 구조 분석"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        # 검색 페이지로 이동
        print("🔍 잡플래닛 검색 페이지 접속 중...")
        page.goto("https://www.jobplanet.co.kr/job/search?keyword=반도체", timeout=60000)
        time.sleep(5)

        # 페이지 구조 분석
        print("\n📊 페이지 구조 분석 중...")

        analysis = page.evaluate("""
            () => {
                const result = {
                    jobItems: [],
                    selectors: {},
                    linkPatterns: []
                };

                // 공고 아이템 찾기 (다양한 패턴 시도)
                const possibleSelectors = [
                    'article', 'div[class*="job"]', 'div[class*="item"]',
                    'li[class*="job"]', 'div[class*="card"]', 'a[href*="/job/"]',
                    'div[class*="list"] > div', 'ul[class*="list"] > li'
                ];

                for (const selector of possibleSelectors) {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        result.selectors[selector] = elements.length;
                    }
                }

                // 공고 링크 패턴 찾기
                const allLinks = document.querySelectorAll('a[href*="/job/"]');
                allLinks.forEach(link => {
                    const href = link.getAttribute('href');
                    if (href && !result.linkPatterns.includes(href)) {
                        result.linkPatterns.push(href);

                        // 링크 정보 수집
                        const jobInfo = {
                            href: href,
                            text: link.innerText.trim().substring(0, 100),
                            class: link.className
                        };

                        if (result.jobItems.length < 5) {
                            result.jobItems.push(jobInfo);
                        }
                    }
                });

                // 페이지 타이틀과 메타 정보
                result.pageTitle = document.title;
                result.totalLinks = allLinks.length;

                return result;
            }
        """)

        print(f"\n✅ 페이지 제목: {analysis['pageTitle']}")
        print(f"✅ 총 링크 수: {analysis['totalLinks']}")

        print("\n📌 발견된 셀렉터:")
        for selector, count in analysis['selectors'].items():
            print(f"  - {selector}: {count}개")

        print("\n🔗 공고 링크 패턴 (첫 5개):")
        for item in analysis['jobItems'][:5]:
            print(f"\n  href: {item['href']}")
            print(f"  text: {item['text'][:50]}...")
            print(f"  class: {item['class']}")

        print("\n⏸️  브라우저를 열어둡니다. 직접 확인 후 Enter를 누르세요...")
        input()

        browser.close()

if __name__ == "__main__":
    analyze_jobplanet()
