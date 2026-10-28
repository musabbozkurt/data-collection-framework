"""Batch scraper: finds X.com pages for keywords via DuckDuckGo and stores their content (via Jina Reader) in MongoDB."""
import argparse
import os
import time
from urllib.parse import quote_plus, urlparse

import requests
from ddgs import DDGS
from pymongo import MongoClient

# Defaults to the MongoDB container of docker-compose.yml, which requires the root credentials
MONGO_URI = os.environ.get("MONGO_URI") or (
    f"mongodb://root:{quote_plus(os.environ.get('MONGO_ROOT_PASSWORD', 'password'))}@localhost:27017/?authSource=admin")
DEFAULT_KEYWORDS = ["Data Science", "MongoDB Atlas", "Python Web Scraping", "OpenAI API"]
DATABASE, COLLECTION = "x_batch_db", "tweets_by_keywords"
JINA_READER = "https://r.jina.ai/"
# The "duckduckgo" backend fails on macOS's LibreSSL (TLS 1.3), so use these engines instead
SEARCH_BACKENDS = ("google", "yahoo", "grokipedia")
X_HOSTS = {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}


def get_x_links(query: str, max_results: int = 5) -> list:
    """Searches the web index for X.com pages matching the keyword; returns url/title/snippet dicts."""
    for backend in SEARCH_BACKENDS:
        try:
            results = DDGS().text(f'"{query}" site:x.com', max_results=max_results, backend=backend)
        except Exception as error:  # a backend may be blocked or have no results; try the next one
            print(f"⚠️ '{backend}' search failed for '{query}': {str(error)[:80]}")
            continue
        links = [{"url": r["href"], "title": r.get("title", ""), "snippet": r.get("body", "")}
                 for r in results if urlparse(r.get("href", "")).hostname in X_HOSTS]
        if links:
            return links
    return []


def fetch_with_jina(x_url: str):
    """Fetches the page content as JSON through the Jina Reader proxy (no X login needed)."""
    try:
        response = requests.get(f"{JINA_READER}{x_url}", headers={"Accept": "application/json"}, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception as error:
        print(f"⚠️ Jina Reader failure on ({x_url}): {error}")
    return None


def process_multiple_keywords(collection, keywords: list, links_per_keyword: int = 5) -> dict:
    """Discovers, fetches and upserts X pages for every keyword; returns {keyword: [saved urls]}."""
    saved = {keyword: [] for keyword in keywords}
    print(f"🚀 Initializing batch pipeline for {len(keywords)} keywords...\n")

    for index, keyword in enumerate(keywords, 1):
        print(f"🔍 [{index}/{len(keywords)}] Processing keyword: '{keyword}'")
        links = get_x_links(keyword, max_results=links_per_keyword)
        print(f"🔗 Discovered {len(links)} X target paths for '{keyword}'.")

        for item in links:
            url = item["url"]
            page = fetch_with_jina(url)
            if page and "data" in page:
                document = {
                    "_id": f"{keyword}_{url}",  # compound key prevents collisions across keywords
                    "keyword": keyword,
                    "tweet_url": url,
                    "search_meta": {"title": item["title"], "snippet": item["snippet"]},
                    "scraped_data": page["data"],
                    "saved_at": time.time(),
                }
                try:
                    collection.update_one({"_id": document["_id"]}, {"$set": document}, upsert=True)
                    saved[keyword].append(url)
                    print(f"   💾 Saved to MongoDB: {url}")
                except Exception as error:
                    print(f"❌ MongoDB persistence fault: {error}")
            time.sleep(2)  # be polite to the Jina Reader service

        print(f"✅ Finished keyword '{keyword}'.\n")
        time.sleep(3)  # cool-down between searches to avoid rate limits
    return saved


def scrape(keywords: list, links_per_keyword: int = 3, mongo_uri: str = MONGO_URI) -> dict:
    """Runs one scraping round and stores the pages in x_batch_db.tweets_by_keywords."""
    with MongoClient(mongo_uri) as mongo_client:
        return process_multiple_keywords(mongo_client[DATABASE][COLLECTION], keywords, links_per_keyword)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape X.com pages for keywords into MongoDB.")
    parser.add_argument("keywords", nargs="*", default=DEFAULT_KEYWORDS, help="keywords to search for")
    parser.add_argument("--limit", type=int, default=3, help="links per keyword and round")
    parser.add_argument("--live", type=int, metavar="SECONDS", default=0,
                        help="keep running and repeat every SECONDS until Ctrl+C (new pages are added, known ones updated)")
    args = parser.parse_args()

    try:
        while True:
            scrape(args.keywords, args.limit)
            if not args.live:
                break
            print(f"⏳ Live mode: next round in {args.live}s (Ctrl+C to stop)\n")
            time.sleep(args.live)
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")


if __name__ == "__main__":
    main()
