---
name: modelverse-api
description: Call any model on UCloud ModelVerse (UModelVerse) — text chat, embeddings, rerank, image generation/edit, video generation, audio TTS/STT — through its OpenAI-compatible endpoints. Use whenever the user wants to invoke a hosted model on ModelVerse, asks "how do I call DeepSeek/Qwen/gpt-image-2/Sora-2/Kling/Veo/Suno via UCloud", needs the right endpoint domain, wants OpenAI/Gemini/Claude compatibility differences, hits an error code, or wants curl/python snippets. Trigger on: "ModelVerse", "UModelVerse", "api.modelverse.cn", "api.umodelverse.ai", `MODELVERSE_API_KEY`, any model name hosted by ModelVerse (DeepSeek-R1/V3, gpt-5, gpt-image-1/2, gemini-2.5/3-flash-image, Wan2.x, Kling, Veo, Sora-2, MiniMax-Hailuo, Suno, Qwen-TTS, …), or Chinese phrases like "调用 ModelVerse", "UCloud 模型市场", "用 OpenAI 兼容接口调 …".
---

# modelverse-api

Operational entry point for UCloud's **ModelVerse / UModelVerse** model service platform.

ModelVerse is OpenAI-compatible at the wire level: one base URL, one `Authorization: Bearer <key>` header, then any `/v1/...` path you would use against OpenAI. That covers ~80% of calls. The remaining 20% — Gemini/Claude-compatible routes, image/video/audio async tasks, batch APIs — is what `references/docs/` exists for.

When the user asks for a ModelVerse call:

1. Pick the **endpoint** for their region (§2).
2. Pick the **route shape** from the decision table (§3).
3. Read the per-model recipe in `references/{text,image,video,audio}_api/<model>.md` if the model has quirks — `gpt-image-2`, `Sora-2`, `Kling-v3`, `Veo-3.1`, `Suno`, etc. all have model-specific param tables.
4. Use `scripts/modelverse_call.py` for ad-hoc calls and ops; switch to the `openai` SDK for production code (it Just Works since the API is OpenAI-compatible).

---

## 1. Credentials

Read from env vars. Never hard-code keys in code or chat output.

```bash
export MODELVERSE_API_KEY="sk-..."           # required
export MODELVERSE_ENDPOINT="https://api.modelverse.cn"   # optional, see §2
```

Keys come from the ModelVerse console (`console.ucloud.cn/modelverse/experience/api-keys`). For provisioning / lifecycle of keys via OpenAPI, use the sibling **`ucloud-api`** skill (`CreateUMInferAPIKey` / `ListUMInferAPIKey` / `DeleteUMInferAPIKey`) — that's the *control plane*; this skill is the *data plane*.

---

## 2. Endpoints

| Region | Domain | Notes |
|---|---|---|
| China mainland | `https://api.modelverse.cn` | default; lowest latency for CN |
| Global / overseas (no `.cn`) | `https://api.umodelverse.ai` | same payloads as CN |
| Singapore | `https://api-sg.umodelverse.ai` | SEA users |
| US — Los Angeles | `https://api-us-ca.umodelverse.ai` | overseas, data does not return to CN |

All four serve identical OpenAI-compatible paths. Pick on latency / data-residency requirements. Switch via `MODELVERSE_ENDPOINT` or the helper's `--endpoint` flag.

---

## 3. Decision table — what route do I call

| Goal | Path | Notes |
|---|---|---|
| List available models | `GET /v1/models` | no auth required at some endpoints, send the key anyway |
| Chat completion (any text model) | `POST /v1/chat/completions` | OpenAI shape; `stream: true` for SSE |
| OpenAI Responses API (tools, structured outputs) | `POST /v1/response` | follow OpenAI's Responses spec |
| Embeddings | `POST /v1/embeddings` | `BAAI/bge-*`, `Qwen-embedding-*`, OpenAI-style |
| Rerank | `POST /v1/rerank` | non-OpenAI route; see `references/text_api/rerank.md` |
| Image generation | `POST /v1/images/generations` | `gpt-image-1/2`, `flux-*`, `gemini-*-image`, `Wan-*`, `doubao-seedream`, … |
| Image edit (with input) | `POST /v1/images/edits` (multipart) | mask optional; `gpt-image-2`, `flux-kontext-*`, `Qwen-Image-Edit` |
| Video generation (async) | `POST /v1/video/generations` → poll | task-based; `Sora-2`, `Veo-3.1`, `Kling`, `MiniMax-Hailuo`, `Wan-*`, `Vidu-*`, `HappyHorse-*`, `doubao-seedance-*` |
| Audio TTS / music / voice clone | `POST /v1/audio/...` | `Suno`, `qwen-tts`, `elevenlabs-music`, `MiniMax-speech`, IndexTTS, … |
| Gemini-native shape | `POST /v1beta/...` (Gemini-compatible) | `references/text_api/gemini_compatible.md` |
| Anthropic / Claude-native shape | `POST /v1/messages` (Claude-compatible) | `references/text_api/claude_compatible.md` |
| Batch jobs (OpenAI-style) | `POST /v1/batches` | see `references/text_api/openai-batch-compatible.md` |
| Gemini batch | see Gemini batch doc | `references/text_api/gemini-batch.md` |

When in doubt, default to the OpenAI shape — it covers every text and most image generations.

---

## 4. Quick workflow

### 4.1 List models, pick one

```bash
./scripts/modelverse_call.py models | jq '.data[].id' | sort
```

### 4.2 Chat completion (curl)

```bash
curl -sS "$MODELVERSE_ENDPOINT/v1/chat/completions" \
  -H "Authorization: Bearer $MODELVERSE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-ai/DeepSeek-V3.2-Think",
    "messages": [{"role":"user","content":"hello"}]
  }' | jq -r '.choices[0].message.content'
```

### 4.3 Chat completion (helper)

```bash
./scripts/modelverse_call.py chat \
  --model deepseek-ai/DeepSeek-V3.2-Think \
  --user "summarize the diff between RAG and fine-tuning in 3 bullets"

# streaming
./scripts/modelverse_call.py chat --stream \
  --model gpt-5 \
  --user "write a haiku about tcp retransmits"
```

### 4.4 Image generation

```bash
./scripts/modelverse_call.py image \
  --model gpt-image-2 \
  --prompt "a cyberpunk vending machine in a Tokyo alley, neon, rainy" \
  --size 1024x1536 --quality high \
  --out vending.png
```

### 4.5 Production code (recommended)

Use the official `openai` SDK — ModelVerse is wire-compatible:

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://api.modelverse.cn/v1",
    api_key=os.environ["MODELVERSE_API_KEY"],
)
r = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3.2-Think",
    messages=[{"role": "user", "content": "hi"}],
)
print(r.choices[0].message.content)
```

For images, use `client.images.generate(model="gpt-image-2", ...)`. For Gemini-native or Claude-native flows, use those SDKs against the corresponding base URLs documented in `references/docs/`.

---

## 5. Per-model quirks (read before first call)

The model recipe under `references/<kind>_api/<model>.md` is authoritative. Notable ones:

- **`gpt-image-2`** — size must be 16-pixel multiple, total pixels 655360–8294400, aspect ratio ≤ 3:1; response is `b64_json`. URL responses, if returned, expire in 7 days.
- **`gemini-2.5-flash-image` / `gemini-3-pro-image` / `gemini-3.1-flash-image-preview`** — different output classification (text vs image price split), see ModelVerse pricing doc.
- **`Sora-2` / `Veo-3.1` / `Kling-*` / `MiniMax-Hailuo-*` / `Wan-2.x` / `Vidu-*` / `HappyHorse-*` / `doubao-seedance-*`** — all video models are **async**: POST returns a task id, you poll status to get the URL. Don't wait synchronously.
- **`deepseek-ai/DeepSeek-R1` / `DeepSeek-V3.2-Think`** — separate "think" / reasoning content channel; see `references/text_api/deepseek.md`.
- **`Doubao` models** — same idea for thinking, see `references/text_api/doubao.md`.
- **Embeddings** — multiple providers, dimension sizes differ; see `references/text_api/embeddings.md`.
- **Audio** — every audio model has its own params; never assume a unified shape.

---

## 6. Error codes (cheatsheet)

| HTTP | Code | Meaning | Action |
|---|---|---|---|
| 400 | `param_error` | unknown/invalid param | check the per-model recipe |
| 400 | `invalid_messages` / `sensitive_check_error` | content moderation | rewrite the prompt |
| 400 | `model_error` | no permission for this model | check `GrantAllModels` / `GrantedModels` on the API key (use `ucloud-api` skill) |
| 400 | `tokens_too_long` | prompt > context | truncate or summarize input |
| 401 | `auth_error` | bad key | rotate; check `Authorization: Bearer` header |
| 408 / 504 | `timeout` / `gateway_timeout_error` | upstream slow | retry; prefer `stream: true` for long generations |
| 429 | `rate_limit` | quota / RPS hit | backoff exponentially; check `DailyLimitAmount` on the key |
| 500 | `internal_error` / `model_server_error` | platform / model | retry with jitter |

Full table: `references/common/error-code.md`.

---

## 7. When to dig deeper

- Reading any specific model's params → `references/{text,image,video,audio}_api/<model>.md`
- Provisioning / rotating API keys via OpenAPI → use sibling skill **`ucloud-api`**
- API-key permission semantics → `references/common/api-key.md`
- Auth / endpoints in detail → `references/common/certificate.md`
- Error code reference → `references/common/error-code.md`
- Quick-start narrative → `references/quick-start.md`
- Q&A grab-bag → `references/qa.md`
- Browse-everything index → `references/INDEX.md`

---

## 8. Keeping references/ current

`references/` is a verbatim mirror of upstream `channel-docs/ai-docs/modelverse` `api_doc/`. Refresh it whenever you suspect the upstream added/changed a model:

```bash
scripts/update-docs.sh             # sync + show diff (does not commit)
scripts/update-docs.sh --commit    # sync + commit if changed
```

The script:
- shallow-clones the upstream repo into a temp dir,
- `rsync --delete`'s `api_doc/` into `references/` so files removed upstream disappear locally,
- strips `_meta.json` and `*.png` (nav/asset noise),
- regenerates `references/INDEX.md` with the upstream commit/date footer,
- shows `git diff --stat` and (with `--commit`) lands a `sync references/ from upstream@<sha>` commit.

Override upstream URL or branch with env vars: `UPSTREAM=...` / `BRANCH=...`. The default points at the internal GitLab over HTTPS; that obviously requires VPN / on-corp network and credentialed access to the repo.

Cadence: run before any nontrivial work that depends on a new model; otherwise quarterly is fine. The control plane (`ucloud-api`) and data plane (this skill) are intentionally decoupled — bumping one doesn't require bumping the other.
