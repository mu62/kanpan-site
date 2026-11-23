#!/usr/bin/env python3
"""content/*.md -> docs/*.html  (pip install markdown)

Usage: python3 build.py
- 画像は assets/img/ に置く。ファイルが無い画像は表示せず、末尾に一覧を出力する。
- ページの追加・並び替えは下の PAGES を編集する。
"""
import re, shutil, html, json
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
    ("gallery", "写真ギャラリー"),
]

# ナビに並べる外部リンク (表示名, URL)
EXTERNAL = []

TEMPLATE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="{robots}">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@600&display=swap&text=KANPAN">
<link rel="icon" href="assets/img/favicon.png">
<link rel="stylesheet" href="assets/style.css?v={v}"></head>
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

import hashlib
# CSS更新がブラウザのキャッシュで古いまま残らないよう、内容のハッシュをURLに付ける
CSS_VER = hashlib.md5((ROOT / "assets" / "style.css").read_bytes()).hexdigest()[:8]

missing = []

def gallery_body():
    """content/gallery.json (DriveのファイルID一覧) から横スクロールギャラリーを生成。
    画像はDriveから直接読み込む（フォルダが「リンクを知っている全員」共有であること）。"""
    g = json.loads((SRC / "gallery.json").read_text(encoding="utf-8"))
    thumb = lambda i, w: f"https://drive.google.com/thumbnail?id={i}&sz=w{w}"
    out = ["<h1>写真ギャラリー</h1>", f"<p>{html.escape(g['intro'])}</p>"]
    for sec in g["sections"]:
        out.append(f"<h2>{html.escape(sec['title'])}</h2>")
        out.append('<div class="gal"><button class="gal-btn prev" aria-label="前へ">‹</button>'
                   '<div class="gal-track">')
        for p in sec["photos"]:
            cap = html.escape(p["caption"])
            out.append(
                f'<figure><a href="{thumb(p["id"], 2000)}" data-cap="{cap}">'
                f'<img src="{thumb(p["id"], 800)}" alt="{cap}" loading="lazy"></a>'
                f'<figcaption>{cap}</figcaption></figure>')
        out.append('</div><button class="gal-btn next" aria-label="次へ">›</button></div>')
    out.append(f'<p class="gal-more"><a href="{g["drive_folder"]}" target="_blank" rel="noopener">'
               'Googleドライブで全ての写真を開く ↗</a></p>')
    out.append(GALLERY_JS)
    return "\n".join(out)

GALLERY_JS = """<div class="lb" hidden><button class="lb-x" aria-label="閉じる">×</button>
<button class="gal-btn lb-prev" aria-label="前へ">‹</button><img alt=""><div class="lb-cap"></div>
<button class="gal-btn lb-next" aria-label="次へ">›</button></div>
<script>
document.querySelectorAll('.gal').forEach(function(g){
  var t=g.querySelector('.gal-track');
  g.querySelector('.prev').onclick=function(){t.scrollBy({left:-t.clientWidth*.8,behavior:'smooth'})};
  g.querySelector('.next').onclick=function(){t.scrollBy({left:t.clientWidth*.8,behavior:'smooth'})};
});
(function(){
  var lb=document.querySelector('.lb'),im=lb.querySelector('img'),cp=lb.querySelector('.lb-cap');
  var set=[],i=0;
  function show(n){i=(n+set.length)%set.length;im.src=set[i].href;cp.textContent=set[i].dataset.cap}
  document.querySelectorAll('.gal-track a').forEach(function(a){
    a.addEventListener('click',function(e){
      e.preventDefault();
      set=[].slice.call(a.closest('.gal-track').querySelectorAll('a'));
      lb.hidden=false;show(set.indexOf(a));
    });
  });
  lb.querySelector('.lb-x').onclick=function(){lb.hidden=true;im.src=''};
  lb.querySelector('.lb-prev').onclick=function(){show(i-1)};
  lb.querySelector('.lb-next').onclick=function(){show(i+1)};
  document.addEventListener('keydown',function(e){
    if(lb.hidden)return;
    if(e.key==='Escape')lb.querySelector('.lb-x').click();
    if(e.key==='ArrowLeft')show(i-1);
    if(e.key==='ArrowRight')show(i+1);
  });
})();
</script>"""

# h2（カテゴリ）への目次を冒頭に出すページ
CATEGORY_NAV = {"equipment"}

def add_category_nav(body):
    """h2(カテゴリ)ごとに、配下のh3(備品)へのリンク一覧を冒頭に出す。「参考」で始まる見出しは除く。"""
    parts = re.split(r"(<h[23]>.*?</h[23]>)", body)
    n2 = n3 = 0
    groups = []  # [(id, title, [(id, label_html)])]
    for k, p in enumerate(parts):
        m = re.fullmatch(r"<h([23])>(.*?)</h[23]>", p)
        if not m:
            continue
        if m.group(1) == "2":
            n2 += 1
            parts[k] = f'<h2 id="cat-{n2}">{m.group(2)}</h2>'
            groups.append((f"cat-{n2}", re.sub("<.*?>", "", m.group(2)), []))
        else:
            n3 += 1
            parts[k] = f'<h3 id="item-{n3}">{m.group(2)}</h3>'
            title = re.sub("<.*?>", "", m.group(2)).strip()
            if groups and not title.startswith("参考"):
                paid = ' <span class="tag">有料</span>' if "有料" in title else ""
                label = re.sub(r"\s*有料$", "", title)
                groups[-1][2].append((f"item-{n3}", label + paid))
    toc = "".join(
        f'<div class="toc-group"><a class="toc-cat" href="#{cid}">{ct}</a><div class="toc-items">'
        + "".join(f'<a href="#{iid}">{t}</a>' for iid, t in items) + "</div></div>"
        for cid, ct, items in groups)
    nav = f'<nav class="toc" aria-label="備品目次">{toc}</nav>'
    return "".join(parts).replace("</h1>", "</h1>\n" + nav, 1)

def render(slug, label):
    if slug == "gallery":
        body = gallery_body()
    else:
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
    if slug in CATEGORY_NAV:
        body = add_category_nav(body)
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
        footer=FOOTER, robots="noindex", v=CSS_VER)  # 公開時は index,follow に変更

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
