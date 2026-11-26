#!/usr/bin/env python3
"""ブログ記事を Qiita に転載する（新規は限定共有、qiita_id があれば更新）。

使い方:
  python3 scripts/qiita_post.py content/posts/<dir>/index.md [--public] [--dry-run]

環境変数 QIITA_TOKEN（write_qiita スコープ）が必要。--dry-run では不要。
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://qiita.com/api/v2/items"
REPO_ROOT = Path(__file__).resolve().parent.parent

# ブログのタグ → Qiita で使われている表記。無いものはそのまま送る
TAG_MAP = {
    "claude-code": "ClaudeCode",
    "claude-md": "CLAUDE.md",
    "nodejs": "Node.js",
    "dotfiles": "dotfiles",
    "chezmoi": "chezmoi",
    "volta": "Volta",
    "cloudflare": "Cloudflare",
}
MAX_TAGS = 5


def split_frontmatter(text):
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not m:
        sys.exit("frontmatter（--- で囲まれた YAML）が見つかりません")
    return m.group(1), m.group(2)


def fm_value(fm, key):
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", fm, re.M)
    if not m:
        return None
    raw = m.group(1).strip()
    if raw.startswith("["):
        return json.loads(raw)
    if raw.startswith('"') and raw.endswith('"'):
        return json.loads(raw)
    return raw


def base_url():
    toml = (REPO_ROOT / "hugo.toml").read_text(encoding="utf-8")
    m = re.search(r'^baseURL\s*=\s*"([^"]+)"', toml, re.M)
    if not m:
        sys.exit("hugo.toml に baseURL が見つかりません")
    return m.group(1).rstrip("/") + "/"


def build_payload(path, fm, body, public):
    title = fm_value(fm, "title")
    if not title:
        sys.exit("title がありません")
    tags = fm_value(fm, "qiita_tags") or [TAG_MAP.get(t, t) for t in (fm_value(fm, "tags") or [])]
    tags = list(dict.fromkeys(tags))[:MAX_TAGS]
    if not tags:
        sys.exit("タグが 1 つもありません（Qiita はタグ必須）")

    url = f"{base_url()}posts/{path.parent.name}/"
    # ブログ内の相対リンク（](/posts/...)）は Qiita では切れるので絶対 URL にする
    body = re.sub(r"\]\(/(?!/)", f"]({base_url()}", body)
    # Page Bundle 内の画像（](architecture.svg)）も切れるので記事 URL 起点の絶対 URL にする
    body = re.sub(r"\]\((?![a-zA-Z][\w+.-]*:|/|#)", f"]({url}", body)
    head = f"> この記事は個人ブログ [fantatchi's notes]({url}) からの転載です。\n\n"
    tail = f"\n\n---\n\n初出: [fantatchi's notes]({url})。ほかの記事もブログに置いています。\n"
    return {
        "title": title,
        "body": head + body.strip("\n") + tail,
        "tags": [{"name": t, "versions": []} for t in tags],
        "private": not public,
    }


def request(method, url, payload, token):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"Qiita API エラー: HTTP {e.code} {e.read().decode('utf-8', 'replace')}")


def write_qiita_id(path, text, item_id):
    fm, body = split_frontmatter(text)
    fm = fm + f'\nqiita_id: "{item_id}"'
    path.write_text(f"---\n{fm}\n---\n{body}", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=Path)
    ap.add_argument("--public", action="store_true", help="公開で送る（既定は限定共有）")
    ap.add_argument("--dry-run", action="store_true", help="送信せず内容を表示")
    args = ap.parse_args()

    text = args.path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    payload = build_payload(args.path, fm, body, args.public)
    item_id = fm_value(fm, "qiita_id")
    if item_id and not args.public:
        # 更新時は公開範囲を変えない（公開済みの記事を誤って限定共有へ戻さない）
        del payload["private"]

    if args.dry_run:
        print(f"{'PATCH ' + item_id if item_id else 'POST（新規）'} / private={payload.get('private', '変更しない')}", file=sys.stderr)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    token = os.environ.get("QIITA_TOKEN")
    if not token:
        sys.exit("環境変数 QIITA_TOKEN が設定されていません")

    if item_id:
        res = request("PATCH", f"{API}/{item_id}", payload, token)
    else:
        res = request("POST", API, payload, token)
        write_qiita_id(args.path, text, res["id"])
        print(f"qiita_id を {args.path} に書き込みました", file=sys.stderr)
    print(f"{'公開' if not res.get('private') else '限定共有'}: {res['url']}")


if __name__ == "__main__":
    main()
