# ElevenLabs Music

本文介绍 ElevenLabs `music-v1` 音乐生成模型的调用方式，支持标准生成、流式生成、详细模式和曲谱生成四个端点。

> **官方文档参考**：
> - [Compose music](https://elevenlabs.io/docs/api-reference/music/compose)
> - [Stream music](https://elevenlabs.io/docs/api-reference/music/stream)
> - [Compose music with details](https://elevenlabs.io/docs/api-reference/music/compose-detailed)
> - [Create composition plan](https://elevenlabs.io/docs/api-reference/music/create-composition-plan)

---

## 音乐生成（同步）[官方文档](https://elevenlabs.io/docs/api-reference/music/compose)

### 接口

`POST https://api.modelverse.cn/v1/audio/music/generate`

### 输入

| 参数 | 类型 | 是否必选 | 描述 |
| :--- | :--- | :--- | :--- |
| model | string | 是 | 模型名称，固定为 `music-v1` |
| input | string | 二选一 | 音乐描述提示词，最多 4100 字符。与 `composition_plan` 不可同时使用 |
| composition_plan | object | 二选一 | 结构化曲谱计划，用于精确控制音乐生成。与 `input` 不可同时使用 |
| composition_plan.positive_global_styles | array | 否 | 全局正面风格标签 |
| composition_plan.negative_global_styles | array | 否 | 全局负面风格标签（不希望出现的风格） |
| composition_plan.sections | array(object) | 否 | 乐章列表 |
| composition_plan.sections.section_name | string | 否 | 乐章名称 |
| composition_plan.sections.positive_local_styles | array(string) | 否 | 乐章正面风格 |
| composition_plan.sections.negative_local_styles | array(string) | 否 | 乐章负面风格 |
| composition_plan.sections.duration_ms | integer | 否 | 乐章时长（毫秒） |
| composition_plan.sections.lines | array(string) | 否 | 歌词行 |
| music_length_ms | integer | 否 | 音乐时长（毫秒），范围 3000-600000。仅与 `input` 配合使用，不填则模型自动决定 |
| seed | integer | 否 | 随机种子，范围 0-2147483647，用于生成更一致的结果。仅与 `composition_plan` 配合使用，不可与 `input` 同时使用 |
| force_instrumental | boolean | 否 | 是否强制生成纯音乐，默认 `false`。仅与 `input` 配合使用 |
| output_format | string | 否 | 输出音频格式，如 `mp3_22050_32`（mp3，22.05kHz，32kbps） |

### 请求示例

```shell
curl --location 'https://api.modelverse.cn/v1/audio/music/generate' \
--header 'Authorization: Bearer <YOUR_API_KEY>' \
--header 'Content-Type: application/json' \
--data '{
  "model": "music-v1",
  "input": "A happy piano melody with soft jazz undertones",
  "music_length_ms": 30000,
  "output_format": "mp3_22050_32"
}' \
--output music.mp3
```

### 输出

直接返回音频二进制流，格式由 `output_format` 决定，默认为 mp3。

### 响应头

| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| song-id | string | 生成歌曲的唯一标识 |

---

## 音乐生成（流式）[官方文档](https://elevenlabs.io/docs/api-reference/music/stream)

### 接口

`POST https://api.modelverse.cn/v1/audio/music/stream`

流式端点的请求参数与标准生成完全一致，区别在于响应以流式方式返回音频数据，适用于需要边生成边播放的场景。

### 输入

参数与 [音乐生成（同步）](#音乐生成同步) 相同。

### 请求示例

```shell
curl --location 'https://api.modelverse.cn/v1/audio/music/stream' \
--header 'Authorization: Bearer <YOUR_API_KEY>' \
--header 'Content-Type: application/json' \
--data '{
  "model": "music-v1",
  "input": "A calm guitar piece with nature sounds",
  "music_length_ms": 30000,
  "output_format": "mp3_22050_32"
}' \
--output music_stream.mp3
```

### 输出

以流式方式返回音频二进制数据。

---

## 音乐生成（详细模式）[官方文档](https://elevenlabs.io/docs/api-reference/music/compose-detailed)

### 接口

`POST https://api.modelverse.cn/v1/audio/music/detailed`

详细模式端点除了返回音频外，还会返回模型生成的曲谱计划和歌曲元数据。

### 输入

| 参数 | 类型 | 是否必选 | 描述 |
| :--- | :--- | :--- | :--- |
| model | string | 是 | 模型名称，固定为 `music-v1` |
| input | string | 二选一 | 音乐描述提示词，最多 4100 字符。与 `composition_plan` 不可同时使用 |
| composition_plan | object | 二选一 | 结构化曲谱计划。与 `input` 不可同时使用 |
| music_length_ms | integer | 否 | 音乐时长（毫秒），范围 3000-600000。仅与 `input` 配合使用 |
| seed | integer | 否 | 随机种子，范围 0-2147483647。仅与 `composition_plan` 配合使用，不可与 `input` 同时使用 |
| force_instrumental | boolean | 否 | 是否强制生成纯音乐，默认 `false`。仅与 `input` 配合使用 |
| respect_sections_durations | boolean | 否 | 是否严格遵循乐章时长，默认 `true`。仅与 `composition_plan` 配合使用 |
| with_timestamps | boolean | 否 | 是否返回歌词时间戳，默认 `false` |
| output_format | string | 否 | 输出音频格式 |

### 请求示例

```shell
curl --location 'https://api.modelverse.cn/v1/audio/music/detailed' \
--header 'Authorization: Bearer <YOUR_API_KEY>' \
--header 'Content-Type: application/json' \
--data '{
  "model": "music-v1",
  "input": "An upbeat jazz tune",
  "music_length_ms": 10000
}' \
--output music_detailed.mp3
```

### 输出

响应为 `multipart/mixed` 格式，包含两部分：

1. **JSON 元数据** — 包含曲谱计划和歌曲元信息
2. **音频二进制数据** — 生成的音频文件

### 元数据结构

| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| composition_plan | object | 模型生成的曲谱计划 |
| composition_plan.positive_global_styles | array | 全局正面风格标签 |
| composition_plan.negative_global_styles | array | 全局负面风格标签 |
| composition_plan.sections | array(object) | 乐章列表 |
| composition_plan.sections.section_name | string | 乐章名称 |
| composition_plan.sections.positive_local_styles | array(string) | 乐章正面风格 |
| composition_plan.sections.negative_local_styles | array(string) | 乐章负面风格 |
| composition_plan.sections.duration_ms | integer | 乐章时长（毫秒） |
| composition_plan.sections.lines | array(string) | 歌词行 |
| song_metadata | object | 歌曲元信息 |
| song_metadata.title | string | 歌曲标题 |
| song_metadata.description | string | 歌曲描述 |
| song_metadata.genres | array | 音乐流派 |
| song_metadata.languages | array | 语言 |
| song_metadata.is_explicit | boolean | 是否包含敏感内容 |

### 元数据响应示例

```json
{
  "composition_plan": {
    "positive_global_styles": ["jazz", "upbeat"],
    "negative_global_styles": ["heavy metal", "aggressive"],
    "sections": [
      {
        "section_name": "Intro",
        "positive_local_styles": ["piano", "light percussion"],
        "negative_local_styles": ["vocals", "distortion"],
        "duration_ms": 3000,
        "lines": []
      },
      {
        "section_name": "Verse",
        "positive_local_styles": ["saxophone", "swing rhythm"],
        "negative_local_styles": ["harsh drums"],
        "duration_ms": 7000,
        "lines": ["Swinging through the night..."]
      }
    ]
  },
  "song_metadata": {
    "title": "Jazz Evening",
    "description": "An upbeat jazz composition",
    "genres": ["jazz"],
    "languages": ["en"],
    "is_explicit": false
  }
}
```

---

## 曲谱生成 [官方文档](https://elevenlabs.io/docs/api-reference/music/create-composition-plan)

### 接口

`POST https://api.modelverse.cn/v1/audio/music/plan`

根据文字描述生成结构化曲谱计划，可用于后续音乐生成。**该端点不消耗额度。**

### 输入

| 参数 | 类型 | 是否必选 | 描述 |
| :--- | :--- | :--- | :--- |
| model | string | 是 | 模型名称，固定为 `music-v1` |
| prompt | string | 是 | 曲谱描述提示词，最多 4100 字符 |
| music_length_ms | integer | 否 | 总时长（毫秒），范围 3000-600000。不填则模型自动决定 |
| source_composition_plan | object | 否 | 基于已有曲谱生成新曲谱 |

### 请求示例

```shell
curl --location 'https://api.modelverse.cn/v1/audio/music/plan' \
--header 'Authorization: Bearer <YOUR_API_KEY>' \
--header 'Content-Type: application/json' \
--data '{
  "model": "music-v1",
  "prompt": "A soft lullaby with gentle piano and female vocals",
  "music_length_ms": 30000
}'
```

### 输出

| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| positive_global_styles | array | 全局正面风格标签（建议使用英文） |
| negative_global_styles | array | 全局负面风格标签（建议使用英文） |
| sections | array(object) | 乐章列表 |
| sections.section_name | string | 乐章名称 |
| sections.positive_local_styles | array(string) | 乐章正面风格 |
| sections.negative_local_styles | array(string) | 乐章负面风格 |
| sections.duration_ms | integer | 乐章时长（毫秒） |
| sections.lines | array(string) | 歌词行 |

### 响应示例

```json
{
  "positive_global_styles": ["lullaby", "soft", "gentle", "calming", "acoustic"],
  "negative_global_styles": ["loud", "heavy drums", "fast tempo", "aggressive"],
  "sections": [
    {
      "section_name": "Verse 1",
      "positive_local_styles": ["soft female vocal", "gentle acoustic guitar", "slow tempo"],
      "negative_local_styles": ["percussion", "bass guitar"],
      "duration_ms": 15000,
      "lines": [
        "Close your eyes and drift away,",
        "Safe and sound until the day."
      ]
    },
    {
      "section_name": "Verse 2",
      "positive_local_styles": ["soft female vocal", "hushed delivery", "dreamy atmosphere"],
      "negative_local_styles": ["strong vocals", "drums"],
      "duration_ms": 15000,
      "lines": [
        "Stars above are shining bright,",
        "Sleep now, darling, sleep so deep."
      ]
    }
  ]
}
```

> **提示**：生成的 `composition_plan` 可以直接传入音乐生成接口的 `composition_plan` 参数，实现基于曲谱的精确音乐生成。
