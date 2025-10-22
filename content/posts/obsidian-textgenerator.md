+++
date = '2025-10-22T17:20:11+09:00'
title = 'Obsidian で内部リンクを自動化する方法（Text Generator × OpenAI API）'
categories = ["tech"]
tags = ["Obsidian", "Text Generator", "OpenAI API"]
draft = false
+++

## 🧠 概要

Obsidian を使いはじめたころから「グラフビューを活かしたい」と思っていたのですが、内部リンクやタグ付けがどうしても面倒で、つい放置してしまっていました。
テンプレート機能でノート作成時に日付タグを付ける程度の運用はしていたものの、グラフビューを見る限りあまり効果は感じられませんでした。

そんな中で、「生成AIを使えば自動化できるのでは？」と思い立ち、AIに方法を尋ねてみたところ、メモ内容から自動で内部リンクを生成し、ノート整理や検索を効率化できる手順が見つかりました。
今回はその方法を紹介します。

使用ツールは以下の通りです。

* **Obsidian**
* **Text Generator プラグイン**
* **OpenAI API**

---

## ⚙️ 手順概要

### 1. Obsidian の準備

1. **Obsidian をインストール**
   [https://obsidian.md/](https://obsidian.md/) からダウンロードします。
2. 使用する Vault（メモ保管フォルダ）を開きます。

---

### 2. Text Generator プラグインの導入

1. 設定 → 「Community plugins」 → 「Browse」
2. 検索バーに「Text Generator」と入力
3. 「Install」 → 「Enable」をクリック

---

### 3. OpenAI API キーの取得

1. [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys) にアクセス
2. 「+ Create new secret key」から新しい API キーを発行
3. 表示されたキーをコピー（後で Text Generator に設定）

※ OpenAI API を利用するには従量課金の設定が必要です。詳細は公式サイトをご確認ください。

---

### 4. Text Generator の API 設定

1. Obsidian → 設定 → 「Text Generator」
2. **Provider Profile** を「OpenAI Chat」に設定
3. **API Key** に先ほど取得したキーを貼り付け
4. **Model name** は `gpt-4.1-nano` または `gpt-4.1-mini` を推奨（高速・低コスト）
5. **Text Generator Options** で `insert-text-From-template` を有効化

---

### 5. テンプレートファイルの作成

1. Vault 内に `templates/` フォルダを作成
2. `generate-links.md` を作成し、以下を記述：

```md
あなたは Obsidian のノートアシスタントです。  
以下のノートの内容やメタ情報を読み取り、関連しそうな概念やトピックを 3〜5 個提案してください。  
これらは「タグ」ではなく、すべて Obsidian の内部リンク（`[[...]]`）として出力してください。

- 各リンクは 1 語または短いフレーズ（例：[[AI]], [[生成AI]], [[OpenAI]], [[Obsidian]] など）  
- 既存ノートに存在していなくても構いません。  
- 出力フォーマットは以下の通り：

出力フォーマット:
[[link1]] [[link2]] [[link3]]

本文：
{{content}}

---

生成理由や説明文は不要です。出力は上記フォーマットのみでお願いします。
```

---

### 6. Text Generator のテンプレート登録

1. Obsidian → 設定 → 「Text Generator」 → 「Advanced Settings」
2. 「Templates Path」に `templates` を指定
3. コマンド「Text Generator: Templates: Insert Template」から呼び出せるようにします

---

### 7. 実行例

1. Obsidian でノートを作成
2. 「Ctrl + P」でコマンドパレットを開く
3. 「text generator」と入力して「Text Generator: Templates: Insert Template」を選択
4. `generate-links.md` テンプレートを選択
5. 実行すると、カーソル位置に内部リンクが自動挿入されます

---

## 💡 補足

* 他の LLM を利用したい場合は、Text Generator の「LLM Settings」で切り替え可能です。
* 無料で構築したい場合は、ローカルモデルの `ollama` なども利用できます。

---

## ✅ 最終構成例

```
📂 Vault
├─ 📁 templates/
│   └─ generate-links.md
├─ 📁 notes/
│   ├─ sample.md
│   └─ ...
└─ .obsidian/
    └─ plugins/
        └─ obsidian-textgenerator-plugin/
```

---

## ✨ まとめ

この構成により、ノート内容から自動で関連タグや内部リンクを生成できるようになります。
整理や検索が効率化し、知識ベースとしての Obsidian 活用がさらに強化されます。

