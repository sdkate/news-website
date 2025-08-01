import os
from markdown import markdown

INPUT_DIR = "content/posts"
OUTPUT_DIR = "public/articles"
os.makedirs(OUTPUT_DIR, exist_ok=True)

for file in os.listdir(INPUT_DIR):
    if file.endswith(".md"):
        with open(os.path.join(INPUT_DIR, file), encoding="utf-8") as f:
            md = f.read()
        body = markdown(md)
        html = f"""<html><body>{body}</body></html>"""
        with open(os.path.join(OUTPUT_DIR, file.replace(".md", ".html")), "w", encoding="utf-8") as f:
            f.write(html)
