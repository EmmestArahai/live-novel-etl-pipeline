import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import time

TEST_SLUGS = [
    "after-the-breakup-i-went-viral-in-the-entertainment-circle",
    "i-am-a-good-man",
]

async def fetch_page_playwright(url):
    """Dùng Playwright để vượt qua Cloudflare"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # ⭐ Thêm dòng này: chờ trang có title khác "Just a moment"
            # (nghĩa là Cloudflare challenge đã pass)
            await page.wait_for_function(
                'document.title !== "Just a moment..."',
                timeout=30000
            )
            
            # Chờ thêm 2 giây để JS trang render hoàn toàn
            await page.wait_for_timeout(2000)
            
            html = await page.content()
            return html
        finally:
            await browser.close()


def parse_novel_page(html):
    soup = BeautifulSoup(html, "lxml")
    data = {}

    # --- Title ---
    title_tag = soup.select_one("h1.seriestitle")
    data["title"] = title_tag.get_text(strip=True) if title_tag else None

    # --- Rating ---
    # Thường nằm trong một span hoặc div có text "(X.X / 5.0, Y votes)"
    rating_span = soup.select_one("span#span_ratings_text")
    if rating_span:
        data["rating_raw"] = rating_span.get_text(strip=True)
    else:
        # Fallback: tìm text chứa "/ 5.0"
        for tag in soup.find_all(string=lambda s: s and "/ 5.0" in str(s)):
            data["rating_raw"] = str(tag).strip()
            break
        if "rating_raw" not in data:
            data["rating_raw"] = None

    # --- Status / Chapters ---
    # Thường trong một div info
    status_tag = soup.select_one("span#editstatus")
    if status_tag:
        data["status_raw"] = status_tag.get_text(strip=True)
    else:
        data["status_raw"] = None

    # Debug: in tất cả text để ta xem structure
    data["html_snippet"] = html[:2000]  # 2000 char đầu để xem structure

    return data


async def main():
    for slug in TEST_SLUGS:
        url = f"https://www.novelupdates.com/series/{slug}/"
        print(f"\n=== Crawling: {url} ===")

        html = await fetch_page_playwright(url)
        print(f"HTML length: {len(html)} bytes")

        data = parse_novel_page(html)
        print("Title:", data.get("title"))
        print("Rating:", data.get("rating_raw"))
        print("Status:", data.get("status_raw"))
        print("\nHTML snippet (2000 chars):")
        print(data["html_snippet"][:1000])

        # Lưu HTML đầy đủ để debug
        debug_file = f"debug_{slug[:30]}.html"
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"-> Đã lưu HTML vào {debug_file}")

        time.sleep(2)  # Delay giữa các request


if __name__ == "__main__":
    asyncio.run(main())