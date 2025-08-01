# generator/scraper.py
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib

POSTS_DIR = "content/posts"
SAVED_URLS_FILE = "generator/saved_urls.txt"

os.makedirs(POSTS_DIR, exist_ok=True)

def slugify(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:10]

def get_existing_urls():
    if not os.path.exists(SAVED_URLS_FILE):
        return set()
    with open(SAVED_URLS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_url(url):
    with open(SAVED_URLS_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")

def save_article(title, content, filename, category="时事"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    md = f"""---
title: {title}
date: {now}
category: {category}
---

{content}
"""
    path = os.path.join(POSTS_DIR, f"{filename}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)

def fetch_news():
    url = "https://news.sina.com.cn/china/"
    r = requests.get(url)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    links = [a["href"] for a in soup.select('a[href^="https://news.sina.com.cn/c/"]') if a["href"].endswith(".shtml")]
    return links[:5]

def parse_article(url):
    r = requests.get(url)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find("h1").text.strip() if soup.find("h1") else "未命名"
    paras = [p.text.strip() for p in soup.select("div.article p") if p.text.strip()]
    content = "\n\n".join(paras)
    return title, content

def main():
    seen = get_existing_urls()
    links = fetch_news()
    for url in links:
        if url in seen:
            continue
        try:
            title, content = parse_article(url)
            filename = slugify(title)
            save_article(title, content, filename)
            save_url(url)
            print(f"[\u2713] Saved: {title}")
        except Exception as e:
            print(f"[\u00d7] Error processing {url}: {e}")

if __name__ == "__main__":
    main()
