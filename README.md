# Aiden-Lite 🏠 - AI 驱动的智能管家

> 一个本地化部署的智能家居 AI 助手系统，结合语音交互、人脸识别、日程管理、设备联动等功能

## 🌟 核心功能

- **🤖 AI 对话引擎** - 基于大模型的自然语言对话，支持连续多轮对话与记忆
- **👤 人脸识别** - 实时摄像头识别，自动匹配人员信息并生成个性化问候
- **📅 日程管理** - 语音创建日程，智能提醒与规划
- **🏠 设备联动** - MQTT 协议支持，米家生态集成，场景自动化
- **🎙️ 语音交互** - 本地语音识别(ASR) + 文字转语音(TTS)，支持唤醒词检测
- **💾 本地优先** - 数据本地存储，隐私安全，网络掉线自动降级

## 🚀 快速开始

### 前置要求
- Python 3.10+
- Windows 11 / Linux / macOS
- 8GB+ RAM (推荐 16GB)
- 摄像头 + 麦克风 + 扬声器

### 环境搭建

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/aiden-lite.git
cd aiden-lite

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境 (Windows)
venv\Scripts\activate
# 或 (Linux/Mac)
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 API Keys
```

### 首次运行

```bash
# 初始化数据库
python scripts/init_db.py

# 启动服务
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# 访问 Web UI
# http://localhost:8000/docs (API 文档)
# http://localhost:8000/ui (Web 界面)
```

## 📁 项目结构

```
aiden-lite/
├── 项目规划/                    # 项目文档
│   ├── 01_项目概述.md
│   ├── 02_技术方案设计.md
│   ├── 03_技术路线图.md
│   ├── 04_工作代办清单.md
│   ├── 05_资源与工具清单.md
│   └── 06_系统架构详设.md
│
├── src/                         # 源代码
│   ├── core/                    # 核心模块
│   │   ├── dialogue/            # 对话引擎
│   │   ├── face/                # 人脸识别
│   │   ├── schedule/            # 日程管理
│   │   ├── device/              # 设备控制
│   │   └── llm/                 # LLM 接口
│   ├── services/                # 服务层
│   │   ├── asr/                 # 语音识别
│   │   ├── tts/                 # 文字转语音
│   │   ├── db/                  # 数据库
│   │   ├── mqtt/                # MQTT 通信
│   │   └── mihome/              # 米家集成
│   ├── utils/                   # 工具函数
│   ├── models/                  # 数据模型
│   ├── database/                # 数据库层
│   └── main.py                  # FastAPI 应用
│
├── tests/                       # 测试代码
├── config/                      # 配置文件
├── scripts/                     # 辅助脚本
├── docker/                      # Docker 配置
├── docs/                        # 文档
├── requirements.txt             # 依赖列表
├── .env.example                 # 环境变量示例
└── README.md                    # 本文件
```

## 📋 主要依赖

### AI 与语言模型
- `openai` - OpenAI API 调用
- `langchain` - LLM 应用框架

### 语音处理
- `faster-whisper` - 本地语音识别 (Whisper)
- `edge-tts` - 文字转语音
- `pyaudio` - 麦克风采集

### 人脸识别
- `face_recognition` - 人脸识别库
- `opencv-python` - 计算机视觉
- `mediapipe` - Google 轻量级检测

### 设备通信
- `paho-mqtt` - MQTT 客户端
- `requests` - HTTP 请求

### 框架与工具
- `fastapi` - Web 框架
- `sqlalchemy` - ORM
- `loguru` - 日志库

更完整的依赖列表见 `requirements.txt`

## 🔑 配置说明

### 必需配置

```env
# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# 语音配置
ASR_MODEL=base        # whisper 模型大小
TTS_PROVIDER=edge     # 文字转语音提供商
LANGUAGE=zh-CN        # 默认语言
```

### 可选配置

```env
# 米家集成
XIAOMI_USERNAME=...
XIAOMI_PASSWORD=...

# MQTT Broker
MQTT_HOST=localhost
MQTT_PORT=1883

# 数据库
DATABASE_URL=sqlite:///./data/aiden.db
```

详见 `.env.example`

## 💡 使用示例

### 对话示例
```
用户: "嘿, 艾登"         (唤醒词)
AI: "我在呢，有什么可以帮助你的?"

用户: "明天上午10点提醒我开会"
AI: "已为你创建日程，明天上午10点提醒开会"

用户: "打开客厅的灯"
AI: "好的，已为你打开客厅的灯"

用户: "现在什么时间了"
AI: "现在是下午 2 点 30 分"
```

### API 调用示例
```bash
# 创建日程
curl -X POST http://localhost:8000/api/schedule \
  -H "Content-Type: application/json" \
  -d '{"title": "开会", "start_time": "2025-01-08T10:00:00"}'

# 控制设备
curl -X POST http://localhost:8000/api/device/light \
  -H "Content-Type: application/json" \
  -d '{"action": "turn_on"}'

# 查询对话记录
curl http://localhost:8000/api/conversation/history
```

## 🏗️ 开发流程

### 第一阶段 (1-10 周): MVP 核心功能
- ✅ 项目基础设施搭建
- ⏳ AI 对话引擎实现
- ⏳ 人脸识别系统
- ⏳ 日程管理模块

### 第二阶段 (11-20 周): 设备联动
- ⏳ MQTT 设备控制
- ⏳ 米家生态集成
- ⏳ 场景自动化

### 第三阶段 (21+ 周): 优化与扩展
- ⏳ 性能优化
- ⏳ 高级功能
- ⏳ 文档与部署

详见 `项目规划/03_技术路线图.md`

## 📚 文档

- **项目概述** - `项目规划/01_项目概述.md`
- **技术方案** - `项目规划/02_技术方案设计.md`
- **技术路线图** - `项目规划/03_技术路线图.md`
- **工作代办清单** - `项目规划/04_工作代办清单.md`
- **资源与工具清单** - `项目规划/05_资源与工具清单.md`
- **系统架构详设** - `项目规划/06_系统架构详设.md`

## 🤝 贡献指南

贡献前，请阅读:
1. 检查现有 Issue
2. Fork 并创建功能分支
3. 提交 Pull Request
4. 等待审核

## ⚖️ 许可证

MIT License

## 📞 联系与支持

- 📧 Email: support@aiden-lite.com
- 💬 讨论区: GitHub Discussions
- 🐛 问题报告: GitHub Issues

## 🙏 鸣谢

感谢以下项目和社区的支持:
- OpenAI Whisper
- FastAPI 框架
- LangChain
- 开源社区

---

**最后更新**: 2025-01-07

