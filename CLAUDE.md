# KANPAN ご説明資料サイト

リポジトリ: mu62/kanpan-site / 公開: GitHub Pages（main ブランチの `/docs`）

レンタルスペース KANPAN（KOFUNE 2F）の社外向け資料サイト。Notionから移行した。
資料の変更は、Claudeへのプロンプトで行う運用。

## 構成
- `content/*.md` … 各ページの本文（これが正本。ここだけ直せば内容が変わる）
- `assets/style.css` … 見た目
- `assets/img/` … 画像（ファイル名は管理番号ベース。元のNotionファイル名は各mdの `<!-- src: -->` コメントに記載）
- `build.py` … `content/` → `dist/` に静的HTMLを生成（`python3 build.py`）。ページの追加・並び替えは `PAGES` を編集
- `docs/` … 生成物（GitHub Pagesの公開対象）。手で編集しない。**変更したら必ず `python3 build.py` を実行し、`docs/` ごとコミット・pushする**（pushで公開が更新される）

## 編集ルール
- 文言・料金・条件の変更は `content/*.md` を直接編集し、`python3 build.py` を実行する
- 同じ内容が複数ページにある（キャンセルポリシーは「ご予約前のご案内」と「利用規約」、利用時間・禁止事項・喫煙は「ご案内」「ご利用ガイド」）。片方を変えたら他方も確認して揃える
- 表記は「規約」ではなく「利用規約」
- 画像が無い場合は表示されないだけでビルドは通る。未配置の一覧はビルド時に出力される
- 現在は `build.py` の `robots="noindex"`（検索エンジンに載せない設定）。検索に出したいなら `index,follow` に変更する

## 未確定事項（要確認）
- 利用料金（日／時間）はNotion資料に無かったため、サイトにも載せていない
- お問い合わせ先（Instagram等）は未掲載
