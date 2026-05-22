# ElevenLabs Text to Sound v2

本文介绍 ElevenLabs `eleven_text_to_sound_v2` 音效生成模型的调用方式，支持将文字描述转换为音效音频。

> **官方文档参考**：
> - [Create sound effect](https://elevenlabs.io/docs/api-reference/sound-generation)

---

## 音效生成（同步）

### 接口

`POST https://api.modelverse.cn/v1/audio/sound-generation`

将文字描述转换为音效音频，适用于视频、配音或游戏等场景。

### 输入

| 参数 | 类型 | 是否必选 | 描述 |
| :--- | :--- | :--- | :--- |
| model | string | 是 | 模型名称，固定为 `text-to-sound-v2` |
| text | string | 是 | 音效描述文本，描述你想要生成的声音 |
| loop | boolean | 否 | 是否生成可循环的音效，默认 `false`。仅 `eleven_text_to_sound_v2` 模型支持 |
| duration_seconds | double | 否 | 音效时长（秒），范围 0.5-30。不填则由模型根据描述自动决定 |
| prompt_influence | double | 否 | 提示词影响程度，范围 0-1，默认 `0.3`。值越高生成结果越贴近描述，但多样性降低 |
| output_format | string | 否 | 输出音频格式，如 `mp3_22050_32`（mp3，22.05kHz，32kbps） |

### 请求示例

```shell
curl --location 'https://api.modelverse.cn/v1/audio/sound-generation' \
--header 'Authorization: Bearer <YOUR_API_KEY>' \
--header 'Content-Type: application/json' \
--data '{
  "model": "text-to-sound-v2",
  "text": "Spacious braam suitable for high-impact movie trailer moments",
  "duration_seconds": 5.0,
  "output_format": "mp3_22050_32"
}' \
--output sound_effect.mp3
```

### 输出

直接返回音频二进制流，格式由 `output_format` 决定，默认为 mp3。

### 响应头

| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| character-cost | string | 本次生成消耗的字符数 |
