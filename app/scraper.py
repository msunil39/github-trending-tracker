import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://github.com/trending"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

LANGUAGES = ["python", "javascript", "go", "rust", "java", ""]


def scrape_trending(language: str = "") -> list:
    url = f"{BASE_URL}/{language}" if language else BASE_URL
    repos = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select("article.Box-row")

        for rank, item in enumerate(items, start=1):
            heading = item.select_one("h2 a")
            if not heading:
                continue

            full_name = heading.get_text(strip=True).replace("\n", "").replace(" ", "")
            full_name = "/".join(p.strip() for p in full_name.split("/"))
            repo_url = "https://github.com" + heading.get("href", "")

            desc_el = item.select_one("p")
            description = desc_el.get_text(strip=True) if desc_el else ""

            lang_el = item.select_one("[itemprop='programmingLanguage']")
            lang = lang_el.get_text(strip=True) if lang_el else language or "Unknown"

            stars_el = item.select("a.Link--muted")
            total_stars = _parse_number(stars_el[0].get_text(strip=True)) if len(stars_el) >= 1 else 0
            forks       = _parse_number(stars_el[1].get_text(strip=True)) if len(stars_el) >= 2 else 0

            stars_today_el = item.select_one("span.d-inline-block.float-sm-right")
            stars_today = _parse_number(stars_today_el.get_text(strip=True)) if stars_today_el else 0

            repos.append({
                "rank":          rank,
                "full_name":     full_name,
                "url":           repo_url,
                "description":   description[:300],
                "language":      lang,
                "total_stars":   total_stars,
                "forks":         forks,
                "stars_today":   stars_today,
                "trending_lang": language or "all",
                "scraped_at":    datetime.utcnow().isoformat(),
            })

        logger.info(f"Scraped {len(repos)} repos for language='{language or 'all'}'")
    except Exception as e:
        logger.error(f"Failed to scrape trending for '{language}': {e}")

    return repos


def scrape_all_languages() -> list:
    all_repos = []
    for lang in LANGUAGES:
        repos = scrape_trending(lang)
        all_repos.extend(repos)
    logger.info(f"Total repos scraped: {len(all_repos)}")
    return all_repos


def _parse_number(text: str) -> int:
    text = text.strip().lower().replace(",", "")
    try:
        if "k" in text:
            return int(float(text.replace("k", "")) * 1000)
        digits = "".join(c for c in text if c.isdigit())
        return int(digits) if digits else 0
    except Exception:
        return 0
