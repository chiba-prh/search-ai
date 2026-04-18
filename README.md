# 📰 AI Daily Digest

AI 関連の最新情報を **3時間ごとに自動収集・日本語要約** してくれるシステム。
GitHub Pages でいつでもブラウザから閲覧でき、ローカルでは Obsidian でもそのまま読めます。

## 🌐 公開サイト

👉 **https://chiba-prh.github.io/search-ai/**

---

## 🏗️ システム構成

```
  ┌─────────────────┐
  │  sources.yml    │  6サイトの RSS URL を定義
  └────────┬────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │  fetch_ai_news.py           │  RSS で記事取得 → Gemini で日本語要約
  │  (GitHub Actions 3時間毎)   │
  └────────┬────────────────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │  Web記事/AI/YYYY-MM-DD.md   │  公開日別のMarkdown
  └────────┬────────────────────┘
           │
           ├──→ Obsidian でローカル閲覧
           │
           ├──→ preview_server.py（localhost:9090）
           │
           └──→ build_static.py → docs/*.html
                                       │
                                       ▼
                         GitHub Pages で公開
```

---

## 📡 収集ソース

| サイト | RSS |
|---|---|
| OpenAI Blog | [openai.com/news/rss.xml](https://openai.com/news/rss.xml) |
| Anthropic News | コミュニティフィード（[Olshansk/rss-feeds](https://github.com/Olshansk/rss-feeds)） |
| Google DeepMind Blog | [deepmind.google/blog/rss.xml](https://deepmind.google/blog/rss.xml) |
| arXiv cs.AI | [export.arxiv.org API](http://export.arxiv.org/api/query?search_query=cat:cs.AI) |
| arXiv cs.LG | [export.arxiv.org/rss/cs.LG](http://export.arxiv.org/rss/cs.LG) |
| MIT Technology Review | [technologyreview.com/.../feed](https://www.technologyreview.com/topic/artificial-intelligence/feed) |

---

## 📂 ディレクトリ構成

```
search-ai/
├── sources.yml              # ソース定義（RSS URL）
├── Web記事/AI/              # 公開日別 Markdown（記事の実体）
│   └── YYYY-MM-DD.md
├── docs/                    # GitHub Pages 用 HTML
│   ├── index.html
│   └── YYYY-MM-DD.html
├── scripts/
│   ├── fetch_ai_news.py     # RSS 取得 + Gemini 要約（本番）
│   ├── preview_server.py    # ローカルプレビュー（port 9090）
│   ├── build_static.py      # Markdown → HTML 変換
│   └── generate_all.py      # 手動で記事一括生成
├── templates/
│   └── daily_digest.md.j2   # Jinja2 テンプレート
└── .github/workflows/
    └── daily-ai-digest.yml  # 3時間ごとの自動実行
```

---

## ⚙️ 使い方

### ローカルでプレビュー

```bash
python scripts/preview_server.py
# → http://localhost:9090/ を開く
```

### 手動で記事取得

```bash
export GEMINI_API_KEY=your_key
python scripts/fetch_ai_news.py
```

### GitHub Pages を再生成

```bash
python scripts/build_static.py
git add docs/ && git commit -m "Update" && git push
```

---

## 🔧 技術スタック

- **Python 3.12**
- **[feedparser](https://pypi.org/project/feedparser/)** — RSS 解析
- **[google-genai](https://ai.google.dev/)** — Gemini API（要約生成）
- **[markdown](https://pypi.org/project/markdown/)** — HTML 変換
- **[PyYAML](https://pypi.org/project/PyYAML/)** — 設定ファイル
- **[Jinja2](https://jinja.palletsprojects.com/)** — Markdown テンプレート
- **GitHub Actions** — 3時間ごとの自動実行
- **GitHub Pages** — 静的サイト配信

---

## 🔄 自動化フロー

1. **3時間ごと** に GitHub Actions が発火（cron `0 */3 * * *`）
2. `fetch_ai_news.py` が 6ソースの RSS をパース（最大 20件/ソース）
3. `Web記事/AI/` 内の既存記事と URL で重複チェック
4. 新規記事のみ Gemini API で日本語要約を生成
5. **公開日ごと** に `Web記事/AI/YYYY-MM-DD.md` へ追記
6. `build_static.py` で `docs/*.html` を再生成
7. Git commit & push → GitHub Pages が自動デプロイ

---

## 📏 ルール

- **日付の扱い**: 記事は **公開日（Published）** のファイルに入る（取得日ではない）
- **重複排除**: URL ベースで厳密にチェック
- **ソース数固定**: 現状 6サイト（増やす場合は `sources.yml` を編集）
- **RSS 必須**: `rss` フィールドが空のソースはスキップ

---

## 🔑 環境変数

| 変数 | 用途 |
|---|---|
| `GEMINI_API_KEY` | Gemini API キー（[Google AI Studio](https://aistudio.google.com/) で取得） |
| `OUTPUT_DIR` | 出力ディレクトリ（デフォルト: プロジェクトルート） |
| `PORT` | プレビューサーバーのポート（デフォルト: 9090） |

GitHub Actions では `GEMINI_API_KEY` を Repository Secrets に登録してください。

---

## 📊 Gemini API 使用量の確認

👉 [Google AI Studio Usage](https://aistudio.google.com/app/usage)

3時間ごとの実行なら無料枠内で収まるはず（Gemini 3 Flash: 1,500 req/日）。

---

## 📄 ライセンス

MIT
