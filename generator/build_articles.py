import os
import markdown
import re
from datetime import datetime

POSTS_DIR = "content/posts"
IMAGES_DIR = "content/images"
OUTPUT_DIR = "articles/auto"
CATEGORY_DIR = "articles/categories"
INDEX_PATH = "index.html"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CATEGORY_DIR, exist_ok=True)

category_map = {}
posts = []

for file in os.listdir(POSTS_DIR):
    if file.endswith(".md"):
        with open(os.path.join(POSTS_DIR, file), "r", encoding="utf-8") as f:
            raw = f.read()

        meta = dict(re.findall(r"^(\w+):\s*\"?(.+?)\"?$", raw, re.M))
        content_raw = re.sub(r"(?s)^---.*?---", "", raw).strip()
        html = markdown.markdown(content_raw)
        html = re.sub(r'src="(.*?)"', lambda m: f'src="../../content/images/{m.group(1)}"', html)

        slug = file.replace(".md", ".html")
        post_url = f"{OUTPUT_DIR}/{slug}"
        post = {
            "title": meta.get("title", "Không có tiêu đề"),
            "date": meta.get("date", "2025-01-01"),
            "image": meta.get("image", ""),
            "category": meta.get("category", "Thời sự"),
            "slug": slug,
            "html": html
        }
        posts.append(post)

        with open(post_url, "w", encoding="utf-8") as out:
            out.write(f"""<!DOCTYPE html>
<html lang='vi'>
<head>
<meta charset='UTF-8'><title>{post['title']}</title>
<link rel='stylesheet' href='../../css/style.css'>
</head><body>
<header class='site-header'><div class='container'><h1><a href='../../index.html'>Tin tức</a></h1></div></header>
<main class='container'>
<h2>{post['title']}</h2>
<p><em>{post['date']}</em></p>
{html}
</main>
<footer class='site-footer'><div class='container'><p>&copy; 2025 Tin tức</p></div></footer>
</body></html>""")

        cat = post["category"]
        category_map.setdefault(cat, []).append(post)

posts.sort(key=lambda x: x["date"], reverse=True)
listing = "\n".join([
    f"<article><h3><a href='articles/auto/{p['slug']}'>{p['title']}</a></h3><p>{p['category']} - {p['date']}</p></article>"
    for p in posts[:10]
])

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    index = f.read()

index = re.sub(r"(?s)(<section class=\"grid\">).*?(</section>)", 
               f"\\1\n{listing}\n\\2", index)

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(index)

for cat, plist in category_map.items():
    plist.sort(key=lambda x: x["date"], reverse=True)
    items = "\n".join([
        f"<article><h3><a href='../auto/{p['slug']}'>{p['title']}</a></h3><p>{p['date']}</p></article>"
        for p in plist
    ])
    filename = f"{cat.lower().replace(' ', '-')}.html"
    with open(f"{CATEGORY_DIR}/{filename}", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang='vi'>
<head><meta charset='UTF-8'><title>{cat} - Tin tức</title><link rel='stylesheet' href='../../css/style.css'></head>
<body>
<header class='site-header'><div class='container'><h1><a href='../../index.html'>Tin tức</a></h1></div></header>
<main class='container'><h2>{cat}</h2><section class='grid'>{items}</section></main>
<footer class='site-footer'><div class='container'><p>&copy; 2025</p></div></footer>
</body></html>""")

print("[✓] Articles and category pages generated.")
