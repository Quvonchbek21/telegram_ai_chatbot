import httpx
import asyncio
from bs4 import BeautifulSoup
from dataclasses import dataclass

BASE_URL = "https://www.uzdaily.uz"

# ❌ MUAMMO 1: Eski headers — server 403 qaytaradi
# ❌ MUAMMO 2: /search endpoint — Cloudflare tomonidan bloklangan
# ❌ MUAMMO 3: Cookie yo'q — sessiya tekshiruvi o'tkazilmaydi
# ✅ YECHIM: To'liq browser headers + cookie + bosh sahifadan qidirish

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "uz,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


@dataclass
class Article:
    title: str
    url: str
    text: str

    def to_text(self) -> str:
        return f"📰 {self.title}\n🔗 {self.url}\n\n{self.text[:1500]}"


async def _fetch_article(client: httpx.AsyncClient, url: str) -> "Article | None":
    """Bitta maqolani o'qish"""
    try:
        # ✅ Referer qo'shildi — sayt bu havoladan kelganini ko'radi
        headers = {**HEADERS, "Referer": BASE_URL + "/uz/"}
        resp = await client.get(url, headers=headers, timeout=12)

        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "lxml")

        title = ""
        for sel in ["h1.article-title", "h1.post-title", "h1.title", "h1"]:
            tag = soup.select_one(sel)
            if tag:
                title = tag.get_text(strip=True)
                break

        body = ""
        for sel in ["div.article-body", "div.post-body", "div.content-text",
                    "div.content", "div.text", "article"]:
            tag = soup.select_one(sel)
            if tag:
                for el in tag.select("script, style, aside, nav, .ads"):
                    el.decompose()
                body = tag.get_text(separator="\n", strip=True)
                break

        if not title:
            return None

        return Article(title=title, url=url, text=body)

    except Exception:
        return None


async def search_uzdaily(query: str, max_results: int = 3) -> list[Article]:
    """Uzdaily.uz da qidirish"""

    # ✅ cookie_jar — avtomatik cookie saqlash
    async with httpx.AsyncClient(
        headers=HEADERS,
        follow_redirects=True,
        timeout=15.0,
    ) as client:

        # ✅ QADAM 1: Avval bosh sahifaga kirib cookie olish
        try:
            await client.get(BASE_URL + "/uz/", timeout=10)
            await asyncio.sleep(0.5)  # Tabiiy kutish
        except Exception:
            pass

        # ✅ QADAM 2: Qidiruv so'rovi (endi cookie bor)
        try:
            search_headers = {**HEADERS, "Referer": BASE_URL + "/uz/"}
            resp = await client.get(
                f"{BASE_URL}/uz/search",
                params={"q": query},
                headers=search_headers,
                timeout=12,
            )
        except Exception:
            return []

        # ✅ 403 bo'lsa — bosh sahifadan qidiramiz
        if resp.status_code == 403:
            return await _search_from_homepage(client, query, max_results)

        soup = BeautifulSoup(resp.text, "lxml")
        links = _extract_links(soup)

        if not links:
            # ✅ Natija yo'q — bosh sahifadan qidiramiz
            return await _search_from_homepage(client, query, max_results)

        # QADAM 3: Maqolalarni parallel o'qish
        tasks = [_fetch_article(client, url) for url in links[:max_results]]
        results = await asyncio.gather(*tasks)
        return [a for a in results if a]


async def _search_from_homepage(
    client: httpx.AsyncClient, query: str, max_results: int
) -> list[Article]:
    """
    ✅ Zaxira usul: bosh sahifa + kategoriya sahifalaridan
    so'nggi yangiliklar olinadi va query bo'yicha filtrlanadi.
    """
    pages_to_check = [
        f"{BASE_URL}/uz/",
        f"{BASE_URL}/uz/category/economy",
        f"{BASE_URL}/uz/category/politics",
        f"{BASE_URL}/uz/category/society",
    ]

    all_links: list[str] = []
    seen: set[str] = set()

    for page_url in pages_to_check:
        try:
            resp = await client.get(page_url, timeout=10)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "lxml")
            for link in _extract_links(soup):
                if link not in seen:
                    all_links.append(link)
                    seen.add(link)
        except Exception:
            continue

    if not all_links:
        return []

    # So'nggi 20 ta maqolani o'qib, query bo'yicha filtrlaymiz
    tasks = [_fetch_article(client, url) for url in all_links[:20]]
    all_articles = await asyncio.gather(*tasks)

    query_lower = query.lower()
    matched = [
        a for a in all_articles
        if a and (
            query_lower in a.title.lower()
            or query_lower in a.text.lower()
        )
    ]

    # Mos kelganlar bo'lmasa — so'nggi maqolalarni qaytaramiz
    result = matched if matched else [a for a in all_articles if a]
    return result[:max_results]


def _extract_links(soup: BeautifulSoup) -> list[str]:
    """Sahifadan maqola havolalarini chiqarish"""
    links = []
    seen: set[str] = set()

    keywords = ["/post/", "/article/", "/news/", "/uz/"]

    for tag in soup.find_all("a", href=True):
        href: str = tag["href"]

        # Faqat maqola ko'rinishdagi havolalar
        if not any(k in href for k in keywords):
            continue
        # Navigatsiya havolalarini o'tkazib yuborish
        if href.rstrip("/") in ["", "/uz", "/ru", "/en"]:
            continue
        if href in seen:
            continue

        full_url = href if href.startswith("http") else BASE_URL + href
        links.append(full_url)
        seen.add(href)

    return links
