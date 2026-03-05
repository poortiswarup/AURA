"""
AURA — Local Data Storage
Replaces Base44 entities with local JSON files.
Stores: NewsArticle, CompanyTracker, SentimentSnapshot
"""

import json
import os
import uuid
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__))

ARTICLES_FILE  = os.path.join(DATA_DIR, "articles.json")
COMPANIES_FILE = os.path.join(DATA_DIR, "companies.json")
SNAPSHOTS_FILE = os.path.join(DATA_DIR, "snapshots.json")


def _load(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def _save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ── NewsArticle ───────────────────────────────────────────────────────────────

def get_articles():
    return sorted(_load(ARTICLES_FILE), key=lambda x: x.get("created_date",""), reverse=True)

def add_article(data: dict):
    articles = _load(ARTICLES_FILE)
    article = {
        "id": str(uuid.uuid4()),
        "created_date": datetime.now().isoformat(),
        **data
    }
    articles.append(article)
    _save(ARTICLES_FILE, articles)
    return article

def delete_article(article_id: str):
    articles = [a for a in _load(ARTICLES_FILE) if a["id"] != article_id]
    _save(ARTICLES_FILE, articles)


# ── CompanyTracker ────────────────────────────────────────────────────────────

def get_companies():
    return _load(COMPANIES_FILE)

def add_company(data: dict):
    companies = _load(COMPANIES_FILE)
    # Prevent duplicates
    tickers = [c["ticker"].upper() for c in companies]
    if data.get("ticker","").upper() in tickers:
        return None
    company = {
        "id": str(uuid.uuid4()),
        "created_date": datetime.now().isoformat(),
        "is_active": True,
        "risk_level": "low",
        "sentiment_trend": "stable",
        "latest_sentiment": None,
        **data
    }
    companies.append(company)
    _save(COMPANIES_FILE, companies)
    return company

def update_company(company_id: str, updates: dict):
    companies = _load(COMPANIES_FILE)
    for c in companies:
        if c["id"] == company_id:
            c.update(updates)
    _save(COMPANIES_FILE, companies)

def delete_company(company_id: str):
    companies = [c for c in _load(COMPANIES_FILE) if c["id"] != company_id]
    _save(COMPANIES_FILE, companies)


# ── SentimentSnapshot ─────────────────────────────────────────────────────────

def get_snapshots():
    return sorted(_load(SNAPSHOTS_FILE), key=lambda x: x.get("date",""), reverse=True)

def add_snapshot(data: dict):
    snapshots = _load(SNAPSHOTS_FILE)
    snap = {
        "id": str(uuid.uuid4()),
        "created_date": datetime.now().isoformat(),
        **data
    }
    snapshots.append(snap)
    _save(SNAPSHOTS_FILE, snapshots)
    return snap
