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

## 写真ギャラリー
- `content/gallery.json` にDriveのファイルID・キャプション・セクションを列挙。画像はDriveから直接表示（データの保存先はDriveのまま）
- Driveフォルダ（https://drive.google.com/drive/folders/1KHEkE5Mve5kKecrOWf2TB_YpSPT9YBL8）は「リンクを知っている全員」共有が前提。共有を外すとサイト上で表示されなくなる
- 写真を追加・差し替え・削除したら、Drive MCPでフォルダ内を一覧して `gallery.json` を更新し、ビルド・pushする（ロゴ画像 KANPAN_Logo.png はギャラリーに入れない）

- 貸出備品ページは、h2見出し（カテゴリ）が自動で冒頭の目次ボタンになる（`build.py` の `CATEGORY_NAV`）。カテゴリを増やすときは `## ` 見出しを足すだけ

## 編集ルール
- 文言・料金・条件の変更は `content/*.md` を直接編集し、`python3 build.py` を実行する
- 同じ内容が複数ページにある（キャンセルポリシーは「ご予約前のご案内」と「利用規約」、利用時間・禁止事項・喫煙は「ご案内」「ご利用ガイド」）。片方を変えたら他方も確認して揃える
- 表記は「規約」ではなく「利用規約」
- 画像が無い場合は表示されないだけでビルドは通る。未配置の一覧はビルド時に出力される
- 現在は `build.py` の `robots="noindex"`（検索エンジンに載せない設定）。検索に出したいなら `index,follow` に変更する

## 方針（確定）
- 検索エンジンには載せない（noindexのまま）
- 利用料金・お問い合わせ先はサイトに載せない
- SAKEメニューのリンクはGitHub版（https://mu62.github.io/kofune-pub-order/）
