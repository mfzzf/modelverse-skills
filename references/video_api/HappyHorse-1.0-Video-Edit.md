# HappyHorse-1.0-Video-Edit

视频编辑模型

## 异步提交任务

### 接口

`https://api.modelverse.cn/v1/tasks/submit`

### 输入

| 参数                     | 类型     | 是否必选 | 描述 |
| :----------------------- | :------- | :------- | :--- |
| model                    | string   | 是       | 模型名称，此处为 `happyhorse-1.0-video-edit` |
| input.prompt             | string   | 是       | 文本指令，用于描述视频编辑意图 |
| input.video_url          | string   | 是       | 待编辑视频 URL |
| input.images             | string[] | 否       | 参考图像 URL 列表，最多 5 张 |
| parameters.resolution    | string   | 否       | 生成视频的分辨率档位，可选值：`720P`、`1080P`，默认 `1080P` |
| parameters.watermark     | boolean  | 否       | 是否添加水印，默认 `true` |
| parameters.audio_setting | string   | 否       | 声音控制，可选值：`auto`、`origin`，默认 `auto` |
| parameters.seed          | int      | 否       | 随机数种子，范围 `[0, 2147483647]` |

### 请求示例

```shell
curl --location --globoff 'https://api.modelverse.cn/v1/tasks/submit' \
--header 'Authorization: Bearer <YOUR_API_KEY>' \
--header 'X-DashScope-Async: enable' \
--header 'Content-Type: application/json' \
--data '{
    "model": "happyhorse-1.0-video-edit",
    "input": {
      "prompt": "让视频中的角色穿上参考图中的条纹毛衣",
      "video_url": "https://example.com/input.mp4",
      "images": [
        "https://example.com/reference.webp"
      ]
    },
    "parameters": {
      "resolution": "720P",
      "audio_setting": "origin"
    }
  }'
```

### 输出

| 参数           | 类型   | 描述               |
| :------------- | :----- | :----------------- |
| output.task_id | string | 异步任务的唯一标识 |
| request_id     | string | 请求的唯一标识     |

## 查询任务状态

### 接口

`https://api.modelverse.cn/v1/tasks/status?task_id=<task_id>`

### 输出

| 参数                 | 类型    | 描述                                              |
| :------------------- | :------ | :------------------------------------------------ |
| output.task_id       | string  | 异步任务的唯一标识                                |
| output.task_status   | string  | 任务状态：`Pending`,`Running`,`Success`,`Failure` |
| output.urls          | array   | 视频结果的 URL 列表                               |
| output.submit_time   | integer | 任务提交时间戳                                    |
| output.finish_time   | integer | 任务完成时间戳                                    |
| output.error_message | string  | 失败时返回的错误信息                              |
| usage.duration       | integer | 计费视频时长（秒）                                |
| usage.input_video_duration | number | 输入视频时长（秒）                          |
| usage.output_video_duration | number | 输出视频时长（秒）                         |
| usage.video_count    | integer | 输出视频数量                                      |
| usage.SR             | integer | 输出视频分辨率高度，例如 `720`、`1080`            |
| request_id           | string  | 请求的唯一标识                                    |
