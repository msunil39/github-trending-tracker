import pytest
from datetime import datetime


SAMPLE_REPO = {
    "rank":          1,
    "full_name":     "test-owner/test-repo",
    "url":           "https://github.com/test-owner/test-repo",
    "description":   "A test repository",
    "language":      "Python",
    "total_stars":   5000,
    "forks":         300,
    "stars_today":   120,
    "trending_lang": "python",
    "scraped_at":    datetime.utcnow().isoformat(),
}


@pytest.fixture()
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test_trending.db")
    monkeypatch.setenv("DB_PATH", db_path)
    import importlib, app.database as m
    importlib.reload(m)
    m.init_db()
    return m


def test_init_creates_table(db, tmp_path):
    import sqlite3
    conn = sqlite3.connect(str(tmp_path / "test_trending.db"))
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    assert "trending_repos" in tables
    conn.close()


def test_insert_and_fetch(db):
    inserted = db.insert_repos([SAMPLE_REPO])
    assert inserted == 1
    results = db.fetch_repos()
    assert len(results) == 1
    assert results[0]["full_name"] == "test-owner/test-repo"


def test_no_duplicate_same_day(db):
    db.insert_repos([SAMPLE_REPO])
    second = db.insert_repos([SAMPLE_REPO])
    assert second == 0


def test_fetch_by_language(db):
    db.insert_repos([SAMPLE_REPO])
    results = db.fetch_repos(language="Python")
    assert len(results) == 1
    results_none = db.fetch_repos(language="Rust")
    assert len(results_none) == 0


def test_fetch_top_by_stars(db):
    repos = [
        {**SAMPLE_REPO, "full_name": "owner/repo-a", "url": "https://github.com/owner/repo-a", "stars_today": 50},
        {**SAMPLE_REPO, "full_name": "owner/repo-b", "url": "https://github.com/owner/repo-b", "stars_today": 200},
        {**SAMPLE_REPO, "full_name": "owner/repo-c", "url": "https://github.com/owner/repo-c", "stars_today": 10},
    ]
    db.insert_repos(repos)
    top = db.fetch_top_by_stars(limit=1)
    assert top[0]["full_name"] == "owner/repo-b"


def test_fetch_history(db):
    db.insert_repos([SAMPLE_REPO])
    history = db.fetch_history("test-owner/test-repo")
    assert len(history) == 1


def test_stats(db):
    db.insert_repos([SAMPLE_REPO])
    stats = db.fetch_stats()
    assert stats["total_records"] == 1
    assert "Python" in stats["by_language"]
