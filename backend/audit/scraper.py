import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


def scrape_metrics(url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    parsed_base = urlparse(url)

    # --- Word count (visible text only) ---
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    visible_text = soup.get_text(separator=" ")
    words = [w for w in visible_text.split() if w.strip()]
    word_count = len(words)

    # --- Headings ---
    h1_count = len(soup.find_all("h1"))
    h2_count = len(soup.find_all("h2"))
    h3_count = len(soup.find_all("h3"))

    # --- CTAs (buttons + links with CTA-like text) ---
    cta_keywords = {"get started", "contact", "learn more", "sign up", "request",
                    "schedule", "download", "try", "buy", "book", "demo", "start"}
    buttons = soup.find_all("button")
    cta_links = [
        a for a in soup.find_all("a")
        if any(kw in (a.get_text(strip=True).lower()) for kw in cta_keywords)
    ]
    cta_count = len(buttons) + len(cta_links)

    # --- Internal vs external links ---
    internal_links = 0
    external_links = 0
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full = urljoin(url, href)
        parsed = urlparse(full)
        if parsed.netloc == parsed_base.netloc:
            internal_links += 1
        elif parsed.scheme in ("http", "https"):
            external_links += 1

    # --- Images ---
    images = soup.find_all("img")
    image_count = len(images)
    images_missing_alt = sum(
        1 for img in images
        if not img.get("alt") or img["alt"].strip() == ""
    )

    # --- Meta tags ---
    meta_title_tag = soup.find("title")
    meta_title = meta_title_tag.get_text(strip=True) if meta_title_tag else ""

    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else ""

    # --- Page text for AI context (capped at 3000 words) ---
    page_text_preview = " ".join(words[:3000])

    return {
        "word_count": word_count,
        "h1_count": h1_count,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "cta_count": cta_count,
        "internal_links": internal_links,
        "external_links": external_links,
        "image_count": image_count,
        "images_missing_alt": images_missing_alt,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "page_text_preview": page_text_preview,
    }