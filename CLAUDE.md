# fantatchi.xyz

Hugo + PaperMod テーマのブログサイト。

## 記事の追加

- パス: `content/posts/YYYY-MM-DD-slug/index.md`
- frontmatter: `draft: false`, tags/categories は配列形式 `["tag1", "tag2"]`
- Obsidian ドラフト (`draft: true`) から追加する場合は `draft: false` に変更する

## 開発

- `hugo server -D` — ローカルプレビュー（http://localhost:1313/）
- `git push origin main` — デプロイ
- `python3 scripts/qiita_post.py <index.md>` — Qiita へ転載（新規は限定共有、`--public` で公開、`--dry-run` で確認。要 `QIITA_TOKEN`。投稿後 `qiita_id` が frontmatter に入る）
