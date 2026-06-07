import sqlite3
import os
import logging

logger = logging.getLogger(__name__)
DB_PATH = os.getenv("DB_PATH", "trending.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trending_repos (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name     TEXT NOT NULL,
            url           TEXT NOT NULL,
            description   TEXT,
            language      TEXT,
            total_stars   INTEGER DEFAULT 0,
            forks         INTEGER DEFAULT 0,
            stars_today   INTEGER DEFAULT 0,
            trending_lang TEXT,
            scraped_at    TEXT NOT NULL,
            created_at    TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_language    ON trending_repos(language)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scraped_at  ON trending_repos(scraped_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_full_name   ON trending_repos(full_name)")
    conn.commit()
    conn.close()
    logger.info("Database initialised")


def insert_repos(repos: list) -> int:
    """Insert repos - duplicate (full_name + scraped date) rows are skipped."""
    conn = get_connection()
    inserted = 0
    for repo in repos:
        try:
            date_key = repo["scraped_at"][:10]
            exists = conn.execute(
                "SELECT 1 FROM trending_repos WHERE full_name = ? AND DATE(scraped_at) = ?",
                (repo["full_name"], date_key)
            ).fetchone()
            if not exists:
                conn.execute("""
                    INSERT INTO trending_repos
                        (full_name, url, description, language, total_stars,
                         forks, stars_today, trending_lang, scraped_at)
                    VALUES
                        (:full_name, :url, :description, :language, :total_stars,
                         :forks, :stars_today, :trending_lang, :scraped_at)
                """, repo)
                inserted += 1
        except Exception as e:
            logger.error(f"Insert error for {repo.get('full_name')}: {e}")
    conn.commit()
    conn.close()
    logger.info(f"Inserted {inserted} new repos into DB")
    return inserted


def fetch_repos(language: str = None, limit: int = 25, offset: int = 0) -> list:
    conn = get_connection()
    if language:
        rows = conn.execute(
            "SELECT * FROM trending_repos WHERE language = ? ORDER BY scraped_at DESC, stars_today DESC LIMIT ? OFFSET ?",
            (language, limit, offset)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM trending_repos ORDER BY scraped_at DESC, stars_today DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_top_by_stars(limit: int = 10) -> list:
    """Return top repos ranked by stars gained today."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM trending_repos ORDER BY stars_today DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_history(full_name: str) -> list:
    """Return all historical records for a specific repo."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM trending_repos WHERE full_name = ? ORDER BY scraped_at ASC",
        (full_name,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_stats() -> dict:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM trending_repos").fetchone()[0]
    by_language = conn.execute(
        "SELECT language, COUNT(*) as count FROM trending_repos GROUP BY language ORDER BY count DESC"
    ).fetchall()
    top_today = conn.execute(
        "SELECT full_name, stars_today FROM trending_repos ORDER BY stars_today DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return {
        "total_records":  total,
        "by_language":    {r["language"]: r["count"] for r in by_language},
        "top_today":      [{"repo": r["full_name"], "stars_today": r["stars_today"]} for r in top_today],
    }
