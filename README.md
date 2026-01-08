# Aiden-Lite 🏠 - AI 驱动的智能管家

> 一个本地化部署的智能家居 AI 助手系统，结合人脸识别、监控管理与智能交互

## 🌟 核心功能 (当前进度)

- **👤 智能人脸识别** - 基于 CompreFace SDK，实现高精度实时人脸匹配。
- **📹 Web 实时监控** - FastAPI 驱动的 MJPEG 视频流传输，支持 720P/1080P 高清显示。
- **📊 实时识别日志** - 使用 Server-Sent Events (SSE) 实时推送识别结果到 Web 端。
- **❄️ 智能日志冷却** - 自动过滤重复识别，支持可配置的消失重现冷却机制。
- **🛡️ 相似度过滤** - 客户端级相似度阈值控制，确保识别准确性。
- **🎨 现代化 UI** - 响应式暗色模式 Web 界面，直观展示视频流与识别动态。

## 📁 项目结构

```
aiden-lite/
├── src/                         # 源代码
│   ├── core/                    # 核心逻辑
│   │   ├── camera.py            # 摄像头捕获模块 (线程化)
│   │   ├── face_recognition.py  # 人脸识别 SDK 集成
│   │   ├── visualizer.py        # PIL/OpenCV 混合绘图引擎
│   │   ├── config.py            # 环境变量与常量管理
│   │   ├── events.py            # 全局异步事件与队列
│   │   └── init.py              # 组件全局初始化
│   ├── web/                     # Web 服务
│   │   ├── app.py               # FastAPI 实例与生命周期
│   │   ├── router.py            # HTTP 路由逻辑
│   │   ├── static/              # 静态资源 (图标等)
│   │   └── templates/           # Jinja2 网页模板
│   ├── utils/                   # 工具类
│   │   ├── logger_config.py     # 分级日志配置
│   │   └── log_filter.py        # 日志流过滤处理器
│   └── main.py                  # 应用启动入口
├── ico/                         # 项目图标资源
├── doc/                         # 技术文档
└── .env.actual                  # 核心配置文件
```

## 🚀 快速开始

### 前置要求
- Python 3.10+
- 摄像头 (USB 或内置)
- CompreFace 服务 (本地或云端)

### 运行应用

```bash
# 安装依赖
pip install -r requirements-actual.txt

# 启动程序
python src/main.py
```

访问地址: `http://localhost:8080`

## ⚙️ 关键配置 (.env.actual)

- `CAMERA_WIDTH / CAMERA_HEIGHT`: 设定摄像头分辨率 (推荐 1280x720)
- `SIMILARITY_THRESHOLD`: 识别相似度阈值 (推荐 0.95+)
- `LOG_COOLDOWN`: 同一人脸再次触发日志的冷却时间 (秒)
- `BOX_COLOR / TEXT_COLOR`: 画面标注的颜色配置 (B,G,R)

---
**最后更新**: 2026-01-09
