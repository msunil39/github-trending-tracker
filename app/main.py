from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from scraper import scrape_trending, scrape_all_languages
from database import init_db, insert_repos, fetch_repos, fetch_top_by_stars, fetch_history, fetch_stats
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GitHub Trending Tracker API",
    description="Tracks GitHub trending repositories over time with history and language filtering.",
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    init_db()


class Repo(BaseModel):
    id: int
    full_name: str
    url: str
    description: Optional[str]
    language: Optional[str]
    total_stars: int
    forks: int
    stars_today: int
    trending_lang: str
    scraped_at: str


class ScrapeResult(BaseModel):
    scraped: int
    inserted: int
    message: str


class Stats(BaseModel):
    total_records: int
    by_language: dict
    top_today: list


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "GitHub Trending Tracker is running"}


@app.post("/scrape", response_model=ScrapeResult, tags=["Pipeline"])
def run_scrape(language: Optional[str] = Query(None, description="Scrape specific language only")):
    """
    Trigger a scrape. Pass ?language=python to scrape one language,
    or leave empty to scrape all configured languages.
    """
    if language:
        raw = scrape_trending(language)
    else:
        raw = scrape_all_languages()
    inserted = insert_repos(raw)
    return ScrapeResult(
        scraped=len(raw),
        inserted=inserted,
        message=f"Done. {inserted} new repos stored."
    )


@app.get("/repos", response_model=list[Repo], tags=["Repos"])
def get_repos(
    language: Optional[str] = Query(None, description="Filter by language e.g. python"),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Return trending repos with optional language filter and pagination."""
    repos = fetch_repos(language=language, limit=limit, offset=offset)
    if not repos:
        raise HTTPException(status_code=404, detail="No repos found")
    return repos


@app.get("/repos/top", response_model=list[Repo], tags=["Repos"])
def get_top(limit: int = Query(10, ge=1, le=50)):
    """Return top repos ranked by stars gained today."""
    repos = fetch_top_by_stars(limit=limit)
    if not repos:
        raise HTTPException(status_code=404, detail="No data yet - run /scrape first")
    return repos


@app.get("/repos/{owner}/{repo}/history", tags=["Repos"])
def get_history(owner: str, repo: str):
    """
    Return historical trending records for a specific repo.
    """
    full_name = f"{owner}/{repo}"
    history = fetch_history(full_name)
    if not history:
        raise HTTPException(status_code=404, detail=f"No history found for {full_name}")
    return history


@app.get("/stats", response_model=Stats, tags=["Analytics"])
def get_stats():
    """Return total records, breakdown by language, and today's top repos."""
    return fetch_stats()
