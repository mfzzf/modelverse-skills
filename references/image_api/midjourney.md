# Midjourney API

本文介绍通过 Modelverse 调用 Midjourney 的完整流程，包含文生图、放大、变体和重新生成四个操作。

---

## 模型列表

| 模型名 | 功能 |
|--------|------|
| `midjourney-fast-imagine` | 文生图，输入提示词，返回 4 张图的拼合网格图 |
| `midjourney-fast-upscale` | 放大单张图（U1~U4 及后续二次操作） |
| `midjourney-fast-variation` | 变体，基于某张图重新生成 4 张（V1~V4） |
| `midjourney-fast-reroll` | 重新生成全部 4 张（🔄） |

---

## 服务地址

| 接口 | 方法 | 地址 |
|------|------|------|
| 提交任务 | POST | `https://api.modelverse.cn/v1/tasks/submit` |
| 查询状态 | GET | `https://api.modelverse.cn/v1/tasks/status` |

认证方式：`Authorization: Bearer <your-api-key>`

---

## 工作流

所有 Midjourney 任务均为**异步**执行：

1. `POST /v1/tasks/submit` 提交任务，得到 `task_id`
2. 轮询 `GET /v1/tasks/status?task_id=<task_id>`，直到 `task_status` 为 `Success` 或 `Failure`

---

## 接口详情

### 提交任务

**POST** `https://api.modelverse.cn/v1/tasks/submit`

#### 请求体

```json
{
  "model": "<模型名>",
  "input": {
    "prompt": "<提示词，仅 imagine 需要>"
  },
  "parameters": {
    "mj_task_id": "<上一步操作的 task_id，upscale / variation / reroll 必填>",
    "mj_custom_id": "<buttons 中的 custom_id，upscale / variation / reroll 必填>"
  }
}
```

#### 参数说明

| 字段 | 类型 | 是否必须 | 说明 |
|------|------|----------|------|
| `model` | string | 必须 | 模型名，见上方模型列表 |
| `input.prompt` | string | imagine 必须 | 文生图提示词 |
| `parameters.mj_task_id` | string | upscale / variation / reroll 必须 | 关联的上一步任务 ID |
| `parameters.mj_custom_id` | string | upscale / variation / reroll 必须 | 来自上一步查询结果 `buttons` 中的 `custom_id` |

#### 响应

```json
{
  "output": {
    "task_id": "1775203239196609"
  },
  "request_id": "abc123..."
}
```

---

### 查询任务状态

**GET** `https://api.modelverse.cn/v1/tasks/status?task_id=<task_id>`

#### 响应

```json
{
  "output": {
    "task_id": "1775203239196609",
    "task_status": "Success",
    "urls": ["https://...图片地址..."],
    "submit_time": 1775203239,
    "buttons": [
      {"custom_id": "MJ::JOB::upsample::1::431a5822-...", "label": "U1"},
      {"custom_id": "MJ::JOB::upsample::2::431a5822-...", "label": "U2"},
      {"custom_id": "MJ::JOB::upsample::3::431a5822-...", "label": "U3"},
      {"custom_id": "MJ::JOB::upsample::4::431a5822-...", "label": "U4"},
      {"custom_id": "MJ::JOB::reroll::0::431a5822-...::SOLO", "emoji": "🔄"},
      {"custom_id": "MJ::JOB::variation::1::431a5822-...", "label": "V1"},
      {"custom_id": "MJ::JOB::variation::2::431a5822-...", "label": "V2"},
      {"custom_id": "MJ::JOB::variation::3::431a5822-...", "label": "V3"},
      {"custom_id": "MJ::JOB::variation::4::431a5822-...", "label": "V4"}
    ]
  }
}
```

#### task_status 枚举

| 值 | 含义 |
|----|------|
| `Pending` | 排队中 |
| `Running` | 生成中 |
| `Success` | 成功 |
| `Failure` | 失败，见 `error_message` 字段 |

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `output.task_id` | string | 任务 ID |
| `output.task_status` | string | 任务状态，见上方枚举 |
| `output.urls` | array | 图片直链列表。imagine / variation / reroll 返回 1 张网格拼合图；upscale 返回 1 张单图 |
| `output.submit_time` | integer | 提交时间的 Unix 时间戳（秒） |
| `output.buttons` | array | 可继续操作的按钮列表，每项含 `custom_id` |

---

## 完整示例

### Step 1 — 文生图（imagine）

```bash
curl -X POST https://api.modelverse.cn/v1/tasks/submit \
  -H "Authorization: Bearer $MODELVERSE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "midjourney-fast-imagine",
    "input": {
      "prompt": "a cute cat sitting on a cloud, anime style"
    }
  }'
```

提交后轮询查询接口，直到 `task_status` 为 `Success`：

```bash
curl "https://api.modelverse.cn/v1/tasks/status?task_id=1775203239196609" \
  -H "Authorization: Bearer $MODELVERSE_API_KEY"
```

成功后记录：
- `urls[0]`：4 张图的拼合网格图地址
- `task_id`：后续 upscale / variation / reroll 需要
- `buttons`：后续操作的 `custom_id` 来源

---

### Step 2a — 放大单张（upscale，以 U1 为例）

从 `buttons` 中找到 `label` 为 `"U1"` 的项，取其 `custom_id`：

```bash
curl -X POST https://api.modelverse.cn/v1/tasks/submit \
  -H "Authorization: Bearer $MODELVERSE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "midjourney-fast-upscale",
    "input": {},
    "parameters": {
      "mj_task_id":   "1775203239196609",
      "mj_custom_id": "MJ::JOB::upsample::1::431a5822-bfb2-4c55-8fc5-fc101abebd91"
    }
  }'
```

upscale 成功后同样返回 `buttons`，包含更多二次操作选项（二次放大、Vary、Zoom、Pan、Animate 等），均可继续通过 `midjourney-fast-upscale` 模型发起。

---

### Step 2b — 变体（variation，以 V1 为例）

从 `buttons` 中找到 `label` 为 `"V1"` 的项，取其 `custom_id`：

```bash
curl -X POST https://api.modelverse.cn/v1/tasks/submit \
  -H "Authorization: Bearer $MODELVERSE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "midjourney-fast-variation",
    "input": {},
    "parameters": {
      "mj_task_id":   "1775203239196609",
      "mj_custom_id": "MJ::JOB::variation::1::431a5822-bfb2-4c55-8fc5-fc101abebd91"
    }
  }'
```

variation 成功后返回新的 `buttons`，可继续对新图执行 upscale 等操作。

---

### Step 2c — 重新生成（reroll）

从 `buttons` 中找到 `emoji` 为 `"🔄"` 的项，取其 `custom_id`：

```bash
curl -X POST https://api.modelverse.cn/v1/tasks/submit \
  -H "Authorization: Bearer $MODELVERSE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "midjourney-fast-reroll",
    "input": {},
    "parameters": {
      "mj_task_id":   "1775203239196609",
      "mj_custom_id": "MJ::JOB::reroll::0::431a5822-bfb2-4c55-8fc5-fc101abebd91::SOLO"
    }
  }'
```