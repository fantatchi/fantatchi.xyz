---
title: "まだ npm で入れてる？Claude Code ネイティブインストールのメリット"
date: 2026-03-16
draft: false
tags: ["claude-code", "cli", "devtools", "npm"]
categories: ["devtools"]
---

## 導入

Claude Code を `npm install -g` で使っている人、まだ多いのではないだろうか。

先日、Claude Code を最新版に更新しようとしたら「すでに最新版です」と言われた。自分で更新した覚えはない。調べてみると、ネイティブインストールにはバックグラウンド自動更新の仕組みがあり、知らないうちに最新版が適用されていたのだった。

実は npm インストールはすでに**非推奨**になっている。この記事では、ネイティブインストールと npm インストールの違い、移行方法をまとめる。

## ネイティブインストールと npm インストールの違い

| | ネイティブインストール（推奨） | npm インストール（非推奨） |
|---|---|---|
| インストール方法 | 公式スクリプト | `npm install -g` |
| Node.js | 不要 | 18 以上が必要 |
| 自動更新 | バックグラウンドで自動 | なし（手動で `npm update -g`） |
| 更新方法 | `claude update` または自動 | `npm update -g @anthropic-ai/claude-code` |
| バイナリ署名 | macOS: Apple 公証済み / Windows: 署名済み | なし |

大きな違いは **自動更新** と **Node.js 不要** の 2 点だ。

ネイティブインストールでは起動時と実行中に定期的に更新チェックが走り、新しいバージョンがあればバックグラウンドでダウンロード・インストールされる。次回起動時に自動で適用されるため、常に最新の機能とセキュリティ修正が使える。

また、Node.js が不要になるのも嬉しい。Claude Code のためだけに Node.js をグローバルに入れていた人は、その依存を外せる。

## ネイティブインストールの手順

> **注意**: インストール手順は変更される可能性があります。最新の方法については[公式ドキュメント](https://code.claude.com/docs/ja/setup)を確認してください。

### macOS / Linux / WSL

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

これだけ。`~/.local/bin/claude` にバイナリが配置される。

### Windows

PowerShell の場合:

```powershell
irm https://claude.ai/install.ps1 | iex
```

CMD の場合:

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

Windows では [Git for Windows](https://git-scm.com/downloads/win) が必要なので、事前にインストールしておこう。

### インストール後の確認

```bash
claude doctor
```

インストールタイプとバージョンが表示される。

## npm からの移行

すでに npm で Claude Code を使っている場合、移行はワンコマンドで済む。

```bash
claude install
```

これでネイティブインストールに切り替わる。切り替え後は npm 版をアンインストールしてOK。

```bash
npm uninstall -g @anthropic-ai/claude-code
```

## 自動更新の設定

### リリースチャネル

自動更新には 2 つのチャネルがある。

- **`latest`**（デフォルト）: リリースされたらすぐに適用
- **`stable`**: 約 1 週間遅れで適用。大きな問題があるリリースはスキップされる

安定重視なら `stable` がおすすめ。設定は `/config` から変更するか、`settings.json` に書く。

```json
{
  "autoUpdatesChannel": "stable"
}
```

インストール時にチャネルを指定することもできる。

```bash
curl -fsSL https://claude.ai/install.sh | bash -s stable
```

### 自動更新を無効にしたい場合

環境変数を設定する。

```bash
export DISABLE_AUTOUPDATER=1
```

この場合は `claude update` で手動更新する。

## まとめ

- npm インストールは**非推奨**。ネイティブインストールに移行しよう
- ネイティブインストールは **Node.js 不要** で **自動更新** が効く
- 移行は `claude install` のワンコマンド
- 安定重視なら `stable` チャネルに切り替えるのもあり

「気づいたら最新版になっている」のは、ちゃんと動いている証拠だった。
