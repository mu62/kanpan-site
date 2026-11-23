#!/usr/bin/env python3
"""content/*.md -> docs/*.html  (pip install markdown)

Usage: python3 build.py
- 画像は assets/img/ に置く。ファイルが無い画像は表示せず、末尾に一覧を出力する。
- ページの追加・並び替えは下の PAGES を編集する。
"""
import re, shutil, html
from pathlib import Path
import markdown

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "content", ROOT / "docs"  # GitHub Pages は docs/ から配信

SITE_NAME = "KANPAN"
FOOTER = "© 合同会社六二酒店 / KOFUNE SAKE BREWERY"

# (slug, ナビ表示名)  ※ index はトップページ
PAGES = [
    ("index", "トップ"),
    ("before-booking", "ご予約前のご案内"),
    ("guide", "ご利用ガイド"),
    ("terms", "利用規約"),
    ("equipment", "貸出備品"),
    ("food", "フードオプション"),
]

# ナビに並べる外部リンク (表示名, URL)
EXTERNAL = [
    ("写真ギャラリー", "https://drive.google.com/drive/folders/1KHEkE5Mve5kKecrOWf2TB_YpSPT9YBL8?usp=sharing"),
]

TEMPLATE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="{robots}">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@600&display=swap&text=KANPAN">
<link rel="icon" href="assets/img/favicon.png">
<link rel="stylesheet" href="assets/style.css"></head>
<body>
<header class="site"><div class="in">
<a class="brand" href="index.html"><img src="assets/img/logo.png" alt="" width="32" height="32"><span>{site}</span></a>
<nav>{nav}</nav></div></header>
<main>
{body}
</main>
<footer>{footer}</footer>
</body></html>
"""

missing = []

def render(slug, label):
    text = (SRC / f"{slug}.md").read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["extra", "sane_lists", "md_in_html"])
    # 画像ファイルが無ければ <img> を外す
    def chk(m):
        src = m.group(1)
        if (ROOT / "assets" / src).exists():
            return m.group(0)
        missing.append(f"{slug}: {src}")
        return ""
    body = re.sub(r'<img[^>]*?src="(img/[^"]+)"[^>]*?>', chk, body)
    h1 = re.search(r"<h1>(.*?)</h1>", body)
    title = html.unescape(re.sub("<.*?>", "", h1.group(1))) if h1 else label
    nav = "".join(
        f'<a href="{s}.html"{" aria-current=page" if s == slug else ""}>{html.escape(l)}</a>'
        for s, l in PAGES) + "".join(
        f'<a href="{u}" target="_blank" rel="noopener">{html.escape(l)} ↗</a>'
        for l, u in EXTERNAL)
    body = body.replace('src="img/', 'src="assets/img/')
    return TEMPLATE.format(
        title=f"{title} | {SITE_NAME}", site=SITE_NAME, nav=nav, body=body,
        footer=FOOTER, robots="noindex")  # 公開時は index,follow に変更

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("")
    for slug, label in PAGES:
        (OUT / f"{slug}.html").write_text(render(slug, label), encoding="utf-8")
    print(f"built {len(PAGES)} pages -> {OUT}")
    if missing:
        print(f"\n画像未配置: {len(missing)} 件 (assets/img/ に置くと表示されます)")
        for m in missing:
            print("  ", m)

if __name__ == "__main__":
    main()
