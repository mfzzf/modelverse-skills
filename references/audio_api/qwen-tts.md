# 通义千问 Qwen-TTS

本文介绍 `modelverse` 接入的阿里云通义千问语音合成模型 `qwen3-tts-flash` 调用 API 的输入输出参数，供您使用接口时查阅字段含义。

该模型提供多种拟人音色，支持多语言及中文方言，并可在同一音色下输出多语言内容，系统可自适应语气、流畅处理复杂文本。

## 支持的模型

| 模型              | 说明                                                                                              |
| :---------------- | :------------------------------------------------------------------------------------------------ |
| `qwen3-tts-flash` | 按字符计费、低延迟，适合导航播报、通知、在线教育课件、短文本高频合成等场景。支持多语种与中文方言。 |

## 同步合成

### 接口

`https://api.modelverse.cn/v1/audio/speech`

> 说明：该接口与 OpenAI `/v1/audio/speech` 路径兼容，但 **响应体为阿里云原始 JSON**（包含音频 URL），并非 OpenAI 的二进制音频流。请参见下文 [响应格式](#响应格式) 章节。

### 请求参数

| 参数                     | 类型   | 是否必选 | 描述                                                                                                                                                                                                                                                                                                |
| :----------------------- | :----- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| model                    | string | 是       | 要使用的 TTS 模型名称，取值见上文 [支持的模型](#支持的模型)，例如：`qwen3-tts-flash`                                                                                                                                                                                                                |
| input                    | string | 是       | 需要合成语音的文本，支持多语种混合输入，最长 `600` 字符                                                                                                                                                                                                                                            |
| voice                    | string | 是       | 使用的系统音色名称，例如：`Cherry`、`Ethan`、`Serena`、`Chelsie` 等。完整音色列表请参见 [阿里云官方音色列表](https://help.aliyun.com/zh/model-studio/qwen-tts)                                                                                                                                         |
| metadata.language_type   | string | 否       | 指定合成音频的语种。不传时为 `Auto`（自动识别，适合无法确定语种或混合语言文本）。文本为单一语种时指定具体语种可显著提升合成质量。可选值：`Chinese`、`English`、`German`、`Italian`、`Portuguese`、`Spanish`、`Japanese`、`Korean`、`French`、`Russian`、`Auto`（大小写均可）。值由上游校验，非法值会返回 `400` 错误并在 `message` 中列出当前支持的完整语种列表。 |

### 请求示例

⚠️ 如果您使用 Windows 系统，建议使用 Postman 或其他 API 调用工具。

#### curl

```bash
curl https://api.modelverse.cn/v1/audio/speech \
  -H "Authorization: Bearer $MODELVERSE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-tts-flash",
    "input": "那我来给大家推荐一款T恤，这款呢真的是超级好看，这个颜色呢很显气质。",
    "voice": "Cherry"
  }'
```

#### python

```python
import os
import requests

resp = requests.post(
    "https://api.modelverse.cn/v1/audio/speech",
    headers={
        "Authorization": f"Bearer {os.getenv('MODELVERSE_API_KEY')}",
        "Content-Type": "application/json",
    },
    json={
        "model": "qwen3-tts-flash",
        "input": "那我来给大家推荐一款T恤，这款呢真的是超级好看，这个颜色呢很显气质。",
        "voice": "Cherry",
    },
)
data = resp.json()
audio_url = data["output"]["audio"]["url"]
print("audio url:", audio_url)

# 下载音频
audio_bytes = requests.get(audio_url).content
with open("output.wav", "wb") as f:
    f.write(audio_bytes)
```

### 指定语种（可选）

当输入文本为单一语种时，通过 `metadata.language_type` 显式指定语种可获得更精准的发音和更自然的语调，效果通常优于默认的 `Auto`：

```bash
curl https://api.modelverse.cn/v1/audio/speech \
  -H "Authorization: Bearer $MODELVERSE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-tts-flash",
    "input": "今天天气真好，我们去公园散步吧。",
    "voice": "Cherry",
    "metadata": {
      "language_type": "Chinese"
    }
  }'
```

## 响应格式

接口返回 `application/json`，为阿里云 DashScope 原始响应结构透传。客户端需从 `output.audio.url` 字段中取到音频 URL 再自行下载（URL 有效期为 **24 小时**）。

### 输出

| 参数                       | 类型    | 描述                                                                                                                      |
| :------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------ |
| request_id                 | string  | 本次请求的唯一标识，可用于定位和排查问题                                                                                  |
| code                       | string  | 业务错误码，成功时为空字符串                                                                                              |
| message                    | string  | 业务错误信息，成功时为空字符串                                                                                            |
| output                     | object  | 模型输出                                                                                                                  |
| output.finish_reason       | string  | 结束原因：生成中为 `null`，正常结束为 `stop`                                                                              |
| output.audio               | object  | 合成音频信息                                                                                                              |
| output.audio.url           | string  | 合成音频的完整文件 URL，有效期 24 小时                                                                                    |
| output.audio.data          | string  | 流式输出时的 Base64 音频数据（当前仅同步模式，固定为空字符串）                                                            |
| output.audio.id            | string  | 音频信息的 ID                                                                                                             |
| output.audio.expires_at    | integer | 音频 URL 的过期时间戳                                                                                                     |
| usage                      | object  | 本次请求的用量信息                                                                                                        |
| usage.characters           | integer | 输入文本字符数，计费依据                                                                                                  |
| usage.input_tokens         | integer | 固定为 `0`                                                                                                                |
| usage.output_tokens        | integer | 固定为 `0`                                                                                                                |

### 响应示例

```json
{
  "request_id": "5c63c65c-cad8-4bf4-959d-xxxxxxxxxxxx",
  "code": "",
  "message": "",
  "output": {
    "finish_reason": "stop",
    "audio": {
      "data": "",
      "url": "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/xx/xxxxxxxx.wav?Expires=1766113409&OSSAccessKeyId=LTAI5xxxxxx&Signature=xxxxxx",
      "id": "audio_5c63c65c-cad8-4bf4-959d-xxxxxxxxxxxx",
      "expires_at": 1766113409
    }
  },
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0,
    "characters": 195
  }
}
```

## 错误响应

当请求失败时，接口会返回标准 JSON 格式错误响应：

```json
{
  "error": {
    "message": "错误描述信息",
    "type": "invalid_request_error",
    "code": "error_code",
    "param": "<请求 ID，用于反馈或排查错误原因>"
  }
}
```

## 注意事项

1. **响应不是二进制音频流**：与 OpenAI 原生 `/v1/audio/speech` 不同，本接口返回 JSON 而非音频字节。若您此前已用 OpenAI SDK 对接本接口（例如 `with_streaming_response.create(...).stream_to_file(...)`），请改为解析 JSON 并二次下载 `output.audio.url`。
2. **音频 URL 有效期 24 小时**：请及时下载或将其落盘到您自己的对象存储。
3. **文本长度限制**：最长 `600` 字符，超长文本请自行切分。
4. **计费方式**：按字符数计费，以上游返回的 `usage.characters` 为准。
5. **音色选择**：`voice` 字段需传入阿里云系统音色名称（如 `Cherry`），完整列表请参见阿里云官方文档。
