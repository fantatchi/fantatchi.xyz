# fantatchi.xyz

Hugo + PaperMod テーマのブログサイト。

## 記事の追加

- パス: `content/posts/YYYY-MM-DD-slug/index.md`
- frontmatter: `draft: false`, tags/categories は配列形式 `["tag1", "tag2"]`
- Obsidian ドラフト (`draft: true`) から追加する場合は `draft: false` に変更する

## 開発

- `hugo server -D` — ローカルプレビュー（http://localhost:1313/）
- `git push origin main` — デプロイ
