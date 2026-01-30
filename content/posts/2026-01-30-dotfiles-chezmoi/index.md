---
title: "dotfiles管理を独自スクリプトからchezmoiに移行した"
date: 2026-01-30
draft: false
tags: ["dotfiles", "chezmoi", "WSL"]
---

## dotfiles とは

`.zshrc` や `.vimrc` など、ドット（`.`）で始まる設定ファイル群を **dotfiles** と呼ぶ。これらを Git で管理しておくと、複数の PC 間で開発環境を統一したり、新しい PC を素早くセットアップしたりできる。

## 移行前の構成

`~/dotfiles` に設定ファイルを置き、`install.sh` でシンボリックリンク（ショートカットのようなもので、実体ファイルを一箇所で管理しつつ本来の場所から参照させる仕組み）を貼る方式で管理していた。

```text
~/dotfiles/
├── .zshrc
├── .zsh/          # env, options, bindings, ohmy
├── .vimrc
├── .vim/          # init.vim, init/
├── .tmux.conf
├── .tmux/plugins/ # TPM (git submodule)
├── install.sh     # ln -sf でリンクを貼るスクリプト
└── README.md
```

`install.sh` の中身はシンボリックリンク作成 + oh-my-zsh / TPM のインストール。

## なぜ [chezmoi](https://www.chezmoi.io/)（シェイ・モワ）に移行したか

独自スクリプト方式には以下の課題があった。

- **ファイル追加のたびに install.sh を手動更新する必要がある** — 管理対象が増えるほど面倒
- **テンプレート機能がない** — PC ごとにトークンやホスト固有設定を変えたい場合、自分で分岐を書く必要がある
- **シンボリックリンク方式の制限** — WSL から Windows 側パスにはリンクが貼れないなど、環境をまたぐと問題が出る

chezmoi はこれらを解決する。

- `chezmoi add ~/.zshrc` だけで管理対象に追加される（スクリプト編集不要）
- テンプレート機能で `.tmpl` ファイルにすればトークンなどを変数化できる
- `chezmoi diff` で適用前に差分確認、`chezmoi apply` で一発適用
- git 連携が組み込み（ソースディレクトリ自体が git リポジトリ）

一方、oh-my-zsh や TPM のインストールのような「ファイル配置以外の処理」は chezmoi でも `run_once_` スクリプト（初回セットアップ時に一度だけ自動実行されるシェルスクリプト）として書くので、そこの手間は変わらない。

## 移行手順

### 1. chezmoi のインストール

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- -b ~/.local/bin
chezmoi init
```

`~/.local/share/chezmoi/` にソースディレクトリが作られる。

### 2. シンボリックリンクを実ファイルに戻す

既存の install.sh がシンボリックリンクを貼っていたため、chezmoi が「リンク先」ではなく「リンクそのもの」を管理してしまう。先にリンクを解除して実ファイルに置き換えた。

```bash
# 単体ファイルのリンクを実体に置き換える
for f in ~/.zshrc ~/.vimrc ~/.tmux.conf; do
  target=$(readlink "$f")  # リンク先のパスを取得
  rm "$f"                  # シンボリックリンクを削除
  cp "$target" "$f"        # リンク先の実体をコピー
done

# ディレクトリも同様に置き換える
for d in ~/.zsh ~/.vim; do
  target=$(readlink "$d")
  rm "$d"
  cp -r "$target" "$d"    # -r でディレクトリごとコピー
done
```

### 3. chezmoi add で管理対象に追加

```bash
chezmoi add ~/.zshrc
chezmoi add ~/.zsh
chezmoi add ~/.vimrc
chezmoi add ~/.vim/init.vim
chezmoi add ~/.vim/init
chezmoi add ~/.tmux.conf
chezmoi add ~/.claude/CLAUDE.md
chezmoi add ~/.claude/settings.json
```

chezmoi はファイル名を `dot_zshrc`、`dot_vim/` のように変換してソースディレクトリに保存する。これはドットで始まるファイルが OS 上で隠しファイル扱いになるのを防ぐためだ。

### 4. run_once スクリプトの作成

`run_once_install-packages.sh` として oh-my-zsh と TPM のインストールを記述。chezmoi は `run_once_` プレフィックスのスクリプトを初回の `chezmoi apply` 時に一度だけ実行する。

### 5. MCP 設定のテンプレート化

Claude の `mcp.json` には GitHub トークンが含まれるため、テンプレート機能で分離した。

**`.chezmoi.toml.tmpl`** — `chezmoi init` 時に対話的にトークンを聞く：

```toml
[data]
  github_token = {{ promptStringOnce . "github_token" "GitHub Personal Access Token" | quote }}
```

**`dot_claude/mcp.json.tmpl`** — トークンを変数で参照：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": {{ .github_token | quote }}
      }
    }
  }
}
```

入力されたトークンは `~/.config/chezmoi/chezmoi.toml` に保存される。このファイルは chezmoi のソースディレクトリの外にあるため git にはコミットされない。

### 6. GitHub リポジトリに push

ソースディレクトリを既存の dotfiles リポジトリに紐付けて push。

## 移行後の構成

```text
~/.local/share/chezmoi/
├── .chezmoi.toml.tmpl
├── .chezmoiignore
├── dot_claude/
│   ├── CLAUDE.md
│   ├── mcp.json.tmpl
│   └── settings.json
├── dot_tmux.conf
├── dot_vim/
│   ├── init.vim
│   └── init/
├── dot_vimrc
├── dot_zsh/
├── dot_zshrc
└── run_once_install-packages.sh
```

## 新しい PC でのセットアップ

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply fantatchi
```

これだけで全設定ファイルの配置、oh-my-zsh / TPM のインストール、GitHub トークンの設定が完了する。

## VSCode の設定について

VSCode は Settings Sync（組み込み機能）で GitHub/Microsoft アカウント経由の同期ができるため、dotfiles での管理は不要と判断した。

---

移行後のリポジトリはこちら: [fantatchi/dotfiles](https://github.com/fantatchi/dotfiles)
