import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import re


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_news_links():
    url = "https://news.sina.com.cn/china/"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    links = []
    for a in soup.select("a[href^='https://news.sina.com.cn/c/']"):
        href = a.get("href")
        title = a.get_text(strip=True)
        if len(title) > 5 and href not in links:
            links.append(href)
        if len(links) >= 3:
            break
    return links

def extract_article(url):
    res = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "无标题"
    p_tags = soup.select("div.article p")
    body = "\n\n".join(p.get_text(strip=True) for p in p_tags if len(p.get_text(strip=True)) > 10)
    return title, body

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower())[:50]

def save_article(title_vi, content_vi, filename, category="Thời sự"):
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    md_path = f"content/posts/{filename}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"""---
title: "{title_vi}"
date: "{date_str}"
category: "{category}"
tags: []
image: ""
---

{content_vi}
""")

def load_saved_urls():
    try:
        with open("generator/saved_urls.txt", "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_url(url):
    with open("generator/saved_urls.txt", "a", encoding="utf-8") as f:
        f.write(url + "\n")

def main():
    links = get_news_links()
saved = load_saved_urls()
    for url in links:
        if url in saved:
            print(f'[✓] Skipping (already processed): {url}')
            continue
        try:
            title_cn, content_cn = extract_article(url)
            filename = slugify(title_cn)
            save_article(title_cn, content_cn, filename)
            save_url(url)
            print(f"[✓] Saved: {filename}")
        except Exception as e:
            print(f"[×] Error processing {url}: {e}")

if __name__ == "__main__":
    main()
