#!/usr/bin/env python3
"""modelverse_call.py — minimal CLI for UCloud ModelVerse (OpenAI-compatible).

Subcommands:
    models                  GET /v1/models
    chat   --model M --user TEXT [--system S] [--stream] [--temperature ...]
    image  --model M --prompt P [--size 1024x1024] [--quality ...] [--n N] [--out FILE]
    raw    --path /v1/foo --data @file.json   # passthrough for anything else

Credentials/endpoint via env:
    MODELVERSE_API_KEY   (required)
    MODELVERSE_ENDPOINT  (default: https://api.modelverse.cn)
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_ENDPOINT = "https://api.modelverse.cn"


def env_or_die() -> tuple[str, str]:
    key = os.environ.get("MODELVERSE_API_KEY")
    if not key:
        sys.exit("error: MODELVERSE_API_KEY is not set")
    ep = os.environ.get("MODELVERSE_ENDPOINT", DEFAULT_ENDPOINT).rstrip("/")
    return key, ep


def http(method: str, url: str, *, key: str,
         payload: dict | None = None, stream: bool = False,
         timeout: int = 120):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {key}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        sys.stderr.write(f"HTTP {e.code} {e.reason}\n{body}\n")
        sys.exit(2)
    if stream:
        return resp  # caller iterates
    body = resp.read().decode("utf-8")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


# ---------- subcommands ----------

def cmd_models(args, key: str, endpoint: str) -> int:
    out = http("GET", f"{endpoint}/v1/models", key=key)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def cmd_chat(args, key: str, endpoint: str) -> int:
    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    if args.user:
        messages.append({"role": "user", "content": args.user})
    elif not sys.stdin.isatty():
        messages.append({"role": "user", "content": sys.stdin.read()})
    else:
        sys.exit("error: pass --user TEXT or pipe a prompt on stdin")

    payload = {"model": args.model, "messages": messages, "stream": args.stream}
    if args.temperature is not None:
        payload["temperature"] = args.temperature
    if args.max_tokens is not None:
        payload["max_tokens"] = args.max_tokens

    url = f"{endpoint}/v1/chat/completions"
    if not args.stream:
        out = http("POST", url, key=key, payload=payload)
        if args.raw:
            print(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            print(out["choices"][0]["message"]["content"])
        return 0

    # streaming SSE
    resp = http("POST", url, key=key, payload=payload, stream=True)
    for raw in resp:
        line = raw.decode("utf-8", errors="replace").rstrip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            obj = json.loads(data)
        except json.JSONDecodeError:
            continue
        delta = obj.get("choices", [{}])[0].get("delta", {}).get("content")
        if delta:
            sys.stdout.write(delta)
            sys.stdout.flush()
    sys.stdout.write("\n")
    return 0


def cmd_image(args, key: str, endpoint: str) -> int:
    payload = {"model": args.model, "prompt": args.prompt, "n": args.n}
    if args.size:    payload["size"] = args.size
    if args.quality: payload["quality"] = args.quality
    if args.format:  payload["output_format"] = args.format
    out = http("POST", f"{endpoint}/v1/images/generations", key=key, payload=payload, timeout=300)

    items = out.get("data", [])
    if not items:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 2

    if args.out:
        base = Path(args.out)
        for i, item in enumerate(items):
            suffix = "" if len(items) == 1 else f"-{i+1}"
            target = base.with_name(f"{base.stem}{suffix}{base.suffix or '.png'}")
            if "b64_json" in item:
                target.write_bytes(base64.b64decode(item["b64_json"]))
                print(f"saved: {target}")
            elif "url" in item:
                with urllib.request.urlopen(item["url"], timeout=120) as r:
                    target.write_bytes(r.read())
                print(f"saved: {target}  (from {item['url']})")
    else:
        # no --out: dump JSON so user can pipe to jq
        print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def cmd_raw(args, key: str, endpoint: str) -> int:
    payload = None
    if args.data:
        src = sys.stdin if args.data == "-" else open(args.data.lstrip("@"), "r", encoding="utf-8")
        with src as f:
            payload = json.load(f)
    method = args.method.upper()
    url = endpoint + args.path if args.path.startswith("/") else endpoint + "/" + args.path
    out = http(method, url, key=key, payload=payload, timeout=args.timeout)
    print(out if isinstance(out, str) else json.dumps(out, indent=2, ensure_ascii=False))
    return 0


# ---------- CLI ----------

def main() -> int:
    ap = argparse.ArgumentParser(description="Call UCloud ModelVerse (OpenAI-compatible).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("models", help="GET /v1/models").set_defaults(func=cmd_models)

    p = sub.add_parser("chat", help="POST /v1/chat/completions")
    p.add_argument("--model", required=True)
    p.add_argument("--user")
    p.add_argument("--system")
    p.add_argument("--stream", action="store_true")
    p.add_argument("--temperature", type=float)
    p.add_argument("--max-tokens", type=int)
    p.add_argument("--raw", action="store_true", help="print full JSON response")
    p.set_defaults(func=cmd_chat)

    p = sub.add_parser("image", help="POST /v1/images/generations")
    p.add_argument("--model", required=True)
    p.add_argument("--prompt", required=True)
    p.add_argument("--size")
    p.add_argument("--quality")
    p.add_argument("--format", choices=["png", "jpeg"])
    p.add_argument("--n", type=int, default=1)
    p.add_argument("--out", help="file to save image(s) to; suffix added when n>1")
    p.set_defaults(func=cmd_image)

    p = sub.add_parser("raw", help="passthrough POST/GET to any /v1/... path")
    p.add_argument("--method", default="POST")
    p.add_argument("--path", required=True, help="e.g. /v1/embeddings")
    p.add_argument("--data", help="JSON file path, '@file.json', or '-' for stdin")
    p.add_argument("--timeout", type=int, default=120)
    p.set_defaults(func=cmd_raw)

    args = ap.parse_args()
    key, endpoint = env_or_die()
    return args.func(args, key, endpoint)


if __name__ == "__main__":
    sys.exit(main())
