import feedparser
from typing import List, Dict, Any

# 示例RSS源列表，可自行扩展
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://news.yahoo.com/rss/",
]

def fetch_rss_feed(url: str) -> List[Dict[str, Any]]:
    """
    抓取并解析单个RSS源，返回新闻列表
    """
    feed = feedparser.parse(url)
    news_list = []
    for entry in feed.entries:
        news = {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "summary": entry.get("summary", ""),
            "published": entry.get("published", ""),
            "category": entry.get("category", "") if "category" in entry else None,
            "author": entry.get("author", "") if "author" in entry else None,
            "source": feed.feed.get("title", url),
            "guid": entry.get("id", entry.get("link", "")),
        }
        news_list.append(news)
    return news_list

def fetch_all_rss_feeds() -> List[Dict[str, Any]]:
    """
    抓取所有RSS源，合并去重返回新闻列表
    """
    all_news = []
    seen = set()
    for url in RSS_FEEDS:
        news_items = fetch_rss_feed(url)
        for item in news_items:
            guid = item["guid"]
            if guid not in seen:
                all_news.append(item)
                seen.add(guid)
    return all_news 