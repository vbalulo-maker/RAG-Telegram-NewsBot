import feedparser
import json
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from config import RSS_FEEDS  

CACHE_FILE = "data/cache.json"

def clean_html(raw_html: str) -> str:
    """Remove HTML tags and entities from RSS summary."""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text()
    return re.sub(r'\s+', ' ', text).strip()

def fetch_new_articles():
    # Load cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
    else:
        cache = {"processed_links": []}

    new_articles = []

    for feed_url in RSS_FEEDS:
        print(f"Fetching feed: {feed_url}")
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:  # limit to 5 per feed
            link = entry.link
            if link not in cache["processed_links"]:
                # === БЕЗОПАСНОЕ ПОЛУЧЕНИЕ СОДЕРЖАНИЯ ===
                # Пробуем взять summary, если нет — берём description, если нет — пустую строку
                raw_content = ""
                if hasattr(entry, 'summary'):
                    raw_content = entry.summary
                elif hasattr(entry, 'description'):
                    raw_content = entry.description
                # Если есть content, можно взять первый элемент
                elif hasattr(entry, 'content') and entry.content:
                    raw_content = entry.content[0].value
                # === КОНЕЦ БЛОКА ===

                article = {
                    "source": feed.feed.title if "title" in feed.feed else "Unknown Source",
                    "title": entry.title,
                    "summary": clean_html(raw_content),  # теперь raw_content всегда определён
                    "link": link,
                    "published": getattr(entry, "published", str(datetime.now())),
                }
                new_articles.append(article)
                cache["processed_links"].append(link)

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

    return new_articles