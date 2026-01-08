# Aiden-Lite API 设计文档

## 一、API 总体设计

### 1.1 基本信息
- **协议**: HTTP/REST + WebSocket
- **基地址**: `http://localhost:8000/api`
- **内容类型**: `application/json`
- **版本**: `v1`
- **认证**: 可选 (Bearer Token)

### 1.2 通用响应格式

#### 成功响应
```json
{
  "code": 0,
  "message": "success",
  "data": {
    // 具体数据
  },
  "timestamp": "2025-01-08T10:30:00Z"
}
```

#### 错误响应
```json
{
  "code": 400,
  "message": "错误描述",
  "error_details": {
    "field": "具体字段错误"
  },
  "timestamp": "2025-01-08T10:30:00Z"
}
```

### 1.3 通用错误码

| 错误码 | 含义 | 说明 |
|--------|------|------|
| 0 | 成功 | 请求成功 |
| 400 | 请求错误 | 参数验证失败 |
| 401 | 未认证 | 需要提供 Token |
| 403 | 无权限 | Token 无效或过期 |
| 404 | 资源不存在 | 数据不存在 |
| 500 | 服务器错误 | 内部服务器错误 |
| 503 | 服务不可用 | 服务暂停或维护 |

---

## 二、对话系统 API

### 2.1 发送消息

**请求**
```
POST /dialogue/chat
```

**请求体**
```json
{
  "message": "打开客厅的灯",
  "user_id": 1,
  "session_id": "abc123",
  "context": {
    "location": "家里",
    "time": "2025-01-08T10:30:00"
  }
}
```

**响应**
```json
{
  "code": 0,
  "data": {
    "response": "好的，我已经为你打开了客厅的灯",
    "response_audio_url": "/audio/response_123.mp3",
    "intent": "device_control",
    "confidence": 0.95,
    "actions": [
      {
        "type": "device_control",
        "device_id": "light_living_room",
        "action": "turn_on"
      }
    ],
    "session_id": "abc123"
  }
}
```

### 2.2 语音输入 (WebSocket)

**连接**
```
WS /dialogue/audio
```

**消息格式**
```json
{
  "type": "audio_chunk",
  "data": "<base64_encoded_audio>",
  "sample_rate": 16000,
  "format": "pcm"
}
```

**响应**
```json
{
  "type": "transcript",
  "text": "打开客厅的灯",
  "confidence": 0.98,
  "is_final": true
}
```

### 2.3 获取对话历史

**请求**
```
GET /dialogue/history?user_id=1&limit=10&offset=0
```

**响应**
```json
{
  "code": 0,
  "data": {
    "conversations": [
      {
        "id": 1,
        "user_id": 1,
        "user_message": "打开客厅的灯",
        "assistant_response": "好的，我已经为你打开了客厅的灯",
        "timestamp": "2025-01-08T10:30:00Z",
        "tokens_used": 45
      }
    ],
    "total": 100,
    "limit": 10,
    "offset": 0
  }
}
```

### 2.4 获取会话信息

**请求**
```
GET /dialogue/session/{session_id}
```

**响应**
```json
{
  "code": 0,
  "data": {
    "session_id": "abc123",
    "user_id": 1,
    "created_at": "2025-01-08T10:00:00Z",
    "last_activity": "2025-01-08T10:30:00Z",
    "message_count": 5,
    "tokens_used": 234
  }
}
```

### 2.5 记忆管理

#### 添加记忆
**请求**
```
POST /memory/add
```

**请求体**
```json
{
  "content": "用户喜欢在晚上8点喝茶",
  "importance": 8,
  "category": "user_preference"
}
```

#### 查询记忆
**请求**
```
GET /memory/search?keywords=喝茶&limit=5
```

**响应**
```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "content": "用户喜欢在晚上8点喝茶",
      "importance": 8,
      "category": "user_preference",
      "access_count": 5,
      "last_accessed": "2025-01-08T10:30:00Z"
    }
  ]
}
```

---

## 三、人脸识别 API

### 3.1 实时人脸识别

**请求**
```
GET /ws /face/recognition
```

**WebSocket 消息**

发送帧:
```json
{
  "type": "frame",
  "data": "<base64_encoded_image>",
  "format": "jpg"
}
```

接收识别结果:
```json
{
  "type": "recognition_result",
  "detected": true,
  "faces": [
    {
      "id": 1,
      "name": "小王",
      "relation": "访客",
      "confidence": 0.96,
      "location": {"x": 100, "y": 150, "width": 150, "height": 200},
      "greeting": "你好，小王，欢迎来访！"
    }
  ],
  "timestamp": "2025-01-08T10:30:00Z"
}
```

### 3.2 人脸库管理

#### 添加人脸
**请求**
```
POST /face/people
```

**请求体**
```json
{
  "name": "小王",
  "relation": "亲戚",
  "occupation": "医生",
  "phone": "13800138000",
  "face_images": ["<base64_image_1>", "<base64_image_2>"]
}
```

**响应**
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "name": "小王",
    "relation": "亲戚",
    "face_count": 2,
    "created_at": "2025-01-08T10:30:00Z"
  }
}
```

#### 获取所有人员
**请求**
```
GET /face/people?limit=20&offset=0
```

**响应**
```json
{
  "code": 0,
  "data": {
    "people": [
      {
        "id": 1,
        "name": "小王",
        "relation": "亲戚",
        "occupation": "医生",
        "face_count": 3
      }
    ],
    "total": 50
  }
}
```

#### 删除人员
**请求**
```
DELETE /face/people/{person_id}
```

### 3.3 识别统计

**请求**
```
GET /face/stats?start_date=2025-01-01&end_date=2025-01-08
```

**响应**
```json
{
  "code": 0,
  "data": {
    "total_recognitions": 156,
    "recognized_people": 12,
    "unknown_faces": 5,
    "recognition_accuracy": 0.97,
    "daily_stats": [
      {
        "date": "2025-01-08",
        "count": 24
      }
    ]
  }
}
```

---

## 四、日程管理 API

### 4.1 创建日程

**请求**
```
POST /schedule/create
```

**请求体**
```json
{
  "title": "客户会议",
  "description": "与 ABC 公司讨论合作事宜",
  "start_time": "2025-01-08T14:00:00",
  "end_time": "2025-01-08T15:00:00",
  "location": "会议室 A",
  "participants": ["张三", "李四"],
  "reminders": [3600, 1800, 0],
  "recurrence": "weekly"
}
```

**响应**
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "title": "客户会议",
    "start_time": "2025-01-08T14:00:00",
    "end_time": "2025-01-08T15:00:00",
    "created_at": "2025-01-08T10:30:00Z"
  }
}
```

### 4.2 查询日程

#### 按时间范围查询
**请求**
```
GET /schedule/range?start=2025-01-08&end=2025-01-15
```

**响应**
```json
{
  "code": 0,
  "data": {
    "schedules": [
      {
        "id": 1,
        "title": "客户会议",
        "start_time": "2025-01-08T14:00:00",
        "end_time": "2025-01-08T15:00:00",
        "location": "会议室 A",
        "status": "upcoming"
      }
    ]
  }
}
```

#### 按人员查询
**请求**
```
GET /schedule/person/{person_id}?date=2025-01-08
```

### 4.3 更新日程

**请求**
```
PUT /schedule/{schedule_id}
```

**请求体**
```json
{
  "title": "客户会议 (改期)",
  "start_time": "2025-01-08T15:00:00",
  "end_time": "2025-01-08T16:00:00"
}
```

### 4.4 删除日程

**请求**
```
DELETE /schedule/{schedule_id}
```

### 4.5 提醒管理

#### 获取待提醒日程
**请求**
```
GET /schedule/reminders/pending?limit=10
```

**响应**
```json
{
  "code": 0,
  "data": [
    {
      "schedule_id": 1,
      "title": "客户会议",
      "start_time": "2025-01-08T14:00:00",
      "remind_at": "2025-01-08T13:30:00",
      "status": "pending"
    }
  ]
}
```

#### 手动触发提醒
**请求**
```
POST /schedule/{schedule_id}/remind
```

---

## 五、设备控制 API

### 5.1 设备列表

**请求**
```
GET /device/list?type=light&location=living_room
```

**响应**
```json
{
  "code": 0,
  "data": {
    "devices": [
      {
        "id": "light_living_room",
        "name": "客厅灯",
        "type": "light",
        "location": "客厅",
        "protocol": "mqtt",
        "status": "on",
        "brightness": 80,
        "color_temp": 4000,
        "last_updated": "2025-01-08T10:30:00Z"
      }
    ]
  }
}
```

### 5.2 设备控制

#### 开/关设备
**请求**
```
POST /device/{device_id}/control
```

**请求体**
```json
{
  "action": "turn_on",
  "params": {}
}
```

#### 调节亮度
**请求**
```
POST /device/{device_id}/control
```

**请求体**
```json
{
  "action": "set_brightness",
  "params": {
    "brightness": 50
  }
}
```

#### 调节温度
**请求**
```
POST /device/{device_id}/control
```

**请求体**
```json
{
  "action": "set_temperature",
  "params": {
    "temperature": 24
  }
}
```

**响应**
```json
{
  "code": 0,
  "data": {
    "device_id": "light_living_room",
    "action": "turn_on",
    "status": "success",
    "new_state": {
      "status": "on"
    }
  }
}
```

### 5.3 场景管理

#### 创建场景
**请求**
```
POST /scene/create
```

**请求体**
```json
{
  "name": "回家模式",
  "description": "打开玄关灯，调节客厅温度",
  "actions": [
    {
      "device_id": "light_entrance",
      "action": "turn_on"
    },
    {
      "device_id": "air_conditioner_living_room",
      "action": "set_temperature",
      "params": {"temperature": 24}
    }
  ],
  "trigger_condition": "face_recognized"
}
```

#### 获取所有场景
**请求**
```
GET /scene/list
```

#### 执行场景
**请求**
```
POST /scene/{scene_id}/execute
```

**响应**
```json
{
  "code": 0,
  "data": {
    "scene_id": 1,
    "name": "回家模式",
    "executed_at": "2025-01-08T18:00:00Z",
    "actions_executed": 2,
    "status": "success"
  }
}
```

### 5.4 房间信息 (米家)

**请求**
```
GET /mihome/rooms
```

**响应**
```json
{
  "code": 0,
  "data": {
    "rooms": [
      {
        "id": "room_1",
        "name": "客厅",
        "devices": ["light_1", "tv_1", "air_conditioner_1"]
      },
      {
        "id": "room_2",
        "name": "卧室",
        "devices": ["light_2", "air_conditioner_2"]
      }
    ]
  }
}
```

---

## 六、系统管理 API

### 6.1 系统状态

**请求**
```
GET /system/status
```

**响应**
```json
{
  "code": 0,
  "data": {
    "status": "healthy",
    "uptime": 86400,
    "version": "0.1.0",
    "database": {
      "status": "connected",
      "tables": 8
    },
    "llm": {
      "status": "connected",
      "provider": "openai",
      "model": "gpt-4"
    },
    "mqtt": {
      "status": "connected",
      "broker": "localhost:1883",
      "subscriptions": 12
    },
    "resources": {
      "cpu_usage": 15.5,
      "memory_usage": 45.2,
      "disk_usage": 20.1
    }
  }
}
```

### 6.2 日志

**请求**
```
GET /system/logs?level=ERROR&limit=50&offset=0
```

**响应**
```json
{
  "code": 0,
  "data": {
    "logs": [
      {
        "timestamp": "2025-01-08T10:30:00Z",
        "level": "ERROR",
        "module": "dialogue",
        "message": "LLM API 超时",
        "details": "Request timeout after 30s"
      }
    ],
    "total": 150
  }
}
```

### 6.3 配置管理

**请求**
```
GET /system/config
```

**响应**
```json
{
  "code": 0,
  "data": {
    "llm": {
      "provider": "openai",
      "model": "gpt-4",
      "temperature": 0.7
    },
    "speech": {
      "asr_model": "base",
      "tts_provider": "edge"
    },
    "face": {
      "recognition_threshold": 0.6,
      "detection_interval": 1.0
    }
  }
}
```

### 6.4 健康检查

**请求**
```
GET /health
```

**响应**
```json
{
  "code": 0,
  "message": "healthy"
}
```

---

## 七、用户管理 API (未来扩展)

### 7.1 获取用户信息

**请求**
```
GET /user/{user_id}
```

### 7.2 更新用户信息

**请求**
```
PUT /user/{user_id}
```

---

## 八、错误处理示例

### 8.1 参数验证错误
```json
{
  "code": 400,
  "message": "参数验证失败",
  "error_details": {
    "start_time": "必须提供开始时间",
    "title": "标题不能为空"
  }
}
```

### 8.2 资源不存在
```json
{
  "code": 404,
  "message": "日程不存在",
  "error_details": {
    "schedule_id": 999
  }
}
```

### 8.3 API 调用失败
```json
{
  "code": 500,
  "message": "调用大模型 API 失败",
  "error_details": {
    "provider": "openai",
    "reason": "API 请求超时"
  }
}
```

---

## 九、速率限制 (Rate Limiting)

- **对话 API**: 10 请求/秒
- **设备控制**: 50 请求/分钟
- **其他 API**: 30 请求/分钟

响应头:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 5
X-RateLimit-Reset: 1609862400
```

---

## 十、认证与授权 (可选)

### 10.1 Bearer Token 认证

**请求头**
```
Authorization: Bearer <token>
```

### 10.2 获取 Token

**请求**
```
POST /auth/token
```

**请求体**
```json
{
  "username": "admin",
  "password": "password"
}
```

---

## 十一、WebSocket 连接管理

### 11.1 连接生命周期

```
连接 → 认证 → 订阅主题 → 接收消息 → 断开连接
```

### 11.2 心跳 (Ping/Pong)

**心跳消息**
```json
{
  "type": "ping",
  "timestamp": "2025-01-08T10:30:00Z"
}
```

**响应**
```json
{
  "type": "pong",
  "timestamp": "2025-01-08T10:30:00Z"
}
```

---

## 十二、API 版本管理

- 当前版本: `v1`
- 版本号在 URL 中: `/api/v1/dialogue/chat`
- 支持向后兼容性
- 废弃的端点会提前 3 个版本通知

---

## 附录: 常见集成例子

### Python 客户端
```python
import requests

# 创建日程
response = requests.post(
    'http://localhost:8000/api/schedule/create',
    json={
        'title': '开会',
        'start_time': '2025-01-08T14:00:00',
        'end_time': '2025-01-08T15:00:00'
    }
)
print(response.json())
```

### JavaScript/React
```javascript
// 发送消息
const response = await fetch('http://localhost:8000/api/dialogue/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: '打开客厅的灯',
    user_id: 1
  })
});
const data = await response.json();
console.log(data);
```

### cURL
```bash
# 获取设备列表
curl http://localhost:8000/api/device/list | jq

# 执行场景
curl -X POST http://localhost:8000/api/scene/1/execute
```

