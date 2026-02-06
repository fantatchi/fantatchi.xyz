---
title: "Node.js バージョン管理を nvm から volta に移行する"
date: 2026-02-06
draft: false
tags: ["nodejs", "volta", "nvm", "migration"]
categories: ["tech"]
---

Node.js のバージョン管理に長らく nvm を使ってきたが、volta に乗り換えた。移行はかなりシンプルだったので、手順をまとめておく。

## なぜ乗り換えたか

nvm は歴史が長く、安定はしているけど、いくつか気になる点があった。

- **シェルの起動が遅くなる** — nvm はシェル起動時に初期化スクリプトを読み込む。シェルを開くたびにわずかなラグが入る
- **シェルごとに設定が必要** — bash と zsh で別々に設定を書く必要がある
- **プロジェクトごとの自動切り替えが面倒** — `.nvmrc` を置いても `nvm use` を手動で叩くか、フックを仕込む必要がある

volta はこのあたりをうまく解決している。

- **シェルに依存しない** — Rust 製のバイナリで、PATH に追加するだけ
- **速い** — シェル起動時のオーバーヘッドがほぼない
- **プロジェクト単位のバージョン固定** — `package.json` に `volta` フィールドを書くだけで、プロジェクトに入ったら自動でバージョンが切り替わる

## 移行手順

### 1. volta をインストール

```bash
curl https://get.volta.sh | bash
```

これだけで `~/.volta/` にインストールされる。インストーラが `.profile` や `.bashrc` に PATH を自動追記してくれるが、zsh を使っている場合は自分で設定した方が確実。

### 2. シェルの設定を更新

`.zshrc` など、普段使っているシェル設定ファイルで nvm の設定を volta に置き換える。

**Before（nvm）:**

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
```

**After（volta）:**

```bash
export VOLTA_HOME="$HOME/.volta"
export PATH="$VOLTA_HOME/bin:$PATH"
```

nvm と比べてだいぶスッキリする。

### 3. Node.js をインストール

```bash
# LTS をインストール
volta install node@22

# 最新版を使いたい場合
volta install node@latest
```

確認：

```bash
$ node --version
v22.22.0

$ which node
/home/user/.volta/bin/node
```

npm も自動で付いてくる。

### 4. nvm をアンインストール

volta で Node.js が動くことを確認したら、nvm を削除する。

```bash
rm -rf ~/.nvm
```

シェル設定から nvm 関連の行を削除するのも忘れずに（ステップ 2 で対応済みなら OK）。

## nvm と volta の違い

| | nvm | volta |
|---|---|---|
| 実装 | シェルスクリプト | Rust バイナリ |
| シェル起動への影響 | 初期化スクリプトの読み込みあり | PATH 追加のみ |
| バージョン切り替え | `nvm use` / `.nvmrc` | `package.json` の `volta` フィールドで自動 |
| シェル設定 | bash / zsh それぞれに記述 | 共通の PATH 設定のみ |
| グローバルツール | npm でインストール | `volta install` で管理 |

## まとめ

移行作業は 30 分もかからなかった。volta のインストール → Node.js インストール → シェル設定の書き換え → nvm の削除、これだけ。

nvm に気になることがあったのは冒頭に述べたとおりだが、正直なところ移行の必要性は、そこまで感じていなかった。ただ、社内ツールの標準化で nvm が使われなくなったため、これもいい機会だと思って移行した。結果的に良い判断だったと思う。

プロジェクトで `package.json` にバージョンを固定しておけばチーム内でのバージョン統一も楽になるので、チーム開発でもおすすめ。
