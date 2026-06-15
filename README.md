# GitHub Trending Tracker

A small project that tracks GitHub trending repositories and stores them locally so I can see which projects were trending over time.

It scrapes GitHub Trending, saves the data in SQLite, and exposes it through a FastAPI API and a simple CLI.

## Features

* Scrape GitHub Trending repositories
* Track repositories across different languages
* Store historical data in SQLite
* View data using FastAPI endpoints
* Query data from the command line
* Basic tests with pytest

## Project Structure

```text
github-trending-tracker/
├── app/
├── tests/
├── requirements.txt
└── README.md
```

## Getting Started

Clone the repository:

```bash
git clone <repo-url>
cd github-trending-tracker
```

Create a virtual environment and install dependencies:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

Install packages:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn app.main:app --reload
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## API

Some of the available endpoints:

```text
POST  /scrape
GET   /repos
GET   /repos/top
GET   /stats
GET   /repos/{owner}/{repo}/history
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/scrape

curl http://127.0.0.1:8000/repos/top?limit=5
```

## CLI Examples

```bash
python -m app.cli

python -m app.cli --language python

python -m app.cli --top 10
```

## Running Tests

```bash
pytest -v
```

## Tech Used

* Python
* BeautifulSoup
* FastAPI
* SQLite
* Pytest

## Why I Built This

I wanted to build a simple project that combines web scraping, data storage, APIs, and a CLI in one place. It was also a good way to practice working with historical data instead of just storing the latest results.
