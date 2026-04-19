# 🔄 セッション引き継ぎメモ

**作成日**: 2026-04-19 (JST)
**前セッション最終状態**: Gemini API 日次クォータ超過で作業中断

---

## 📌 現状サマリー

### プロジェクト: AI Daily Digest
- **リポジトリ**: https://github.com/chiba-prh/search-ai
- **公開サイト**: https://chiba-prh.github.io/search-ai/
- **ローカルパス**: `C:\Users\Chiba\Desktop\search-ai`

### 記事データの状態
| 項目 | 数 |
|---|---|
| 総記事数 | **153件**（34日分） |
| ✅ 要約済み | **61件** |
| ❌ 要約失敗（`要約の取得に失敗しました`） | **92件** |

### 失敗日付の内訳（要対応）
```
2026-04-18: 20件全滅
2026-04-17: 22/25件失敗
2026-04-16: 8/9件失敗
2026-04-10: 14/17件失敗
... その他散発的
```

---

## 🏗️ システム構成（現状の仕組み）

```
sources.yml（6ソース、RSS URL定義）
    ↓
fetch_ai_news.py
  - feedparser で RSS 取得
  - 既存 Web記事/AI/*.md と URL で重複排除
  - Gemini 3 Flash Preview で日本語要約
  - 公開日別に YYYY-MM-DD.md へ振り分け
    ↓
build_static.py（Markdown → HTML）
    ↓
docs/*.html（GitHub Pages 公開）
```

### GitHub Actions
- **`.github/workflows/daily-ai-digest.yml`**: cron `0 21 * * *`（毎朝6時 JST）
- **`.github/workflows/resummarize.yml`**: 手動実行用、失敗記事の再要約

### 使用モデル
- `gemini-3-flash-preview`（Google AI Studio 無料枠）
- 1日1,500 req/日、15 RPM
- **Preview モデルは本番より枠が厳しい可能性あり**

---

## 🚨 途中になっている作業

### 直前の失敗
1. GitHub Actions で手動実行 (`workflow_dispatch`) → 初回一括取得で153件取得、92件要約失敗
2. `resummarize.yml` 起動 → Gemini API **429 RESOURCE_EXHAUSTED** でクォータ切れ
3. 再実行試みるも同様に失敗

### クォータリセット予定
- **UTC 0:00 = JST 9:00 にリセット**
- 2026-04-20 09:00 JST 以降に再実行可能

---

## 📋 次セッションでやるべきこと

### 優先度: 高
**ユーザーに以下の選択肢を再提示し、方針確定してから実行:**

| 案 | 内容 |
|---|---|
| **A. 明朝9時以降に resummarize 再実行** | クォータ回復待ち |
| **B. 失敗92件を削除して通常実行に任せる** | シンプル、ただし記事は減る |
| **C. モデルを `gemini-1.5-flash` に変更** | 別クォータかもしれない |
| **D. arXiv 論文を要約対象から除外** | 枠節約、論文は読み物向きではない |

**前セッションでの推奨: A + D の組み合わせ**

### arXiv 除外を実装する場合
`scripts/resummarize_failed.py` と `scripts/fetch_ai_news.py` に以下を追加:

```python
# Skip arXiv sources from Gemini summarization
if "arXiv" in article.get("source", ""):
    # Use title as-is, skip summary generation
    return {
        **article,
        "title_ja": article.get("title_en", ""),
        "summary": "（arXiv論文 — 詳細はリンク先をご参照ください）",
        "bullet_points": [],
        "tags": ["arxiv", "research"],
        "importance": 2,
    }
```

### 実行方法
```bash
cd "C:\Users\Chiba\Desktop\search-ai"
gh workflow run "Re-summarize Failed Articles"
gh run watch <run-id>
```

---

## 📂 重要ファイル一覧

| ファイル | 役割 |
|---|---|
| `sources.yml` | 6ソースのRSS定義 |
| `scripts/fetch_ai_news.py` | RSS取得＋Gemini要約（本番） |
| `scripts/resummarize_failed.py` | 失敗記事の再要約専用 |
| `scripts/build_static.py` | Markdown→HTML |
| `scripts/preview_server.py` | ローカルプレビュー（port 9090） |
| `scripts/generate_all.py` | 手動一括生成（過去分用） |
| `templates/daily_digest.md.j2` | Jinja2テンプレート |
| `.github/workflows/daily-ai-digest.yml` | 毎日6時JST自動実行 |
| `.github/workflows/resummarize.yml` | 手動リトライ用 |
| `Web記事/AI/YYYY-MM-DD.md` | 記事本体（公開日別） |
| `docs/*.html` | GitHub Pages公開ファイル |
| `README.md` | プロジェクト説明 |

---

## 🔑 RSS ソース（6サイト、全動作確認済み）

```yaml
- OpenAI Blog           : https://openai.com/news/rss.xml (940件)
- Anthropic Blog        : コミュニティフィード Olshansk/rss-feeds (200件)
- Google DeepMind Blog  : https://deepmind.google/blog/rss.xml (100件)
- arXiv (cs.AI)         : http://export.arxiv.org/api/query?... (20件)
- arXiv (cs.LG)         : http://export.arxiv.org/rss/cs.LG (265件)
- MIT Technology Review : https://www.technologyreview.com/.../feed (10件)

# enabled=false（RSS非対応）
- Anthropic (X/Twitter)
- Google Gemini (X/Twitter)
```

---

## 💡 注意点・ハマりポイント

1. **`output/` ディレクトリ**: `preview_server.py` は `SERVE_DIR = output/` を見る。`Web記事/AI/` の変更を反映するにはコピーが必要:
   ```bash
   rm -rf output/Web記事/AI && mkdir -p output/Web記事/AI && cp Web記事/AI/*.md output/Web記事/AI/
   ```

2. **`count: all` は文字列**: `fetch_ai_news.py` の `build_search_prompt()` で文字列として処理（`int += str` のバグ修正済み）

3. **日付のルール**: 記事は必ず **公開日（Published）** のファイルに入れる。取得日ではない。

4. **X/Twitter**: Google検索インデックスに載らないため RSS 取得不可。手動追記運用

5. **Gemini 3 Flash Preview のクォータ**:
   - 無料枠: 1,500 req/日、15 RPM
   - Preview モデルは本番より厳しい可能性あり
   - 確認: https://aistudio.google.com/app/usage

6. **日次運用は余裕**: 1日5〜10件程度の新規取得なら無料枠で余裕

---

## 🎯 当初のユーザー要望

1. ✅ 5つのAIソースから最新記事を自動収集
2. ✅ 日本語要約＋重要度スコア付きで保存
3. ✅ Obsidian とWebブラウザ両方で閲覧
4. ✅ GitHub Pages で公開
5. ✅ 公開日別にファイル分け
6. ✅ 当初「3時間ごと」→ **最終的に「毎朝6時」に変更**
7. ✅ X/Twitter（Anthropic, Gemini）ソース追加希望 → RSS非対応のため手動運用
8. ⏸️ **残課題**: 失敗92件の要約再生成

---

## 📝 最後のユーザー発言

> 「セッション切り替えるので、履歴保存で引継ぎ　お願いします。」

その前の私の提案（A/B/C/D案）への選択は未回答。

**次セッションの最初にやること**: この HANDOFF.md を読んで、ユーザーに選択肢を再提示し、方針を確定させてから作業再開。
